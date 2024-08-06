import { Injectable } from '@angular/core';
import { HttpRequest, HttpHandler, HttpEvent, HttpInterceptor } from '@angular/common/http';
import { Observable } from 'rxjs';

import { environment } from '@environments/environment';
import { AccountService } from '@app/_services/account.service';

@Injectable()
export class JwtInterceptor implements HttpInterceptor {
    constructor(private accountService: AccountService) { }

    intercept(request: HttpRequest<any>, next: HttpHandler): Observable<HttpEvent<any>> {
        // add auth header with jwt if user is logged in and request is to the api url
        ///console.log("inside the intercept", request)
        const user = this.accountService.userValue;
        const usertoken = localStorage.getItem("token");
        const isLoggedIn = usertoken; //user && usertoken;
        const isApiUrl = request.url.startsWith(environment.apiUrl);

        ///console.log("inside jwt intercept,",user, usertoken, isApiUrl, isLoggedIn);
        if (isLoggedIn && isApiUrl) {
            request = request.clone({
                setHeaders: {
                    Authorization: `Bearer ${usertoken}`
                }
            });
        }
        //console.log("in the jwt intercepter",request);

        return next.handle(request);
    }
}