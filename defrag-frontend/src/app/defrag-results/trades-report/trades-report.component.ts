import { Component, Input, OnInit } from '@angular/core';
import { BackendApiService } from '../../services/backend-api.service';
import { CommonModule } from '@angular/common';
import { StorageService } from '../../services/storage-service.service';

@Component({
  selector: 'app-trades-report',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './trades-report.component.html',
  styleUrl: './trades-report.component.css'
})
export class TradesReportComponent implements OnInit {
  tradesData: Array<{
    id: string;
    area: number;
    oldOwner: string;
    newOwner: string;
  }> = [];

  private initialKey = 'initial_simulation'; 
  private resultsKey = 'results_data'; 

  constructor(
    private storageService: StorageService,
    private backendApiService: BackendApiService
  ) {}

  ngOnInit(): void {
    this.loadTradesData();
  }

  loadTradesData(): void {
    const initialData = this.storageService.getItem<any>(this.initialKey);
    const resultsData = this.storageService.getItem<any>(this.resultsKey);

    console.log('Initial Data:', initialData);  
    if (initialData && resultsData) {
      console.log('Dados carregados do localStorage.');
      this.generateTradesData(initialData, resultsData);
    } else {
      console.log('Buscando dados da API...');
      this.fetchDataFromAPI();
    }
  }

  fetchDataFromAPI(): void {
    const initialData = this.backendApiService.initial_simulation;
    const resultsData = this.backendApiService.defrag_result;

    if (initialData && resultsData) {
      console.log('Dados carregados da API.');
      this.storageService.setItem(this.initialKey, initialData);
      this.storageService.setItem(this.resultsKey, resultsData);

      this.generateTradesData(initialData, resultsData);
    } else {
      console.error('Erro ao buscar dados do BackendApiService.');
    }
  }

  generateTradesData(initialData: any, resultsData: any): void {
    this.tradesData = resultsData.gdf.features.map((feature: any) => ({
      id: feature.properties?.PAR_ID || 'N/A',
      area: parseFloat(feature.properties?.Shape_Area).toFixed(2) || 0,
      oldOwner: this.findOldOwner(initialData, feature.properties?.PAR_ID),
      newOwner: feature.properties?.OWNER_ID || '0',
    }));
  }

  findOldOwner(initialData: any, parcelId: string): string {
    const matchingFeature = initialData.features.find(
      (feature: any) => feature.properties?.PAR_ID === parcelId
    );
    return matchingFeature?.properties?.OWNER_ID || '0';
  }
}
