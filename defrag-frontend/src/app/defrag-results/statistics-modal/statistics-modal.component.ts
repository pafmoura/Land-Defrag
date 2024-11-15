import { CommonModule } from '@angular/common';
import { Component, EventEmitter, Input, Output, OnInit } from '@angular/core';
import { StatisticsService } from '../../services/statistics.service';
import { BaseChartDirective } from 'ng2-charts';
import { BarController, ChartData, ChartOptions } from 'chart.js';
import { Chart as ChartJS, Title, Tooltip, Legend, BarElement, CategoryScale, LinearScale } from 'chart.js'; // Importando todos os módulos necessários do Chart.js
import { BackendApiService } from '../../services/backend-api.service';

ChartJS.register(Title, Tooltip, Legend, BarElement, CategoryScale, LinearScale, BarController); // Adicionando BarController


@Component({
  selector: 'app-statistics-modal',
  standalone: true,
  imports: [CommonModule, BaseChartDirective],
  templateUrl: './statistics-modal.component.html',
  styleUrls: ['./statistics-modal.component.css'],
})
export class StatisticsModalComponent implements OnInit {
  @Input() isOpen = false;
  @Output() close = new EventEmitter<void>();

  resultsData: any = null;
  initialSimulation: any = null;

  constructor(private statisticsService: StatisticsService, private backendApiService : BackendApiService) {}

  ngOnInit() {
    this.resultsData = this.backendApiService.defrag_result;
    this.initialSimulation = this.backendApiService.initial_simulation

    console.log('Results Data:', this.resultsData);
    console.log('Initial Simulation:', this.initialSimulation);

    console.log('Number of Changed Owners Parcels:', 
      this.statisticsService.calculateNumberOfChangedOwnersParcels(
        this.resultsData, 
        this.initialSimulation
      ),
    );
    this.updateBarChartData();
  }

  generateBasicStatistics() {
    const basicStatistics = this.statisticsService.generateBasicStatistics(
      this.resultsData,
      this.initialSimulation
    );
    console.log('Basic Statistics:', basicStatistics);
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
    this.barChartData.datasets[0].data = Object.values(ownerPropertyCount).map(o => o.before); // Contagem antes
    this.barChartData.datasets[1].data = Object.values(ownerPropertyCount).map(o => o.after); // Contagem depois
  
console.log('before', this.barChartData.datasets[0].data);
console.log('after', this.barChartData.datasets[1].data);

    const sumBefore = Object.values(ownerPropertyCount).reduce((acc, o) => acc + o.before, 0);
    const sumAfter = Object.values(ownerPropertyCount).reduce((acc, o) => acc + o.after, 0);
  
  }
  
  selectedTab = 'chart1';
  selectTab(tab: string) {
    this.selectedTab = tab;
  }

}


