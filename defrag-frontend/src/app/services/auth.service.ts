import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable, tap } from 'rxjs';

@Injectable({
  providedIn: 'root',
})
export class AuthService {
  private loginUrl = 'http://localhost:8000/login/'; 

  constructor(private http: HttpClient) {}

  login(username: string, password: string): Observable<any> {
    return this.http.post(this.loginUrl, { username, password }).pipe(
      tap((response: any) => {
        if (response.token) {
          this.saveToken(response.token);
          this.setCookie('username', username, 7); // Expira em 7 dias
        }
      })
    );
  }

  saveToken(token: string): void {
    this.setCookie('authToken', token, 7); // Expira em 7 dias
  }

  getToken(): string | null {
    return this.getCookie('authToken');
  }

  logout(): void {
    this.deleteCookie('authToken');
    this.deleteCookie('username');
  }

  isLoggedIn(): boolean {
    return !!this.getToken();
  }

  // Métodos auxiliares para manipular cookies
  private setCookie(name: string, value: string, days: number): void {
    const date = new Date();
    date.setTime(date.getTime() + days * 24 * 60 * 60 * 1000);
    document.cookie = `${name}=${value};expires=${date.toUTCString()};path=/`;
  }

  private getCookie(name: string): string | null {
    const nameEQ = name + '=';
    const cookies = document.cookie.split(';');
    for (let i = 0; i < cookies.length; i++) {
      let c = cookies[i];
      while (c.charAt(0) === ' ') c = c.substring(1, c.length);
      if (c.indexOf(nameEQ) === 0) return c.substring(nameEQ.length, c.length);
    }
    return null;
  }

  private deleteCookie(name: string): void {
    document.cookie = `${name}=;expires=Thu, 01 Jan 1970 00:00:00 UTC;path=/`;
  }
}
