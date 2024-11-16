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

  sortDirection: { [key: string]: boolean } = {
    id: true,
    area: true,
    oldOwner: true,
    newOwner: true,
    owners: true, 
  };

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

    if (initialData && resultsData) {
      this.generateTradesData(initialData, resultsData);
    } else {
      this.fetchDataFromAPI();
    }
  }

  fetchDataFromAPI(): void {
    const initialData = this.backendApiService.initial_simulation;
    const resultsData = this.backendApiService.defrag_result;

    if (initialData && resultsData) {
      this.storageService.setItem(this.initialKey, initialData);
      this.storageService.setItem(this.resultsKey, resultsData);
      this.generateTradesData(initialData, resultsData);
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

  activeSort: string = '';
  findOldOwner(initialData: any, parcelId: string): string {
    const matchingFeature = initialData.features.find(
      (feature: any) => feature.properties?.PAR_ID === parcelId
    );
    return matchingFeature?.properties?.OWNER_ID || '0';
  }

  sortTable(column: string): void {
    this.activeSort = column;
  
    const direction = this.sortDirection[column];
    this.tradesData = [...this.tradesData].sort((a, b) => {
      if (column === 'owners') {
        const ownerA = a.oldOwner === a.newOwner ? '' : `${a.oldOwner}→${a.newOwner}`;
        const ownerB = b.oldOwner === b.newOwner ? '' : `${b.oldOwner}→${b.newOwner}`;
        return direction
          ? ownerA.localeCompare(ownerB)
          : ownerB.localeCompare(ownerA);
      }
  
      const aValue = a[column as keyof typeof a];
      const bValue = b[column as keyof typeof b];
  
      if (typeof aValue === 'string' && typeof bValue === 'string') {
        return direction ? aValue.localeCompare(bValue) : bValue.localeCompare(aValue);
      }
  
      if (typeof aValue === 'number' && typeof bValue === 'number') {
        return direction ? aValue - bValue : bValue - aValue;
      }
  
      return 0; 
    });
  
    this.sortDirection[column] = !direction;
  }
  
  
}  