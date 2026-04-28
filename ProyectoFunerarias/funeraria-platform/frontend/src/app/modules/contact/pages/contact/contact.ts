import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ReactiveFormsModule, FormBuilder, FormGroup, Validators } from '@angular/forms';
import { CatalogService } from '../../../../core/services/catalog';
import { TenantService } from '../../../../core/services/tenant';

@Component({
  selector: 'app-contact',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule],
  templateUrl: './contact.html',
  styleUrl: './contact.css'
})
export class Contact implements OnInit {
  contactForm: FormGroup;
  loading = false;
  success = false;
  errorMsg = '';
  tenantSlug = '';

  constructor(
    private fb: FormBuilder,
    private catalogService: CatalogService,
    private tenantService: TenantService
  ) {
    this.contactForm = this.fb.group({
      name: ['', Validators.required],
      email: ['', [Validators.required, Validators.email]],
      phone: [''],
      message: ['', [Validators.required, Validators.minLength(10)]]
    });
  }

  ngOnInit(): void {
    // Resolución dinámica del slug
    this.tenantSlug = this.tenantService.resolveSlug();

    // Aplicar tema del tenant también en la página de contacto
    this.tenantService.getConfig(this.tenantSlug).subscribe({
      next: (config) => this.tenantService.applyTheme(config),
      error: () => {}
    });
  }

  onSubmit(): void {
    if (this.contactForm.invalid) return;
    this.loading = true;
    this.errorMsg = '';
    const payload = { ...this.contactForm.value, tenant_slug: this.tenantSlug };
    this.catalogService.sendContact(payload).subscribe({
      next: () => {
        this.loading = false;
        this.success = true;
        this.contactForm.reset();
      },
      error: (err) => {
        this.loading = false;
        this.errorMsg = err.error?.msg ?? 'Error al enviar mensaje';
      }
    });
  }
}

