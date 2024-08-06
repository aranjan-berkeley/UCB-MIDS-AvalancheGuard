import { Injectable } from '@angular/core';
import { Router } from '@angular/router';
import { HttpClient, HttpResponse } from '@angular/common/http';

import { BehaviorSubject, EMPTY, empty, Observable, throwError} from 'rxjs';
import { map } from 'rxjs/operators';
import { catchError } from 'rxjs/operators';


import { environment } from '@environments/environment';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';

import { User } from '@app/_models';

@Injectable({ providedIn: 'root' })
export class AccountService {
    private userSubject: BehaviorSubject<User | null>;
    public user: Observable<User | null>;
    userToken : any;

    constructor(
        private router: Router,
        private http: HttpClient
    ) {
        this.userSubject = new BehaviorSubject(JSON.parse(localStorage.getItem('user')!));
        this.user = this.userSubject.asObservable();
    }

    public get userValue() {
        return this.userSubject.value;
    }

    private handleErrorObservable (error: Response | any) 
    {
        console.error(error.message || error);
        //console.log("Error in Observable");
        throwError(() => new Error(error.message));
    }

    xxlogin(username: string, password: string):Observable<Object> {
         //class UserPassword { username?: string; password?: string;}
         //const userpassword : UserPassword = {"username":username, "password":password};


        //console.log(userpassword)
        

        return this.http.get<User>(`${environment.apiUrl}/login?username=${username}&password=${password}`)
            .pipe(map(user => {
                // store user details and jwt token in local storage to keep user logged in between page refreshes
                localStorage.setItem('user', JSON.stringify(user));
                this.userSubject.next(user);
                return user;
            }));
    }

    async getToken(username: string, password: string){ 
        console.log("inside get token",username, password);
        const formData = new FormData();
        formData.append("username", username);
        formData.append("password", password);
        localStorage.removeItem('token');

        await this.http.post(`${environment.apiUrl}/token`, formData)
            
            .subscribe((res: any) => { 
                console.log(res); 
                if(res.access_token){ 
                    localStorage.setItem('token',res.access_token);
                }
            })
    }
    
    /** Original login ***
    origlogin(username: string, password: string):Observable<Object> {

       return this.http.get<User>(`${environment.apiUrl}/login?username=${username}&password=${password}`)
           .pipe(map(user => {
               // store user details and jwt token in local storage to keep user logged in between page refreshes
               localStorage.setItem('user', JSON.stringify(user));
               this.userSubject.next(user);
               return user;
           }));
    }
    */
   
    login(username: string, password: string):Observable<Object> {

        this.userToken = localStorage.getItem('token');
        if (!this.userToken){
            this.getToken(username, password);
            this.userToken = localStorage.getItem('token');
        }
        console.log("inside login, token:",this.userToken);
        console.log("inside login:",username, password);
        console.log("calling users/me",`${environment.apiUrl}/users/me`);
        const formData = new FormData();
        formData.append("username", username);
        formData.append("password", password);
        localStorage.removeItem('token');
        localStorage.removeItem('user');

        return this.http.post(`${environment.apiUrl}/token`, formData)

        //return this.http.get<User>(`${environment.apiUrl}/users/me`)
            .pipe(map(res  => {
                console.log("res=",res);
                const rslt = JSON.stringify(res);
                console.log("rslt=",rslt);
                const rslt1 = JSON.parse(rslt);
                console.log("rslt",rslt);
                const usr = JSON.stringify(rslt1.user);
                const acctkn = rslt1.access_token;
                console.log("usr/token",usr,acctkn);
                
                // store user details and jwt token in local storage to keep user logged in between page refreshes
                localStorage.setItem('token',acctkn);
                localStorage.setItem('user', usr);
                this.userSubject.next(JSON.parse(usr));
                return usr;
            }));
     }
 
 
 

    logout() {
        // remove user from local storage and set current user to null
        localStorage.removeItem('user');
        localStorage.removeItem('token');
        
        this.userSubject.next(null);
        this.router.navigate(['/account/login']);
    }

    /*
    x_register(user: User) {
        console.log(`within register : ${environment.apiUrl}/users/register`)
        console.log(`within register : ${user}`)

        let body = JSON.stringify(user);
        return this.http.post(`${environment.apiUrl}/users/register`, body)
    }
    */
    register(user: User): Observable<Object>{
            return this.http.post(`${environment.apiUrl}/users/register`, user, { responseType: 'text' });
          }

    
    /*
    x_getAll() {
        return this.http.get<User[]>(`${environment.apiUrl}/users`);
    }
    */

    getAll() {
        return this.http.get<User[]>(`${environment.apiUrl}/users`);
    }

    getById(username: string) {
        return this.http.get<User>(`${environment.apiUrl}/users/get_user?username=${username}`);
    }

    update(p_user: User) {
        return this.http.post<User>(`${environment.apiUrl}/users/update`, p_user)
            .pipe(map(x => {
                // update stored user if the logged in user updated their own record
                if (p_user.username == this.userValue?.username) {
                    // update local storage
                    const user = { ...this.userValue, ...p_user };
                    localStorage.setItem('user', JSON.stringify(user));

                    // publish updated user to subscribers
                    this.userSubject.next(user);
                }
                return x;
            }));
    }

    delete(username: string) {
        console.log("in accounbt service delete user");
        return this.http.delete(`${environment.apiUrl}/users/delete_user?username=${username}`)
            .pipe(map(x => {
                // auto logout if the logged in user deleted their own record
                if (username == this.userValue?.username) {
                    this.logout();
                }
                return x;
            }));
    }
}