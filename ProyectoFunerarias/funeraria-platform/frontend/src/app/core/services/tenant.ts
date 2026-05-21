import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
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
   * Aplica el tema directamente desde el environment compilado (sin petición HTTP).
   * Se llama al bootstrap para evitar flash de colores incorrectos.
   */
  applyThemeFromEnvironment(): void {
    const t = environment.tenant;
    if (t?.primaryColor) {
      this.applyTheme({
        primary_color:    t.primaryColor,
        secondary_color:  t.secondaryColor,
        accent_color:     t.accentColor,
        background_color: t.backgroundColor,
        text_color:       t.textColor,
        name:             t.name,
        logo_url:         t.logoUrl,
      });
    }
  }

  /**
   * Resuelve el slug del tenant desde:
   *  1. El environment compilado (baked en build — fuente primaria sin URL params).
   *  2. El primer segmento del hostname (ej: eternidad.funeraria.local → "eternidad").
   *  3. El localStorage (si el usuario ya está autenticado).
   *  4. Fallback: 'eternidad'.
   */
  resolveSlug(): string {
    // Fuente primaria: slug embebido en el environment del build
    if (environment.tenant?.slug) {
      return environment.tenant.slug;
    }

    // Hostname por subdominio (para despliegue con subdominios reales)
    const hostname = window.location.hostname;
    const parts = hostname.split('.');
    if (parts.length >= 2 && parts[0] !== 'localhost' && parts[0] !== 'www') {
      return parts[0];
    }

    // Sesión previa en localStorage
    const fromStorage = localStorage.getItem('tenant_slug');
    if (fromStorage) return fromStorage;

    return 'eternidad';
  }
}
