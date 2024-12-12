import { HttpClient, HttpClientModule, HttpErrorResponse, HttpHeaders, HttpParams } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { catchError, Observable, throwError } from 'rxjs';
import { AuthService } from './auth.service';

@Injectable({
  providedIn: 'root',
})



export class BackendApiService {
  private baseUrl = 'http://localhost:8000/api';

  public generated_file_name: string = '';
  public initial_simulation: any = null;
  public defrag_result: any = null;

  constructor(private http: HttpClient, private authService : AuthService) { }


  
  testConnection(): Observable<any> {
    return this.http.get(`${this.baseUrl}/test_connection`).pipe(
      catchError(this.handleError)
    );
  }


    private getAuthHeaders(): HttpHeaders {
      const token = this.authService.getToken();
      return new HttpHeaders({
        Authorization: `Token ${token}`,
      });
    }

  simulate(data: { file_name: string; distribuition_name: string; owners_average_land: number, gdf_file : any }): Observable<any> {
    const formData = new FormData();
    formData.append('file_name', data.file_name);
    formData.append('distribuition_name', data.distribuition_name);
    formData.append('owners_average_land', data.owners_average_land.toString());
    if(data.gdf_file) {
      formData.append('gdf_file', data.gdf_file);
    }

    return this.http.post(`${this.baseUrl}/simulate`, formData,{ headers: this.getAuthHeaders() }).pipe(
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
    return this.http.post<any>(`${this.baseUrl}/defrag`, formData,{ headers: this.getAuthHeaders() });
  }


  getStatesDefrag(generatedFileName?: string): Observable<any> {
    let params = new HttpParams();
    if (generatedFileName) {
      params = params.append('generated_file_name', generatedFileName);
    }
  
    if (!generatedFileName) {
      console.log('getStatesDefrag');
      return this.http.get<any>(`${this.baseUrl}/processes`, {
        headers: this.getAuthHeaders(),
        params: params,
      }).pipe(
        catchError(this.handleError)
      );
    }
    else{
      return this.http.get<any>(`${this.baseUrl}/processes/`+generatedFileName, {
        headers: this.getAuthHeaders(),
        params: params,
      }).pipe(
        catchError(this.handleError)
      );

    }
    
  }

  getSimulationByFilename(filename: string): Observable<any> {
    return this.http.get<any>(`${this.baseUrl}/get_simulation_by_filename/${filename}/`, { headers: this.getAuthHeaders() });
  }
  

  





}
