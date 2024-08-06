import { NgModule } from '@angular/core';
import { ReactiveFormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';

import { InfoComponent } from './info.component';


@NgModule({
    imports: [
    CommonModule,
    ReactiveFormsModule,
],
    declarations: [
        InfoComponent
        
    ],
    providers: [],
})
export class InfoModule { }