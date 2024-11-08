import { Component, OnInit } from '@angular/core';
import { LeafletModule } from '@bluehalo/ngx-leaflet';
import * as Leaflet from 'leaflet';
import { BackendApiService } from '../../services/backend-api.service';
import proj4 from 'proj4';
import 'proj4leaflet';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';

@Component({
  selector: 'app-simulatorsetup',
  standalone: true,
  imports: [LeafletModule, CommonModule, FormsModule],
  templateUrl: './simulatorsetup.component.html',
  styleUrl: './simulatorsetup.component.css'
})
export class SimulatorsetupComponent implements OnInit {
  mapInstance!: Leaflet.Map;
  polygonsLayer: Leaflet.FeatureGroup = new Leaflet.FeatureGroup();

  epsg3763Projection = '+proj=tmerc +lat_0=39.6682583333333 +lon_0=-8.13310833333333 +k=1 +x_0=0 +y_0=0 +datum=ETRS89 +units=m +no_defs';


  distributionName: string = 'uniform';
  ownersAverageLand: number = 8;
  algorithm: string = 'Maximização de Agregação';
  maxAreaDifference: number = 5500;


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

  constructor(private backendApiService: BackendApiService) {
    proj4.defs('EPSG:3763', this.epsg3763Projection);
  }

  ngOnInit() {
   // this.getLoadedLands();
  }

  onMapReady(map: Leaflet.Map) {
    this.mapInstance = map;
    this.polygonsLayer.addTo(map);
  }

  convertTM06ToLatLng(x: number, y: number): [number, number] {
    const result = proj4('EPSG:3763', 'WGS84', [x, y]);
    return [result[1], result[0]]; 
  }

  numberOfLands : any = 'Por Apurar';
  totalArea : any = 'Por Apurar';

  getNumberOfLands() {
    return this.polygonsLayer.getLayers().length;
  }

  getTotalArea() {
    let totalArea = 0;
  
    this.GeoJSONData.features.forEach((feature: any) => {
      if (feature.properties?.Shape_Area) {
        totalArea += feature.properties.Shape_Area;
      }
    });
  
    totalArea = totalArea / 1000;
  
    totalArea = parseFloat(totalArea.toFixed(2));
  
    console.log(totalArea);
    return totalArea;
  }

  addPolygonsFromGeoJSON(geoJsonData: any) {
    if (!this.mapInstance || !geoJsonData?.features) {
      console.error('Mapa não inicializado');
      return;
    }

    this.polygonsLayer.clearLayers();

    try {
      geoJsonData.features.forEach((feature: any) => {
        if (feature?.geometry?.type === "MultiPolygon") {
          const polygons = feature.geometry.coordinates.map((polygonCoords: any) =>
            polygonCoords.map((coords: any) =>
              coords.map((coordPair: any) => 
                this.convertTM06ToLatLng(coordPair[0], coordPair[1])
              )
            )
          );

          polygons.forEach((polygonCoords: any) => {
            const polygon = Leaflet.polygon(polygonCoords, {
              color: '#FF0000',
              fillColor: '#FFAAAA',
              fillOpacity: 0.5,
              weight: 1
            });

            const properties = feature.properties;
            polygon.bindPopup(`
              <b>Informações da Parcela</b><br>
              ID: ${properties.PAR_ID}<br>
              Área: ${properties.Shape_Area.toFixed(2)} m²<br>
              Proprietário ID: ${properties.OWNER_ID}
            `);

            this.polygonsLayer.addLayer(polygon);
          });
        }
      });

      if (this.polygonsLayer.getLayers().length > 0) {
        const bounds = this.polygonsLayer.getBounds();
        this.mapInstance.flyToBounds(bounds, {
          padding: [50, 50],  
          duration: 1.5,  
         
        });
      }
    } catch (error) {
      console.error('Erro ao processar GeoJSON:', error);
    }

  }

  circumference = 0;
  dashOffset = 0;
  progress = 0;

GeoJSONData: any = {};

  getLoadedLands() {
    this.backendApiService.simulate({
      default_file: 'portalegre.gpkg',
      distribuition_name: this.distributionName,
      owners_average_land: this.ownersAverageLand
    }).subscribe({
      next: (response) => {
        console.log(response);
        this.GeoJSONData = response;
        this.addPolygonsFromGeoJSON(response);
        this.numberOfLands = this.getNumberOfLands();
        this.totalArea = this.getTotalArea();
      },
      error: (error) => {
        console.error('Erro ao carregar dados:', error);
      }
    });
  }
}
