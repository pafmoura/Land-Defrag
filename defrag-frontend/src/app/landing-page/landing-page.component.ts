import { Component } from '@angular/core';
import { HeaderComponent } from '../utils/header/header.component';

@Component({
  selector: 'app-landing-page',
  standalone: true,
  imports: [LandingPageComponent, HeaderComponent],
  templateUrl: './landing-page.component.html',
  styleUrl: './landing-page.component.css'
})
export class LandingPageComponent {

}
