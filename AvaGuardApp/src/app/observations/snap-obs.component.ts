import { Component, OnInit } from '@angular/core';
import { Router, ActivatedRoute } from '@angular/router';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { first } from 'rxjs/operators';

import { ObservationService } from '@app/_services/observation.service';
import { AlertService } from '@app/_services/alert.service';

@Component({ templateUrl: 'snap-obs.component.html' })
export class SnapObsComponent implements OnInit {
    form!: FormGroup;
    loading = false;
    submitted = false;

    constructor(
        private formBuilder: FormBuilder,
        private route: ActivatedRoute,
        private router: Router,
        private observationService: ObservationService,
        private alertService: AlertService
    ) { }

    ngOnInit() {
        this.form = this.formBuilder.group({
            submitted_user: ['', Validators.required],
            general_location: ['', Validators.required],
            datetime_taken_UTC: ['', Validators.required],
            imagefile_url: ['', [Validators.required]],
            observation_notes: ['', [Validators.required]],
        });
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

        this.loading = true;
        this.observationService.register_observation(this.form.value)
            .pipe(first())
            .subscribe({
                next: () => {
                    this.alertService.success('Observation Entry successful', { keepAfterRouteChange: true });
                    this.router.navigate(['../login'], { relativeTo: this.route });
                },
                error: error => {
                    this.alertService.error(error);
                    this.loading = false;
                }
            });
    }
}