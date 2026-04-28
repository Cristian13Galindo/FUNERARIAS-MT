import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { CatalogService } from '../../../../core/services/catalog';
import { TenantService } from '../../../../core/services/tenant';

@Component({
  selector: 'app-catalog',
  standalone: true,
  imports: [CommonModule, RouterModule],
  templateUrl: './catalog.html',
  styleUrl: './catalog.css'
})
export class Catalog implements OnInit {
  products: any[] = [];
  filtered: any[] = [];
  activeFilter: string = 'all';
  loading = true;
  tenantSlug = '';

  constructor(
    private catalogService: CatalogService,
    private tenantService: TenantService
  ) {}

  ngOnInit(): void {
    // Resolución dinámica del slug
    this.tenantSlug = this.tenantService.resolveSlug();

    // Cargar y aplicar el tema del tenant
    this.tenantService.getConfig(this.tenantSlug).subscribe({
      next: (config) => this.tenantService.applyTheme(config),
      error: () => {}
    });

    // Cargar catálogo de productos
    this.catalogService.getCatalog(this.tenantSlug).subscribe({
      next: (products) => {
        this.products = products;
        this.filtered = products;
        this.loading = false;
      },
      error: () => (this.loading = false)
    });
  }

  filter(type: string): void {
    this.activeFilter = type;
    this.filtered = type === 'all'
      ? this.products
      : this.products.filter(p => p.type === type);
  }
}

