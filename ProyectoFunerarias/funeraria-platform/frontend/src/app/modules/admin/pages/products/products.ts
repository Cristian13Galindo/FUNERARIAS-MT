import { Component, OnInit, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { ReactiveFormsModule, FormBuilder, FormGroup, Validators } from '@angular/forms';
import { CatalogService } from '../../../../core/services/catalog';

@Component({
  selector: 'app-products',
  standalone: true,
  imports: [CommonModule, RouterModule, ReactiveFormsModule],
  templateUrl: './products.html',
  styleUrl: './products.css'
})
export class Products implements OnInit {
  products: any[] = [];
  loading = true;
  showForm = false;
  editingProduct: any = null;
  productForm!: FormGroup;
  saving = false;
  errorMsg = '';

  constructor(
    private catalogService: CatalogService,
    private fb: FormBuilder,
    private cdr: ChangeDetectorRef
  ) {}

  ngOnInit(): void {
    this.buildForm();
    this.loadProducts();
  }

  buildForm(product?: any): void {
    this.productForm = this.fb.group({
      title: [product?.title || '', Validators.required],
      type: [product?.type || 'flower', Validators.required],
      description: [product?.description || ''],
      price: [product?.price || null],
      is_visible: [product?.is_visible ?? true]
    });
  }

  loadProducts(): void {
    this.loading = true;
    this.catalogService.listProducts().subscribe({
      next: (p) => {
        this.products = p;
        this.loading = false;
        this.cdr.detectChanges();
      },
      error: () => {
        this.loading = false;
        this.cdr.detectChanges();
      }
    });
  }

  openCreate(): void {
    this.editingProduct = null;
    this.buildForm();
    this.showForm = true;
    this.errorMsg = '';
    this.cdr.detectChanges();
  }

  openEdit(product: any): void {
    this.editingProduct = product;
    this.buildForm(product);
    this.showForm = true;
    this.errorMsg = '';
    this.cdr.detectChanges();
  }

  cancelForm(): void {
    this.showForm = false;
    this.editingProduct = null;
    this.cdr.detectChanges();
  }

  saveProduct(): void {
    if (this.productForm.invalid) return;
    this.saving = true;
    this.cdr.detectChanges();
    const data = this.productForm.value;
    const obs = this.editingProduct
      ? this.catalogService.updateProduct(this.editingProduct._id, data)
      : this.catalogService.createProduct(data);

    obs.subscribe({
      next: () => {
        this.saving = false;
        this.showForm = false;
        this.cdr.detectChanges();
        this.loadProducts();
      },
      error: (err) => {
        this.saving = false;
        this.errorMsg = err.error?.msg ?? 'Error al guardar';
        this.cdr.detectChanges();
      }
    });
  }

  deleteProduct(id: string): void {
    if (!confirm('¿Eliminar este producto?')) return;
    this.catalogService.deleteProduct(id).subscribe({
      next: () => {
        this.loadProducts();
      },
      error: () => {
        alert('Error al eliminar');
        this.cdr.detectChanges();
      }
    });
  }
}


