
import { Component, OnInit } from '@angular/core';
import { BackendApiService } from '../../services/backend-api.service';
import * as Leaflet from 'leaflet';
import proj4 from 'proj4';
import { LeafletModule } from '@bluehalo/ngx-leaflet';
import { StorageService } from '../../services/storage-service.service';
import { GeoJsonUtilsService } from '../../services/geo-json-utils.service';
import { CommonModule } from '@angular/common';
import { StatisticsModalComponent } from '../statistics-modal/statistics-modal.component';
import { RouterModule } from '@angular/router';


@Component({
  selector: 'app-results-map',
  standalone: true,
  imports: [LeafletModule, CommonModule, StatisticsModalComponent, RouterModule],
  templateUrl: './results-map.component.html',
  styleUrl: './results-map.component.css'
})
export class ResultsMapComponent implements OnInit {
  results_data: any = null;
  mapInstance!: Leaflet.Map;
  polygonsLayer: Leaflet.FeatureGroup = new Leaflet.FeatureGroup();
  private storageKey = 'results_data';
  isWelcomeModalOpen = true;

  constructor(
    private backendApiService: BackendApiService,
    private storageService: StorageService,
    private geoJsonUtils: GeoJsonUtilsService
  ) {}

  options = {
    layers: [
      Leaflet.tileLayer('https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png', {
        maxZoom: 18,
        attribution: '...'
      })
    ],
    zoom: 5,
    center: Leaflet.latLng(39.3999, -8.2245),
  };

  ngOnInit() {
    const storedData = this.storageService.getItem<any>(this.storageKey)

    if (storedData) {
      console.log('Dados carregados do Storage:', storedData);
      this.results_data = storedData;
      this.geoJsonUtils.addPolygonsFromGeoJSON(this.mapInstance, this.polygonsLayer, this.results_data.gdf);
    } else {
      this.results_data = this.backendApiService.defrag_result;
      if (this.results_data) {
        this.storageService.setItem(this.storageKey, this.results_data); 
        this.geoJsonUtils.addPolygonsFromGeoJSON(this.mapInstance, this.polygonsLayer, this.results_data.gdf);
      }
    }
  }

  onMapReady(map: Leaflet.Map) {
    this.mapInstance = map;
    this.polygonsLayer.addTo(map);
    if (this.results_data) {
      this.geoJsonUtils.addPolygonsFromGeoJSON(this.mapInstance, this.polygonsLayer, this.results_data.gdf);
    }
  }

  isModalOpen = false;
  openStatistics() {
    this.isModalOpen = true;
  }

  closeStatistics() {
    this.isModalOpen = false;
  }

  closeWelcomeModal(){
    this.isWelcomeModalOpen = false;
    this.isToastOpen = true;
  }

  isToastOpen = false;
  openToast() {
    this.isToastOpen = true;
  }

  closeToast() {
    this.isToastOpen = false;
  }

}
