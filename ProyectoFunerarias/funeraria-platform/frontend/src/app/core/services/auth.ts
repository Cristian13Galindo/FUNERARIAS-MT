import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, BehaviorSubject, tap } from 'rxjs';
import { Router } from '@angular/router';
import { environment } from '../../../environments/environment';

export interface LoginResponse {
  access_token: string;
  tenant_slug: string;
  user: {
    id: string;
    email: string;
    role: string;
    first_name: string;
    last_name: string;
  };
}

@Injectable({ providedIn: 'root' })
export class AuthService {
  private readonly API = `${environment.apiUrl}/auth`;
  private currentUserSubject = new BehaviorSubject<any>(this.loadUser());
  currentUser$ = this.currentUserSubject.asObservable();

  constructor(private http: HttpClient, private router: Router) {}

  private loadUser() {
    const stored = localStorage.getItem('current_user');
    return stored ? JSON.parse(stored) : null;
  }

  login(email: string, password: string): Observable<LoginResponse> {
    return this.http
      .post<LoginResponse>(`${this.API}/login`, { email, password })
      .pipe(
        tap(res => {
          localStorage.setItem('access_token', res.access_token);
          localStorage.setItem('current_user', JSON.stringify(res.user));
          localStorage.setItem('tenant_slug', res.tenant_slug);
          this.currentUserSubject.next(res.user);
        })
      );
  }

  logout(): void {
    localStorage.removeItem('access_token');
    localStorage.removeItem('current_user');
    localStorage.removeItem('tenant_slug');
    this.currentUserSubject.next(null);
    this.router.navigate(['/login']);
  }

  isLoggedIn(): boolean {
    return !!localStorage.getItem('access_token');
  }

  getCurrentUser() {
    return this.currentUserSubject.value;
  }

  getRole(): string {
    return this.getCurrentUser()?.role ?? '';
  }

  getTenantSlug(): string {
    return localStorage.getItem('tenant_slug') ?? '';
  }

  verify(): Observable<any> {
    return this.http.get(`${this.API}/verify`);
  }
}
