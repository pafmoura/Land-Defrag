import { HttpClient, HttpClientModule, HttpErrorResponse } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { catchError, Observable, throwError } from 'rxjs';

@Injectable({
  providedIn: 'root',
})



export class BackendApiService {
  private baseUrl = 'http://localhost:8000/api';

  public generated_file_name: string = '';
  public initial_simulation: any = null;
  public defrag_result: any = null;

  constructor(private http: HttpClient) { }


  
  testConnection(): Observable<any> {
    return this.http.get(`${this.baseUrl}/test_connection`).pipe(
      catchError(this.handleError)
    );
  }


  

  simulate(data: { file_name: string; distribuition_name: string; owners_average_land: number, gdf_file : any }): Observable<any> {
    const formData = new FormData();
    formData.append('file_name', data.file_name);
    formData.append('distribuition_name', data.distribuition_name);
    formData.append('owners_average_land', data.owners_average_land.toString());
    if(data.gdf_file) {
      formData.append('gdf_file', data.gdf_file);
    }

    return this.http.post(`${this.baseUrl}/simulate`, formData).pipe(
      catchError(this.handleError)
    );
  }


  

  private handleError(error: HttpErrorResponse): Observable<never> {
    let errorMsg = 'Ocorreu um erro desconhecido!';
    if (error.error instanceof ErrorEvent) {
      errorMsg = `Erro do lado do cliente: ${error.error.message}`;
    } else {
      errorMsg = `Erro do lado do servidor: ${error.status} - ${error.message}`;
    }
    console.error(errorMsg);
    return throwError(() => new Error(errorMsg));
  }

  defrag(data: { algorithm_name: string, generated_file_name: string }): Observable<any> {
    console.log(data);
    const formData = new FormData();
    formData.append('algorithm_name', data.algorithm_name);
    formData.append('generated_file_name', data.generated_file_name);
    return this.http.post<any>(`${this.baseUrl}/defrag`, formData);
  }





}
