import { Routes } from '@angular/router';
import { LandingPageComponent } from './landing-page/landing-page.component';
import { SimulatorsetupComponent } from './simulator/simulatorsetup/simulatorsetup.component';
import { ResultsMapComponent } from './defrag-results/results-map/results-map.component';
import { TradesReportComponent } from './defrag-results/trades-report/trades-report.component';
import { ReportPageComponent } from './defrag-results/report-page/report-page.component';
import { LoginComponent } from './login/login.component';
import { ProcessqueueComponent } from './simulator/processqueue/processqueue.component';
import { authGuard } from './auth.guard';

export const routes: Routes = [
    { path: '', component: LandingPageComponent },
    { path: 'home', redirectTo: '', pathMatch: 'full' },
    { path: 'simulator/setup', component: SimulatorsetupComponent, canActivate: [authGuard]},
    { path: 'results/map', component: ResultsMapComponent, canActivate: [authGuard]},
    { path: 'results/report', component: ReportPageComponent, canActivate: [authGuard]},
    {path: 'login', component: LoginComponent, },
    {path: 'processqueue', component: ProcessqueueComponent, canActivate: [authGuard]}


];

