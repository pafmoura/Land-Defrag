import { Injectable } from '@angular/core';
import { BackendApiService } from './backend-api.service';
import { StorageService } from './storage-service.service';


@Injectable({
  providedIn: 'root',
})
export class StatisticsService {
  constructor(
    private backendApiService: BackendApiService,
    private storageService: StorageService
  ) {}

  getResultsData(): any {
    let resultsData = this.storageService.getItem<any>('results_data');
    if (!resultsData) {
      resultsData = this.backendApiService.defrag_result;
      if (resultsData) {
        this.storageService.setItem('results_data', resultsData);
      }
    }
    return resultsData;
  }

  getInitialSimulation(): any {
    let initialSimulation = this.storageService.getItem<any>('initial_simulation');
    if (!initialSimulation) {
      initialSimulation = this.backendApiService.initial_simulation;
      if (initialSimulation) {
        this.storageService.setItem('initial_simulation', initialSimulation);
      }
    }
    return initialSimulation;
  }

  calculateNumberOfChangedOwnersParcels(resultsData: any, initialSimulation: any): number {
    let changedOwners = 0;

    resultsData.gdf.features.forEach((feature: any) => {
      const initialFeature = initialSimulation.features.find(
        (initialFeature: any) =>
          initialFeature.properties?.id === feature.properties?.id
      );

      if (feature.properties?.OWNER_ID !== initialFeature?.properties?.OWNER_ID) {
        changedOwners++;
      }
    });

    return changedOwners;
  }

  generateBasicStatistics(resultsData: any, initialSimulation: any): any {
    return {
      numberOfParcels: resultsData.gdf.features.length,
      numberOfChangedOwnersParcels: this.calculateNumberOfChangedOwnersParcels(
        resultsData,
        initialSimulation
      ),
    };
  }
}
