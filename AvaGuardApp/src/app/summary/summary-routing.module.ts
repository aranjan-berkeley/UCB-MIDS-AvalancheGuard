import { NgModule } from '@angular/core';
import { Routes, RouterModule } from '@angular/router';

import { SummaryLayoutComponent } from './summary-layout.component';
import { SummaryListComponent } from './summary-list.component';
import { Summary1Component } from './summary-1.component';

const routes: Routes = [
    {
        path: '', component: SummaryLayoutComponent,
        children: [
            { path: '', component: SummaryListComponent },
            { path: 'summary1', component: Summary1Component },
            { path: 'summary2', component: Summary1Component },
        ]
    }
];

@NgModule({
    imports: [RouterModule.forChild(routes)],
    exports: [RouterModule]
})
export class SummaryRoutingModule { }