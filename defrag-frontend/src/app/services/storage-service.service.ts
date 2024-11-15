import { Injectable } from '@angular/core';

@Injectable({
  providedIn: 'root'
})
export class StorageService {
  private storage: Storage;

  constructor() {
    this.storage = window.localStorage; // Use sessionStorage aqui se preferir
  }

  setItem(key: string, value: any): void {
    try {
      const stringValue = JSON.stringify(value);
      this.storage.setItem(key, stringValue);
    } catch (error) {
      console.error('Erro ao salvar no storage:', error);
    }
  }

  getItem<T>(key: string): T | null {
    try {
      const stringValue = this.storage.getItem(key);
      return stringValue ? JSON.parse(stringValue) as T : null;
    } catch (error) {
      console.error('Erro ao recuperar do storage:', error);
      return null;
    }
  }

  removeItem(key: string): void {
    try {
      this.storage.removeItem(key);
    } catch (error) {
      console.error('Erro ao remover do storage:', error);
    }
  }

  clear(): void {
    try {
      this.storage.clear();
    } catch (error) {
      console.error('Erro ao limpar o storage:', error);
    }
  }
}
