import { Component, OnInit } from '@angular/core';
import { first } from 'rxjs/operators';
import { Observable } from 'rxjs';

import { SummaryService } from '@app/_services/summary.service';
import { AlertService } from '@app/_services/alert.service';
import {LocationService} from '@app/_services/location.service';

import { HttpClient } from '@angular/common/http';
import { DomSanitizer } from '@angular/platform-browser';


@Component({ templateUrl: 'summary-1.component.html' })  
export class Summary1Component implements OnInit {
    //observations?: any[];
    imgPath: string | any = null;
    loading = false;
    base64Data : any;
    name: any;
    daysold = 3000 ;
    selectedMainArea = "Alps";
    selectedChart = 1;
    mainAreaArray : string[] | any;
    chartList: [] | any;


    constructor(
        private summaryService: SummaryService,
        private alertService: AlertService,
        private locationService: LocationService,
        private sanitizer: DomSanitizer
    ) {}


    ngOnInit() {

        this.mainAreaArray = this.locationService.getMainAreas();
        this.chartList = this.summaryService.getChartList();
        this.loading = false;
        
        console.clear();
        console.log("in summary1 component-> before calling service");
        this.getImageFromService();

    
    }


    getImageFromService() {
        this.loading = true;
        if (!this.daysold){this.daysold = 10000}
        this.summaryService.getSummary1(this.daysold, this.selectedMainArea, this.selectedChart)
        .pipe(first())
        .subscribe({
                next: (img_blob:any) => {
                    console.log("called image service, returned url=",img_blob);
                    var reader = new FileReader();
                    var base64Data;
                    var objectURL;
                    reader.readAsDataURL(img_blob); 
                    reader.onloadend = () =>  {
                        base64Data = reader.result; 
                        console.log("in reader function base64=",base64Data); 
                        console.log("blob=",img_blob);
                        objectURL = this.sanitizer.bypassSecurityTrustUrl(""+ base64Data);
                        console.log("objectURL=",objectURL);                        
                        this.imgPath = objectURL; 
                        this.loading = false;  
                    }

                },
                error: (error: string)  => {
                    this.alertService.error(error);
                    this.loading = false;
                    console.log("in summary1 component-> errored in the service");
                }
        });
  
    }

    onMainAreaChange(){
        //here is where we can call out to other services to use the value selected
        }

}