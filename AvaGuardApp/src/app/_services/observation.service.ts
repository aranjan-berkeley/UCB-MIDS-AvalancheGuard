import { Injectable } from '@angular/core';
import { Router } from '@angular/router';
import { HttpClient } from '@angular/common/http';
import { BehaviorSubject, Observable } from 'rxjs';
import { map } from 'rxjs/operators';

import { environment } from '@environments/environment';

import { Observation } from '@app/_models';

@Injectable({ providedIn: 'root' })
export class ObservationService {
    private observationSubject: BehaviorSubject<Observation | null>;
    public observation: Observable<Observation | null>;

    constructor(
        private router: Router,
        private http: HttpClient
    ) {
        this.observationSubject = new BehaviorSubject(JSON.parse(localStorage.getItem('observation')!));
        this.observation = this.observationSubject.asObservable();
    }

    public get observationValue() {
        return this.observationSubject.value;
    }


    register_observation(observation: Observation, file: File) {
        console.log("Inside regiter obs service");
        const formData: FormData = new FormData();
        Object.entries(observation).forEach(([key, value]) => {
            formData.append(key, value);
          });
        
        // Append the things that are not tracked yet
        formData.append("cracking","False");
        formData.append("collapsing","False");

        const fileName:string = "obsImageFile";const fileExtension:string = "jpg";

        formData.append('file', file, fileName+'.'+fileExtension) ;
        console.log("calling API form data=",formData);
        return this.http.post(`${environment.apiUrl}/observations/register_observation`, formData);
    }





    /*
    logout() {
        // remove user from local storage and set current user to null
        localStorage.removeItem('user');
        this.observationSubject.next(null);
        this.router.navigate(['/account/login']);
    }

    register(user: User) {
        return this.http.post(`${environment.apiUrl}/users/register`, user);
    }
    */

    getAll() {
        return this.http.get<Observation[]>(`${environment.apiUrl}/observations`);
    }

    getById(observation_id: string) {
        return this.http.get<Observation>(`${environment.apiUrl}/observations/get_observation?observation_id=${observation_id}`);
    }

    update(observation_id: string, params: any) {
        return this.http.put(`${environment.apiUrl}/observations/get_observation?observation_id=${observation_id}`, params)
            .pipe(map(x => {
                // update stored user if the logged in user updated their own record
                if (observation_id == this.observationValue?.observation_id) {
                    // update local storage
                    const observation = { ...this.observationValue, ...params };
                    localStorage.setItem('observation', JSON.stringify(observation));

                    // publish updated user to subscribers
                    this.observationSubject.next(observation);
                }
                return x;
            }));
    }

    delete(observation_id: string) {
        console.log("calling api to delete observation id =",observation_id)
        return this.http.delete(`${environment.apiUrl}/observations/delete_observation?observation_id=${observation_id}`)
            .pipe(map(x => {
                
                return x;
            }));
    }
}