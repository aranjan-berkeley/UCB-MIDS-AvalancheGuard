import { Component, OnInit } from '@angular/core';
import { Router, ActivatedRoute } from '@angular/router';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { first } from 'rxjs/operators';

import { AccountService } from '@app/_services/account.service';
import {  AlertService } from '@app/_services/alert.service';

@Component({ templateUrl: 'add-edit.component.html' })
export class AddEditComponent implements OnInit {
    form!: FormGroup;
    username?: string;
    title!: string;
    loading = false;
    submitting = false;
    submitted = false;
    showAdminUserFlag = false;

    constructor(
        private formBuilder: FormBuilder,
        private route: ActivatedRoute,
        private router: Router,
        private accountService: AccountService,
        private alertService: AlertService
    ) { }

    ngOnInit() {
        this.username = this.route.snapshot.params['username'];

        // form with validation rules
        this.form = this.formBuilder.group({
            firstName: ['', Validators.required],
            lastName: ['', Validators.required],
            email: ['', Validators.required],
            username: ['', Validators.required],
            admin_user_flag:[false,Validators.required],
            // password only required in add mode
            password: ['', [Validators.minLength(6), ...(!this.username ? [Validators.required] : [])]]
        });

        this.title = 'Add User';
        if (this.username) {
            // edit mode
            this.title = 'Edit User';
            this.showAdminUserFlag = false;
            this.loading = true;
            this.accountService.getById(this.username)
                .pipe(first())
                .subscribe(x => {
                    console.log("getbyid for edit user:",x)
                    this.form.patchValue(x);
                    this.loading = false;
                    console.log("getbyid for edit user - admin user:",this.accountService.userValue?.admin_user_flag)
                    if (this.accountService.userValue?.admin_user_flag){
                        this.showAdminUserFlag = true;
                    }
                });
        }
    }

    // convenience getter for easy access to form fields
    get f() { return this.form.controls; }

    onSubmit() {
        this.submitted = true;

        // reset alerts on submit
        this.alertService.clear();

        // stop here if form is invalid
        if (this.form.invalid) {
            return;
        }

        this.submitting = true;
        this.saveUser()
            .pipe(first())
            .subscribe({
                next: () => {
                    this.alertService.success('User saved', { keepAfterRouteChange: true });
                    this.router.navigateByUrl('/users');
                },
                error: error => {
                    this.alertService.error(error);
                    this.submitting = false;
                }
            })
    }

    private saveUser() {
        // create or update user based on id param
        return this.username
            ? this.accountService.update( this.form.value)
            : this.accountService.register(this.form.value);
    }
}