import { CommonModule } from '@angular/common';
import { Component, OnDestroy, OnInit } from '@angular/core';
import { Router, RouterModule } from '@angular/router';
import { BackendApiService } from '../../services/backend-api.service';
import { FormsModule } from '@angular/forms';
import { StorageService } from '../../services/storage-service.service';
import { switchMap, tap } from 'rxjs';
import { interval, Subscription } from 'rxjs';
import { AuthService } from '../../services/auth.service';
import { SseClient } from 'ngx-sse-client';
import { HttpHeaders } from '@angular/common/http';

@Component({
  selector: 'app-processqueue',
  standalone: true,
  imports: [RouterModule, CommonModule, FormsModule],
  templateUrl: './processqueue.component.html',
  styleUrl: './processqueue.component.css'
})
export class ProcessqueueComponent implements OnInit, OnDestroy {
  private eventSource: EventSource | null = null;

  constructor(
    private router: Router,
    private backendApiService: BackendApiService,
    private storageService: StorageService,
    private authService: AuthService,
    private sseClient: SseClient
  ) {}
  private sseSubscription: any;  

  ngOnInit(): void {
    this.connectToSSE();
  }

  ngOnDestroy(): void {
    if (this.sseSubscription) {
      this.sseSubscription.unsubscribe(); 
    }

  }

  filters = {
    algoritmo: '',
    is_completed: '',
  };

  filteredProcessQueue: any[] = [];
  uniqueAlgorithms: string[] = [];

  processQueue: {
    id: number;
    is_completed: boolean;
    generated_file_name: string;
    algoritmo: string;
    distribuicao: string;
    avg: string;
  }[] = [];

  numberOfProcesses = 0;
  processesCompleted = 0;

  connectToSSE(): void {
    const url = 'http://localhost:8000/api/sse'; 
    const headers = new HttpHeaders().set('Authorization', `Token ${this.authService.getToken()}`);

    this.sseSubscription = this.sseClient
    .stream(url, { keepAlive: true, reconnectionDelay: 1000, responseType: 'event' }, { headers }, 'GET')  
    .subscribe(
      (event) => {
        if (event.type === 'error') {
          const errorEvent = event as ErrorEvent;
          console.error('Erro SSE:', errorEvent.error, errorEvent.message);
        } else {
          const messageEvent = event as MessageEvent;
          console.info('Evento SSE recebido:', messageEvent);
          
          this.handleSSEData(messageEvent);
        }
      },
      (error) => {
        console.error('Erro na conexão SSE:', error);
      }
    );
  
  }

  handleSSEData(messageEvent: MessageEvent): void {
    try {
      const data = JSON.parse(messageEvent.data);  

      if (Array.isArray(data)) {
        this.processQueue = data.map((item: any, index: number) => {
          const details = this.extractDetails(item.generated_file_name);
          return {
            ...item,
            id: index + 1,
            algoritmo: details.algoritmo,
            distribuicao: details.distribuicao,
            avg: details.avg,
          };
        });

        this.uniqueAlgorithms = [...new Set(this.processQueue.map(item => item.algoritmo))];
        this.applyFilters();
        this.extractStats();
      }
    } catch (error) {
      console.error('Erro ao processar dados SSE:', error);
    }
  }





  applyFilters(): void {
    this.filteredProcessQueue = this.processQueue.filter((process) => {
      const matchesAlgorithm = this.filters.algoritmo ? process.algoritmo === this.filters.algoritmo : true;
      const matchesStatus =
        this.filters.is_completed !== ''
          ? process.is_completed === (this.filters.is_completed === 'true')
          : true;
      return matchesAlgorithm && matchesStatus;
    });
  }

  extractStats(): void {
    const stats = this.processQueue.reduce(
      (acc, item) => {
        if (item.is_completed) {
          acc.completed++;
        } else {
          acc.pending++;
        }
        return acc;
      },
      { completed: 0, pending: 0 }
    );

    this.numberOfProcesses = this.processQueue.length;
    this.processesCompleted = stats.completed;
    console.log('Estatísticas extraídas:', this.numberOfProcesses, this.processesCompleted);
  }

  extractDetails(fileName: string): { algoritmo: string; distribuicao: string; avg: string } {
    const parts = fileName.split('/');

    return {
      algoritmo: parts[0],
      distribuicao: parts[1],
      avg: parts[2],
    };
  }

  handleProcessComplete(generated_file_name: string, old_file_name: string): void {
    const encodedFileName = encodeURIComponent(generated_file_name);

    this.backendApiService
      .getStatesDefrag(encodedFileName)
      .pipe(
        tap((response) => {
          console.log('Arquivo recebido:', response);
          this.backendApiService.defrag_result = response;
          this.storageService.setItem('results_data', response);
        }),
        switchMap(() => this.backendApiService.getSimulationByFilename(old_file_name))
      )
      .subscribe({
        next: (simulationResponse) => {
          console.log('Simulação recebida:', simulationResponse);
          this.storageService.setItem('initial_simulation', simulationResponse.gdf);
          this.router.navigate(['/results/map']);
        },
        error: (error) => {
          console.error('Erro no processo:', error);
        },
      });
  }
}