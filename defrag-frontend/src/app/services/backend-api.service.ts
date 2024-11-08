import { HttpClient, HttpClientModule, HttpErrorResponse } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { catchError, Observable, throwError } from 'rxjs';

@Injectable({
  providedIn: 'root',
})



export class BackendApiService {
  private baseUrl = 'http://localhost:8000/api';

  constructor(private http: HttpClient) { }


  
  testConnection(): Observable<any> {
    return this.http.get(`${this.baseUrl}/test_connection`).pipe(
      catchError(this.handleError)
    );
  }


  

  simulate(data: { default_file: string; distribuition_name: string; owners_average_land: number }): Observable<any> {
    const formData = new FormData();
    formData.append('default_file', data.default_file);
    formData.append('distribuition_name', data.distribuition_name);
    formData.append('owners_average_land', data.owners_average_land.toString());
    console.log(formData);

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




}
