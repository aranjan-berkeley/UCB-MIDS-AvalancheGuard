import { Component, OnInit } from '@angular/core';
import { first } from 'rxjs/operators';

import { AccountService } from '@app/_services/account.service';


//import { GuiColumn } from '@generic-ui/ngx-grid';
//import { GuiGridModule } from '@generic-ui/ngx-grid';

@Component({ templateUrl: 'list.component.html' })
export class ListComponent implements OnInit {
    users?: any[];
    isDeleting: any = false;

    constructor(private accountService: AccountService) {}

    ngOnInit() {
        this.accountService.getAll()
            .pipe(first())
            .subscribe(users => {this.users = users; 
                                //console.log("users:",users);
                                //console.log("this.users = ",this.users);
                            });
        
            
    }

    deleteUser(id: string) {
        if(confirm("Are you sure to delete ")){
                const observation = this.users!.find(x => x.username === id);
                this.isDeleting = true;
                console.log("going to call service to delete observatiobn id=", id);
                this.accountService.delete(id)
                    .pipe(first())
                    .subscribe(() => {
                        this.users = this.users!.filter(x => x.username !== id);
                        this.isDeleting = false;

                    });
        }
    }



}