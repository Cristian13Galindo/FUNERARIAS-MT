import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../../environments/environment';

@Injectable({ providedIn: 'root' })
export class CatalogService {
  private readonly publicAPI = `${environment.apiUrl}/public`;
  private readonly adminAPI = `${environment.apiUrl}/admin/products`;

  constructor(private http: HttpClient) { }

  // ── Public endpoints ──────────────────────────────────────────────────────
  getCatalog(tenantSlug: string, type?: string): Observable<any[]> {
    let params: any = { tenant_slug: tenantSlug };
    if (type) params['type'] = type;
    return this.http.get<any[]>(`${this.publicAPI}/catalog`, { params });
  }

  sendContact(payload: any): Observable<any> {
    return this.http.post(`${this.publicAPI}/contact`, payload);
  }

  // ── Admin endpoints ───────────────────────────────────────────────────────
  listProducts(type?: string): Observable<any[]> {
    let params: any = {};
    if (type) params['type'] = type;
    return this.http.get<any[]>(`${this.adminAPI}/`, { params });
  }

  createProduct(product: any): Observable<any> {
    return this.http.post(`${this.adminAPI}/`, product);
  }

  updateProduct(id: string, product: any): Observable<any> {
    return this.http.put(`${this.adminAPI}/${id}`, product);
  }

  deleteProduct(id: string): Observable<any> {
    return this.http.delete(`${this.adminAPI}/${id}`);
  }
}
