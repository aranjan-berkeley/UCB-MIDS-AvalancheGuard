import { Injectable } from '@angular/core';
import { Router } from '@angular/router';
import { HttpClient, HttpResponse } from '@angular/common/http';

import { catchError } from 'rxjs/operators';
import { environment } from '@environments/environment';
import { throwError } from 'rxjs';

@Injectable({ providedIn: 'root' })
export class LocationService {
    locDB : any;

    constructor(
        private router: Router,
        private http: HttpClient
    ) {
    }


    private handleErrorObservable (error: Response | any) 
    {
        console.error(error.message || error);
        //console.log("Error in Observable");
        throwError(() => new Error(error.message));
    }

    public getMainAreas():string[]{
        let mainAreaList = [];
        mainAreaList.push("Alps");
        mainAreaList.push("Colorado");
        mainAreaList.push("Tahoe-Sierras");
        mainAreaList.push("Unknown");
        return mainAreaList;
    }
    public getAreas(x:string):string[]{
        let areaList = [];
        if (x== "Alps"){
            areaList.push("Tirol");
            areaList.push("Bavaria");
        }
        if (x== "Tahoe-Sierras"){
            areaList.push("North-West Tahoe");
            areaList.push("North-East Tahoe");
            areaList.push("South-West Tahoe");
            areaList.push("South-East Tahoe");
        }
        if (x== "Colorado"){
            areaList.push("North-West Tahoe");
            areaList.push("Aspen");
            areaList.push("Front Range");
            areaList.push("Grand Mesa");
            areaList.push("Gunnison");
            areaList.push("Northern San Juan");
            areaList.push("Southern San Juan");
            areaList.push("Sawatch");
            areaList.push("Vail and Summit County");
            areaList.push("Sangre de Cristo");

        }
        if (x== "Unknown"){
            areaList.push("Unknown");
            
        }
        return areaList;
    }


}