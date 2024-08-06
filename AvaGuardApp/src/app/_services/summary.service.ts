import { Injectable } from '@angular/core';
import { Router } from '@angular/router';
import { HttpClient } from '@angular/common/http';
import { BehaviorSubject, Observable } from 'rxjs';
import { map } from 'rxjs/operators';

import { environment } from '@environments/environment';

import { Observation } from '@app/_models';

@Injectable({ providedIn: 'root' })
export class SummaryService {
    //private observationSubject: BehaviorSubject<Observation | null>;
    //public observation: Observable<Observation | null>;

    constructor(
        private router: Router,
        private http: HttpClient
    ) {
        //this.observationSubject = new BehaviorSubject(JSON.parse(localStorage.getItem('observation')!));
        //this.observation = this.observationSubject.asObservable();
    }

    public get observationValue() {
        return ""//this.observationSubject.value;
    }

    public getChartList():any{
        let chartList = [];
        chartList.push({"key":1,"value":"Summary-Table"});
        chartList.push({"key":2,"value":"Summary-Bar-By-Area"});
        chartList.push({"key":3,"value":"Summary-Map"});
        chartList.push({"key":4,"value":"Others"});
        chartList.push({"key":5,"value":"Another Map"});
        
        return chartList;
    }

    getSummary1(d: number, mainarea:string, chart:number):Observable<Blob> {
        console.clear();
        console.log("In summary service-> getSummary1", d, mainarea);
        return this.http.get(`${environment.apiUrl}/summary1?daysold=${d}&mainArea=${mainarea}&chartnum=${chart}`,
            { responseType: 'blob' });
    }

 
    






}