import { Component } from '@angular/core';
import { LeafletModule } from '@bluehalo/ngx-leaflet';
import * as Leaflet from 'leaflet';


@Component({
  selector: 'app-simulatorsetup',
  standalone: true,
  imports: [LeafletModule],
  templateUrl: './simulatorsetup.component.html',
  styleUrl: './simulatorsetup.component.css'
})
export class SimulatorsetupComponent {
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
  
  

}

export const getLayers = (): Leaflet.Layer[] => {
  return [
    new Leaflet.TileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      attribution: '&copy; OpenStreetMap contributors'
    } as Leaflet.TileLayerOptions),
  ] as Leaflet.Layer[];
};

