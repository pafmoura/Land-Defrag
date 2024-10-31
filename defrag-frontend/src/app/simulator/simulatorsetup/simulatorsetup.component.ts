import { Component } from '@angular/core';
import { LeafletModule } from '@bluehalo/ngx-leaflet';
import * as Leaflet from 'leaflet';
import { BackendApiService } from '../../services/backend-api.service';


@Component({
  selector: 'app-simulatorsetup',
  standalone: true,
  imports: [LeafletModule],
  templateUrl: './simulatorsetup.component.html',
  styleUrl: './simulatorsetup.component.css'
})
export class SimulatorsetupComponent {

  constructor(private backendApiService: BackendApiService) {

   }

  mapInstance!: Leaflet.Map;

  progress: number = 25;
  radius: number = 45;
  circumference: number = 2 * Math.PI * this.radius;

  get dashOffset(): number {
    return this.circumference * (1 - this.progress / 100);
  }

  options = {
    layers: [
      Leaflet.tileLayer('https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png', { maxZoom: 18, attribution: '...' })
    ],
    zoom: 14,
    center: Leaflet.latLng(40.954344, -8.313531),
    
  };
  




  
  ngOnInit() {
  }


  addPolygonToMap() {
    const polygon = Leaflet.polygon([
      [40.955, -8.315],
      [40.955, -8.310],
      [40.950, -8.310],
      [40.950, -8.315]
    ], {
      color: '#FF0000',
      fillColor: '#FFAAAA',
      fillOpacity: 0.5

    });

     // Adiciona eventos de mouseover e mouseout para exibir/esconder o popup
     polygon.on('click', (e) => {
      polygon.bindPopup(`<b>Informações do Polígono</b><br>Área: 50m²<br>Proprietário: Pedro`).openPopup();
    });
    
    polygon.on('click', () => {
      polygon.closePopup();
    });

    polygon.addTo(this.mapInstance);
  }


  onMapReady(map: Leaflet.Map) {
    this.mapInstance = map;
    this.addPolygonToMap();
  }


  getLoadedLands(){
    console.log('Loaded Lands');
    this.backendApiService.simulate({default_file: 'Madeira.gpkg', distribuition_name: 'uniform', owners_average_land: 8}).subscribe(
      (response) => {
        console.log(response);
      },
      (error) => {
        console.log(error);
      }
    );

  }


}

export const getLayers = (): Leaflet.Layer[] => {
  return [
    new Leaflet.TileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      attribution: '&copy; OpenStreetMap contributors'
    } as Leaflet.TileLayerOptions),
  ] as Leaflet.Layer[];
};

