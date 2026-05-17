import { Component, OnInit, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { TenantService } from '../../../../core/services/tenant';
import { CatalogService } from '../../../../core/services/catalog';

@Component({
  selector: 'app-home',
  standalone: true,
  imports: [CommonModule, RouterModule],
  templateUrl: './home.html',
  styleUrl: './home.css'
})
export class Home implements OnInit {
  tenant: any = null;
  featuredProducts: any[] = [];
  tenantSlug = '';

  constructor(
    private tenantService: TenantService,
    private catalogService: CatalogService,
    private cdr: ChangeDetectorRef
  ) {}

  ngOnInit(): void {
    // Resolución dinámica del slug (hostname → localStorage → query → fallback)
    this.tenantSlug = this.tenantService.resolveSlug();

    this.tenantService.getConfig(this.tenantSlug).subscribe({
      next: (data) => {
        this.tenant = data;
        // Aplica colores del tenant como CSS custom properties globales
        this.tenantService.applyTheme(data);
        this.cdr.detectChanges();
      },
      error: () => {
        this.cdr.detectChanges();
      }
    });

    this.catalogService.getCatalog(this.tenantSlug).subscribe({
      next: (products) => {
        this.featuredProducts = products.slice(0, 4);
        this.cdr.detectChanges();
      },
      error: () => {
        this.cdr.detectChanges();
      }
    });
  }
}



