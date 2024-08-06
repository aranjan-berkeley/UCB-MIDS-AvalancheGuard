import { Component, OnInit } from '@angular/core';
import { first } from 'rxjs/operators';
import { Observable } from 'rxjs';

import { ObservationService } from '@app/_services/observation.service';
import { HttpClient } from '@angular/common/http';

@Component({ templateUrl: 'list.component.html' })  
export class ListComponent implements OnInit {
    observations?: any[];
    imgPath: string | any = null;


    constructor(private observationService: ObservationService) {}


    ngOnInit() {
        this.observationService.getAll()
            .pipe(first())
            .subscribe(observations => this.observations = observations);
    }

    /*
    clicked(img:any):  {
        console.log(img);
        this.imgPath = img;
        // Open the image in new tab. 
        window.open(this.imgPath, "_blank");
    }
        */
    onClick(img_path: string) {
        console.log(img_path);
        window.open(img_path, "_blank");
    }



    deleteObservation(observation_id: string) {
        if(confirm("Are you sure to delete "))
        {
            const observation = this.observations!.find(x => x.observation_id === observation_id);
            observation.isDeleting = true;
            console.log("going to call service to delete observatiobn id=", observation_id);
            this.observationService.delete(observation_id)
                .pipe(first())
                .subscribe(() => this.observations = this.observations!.filter(x => x.observation_id !== observation_id));
        }
    }


}