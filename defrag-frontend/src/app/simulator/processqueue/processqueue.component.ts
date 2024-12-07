import { CommonModule } from '@angular/common';
import { Component, OnInit } from '@angular/core';
import { Router, RouterModule } from '@angular/router';
import { BackendApiService } from '../../services/backend-api.service';
import { FormsModule } from '@angular/forms';
import { StorageService } from '../../services/storage-service.service';

@Component({
  selector: 'app-processqueue',
  standalone: true,
  imports: [RouterModule, CommonModule, FormsModule],
  templateUrl: './processqueue.component.html',
  styleUrl: './processqueue.component.css'
})
export class ProcessqueueComponent implements OnInit {

  constructor(private router: Router, private backendApiService : BackendApiService, private storageService : StorageService ) {}
  ngOnInit(): void {
    this.getStatesDefrag();
    
  }

  filters = {
    algoritmo: '',
    is_completed: ''
  };
  
  filteredProcessQueue: any[] = [];
  uniqueAlgorithms: string[] = [];
  
  applyFilters(): void {
    this.filteredProcessQueue = this.processQueue.filter(process => {
      const matchesAlgorithm = this.filters.algoritmo ? process.algoritmo === this.filters.algoritmo : true;
      const matchesStatus = this.filters.is_completed !== '' 
        ? process.is_completed === (this.filters.is_completed === 'true') 
        : true;
      return matchesAlgorithm && matchesStatus;
    });
  }
  


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
  
  extractStats(){
    const stats = this.processQueue.reduce((acc, item) => {
      if (item.is_completed) {
        acc.completed++;
      } else {
        acc.pending++;
      }
      return acc;
    }, { completed: 0, pending: 0 });
    
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
  
  
  getStatesDefrag(): void {
    this.backendApiService.getStatesDefrag().subscribe({
      next: (response: any) => {
        if (response && Array.isArray(response.result)) {
          this.processQueue = response.result.map((item: any, index: number) => {
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
        } else {
          console.error('A resposta não contém um array válido:', response);
          this.processQueue = [];
        }
        this.extractStats();
      },
      error: (error: any) => {
        console.error('Erro ao buscar estados:', error);
      },
    });
  }
    

  
  handleProcessComplete(generated_file_name: string): void {
    const encodedFileName = encodeURIComponent(generated_file_name);  
    this.backendApiService.getStatesDefrag(encodedFileName).subscribe({
      next: (response) => {
        
        console.log('Arquivo recebido:', response);
        this.backendApiService.defrag_result = response;
        this.storageService.setItem('results_data', response);

      },
      complete: () => {
        this.router.navigate(['/results/map']); 
      },
      error: (error) => {
        console.error('Erro ao processar o arquivo:', error);
      },
    });
  }
  }
