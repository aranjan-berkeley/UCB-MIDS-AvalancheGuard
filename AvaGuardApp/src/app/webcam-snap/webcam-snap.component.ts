import { AfterViewInit, Component, ElementRef, ViewChild, EventEmitter, Output } from "@angular/core";

@Component({
  selector: "app-webcam-snap",
  templateUrl: "./webcam-snap.component.html",
  styleUrls: ["./webcam-snap.component.scss"]
})
export class WebcamSnapComponent implements AfterViewInit {
  WIDTH = 640;
  HEIGHT = 480;

  @ViewChild("video")
  public video: ElementRef | any = null;

  @ViewChild("canvas")
  public canvas: ElementRef | any = null;

  @Output() webcam_image_file_emitter = new EventEmitter<File>();

  captures: string[] = [];
  error: any;
  isCaptured: boolean=false;

  async ngAfterViewInit() {
    await this.setupDevices();
  }

  async setupDevices() {
    if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
      try {
        const stream = await navigator.mediaDevices.getUserMedia({
          video: true
        });
        if (stream) {
          this.video.nativeElement.srcObject = stream;
          this.video.nativeElement.play();
          this.error = null;
        } else {
          this.error = "You have no output video device";
        }
      } catch (e) {
        this.error = e;
      }
    }
  }


  capture() {
    this.drawImageToCanvas(this.video.nativeElement);
    const img1 = this.canvas.nativeElement.toDataURL("image/jpeg")

    console.log("Now convert the webcam image to file,",img1)
    
    const date = new Date().valueOf();
    const imageName = date + '.' + "WebcamImage" + '.jpeg';
  
    // Create a Blob from the Data URI of the webcam image
    const imageBlob = img1;
    const imageFile = new File([imageBlob], imageName, { type: 'image/jpeg' });
    
    
    
    
    const captured_image : File = imageFile;//this.canvas.nativeElement.toDataURL("image/jpg");
    console.log("child, image=",captured_image)
    this.captures.push(this.canvas.nativeElement.toDataURL("image/jpeg"));




    this.webcam_image_file_emitter.emit(captured_image);
    
    console.log('Emitted event in child:');
    this.isCaptured = true;
    console.log("length of captures = ",this.captures.length)
  }

  removeCurrent() {
    this.isCaptured = false;
  }

  setPhoto(idx: number) {
    this.isCaptured = true;
    var image = new Image();
    image.src = this.captures[idx];
    this.drawImageToCanvas(image);
  }

  drawImageToCanvas(image: any) {
    this.canvas.nativeElement
      .getContext("2d")
      .drawImage(image, 0, 0) ;//, this.WIDTH, this.HEIGHT);
  }

  dataURItoBlob(dataURI: string) {
    const byteString = window.atob(dataURI);
    const arrayBuffer = new ArrayBuffer(byteString.length);
    const int8Array = new Uint8Array(arrayBuffer);
    for (let i = 0; i < byteString.length; i++) {
      int8Array[i] = byteString.charCodeAt(i);
    }
    const blob = new Blob([int8Array], { type: 'image/jpeg' });
    return blob;
  }
}
