import { Routes } from '@angular/router';
import { LandingPageComponent } from './landing-page/landing-page.component';
import { SimulatorsetupComponent } from './simulator/simulatorsetup/simulatorsetup.component';
import { ResultsMapComponent } from './defrag-results/results-map/results-map.component';
import { TradesReportComponent } from './defrag-results/trades-report/trades-report.component';
import { ReportPageComponent } from './defrag-results/report-page/report-page.component';

export const routes: Routes = [
    { path: '', component: LandingPageComponent },
    { path: 'home', redirectTo: '', pathMatch: 'full' },
    { path: 'simulator/setup', component: SimulatorsetupComponent},
    { path: 'results/map', component: ResultsMapComponent},
    { path: 'results/report', component: ReportPageComponent},


];

