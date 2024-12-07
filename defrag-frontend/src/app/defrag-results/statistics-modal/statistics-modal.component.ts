import { CommonModule } from '@angular/common';
import { Component, EventEmitter, Input, Output, OnInit } from '@angular/core';
import { StatisticsService } from '../../services/statistics.service';
import { BaseChartDirective } from 'ng2-charts';
import { BarController, ChartData, ChartOptions } from 'chart.js';
import { Chart as ChartJS, Title, Tooltip, Legend, BarElement, CategoryScale, LinearScale } from 'chart.js'; 
import { BackendApiService } from '../../services/backend-api.service';
import * as Leaflet from 'leaflet';
import proj4 from 'proj4';
import { LeafletModule } from '@bluehalo/ngx-leaflet';
import { FormsModule } from '@angular/forms';
import { GeoJsonUtilsService } from '../../services/geo-json-utils.service';
import { StorageService } from '../../services/storage-service.service';

ChartJS.register(Title, Tooltip, Legend, BarElement, CategoryScale, LinearScale, BarController); 


@Component({
  selector: 'app-statistics-modal',
  standalone: true,
  imports: [CommonModule, BaseChartDirective, LeafletModule, FormsModule],
  templateUrl: './statistics-modal.component.html',
  styleUrls: ['./statistics-modal.component.css'],
})
export class StatisticsModalComponent implements OnInit {
  @Input() isOpen = false;
  @Output() close = new EventEmitter<void>();

  resultsData: any = null;
  initialSimulation: any = null;

  constructor(private statisticsService: StatisticsService, private storageService: StorageService, private backendApiService : BackendApiService, private geoJsonUtilsService: GeoJsonUtilsService,) {}
  ownersList: string[] = [];
  filteredOwner: string | null = null;
  filteredLayer: Leaflet.FeatureGroup = new Leaflet.FeatureGroup();
  mapInstance!: Leaflet.Map;
  polygonsLayer: Leaflet.FeatureGroup = new Leaflet.FeatureGroup();

  ngOnInit() {
    this.resultsData = this.backendApiService.defrag_result;
    if(this.backendApiService.initial_simulation){
      this.initialSimulation = this.backendApiService.initial_simulation;
    }else{  
      this.initialSimulation = this.storageService.getItem<any>("initial_simulation");

    }


    console.log('Results Data:', this.resultsData);
    console.log('Initial Simulation:', this.initialSimulation);

    console.log('Number of Changed Owners Parcels:', 
      this.statisticsService.calculateNumberOfChangedOwnersParcels(
        this.resultsData, 
        this.initialSimulation
      ),
    );

    const ownerSet = new Set<string>();
    this.initialSimulation.features.forEach((feature: any) => {
      const ownerId = feature.properties?.OWNER_ID;
      if (ownerId) {
        ownerSet.add(ownerId);
      }
    });
    this.ownersList = Array.from(ownerSet);

    //sort
    this.ownersList.sort((a, b) => {
      return Number(a) - Number(b);
    });

    this.updateBarChartData();
  }

  mapOptions = {
    layers: [
      Leaflet.tileLayer(
        'https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png',
        {
          maxZoom: 18,
          attribution: '...',
        }
      ),
    ],
    zoom: 5,
    center: Leaflet.latLng(39.3999, -8.2245),

  };

  onMapReady(map: Leaflet.Map) {
    this.mapInstance = map;
    this.polygonsLayer.addTo(map);
    this.filteredLayer.addTo(map); 


    if (this.resultsData && this.resultsData.gdf) {
      const filteredPolygons = this.filterPolygonsByOwner(this.resultsData.gdf, this.filteredOwner);
      this.geoJsonUtilsService.addPolygonsFromGeoJSON(this.mapInstance, this.polygonsLayer, filteredPolygons);
    }
  }

  private filterPolygonsByOwner(geoJsonData: any, owner: string | null): any {
    if (!geoJsonData || !owner) {
      console.warn('Dados do GeoJSON não fornecidos.');
      return geoJsonData; 
    }

    const filteredFeatures = geoJsonData.features.filter((feature: any) => {
      return feature.properties?.OWNER_ID === Number(owner);
    });

    return { ...geoJsonData, features: filteredFeatures };
  }


  private calculateOwnerAreas(data: any): { [ownerId: string]: number } {
    const ownerAreas: { [ownerId: string]: number } = {};
  
    data.features.forEach((feature: any) => {
      const ownerId = feature.properties?.OWNER_ID;
      const area = feature.properties?.Shape_Area || 0;
  
      if (!ownerAreas[ownerId]) {
        ownerAreas[ownerId] = 0;
      }
  
      ownerAreas[ownerId] += area; // Soma a área
    });
  
    return ownerAreas;
  }
  
  

  onOwnerChange(ownerId: string) {
    console.log('Owner Changed:', ownerId);
    this.filteredOwner = ownerId;
    this.updateMapWithFilteredData();
  }

  updateMapWithFilteredData() {
    if (!this.mapInstance || !this.resultsData) return;
  
    this.polygonsLayer.clearLayers();
    this.filteredLayer.clearLayers();
  
    this.geoJsonUtilsService.addPolygonsWithBorders(
      this.mapInstance,
      this.polygonsLayer,
      this.resultsData.gdf,
      'grey' 
    );
  
    const filteredGeoJson = this.filterPolygonsByOwner(this.resultsData.gdf, this.filteredOwner);
  
    if (filteredGeoJson.features.length > 0) {
      this.geoJsonUtilsService.addPolygonsFromGeoJSON(
        this.mapInstance,
        this.filteredLayer,
        filteredGeoJson
      );
    }
  
    // atualizar
    this.mapInstance.invalidateSize();
  
    try {
      const allBounds = new Leaflet.LatLngBounds([]);
      if (this.polygonsLayer.getLayers().length > 0) {
        allBounds.extend(this.polygonsLayer.getBounds());
      }
      if (this.filteredLayer.getLayers().length > 0) {
        allBounds.extend(this.filteredLayer.getBounds());
      }
      this.mapInstance.fitBounds(allBounds);
    } catch (e) {
      console.error('Erro ao ajustar os limites do mapa:', e);
    }
  }
  
  
  
  
  
  
  

  barChartOptions: ChartOptions = {
    responsive: true,
    scales: {
      x: {
        beginAtZero: true
      },
      y: {
        beginAtZero: true
      }
    }
  };

  barChartLabels: string[] = []; 
  barChartData: ChartData<'bar'> = {
    labels: this.barChartLabels,
    datasets: [
      {
        data: [],
        label: 'Antes da Simulação',
        backgroundColor: 'blue',
        barThickness: 20
      },
      {
        data: [], 
        label: 'Depois da Simulação',
        backgroundColor: 'orange',
        barThickness: 20
      }
    ]
  };

  areaBefore: { [ownerId: string]: number } = {};
  areaAfter: { [ownerId: string]: number } = {};
  areaChartLabels: string[] = [];
  areaChartData: ChartData<'bar'> = {
    labels: this.areaChartLabels,
    datasets: [
      {
        data: [],
        label: 'Área Antes da Simulação',
        backgroundColor: 'blue',
        barThickness: 20,
      },
      {
        data: [],
        label: 'Área Depois da Simulação',
        backgroundColor: 'orange',
        barThickness: 20,
      },
    ],
  };

  updateBarChartData() {
    const ownerPropertyCount: { [key: string]: { before: number; after: number } } = {};

    this.initialSimulation.features.forEach((feature: any) => {
      const ownerId = feature.properties?.OWNER_ID;

      if (!ownerPropertyCount[ownerId]) {
        ownerPropertyCount[ownerId] = { before: 0, after: 0 };
      }

      ownerPropertyCount[ownerId].before++;
    });

    this.resultsData.gdf.features.forEach((feature: any) => {
      const ownerId = feature.properties?.OWNER_ID;

      if (!ownerPropertyCount[ownerId]) {
        ownerPropertyCount[ownerId] = { before: 0, after: 0 };
      }

      ownerPropertyCount[ownerId].after++;
    });

    this.barChartLabels = Object.keys(ownerPropertyCount);
    this.barChartData.datasets[0].data = Object.values(ownerPropertyCount).map(o => o.before); 
    this.barChartData.datasets[1].data = Object.values(ownerPropertyCount).map(o => o.after); 

    console.log('before', this.barChartData.datasets[0].data);
    console.log('after', this.barChartData.datasets[1].data);

    const sumBefore = Object.values(ownerPropertyCount).reduce((acc, o) => acc + o.before, 0);
    const sumAfter = Object.values(ownerPropertyCount).reduce((acc, o) => acc + o.after, 0);

    this.areaBefore = this.calculateOwnerAreas(this.initialSimulation);
    this.areaAfter = this.calculateOwnerAreas(this.resultsData.gdf);
    this.areaChartLabels = Object.keys(this.areaBefore);
    this.areaChartData.datasets[0].data = this.areaChartLabels.map(owner => this.areaBefore[owner] || 0);
    this.areaChartData.datasets[1].data = this.areaChartLabels.map(owner => this.areaAfter[owner] || 0);

    console.log('Área Antes:', this.areaChartData.datasets[0].data);
    console.log('Área Depois:', this.areaChartData.datasets[1].data);



  }

  selectedTab = 'chart1';
  selectTab(tab: string) {
    this.selectedTab = tab;
  }
}
