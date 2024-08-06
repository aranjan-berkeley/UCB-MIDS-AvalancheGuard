import { NgModule } from '@angular/core';
import { Routes, RouterModule } from '@angular/router';

import { HomeComponent } from './home/home.component';
import { AuthGuard } from './_helpers';
import { ObservationsModule } from './observations/observations.module';

const accountModule = () => import('./account/account.module').then(x => x.AccountModule);
const usersModule = () => import('./users/users.module').then(x => x.UsersModule);
const observationsModule = () => import('./observations/observations.module').then(x => x.ObservationsModule);
const summaryModule = () => import ('./summary/summary.module').then(x => x.SummaryModule);
 
//const infoModule = () => import ('./info/info.module').then(x => x.InfoModule);

const routes: Routes = [
    { path: '', component: HomeComponent, canActivate: [AuthGuard] },
    { path: 'users', loadChildren: usersModule, canActivate: [AuthGuard] },
    { path: 'observations', loadChildren: observationsModule, canActivate: [AuthGuard] },
    { path: 'account', loadChildren: accountModule },
    { path: 'summary', loadChildren: summaryModule , canActivate: [AuthGuard] },
    //{ path: 'info', loadChildren: infoModule, canActivate: [AuthGuard] },
    

    // otherwise redirect to home
    { path: '**', redirectTo: '' }
];

@NgModule({
    imports: [RouterModule.forRoot(routes)],
    exports: [RouterModule]
})
export class AppRoutingModule { }