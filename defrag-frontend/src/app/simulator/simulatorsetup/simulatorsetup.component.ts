import { Component, OnInit } from '@angular/core';
import { LeafletModule } from '@bluehalo/ngx-leaflet';
import * as Leaflet from 'leaflet';
import { BackendApiService } from '../../services/backend-api.service';
import proj4 from 'proj4';
import 'proj4leaflet';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { GeoJsonUtilsService } from '../../services/geo-json-utils.service';
import { StorageService } from '../../services/storage-service.service';
import { AuthService } from '../../services/auth.service';

@Component({
  selector: 'app-simulatorsetup',
  standalone: true,
  imports: [LeafletModule, CommonModule, FormsModule  ],
  templateUrl: './simulatorsetup.component.html',
  styleUrl: './simulatorsetup.component.css'
})
export class SimulatorsetupComponent implements OnInit {
  mapInstance!: Leaflet.Map;
  polygonsLayer: Leaflet.FeatureGroup = new Leaflet.FeatureGroup();

  isLoading: boolean = false;
  distributionName: string = 'uniform';
  ownersAverageLand: number = 8;
  algorithm: string = 'unico';
  maxAreaDifference: number = 5500;

  isSimulationLoaded = false;

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

  constructor(
    private backendApiService: BackendApiService,
    private router: Router,
    private geoJsonUtils: GeoJsonUtilsService,
    private storageService: StorageService,
    private authService: AuthService
  ) {}

  username: string = '';
  ngOnInit() {

    this.username = localStorage.getItem('username') || '';



  }

  logout() {
    this.authService.logout();
    this.router.navigate(['/login']);
  }
  progress = 0;
  
selectedFile: any;

onFileChange(event: any) {
  const fileList: FileList = event.target.files;

  if (fileList.length > 0) {
    this.selectedFile = fileList[0]; 
    console.log('Selected file:', this.selectedFile);
    this.readFile();
  } else {
    console.error('No file selected');
  }
}

gdf_file : any = null;
readFile() {
  if (!this.selectedFile) {
    console.error('No file to read');
    return;
  }


  const reader = new FileReader();
  reader.readAsArrayBuffer(this.selectedFile); 
  reader.onload = () => {
    if (reader.result != null) {
      const blob = new Blob([reader.result], { type: this.selectedFile.type });
      console.log('Blob created:', blob);
      this.gdf_file = blob;
    }
  };
  reader.onerror = (error) => {
    console.error('Error reading file:', error);
  };
}




  onMapReady(map: Leaflet.Map) {
    this.mapInstance = map;
    this.polygonsLayer.addTo(map);
  }

  numberOfLands: any = 'Por Apurar';
  totalArea: any = 'Por Apurar';

  getNumberOfLands() {
    return this.polygonsLayer.getLayers().length;
  }

  getTotalArea() {
    let totalArea = 0;

    this.initial_simulation.features.forEach((feature: any) => {
      if (feature.properties?.Shape_Area) {
        totalArea += feature.properties.Shape_Area;
      }
    });

    totalArea = totalArea / 1000;
    totalArea = parseFloat(totalArea.toFixed(2));
    console.log(totalArea);
    return totalArea;
  }

  initial_simulation: any = {};

  getLoadedLands() {
    this.isLoading = true;

    this.backendApiService.simulate({
      file_name: this.selectedFile.name,
      distribuition_name: this.distributionName,
      owners_average_land: this.ownersAverageLand,
      gdf_file: this.gdf_file
    }).subscribe({
      next: (response) => {
        console.log(response);
        this.backendApiService.initial_simulation = response.gdf;

        this.storageService.setItem('initial_simulation', response.gdf);

        this.initial_simulation = this.backendApiService.initial_simulation;
        this.backendApiService.generated_file_name = response.generated_file_name;
        this.geoJsonUtils.addPolygonsFromGeoJSON(this.mapInstance, this.polygonsLayer, this.initial_simulation);
        this.numberOfLands = this.getNumberOfLands();
        this.totalArea = this.getTotalArea();
        this.isSimulationLoaded = true;
        this.isLoading = false;
      },
      error: (error) => {
        console.error('Erro ao carregar dados:', error);
      }
    });
  }

  runDefrag() {
    console.log('Iniciando defrag com algoritmo:', this.algorithm);
  
    this.backendApiService.defrag({
      algorithm_name: this.algorithm,
      generated_file_name: this.backendApiService.generated_file_name
    }).subscribe({
      error: (error) => {
        console.error('Erro ao iniciar defrag:', error);
      }
    });
  
    this.router.navigate(['/processqueue']);
  }}