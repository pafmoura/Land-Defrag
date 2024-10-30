import { Routes } from '@angular/router';
import { LandingPageComponent } from './landing-page/landing-page.component';
import { SimulatorsetupComponent } from './simulator/simulatorsetup/simulatorsetup.component';

export const routes: Routes = [
    { path: '', component: LandingPageComponent },
    { path: 'home', redirectTo: '', pathMatch: 'full' },
    { path: 'simulator/setup', component: SimulatorsetupComponent}

];

