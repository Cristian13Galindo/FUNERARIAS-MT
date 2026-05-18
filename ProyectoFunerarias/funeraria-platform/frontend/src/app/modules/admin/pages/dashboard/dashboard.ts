import { Component, OnInit, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { AuthService } from '../../../../core/services/auth';
import { CatalogService } from '../../../../core/services/catalog';
import { TenantService } from '../../../../core/services/tenant';

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [CommonModule, RouterModule],
  templateUrl: './dashboard.html',
  styleUrl: './dashboard.css'
})
export class Dashboard implements OnInit {
  user: any = null;
  totalProducts = 0;
  flowers = 0;
  coffins = 0;
  loading = true;

  constructor(
    private authService: AuthService,
    private catalogService: CatalogService,
    private tenantService: TenantService,
    private cdr: ChangeDetectorRef
  ) {}

  ngOnInit(): void {
    this.user = this.authService.getCurrentUser();
    const slug = this.tenantService.resolveSlug();
    this.tenantService.getConfig(slug).subscribe({
      next: (config: any) => this.tenantService.applyTheme(config)
    });
    this.catalogService.listProducts().subscribe({
      next: (products) => {
        this.totalProducts = products.length;
        this.flowers = products.filter(p => p.type === 'flower').length;
        this.coffins = products.filter(p => p.type === 'coffin').length;
        this.loading = false;
        this.cdr.detectChanges();
      },
      error: () => {
        this.loading = false;
        this.cdr.detectChanges();
      }
    });
  }

  logout(): void {
    this.authService.logout();
  }
}


