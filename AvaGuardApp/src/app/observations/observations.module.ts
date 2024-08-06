import { NgModule } from '@angular/core';
import { ReactiveFormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';

import { ObservationsRoutingModule } from './observations-routing.module';
import { LayoutComponent } from './layout.component';
import { ListComponent } from './list.component';
import { AddEditComponent } from './add-edit.component';

import {WebcamModule} from 'ngx-webcam';
import { WebcamSnapModule } from "../webcam-snap/webam-snap.module";
import { WebcamSnapComponent } from '@app/webcam-snap/webcam-snap.component';


@NgModule({
    imports: [
    CommonModule,
    ReactiveFormsModule,
    ObservationsRoutingModule,
    WebcamModule,
    WebcamSnapModule
],
    declarations: [
        LayoutComponent,
        ListComponent,
        AddEditComponent
    ],
    providers: [WebcamSnapComponent],
})
export class ObservationsModule { }