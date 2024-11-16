import { Component } from '@angular/core';
import { HeaderComponent } from '../../utils/header/header.component';
import { TradesReportComponent } from '../trades-report/trades-report.component';
import { RouterModule } from '@angular/router';

@Component({
  selector: 'app-report-page',
  standalone: true,
  imports: [HeaderComponent,TradesReportComponent, RouterModule],
  templateUrl: './report-page.component.html',
  styleUrl: './report-page.component.css'
})
export class ReportPageComponent {

}
