import { Component, OnInit } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { TenantService } from './core/services/tenant';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [RouterOutlet],
  templateUrl: './app.html',
  styleUrl: './app.css'
})
export class App implements OnInit {
  title = 'funeraria-platform';

  constructor(private tenantService: TenantService) {}

  ngOnInit(): void {
    // 1. Aplica tema desde el environment compilado (instantáneo, sin flash)
    this.tenantService.applyThemeFromEnvironment();

    // 2. Confirma/sobrescribe con datos reales del backend
    const slug = this.tenantService.resolveSlug();
    this.tenantService.getTenantInfo(slug).subscribe({
      next: (config) => this.tenantService.applyTheme(config),
      error: (err) => console.warn('[TenantService] Usando theme del environment:', err)
    });
  }
}
