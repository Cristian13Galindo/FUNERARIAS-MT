import { Routes } from '@angular/router';
import { authGuard } from './core/guards/auth-guard';

export const routes: Routes = [
  {
    path: '',
    redirectTo: 'home',
    pathMatch: 'full'
  },
  {
    path: 'home',
    loadComponent: () =>
      import('./modules/home/pages/home/home').then(m => m.Home)
  },
  {
    path: 'login',
    loadComponent: () =>
      import('./modules/auth/pages/login/login').then(m => m.Login)
  },
  {
    path: 'catalog',
    loadComponent: () =>
      import('./modules/catalog/pages/catalog/catalog').then(m => m.Catalog)
  },
  {
    path: 'contact',
    loadComponent: () =>
      import('./modules/contact/pages/contact/contact').then(m => m.Contact)
  },
  {
    path: 'admin',
    canActivate: [authGuard],
    children: [
      { path: '', redirectTo: 'dashboard', pathMatch: 'full' },
      {
        path: 'dashboard',
        loadComponent: () =>
          import('./modules/admin/pages/dashboard/dashboard').then(m => m.Dashboard)
      },
      {
        path: 'products',
        loadComponent: () =>
          import('./modules/admin/pages/products/products').then(m => m.Products)
      },
      {
        path: 'users',
        loadComponent: () =>
          import('./modules/admin/pages/users/users').then(m => m.Users)
      },
      {
        path: 'config',
        loadComponent: () =>
          import('./modules/admin/pages/config/config').then(m => m.Config)
      }
    ]
  },
  { path: '**', redirectTo: 'home' }
];

