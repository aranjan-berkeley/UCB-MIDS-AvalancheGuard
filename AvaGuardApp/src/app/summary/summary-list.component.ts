import { Component, OnInit } from '@angular/core';
import { first } from 'rxjs/operators';

import { SummaryService } from '@app/_services/summary.service';


//import { GuiColumn } from '@generic-ui/ngx-grid';
//import { GuiGridModule } from '@generic-ui/ngx-grid';

@Component({ templateUrl: 'summary-list.component.html' })
export class SummaryListComponent implements OnInit {


    constructor(private summaryService: SummaryService) {}

    ngOnInit() {
        
    }


}