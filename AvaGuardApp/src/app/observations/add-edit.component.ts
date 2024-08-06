import { AfterViewInit, Component, OnInit } from '@angular/core';
import { Router, ActivatedRoute, RouterModule } from '@angular/router';
import { FormBuilder, FormGroup, Validators, ReactiveFormsModule , FormsModule, FormControl} from '@angular/forms';
import { first } from 'rxjs/operators';
 

import { ObservationService } from '@app/_services/observation.service';
import {  AlertService } from '@app/_services/alert.service';

import { User } from '@app/_models';
import { AccountService } from '@app/_services/account.service';
import { LocationService } from '@app/_services/location.service';

import { ImageFileUploadService } from '@app/_services/image-file-upload.service';

import {formatDate} from '@angular/common';

import { HttpResponse } from '@angular/common/http';

import { CommonModule } from '@angular/common';
////import {WebcamImage, WebcamInitError, WebcamUtil} from 'ngx-webcam';
import { Subject } from 'rxjs/internal/Subject';
import { Observable } from 'rxjs/internal/Observable';

import { WebcamSnapComponent } from '@app/webcam-snap/webcam-snap.component';
//import { WebcamSnapModule } from '@app/webcam-snap/webam-snap.module';
 



@Component({ 
  //standalone: true,
  templateUrl: 'add-edit.component.html' ,
  //providers: [WebcamSnapComponent],
  //styleUrl : 'add-edit.component.css'
  //imports: [ReactiveFormsModule , RouterModule, CommonModule, WebcamModule, FormsModule],

})  
export class AddEditComponent implements OnInit {
  
    WIDTH = 640;
    HEIGHT = 480;
    
    form!: FormGroup;
    observation_id?: string;
    currentDate?: Date;
    title!: string;
    form_mode: string;
    loading = false;
    submitting = false;
    submitted = false;

    using_webcam: boolean = false;

    user: User | null;
    //file: File | null = null;
    currentFile?: File | any;
    currentWebCamFile?: File | any;
    fileUploadMessage = '';
    apiResponseMessage = '';
    fileInfos?: Observable<any>;
    preview = '';
    useSnap=false;

    defCurDate: string | any = ""

    public locstring : any;
    public lat: any;
    public lng: any;

    public mainAreas: any;
    public areas: any;
    public selectedMainArea: string ="";
    public selectedArea: string="";
    public gen_loc : string = "";
  
    // toggle webcam on/off
    public showWebcam = true;
    public allowCameraSwitch = true;
    public multipleWebcamsAvailable = false;
    public deviceId: string ="";
    public videoOptions: MediaTrackConstraints = {
      // width: {ideal: 1024},
      // height: {ideal: 576}
    }

    ////public errors: WebcamInitError[] = [];

    // latest snapshot
    ////public webcamImage: WebcamImage | undefined;
    // webcam snapshot trigger
    private trigger: Subject<void> = new Subject<void>();
    // switch to next / previous / specific webcam; true/false: forward/backwards, string: deviceId
    private nextWebcam: Subject<boolean|string> = new Subject<boolean|string>();


    constructor(
        private formBuilder: FormBuilder,
        private route: ActivatedRoute,
        private router: Router,
        private observationService: ObservationService,
        private alertService: AlertService,
        private accountService: AccountService,
        private locationService: LocationService,
        private imagefileuploadService: ImageFileUploadService,
        private webcamsnap: WebcamSnapComponent
        
    ) {

        this.user = this.accountService.userValue;
        this.form_mode =""
     }
    

    ngOnInit() {
        this.defCurDate = new  Date().toISOString().slice(0, 10)+"T00:00";
        console.log("current time is:",this.defCurDate);
        this.mainAreas = this.locationService.getMainAreas();
        //this.currentDate = new Date().toISOString().substring(0, 16);
        this.gen_loc = "";

        this.observation_id = this.route.snapshot.params['observation_id'];


        this.getLocation()
        console.log("In ngOnInit locstring = ",this.locstring)
 

        // form with validation rules
        this.form = this.formBuilder.group({
            submitted_user: [this.user?.username, Validators.required],
            general_location: [this.gen_loc , Validators.required],
            
            datetime_taken_UTC: [this.defCurDate ,Validators.required],
            avalanche_triggered: [false,Validators.required],
            avalanche_observed: [false,Validators.required],
            avalanche_experienced: [false,Validators.required],
            elevation_type:["above_treeline",Validators.required],

            observation_notes: ['some comments here' , Validators.required],
            // password only required in add mode
            imagefile_url: ['', ]
        });

        

        this.title = 'Add Observation';
        this.form_mode = 'Add'
        if (this.observation_id) {
            // edit mode
            this.form_mode = 'Edit'
            this.title = `Edit Observation(${this.observation_id})`;
            this.loading = true;
            this.observationService.getById(this.observation_id)
                .pipe(first())
                .subscribe(x => {
                    this.form.patchValue(x);
                    this.loading = false;
                });
        }
    }

    ngOnAfterInit(){
      this.getLocation()
    }

    // convenience getter for easy access to form fields
    get f() { return this.form.controls; }

    onWebCamImageFile(webcamfile: File){
      console.log("parent webcvam image event occured");
      this.currentWebCamFile = webcamfile;
      console.log("Imported webcamfile to parent");
    }

    onUseSnapChange(event:any){
      if (event.target.checked){
        this.using_webcam = true;
      }
      else{
        this.using_webcam = false;
      }
      console.log("in parent, imported snap flag=",this.using_webcam , "use snapshot =", this.using_webcam);
      
    }

    // On submit button call all services
    onSubmit() {
        console.log("Submitted observation "," length of captures from subcomponent=",this.webcamsnap.captures.length);
  
        //this.currentFile = this.webcamsnap.captures[0];
        this.submitted = true;

        // reset alerts on submit
        this.alertService.clear();
        // stop here if form is invalid
        if (this.form.invalid) {
          for (let el in this.form.controls) {
            if (this.form.controls[el].errors) {
              console.log(el)
            }
          }    
          console.log("form is invalid, returining")
          return;
        }
        console.log("form controls;",this.form.controls);
        console.log("now submitting observation");
        this.submitting = true;
        this.saveObservation();
    }

    // save observation and upload dfile 
    saveObservation():any {
        // In edit mode there is no upload of file
        if (this.form_mode == 'Edit'){
          return this.observation_id
             this.observationService.update(this.observation_id!, this.form.value)
        }

        if (this.form_mode == 'Add'){
          console.log("saveobs add mode");
          file_to_upload : File;
          console.log("befoe check", "length of captures from subcomponent=",this.webcamsnap.captures.length, "check box is ",this.using_webcam)
          console.log("webcam image file=",this.currentWebCamFile)
          if (this.using_webcam){
            this.currentFile = this.currentWebCamFile;
            console.log("using snapshot image");
          }

          this.form.addControl("lat", new FormControl(this.lat));
          this.form.addControl("lng", new FormControl(this.lng));

          if (this.currentFile) {
            console.log("has current file");
            this.observationService.register_observation(this.form.value, this.currentFile)
            .pipe(first())
            .subscribe({
                next: () => {
                    this.alertService.success('Observation saved', { keepAfterRouteChange: true });
                    this.router.navigateByUrl('/observations');
                },
                error: error => {
                    this.alertService.error(error);
                    this.submitting = false;
                }
            })

            //.pipe(first())
            //.subscribe({
            //    response => console.log(response.text()),
            //    next: () => {
            //        this.alertService.success('Observation saved', { keepAfterRouteChange: true });
            //        this.router.navigateByUrl('/observations');
            //    },
            //    error: error => {
            //        this.alertService.error(error);
            //        this.submitting = false;
            //    }
            //})
              
          }
        }
        else {
            console.log("error form mdoe not known");
        }
        
    }

    onFilechange(event: any) {
        //this.message = '';
        this.preview = '';
        const selectedFiles = event.target.files;
    
        if (selectedFiles) {
          const file: File | null = selectedFiles.item(0);
    
          if (file) {
            this.preview = '';
            this.currentFile = file;
            console.log("Current file has been set now", this.currentFile);      
            const reader = new FileReader();
      
            reader.onload = (e: any) => {
              console.log(e.target.result);
              this.preview = e.target.result;
            };    
      
            reader.readAsDataURL(this.currentFile);
          }
        } 
     
        console.log(event.target.files[0])
        this.currentFile = event.target.files[0]
    }
    
    /*
    xxuploadImageFile(): void {
        if (this.currentFile) {
          this.imagefileuploadService.upload(this.currentFile).subscribe({
            next: (event: any) => {
              if (event instanceof HttpResponse) {
                this.fileUploadMessage = event.body.message;
                this.fileInfos = this.imagefileuploadService.getFiles();
              }
            },
            error: (err: any) => {
              console.log(err);
    
              if (err.error && err.error.message) {
                this.fileUploadMessage = err.error.message;
              } else {
                this.fileUploadMessage = 'Could not upload the file!';
              }
            },
            complete: () => {
              this.currentFile = undefined;
            },
          });
        }
    }
    */
    /*
    //Webcam related
    public triggerSnapshot(): void {
      this.trigger.next();
    }
  
    public toggleWebcam(): void {
      this.showWebcam = !this.showWebcam;
    }
  
    public handleInitError(error: WebcamInitError): void {
      this.errors.push(error);
    }
  
    public showNextWebcam(directionOrDeviceId: boolean|string): void {
      // true => move forward through devices
      // false => move backwards through devices
      // string => move to device with given deviceId
      this.nextWebcam.next(directionOrDeviceId);
    }
  
    public handleImage(webcamImage: WebcamImage): void {
      console.info('received webcam image', webcamImage);
      this.webcamImage = webcamImage;
    }
  
    public cameraWasSwitched(deviceId: string): void {
      console.log('active device: ' + deviceId);
      this.deviceId = deviceId;
    }
  
    public get triggerObservable(): Observable<void> {
      return this.trigger.asObservable();
    }
  
    public get nextWebcamObservable(): Observable<boolean|string> {
      return this.nextWebcam.asObservable();
    } 
    */
  


    getLocation() :String {
      if (navigator.geolocation) {
        locstring : String
        navigator.geolocation.getCurrentPosition((position: GeolocationPosition) => {
          if (position) {
            //console.log("Latitude: " + position.coords.latitude +
            //  "Longitude: " + position.coords.longitude);
            this.lat = position.coords.latitude;
            this.lng = position.coords.longitude;
            this.locstring = "Latitude="+this.lat +" , Longitude="+ this.lng
            console.log("Inside the getLocation, lat=",this.lat);
            console.log("Inside the getLocation, lng=",this.lat);
            console.log("Inside the getLocation, locstring=",this.locstring);
            
          }
        },
          (error: GeolocationPositionError) => console.log(error));
      } else {
        alert("Geolocation is not supported by this browser.");
      }

      console.log("Exiting the getLocation, locstring=",this.locstring);
      return this.locstring

    }

    updateMainArea(e: any){
      this.selectedMainArea = e.target.value;
      this.areas = this.locationService.getAreas(this.selectedMainArea);
      //this.form.controls['arealist'].patchValue(this.areas[0])
      this.form.controls['general_location'].patchValue(null);
    }
    updateArea(e: any){
      this.selectedArea = e.target.value;
      if (this.selectedArea && this.selectedMainArea 
        && this.selectedArea != "" 
        && this.selectedMainArea != ""
        && this.selectedMainArea != "null"
        && this.selectedArea != "null" 
        ){
        this.form.controls['general_location'].patchValue(this.selectedMainArea + "/" +this.selectedArea);
      }
    }


 
    
}