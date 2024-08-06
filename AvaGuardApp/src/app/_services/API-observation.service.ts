import { Injectable } from '@angular/core';
import { HttpClient, HttpRequest, HttpEvent } from '@angular/common/http';
import { Observable } from 'rxjs';
import { BehaviorSubject} from 'rxjs';
import { environment } from '@environments/environment';
import { Observation } from '@app/_models';

@Injectable({
  providedIn: 'root'
})
export class APIObservationService {
  private baseUrl = environment.apiUrl; //'http://localhost:8080';
  private observationSubject: BehaviorSubject<Observation | null>;
  public observation: Observable<Observation | null>;


  constructor(private http: HttpClient) {
    this.observationSubject = new BehaviorSubject(JSON.parse(localStorage.getItem('observation')!));
    this.observation = this.observationSubject.asObservable();
  }


  register_observation(observation: Observation, file: File) {
    const formData: FormData = new FormData();

    formData.append('file', file);

    const req = new HttpRequest('POST', `${this.baseUrl}/submit_obs`, formData, {
      responseType: 'json'
    });

    return this.http.post(`${environment.apiUrl}/submit_obs`, observation);
}



  xupload(file: File): Observable<HttpEvent<any>> {
    const formData: FormData = new FormData();

    formData.append('file', file);

    const req = new HttpRequest('POST', `${this.baseUrl}/submit_obs`, formData, {
      responseType: 'json'
    });

    return this.http.request(req);
  }

  xgetFiles(): Observable<any> {
    return this.http.get(`${this.baseUrl}/files`);
  }
}
