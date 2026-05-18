import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, tap } from 'rxjs';
import { environment } from '../../../environments/environment';

@Injectable({ providedIn: 'root' })
export class TenantService {
  private readonly API = `${environment.apiUrl}/public`;

  constructor(private http: HttpClient) {}

  /**
   * Obtiene la información pública del tenant por slug.
   * Alias explícito `getConfig` para que los componentes lo usen con nombre semántico.
   */
  getTenantInfo(slug: string): Observable<any> {
    return this.http.get(`${this.API}/tenant`, { params: { slug } });
  }

  getConfig(slug: string): Observable<any> {
    return this.getTenantInfo(slug);
  }

  /**
   * Aplica los colores del tenant como CSS custom properties globales.
   * Esto permite que cualquier componente los consuma con var(--primary-color).
   */
  applyTheme(config: {
    primary_color?: string;
    secondary_color?: string;
    accent_color?: string;
    background_color?: string;
    text_color?: string;
    name?: string;
    logo_url?: string;
  }): void {
    const root = document.documentElement;
    if (config.primary_color) {
      root.style.setProperty('--primary-color', config.primary_color);
    }
    if (config.secondary_color) {
      root.style.setProperty('--secondary-color', config.secondary_color);
    }
    if (config.accent_color) {
      root.style.setProperty('--accent-color', config.accent_color);
    }
    if (config.background_color) {
      root.style.setProperty('--background-color', config.background_color);
    }
    if (config.text_color) {
      root.style.setProperty('--text-color', config.text_color);
    }
    if (config.name) {
      document.title = config.name;
    }
  }

  /**
   * Resuelve el slug del tenant desde:
   *  1. El localStorage (si el usuario ya está autenticado).
   *  2. El primer segmento del hostname (ej: eternidad.funeraria.local → "eternidad").
   *  3. El parámetro ?tenant=slug de la query string.
   *  4. Fallback: 'eternidad' (para desarrollo local).
   */
  resolveSlug(): string {
    const params = new URLSearchParams(window.location.search);
    const fromQuery = params.get('tenant');
    if (fromQuery) return fromQuery;

    const hostname = window.location.hostname;
    const parts = hostname.split('.');
    if (parts.length >= 2 && parts[0] !== 'localhost' && parts[0] !== 'www') {
      return parts[0];
    }

    const fromStorage = localStorage.getItem('tenant_slug');
    if (fromStorage) return fromStorage;

    return 'eternidad'; // fallback para desarrollo local
  }
}
