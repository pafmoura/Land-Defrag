import { Injectable } from '@angular/core';
import * as Leaflet from 'leaflet';
import proj4 from 'proj4';
import { StorageService } from './storage-service.service';

@Injectable({
  providedIn: 'root'
})
export class GeoJsonUtilsService {
  private epsg3763Projection = '+proj=tmerc +lat_0=39.6682583333333 +lon_0=-8.13310833333333 +k=1 +x_0=0 +y_0=0 +datum=ETRS89 +units=m +no_defs';
  private ownerColorMap: Map<string, string> = new Map();
  private readonly STORAGE_KEY = 'ownerColors';

  constructor(private storageService: StorageService) {
    proj4.defs('EPSG:3763', this.epsg3763Projection);
    this.loadColorsFromStorage();
  }

  private loadColorsFromStorage(): void {
    const storedColors = this.storageService.getItem<Record<string, string>>(this.STORAGE_KEY);
    if (storedColors) {
      this.ownerColorMap = new Map(Object.entries(storedColors));
    }
  }

  private saveColorsToStorage(): void {
    const colorsObject = Object.fromEntries(this.ownerColorMap);
    this.storageService.setItem(this.STORAGE_KEY, colorsObject);
  }

  convertTM06ToLatLng(x: number, y: number): [number, number] {
    const result = proj4('EPSG:3763', 'WGS84', [x, y]);
    return [result[1], result[0]]; 
  }

  generateColorPalette(count: number): string[] {
    const colors: string[] = [];
    for (let i = 0; i < count; i++) {
      const hue = (i * 360) / count;
      colors.push(`hsl(${hue}, 70%, 50%)`);
    }
    return colors;
  }

  addPolygonsFromGeoJSON(
    map: Leaflet.Map, 
    layerGroup: Leaflet.FeatureGroup, 
    gdf: any
  ): void {
    if (!map) {
      console.error('Mapa não inicializado');
      return;
    }

    if (!gdf?.features || gdf.features.length === 0) {
      console.error('Dados GeoJSON ausentes ou inválidos');
      return;
    }

    layerGroup.clearLayers();

    const uniqueOwners: string[] = Array.from(
      new Set(gdf.features.map((feature: any) => feature.properties.OWNER_ID as string))
    );

    // Gera cores apenas para novos proprietários
    const newOwners = uniqueOwners.filter(ownerId => !this.ownerColorMap.has(ownerId));
    if (newOwners.length > 0) {
      const newColors = this.generateColorPalette(newOwners.length);
      newOwners.forEach((ownerId, index) => {
        this.ownerColorMap.set(ownerId, newColors[index]);
      });
      // Salva as novas cores no storage
      this.saveColorsToStorage();
    }

    try {
      gdf.features.forEach((feature: any) => {
        if (feature?.geometry?.type === "MultiPolygon") {
          const polygons = feature.geometry.coordinates.map((polygonCoords: any) =>
            polygonCoords.map((coords: any) =>
              coords.map((coordPair: any) => 
                this.convertTM06ToLatLng(coordPair[0], coordPair[1])
              )
            )
          );

          polygons.forEach((polygonCoords: any) => {
            const ownerColor = this.ownerColorMap.get(feature.properties.OWNER_ID) || '#000000';
            const polygon = Leaflet.polygon(polygonCoords, {
              color: ownerColor,
              fillColor: ownerColor,
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

            layerGroup.addLayer(polygon);
          });
        }
      });

      if (layerGroup.getLayers().length > 0) {
        const bounds = layerGroup.getBounds();
        map.flyToBounds(bounds, {
          padding: [50, 50],
          duration: 1.5
        });
      }
    } catch (error) {
      console.error('Erro ao processar GeoJSON:', error);
    }
  }

  clearColorMap(): void {
    this.ownerColorMap.clear();
    this.storageService.removeItem(this.STORAGE_KEY);
  }
}