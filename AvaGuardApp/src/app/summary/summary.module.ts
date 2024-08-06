import { NgModule } from '@angular/core';
import { ReactiveFormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';


import { SummaryRoutingModule } from './summary-routing.module';
import { SummaryLayoutComponent } from './summary-layout.component';
import {SummaryListComponent} from './summary-list.component'
import { Summary1Component } from './summary-1.component';
import { FormsModule } from '@angular/forms';  // <<<< import it here

@NgModule({
    imports: [
        CommonModule,
        ReactiveFormsModule,
        SummaryRoutingModule,
        FormsModule
    ],
    declarations: [
        SummaryLayoutComponent,
        SummaryListComponent,
        Summary1Component
         
    ]
})
export class SummaryModule { }