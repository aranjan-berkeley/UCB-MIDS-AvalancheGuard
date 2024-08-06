import { Injectable } from '@angular/core';
import { HttpRequest, HttpResponse, HttpHandler, HttpEvent, HttpInterceptor, HTTP_INTERCEPTORS } from '@angular/common/http';
import { Observable, of, throwError } from 'rxjs';
import { delay, materialize, dematerialize } from 'rxjs/operators';
import { HttpClient } from '@angular/common/http';

// array in local storage for registered users
const usersKey = 'avalancheguard-users';
let users: any[] = JSON.parse(localStorage.getItem(usersKey)!) || [];
// array in local storage for registered observations
const observationsKey = 'avalancheguard-observations';
let observations: any[] = JSON.parse(localStorage.getItem(observationsKey)!) || [];


@Injectable()
export class BackendInterceptor implements HttpInterceptor {
    intercept(request: HttpRequest<any>, next: HttpHandler): Observable<HttpEvent<any>> {
        const { url, method, headers, body } = request;

        console.log('url being used is ${url}',url)
        console.log(headers)
        console.log(body)

        return handleRoute();

        function handleRoute() {
            switch (true) {
                case url.endsWith('/users/authenticate') && method === 'POST':
                    return authenticate();
                case url.endsWith('/users/register') && method === 'POST':
                    return register();
                case url.endsWith('/users') && method === 'GET':
                    return getUsers();
                case url.match(/\/users\/\d+$/) && method === 'GET':
                    return getUserById();
                case url.match(/\/users\/\d+$/) && method === 'PUT':
                    return updateUser();
                case url.match(/\/users\/\d+$/) && method === 'DELETE':
                    return deleteUser();

                case url.endsWith('/observations/register_observation') && method === 'POST':
                    return register_observation();
                case url.endsWith('/observations') && method === 'GET':
                    return getObservations();
                case url.match(/\/observations\/\d+$/) && method === 'GET':
                    return getObservationById();
                case url.match(/\/observations\/\d+$/) && method === 'PUT':
                    return updateObservation();
                case url.match(/\/observations\/\d+$/) && method === 'DELETE':
                    return deleteObservation();
                        
                default:
                    // pass through any requests not handled above
                    return next.handle(request);
            }    
        }

        // route functions

        function authenticate() {
            const { username, password } = body;
            const user = users.find(x => x.username === username && x.password === password);
            if (!user) return error('Username or password is incorrect');
            return ok({
                ...basicDetails(user),
                token: 'fake-jwt-token'
            })
        }

        function register() {
            const user = body
            console.log('user=',user)
            console.log('users=',users)

            if (users.find(x => x.username === user.username)) {
                return error('Username "' + user.username + '" is already taken')
            }
            if (users.find(x => x.email === user.email)) {
                return error('Email "' + user.email + '" is already associated with another user')
            }


            user.id = users.length ? Math.max(...users.map(x => x.id)) + 1 : 1;
            users.push(user);
            localStorage.setItem(usersKey, JSON.stringify(users));
            console.log('registered user: ',usersKey,JSON.stringify(users) )
            return ok();
        }

        function registerAPIV() {
            const user = body

            if (users.find(x => x.username === user.username)) {
                return error('Username "' + user.username + '" is already taken')
            }

            user.id = users.length ? Math.max(...users.map(x => x.id)) + 1 : 1;
            users.push(user);
            localStorage.setItem(usersKey, JSON.stringify(users));

            //this.http.post(this.apiUrl, register, httpOptions)
            //.pipe( catchError(this.handleError('addHero', hero))
       

            return ok();
        }






        function getUsers() {
            if (!isLoggedIn()) return unauthorized();
            return ok(users.map(x => basicDetails(x)));
        }

        function getUserById() {
            if (!isLoggedIn()) return unauthorized();

            const user = users.find(x => x.id === idFromUrl());
            return ok(basicDetails(user));
        }

        function updateUser() {
            if (!isLoggedIn()) return unauthorized();

            let params = body;
            let user = users.find(x => x.id === idFromUrl());

            // only update password if entered
            if (!params.password) {
                delete params.password;
            }

            // update and save user
            Object.assign(user, params);
            localStorage.setItem(usersKey, JSON.stringify(users));

            return ok();
        }

        function deleteUser() {
            if (!isLoggedIn()) return unauthorized();

            users = users.filter(x => x.id !== idFromUrl());
            localStorage.setItem(usersKey, JSON.stringify(users));
            return ok();
        }

        // Observations
        function register_observation() {
            const observation = body
            observation.id = observations.length ? Math.max(...observations.map(x => x.id)) + 1 : 1;
            observations.push(observation);
            localStorage.setItem(observationsKey, JSON.stringify(observations));
            return ok();
        }

        function register_observation_API() {
            const observation = body
            
            observations.push(observation);
            localStorage.setItem(observationsKey, JSON.stringify(observations));
            return ok();
        }


        /////////////////////////////////////////////////////////////////////

        function getObservations() {
            if (!isLoggedIn()) return unauthorized();
            return ok(observations.map(x => basicDetails_observation(x)));
        }

        function getObservationById() {
            if (!isLoggedIn()) return unauthorized();

            const observation = observations.find(x => x.id === idFromUrl());
            return ok(basicDetails_observation(observation));
        }


        function updateObservation() {
            if (!isLoggedIn()) return unauthorized();

            let params = body;
            let observation = observations.find(x => x.id === idFromUrl());

            // only update password if entered
            if (!params.img_loc) {
                delete params.img_loc;
            }

            // update and save observation
            Object.assign(observation, params);
            localStorage.setItem(observationsKey, JSON.stringify(observations));

            return ok();
        }

        function deleteObservation() {
            if (!isLoggedIn()) return unauthorized();

            observations = observations.filter(x => x.id !== idFromUrl());
            localStorage.setItem(observationsKey, JSON.stringify(observations));
            return ok();
        }

        function basicDetails_observation(observation: any) {
            const { id, username, obsLocation, datetaken, img_loc } = observation;
            return { id, username, obsLocation, datetaken, img_loc};
        }


        // helper functions

        function ok(body?: any) {
            return of(new HttpResponse({ status: 200, body }))
                .pipe(delay(500)); // delay observable to simulate server api call
        }

        function error(message: string) {
            return throwError(() => ({ error: { message } }))
                .pipe(materialize(), delay(500), dematerialize()); // call materialize and dematerialize to ensure delay even if an error is thrown (https://github.com/Reactive-Extensions/RxJS/issues/648);
        }

        function unauthorized() {
            return throwError(() => ({ status: 401, error: { message: 'Unauthorized' } }))
                .pipe(materialize(), delay(500), dematerialize());
        }

        function basicDetails(user: any) {
            const { id, username, firstName, lastName, email } = user;
            return { id, username, firstName, lastName, email };
        }

        function isLoggedIn() {
            return headers.get('Authorization') === 'Bearer fake-jwt-token';
        }

        function idFromUrl() {
            const urlParts = url.split('/');
            return parseInt(urlParts[urlParts.length - 1]);
        }
    }
}

export const BackendProvider = {
    // use fake backend in place of Http service for backend-less development
    provide: HTTP_INTERCEPTORS,
    useClass: BackendInterceptor,
    multi: true
};