import { ComponentFixture, TestBed } from '@angular/core/testing';

import { WebcamSnapComponent } from './webcam-snap.component';

describe('WebcamSnapComponent', () => {
  let component: WebcamSnapComponent;
  let fixture: ComponentFixture<WebcamSnapComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [WebcamSnapComponent]
    })
    .compileComponents();
    
    fixture = TestBed.createComponent(WebcamSnapComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
