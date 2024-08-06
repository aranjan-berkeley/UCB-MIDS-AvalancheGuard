import { NgModule } from "@angular/core";
import { CommonModule } from "@angular/common";
import { WebcamSnapComponent } from "./webcam-snap.component";

@NgModule({
  imports: [CommonModule],
  declarations: [WebcamSnapComponent],
  exports: [WebcamSnapComponent]
})
export class WebcamSnapModule {}