import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { AuthService } from '../../../../core/services/auth';
import { CatalogService } from '../../../../core/services/catalog';

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
    private catalogService: CatalogService
  ) {}

  ngOnInit(): void {
    this.user = this.authService.getCurrentUser();
    this.catalogService.listProducts().subscribe({
      next: (products) => {
        this.totalProducts = products.length;
        this.flowers = products.filter(p => p.type === 'flower').length;
        this.coffins = products.filter(p => p.type === 'coffin').length;
        this.loading = false;
      },
      error: () => (this.loading = false)
    });
  }

  logout(): void {
    this.authService.logout();
  }
}
