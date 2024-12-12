import { Component, OnInit } from '@angular/core';
import { HeaderComponent } from '../../utils/header/header.component';
import { TradesReportComponent } from '../trades-report/trades-report.component';
import { RouterModule } from '@angular/router';
import { BackendApiService } from '../../services/backend-api.service';
import { StorageService } from '../../services/storage-service.service';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-report-page',
  standalone: true,
  imports: [HeaderComponent,TradesReportComponent, RouterModule, CommonModule],
  templateUrl: './report-page.component.html',
  styleUrl: './report-page.component.css'
})
export class ReportPageComponent implements OnInit {
  
  storage : Storage;
  constructor(private backendApiService: BackendApiService, private storageService : StorageService) {
    this.storage = window.localStorage;
  }

  results_data: any = null;

  number_of_parcels = 0;
  aggregation_error = 0;
  rmse = 0;
  how_better = 0;

  ngOnInit(): void {
    this.results_data = this.storageService.getItem<any>('results_data');
    if (!this.results_data) {
      this.results_data = this.backendApiService.defrag_result;
    }
    
    console.log(this.results_data);
    this.aggregation_error = this.results_data.stats.aggregation_error;
    this.rmse = this.results_data.stats.error_diff;

    this.number_of_parcels = this.results_data.gdf.features.length;
    this.how_better = (1 - this.results_data.stats.aggregation_error) * 100
  }
  



}
