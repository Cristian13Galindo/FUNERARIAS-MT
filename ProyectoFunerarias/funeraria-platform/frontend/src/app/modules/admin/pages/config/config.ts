import { Component, OnInit, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { ReactiveFormsModule, FormBuilder, FormGroup, Validators } from '@angular/forms';
import { HttpClient } from '@angular/common/http';
import { environment } from '../../../../../environments/environment';

@Component({
  selector: 'app-config',
  standalone: true,
  imports: [CommonModule, RouterModule, ReactiveFormsModule],
  templateUrl: './config.html',
  styleUrl: './config.css'
})
export class Config implements OnInit {
  configForm!: FormGroup;
  loading = true;
  saving = false;
  successMsg = '';
  errorMsg = '';

  constructor(
    private http: HttpClient,
    private fb: FormBuilder,
    private cdr: ChangeDetectorRef
  ) {}

  ngOnInit(): void {
    this.configForm = this.fb.group({
      primary_color: ['#18222e', Validators.required],
      secondary_color: ['#bf9f62', Validators.required],
      contact_email: ['', [Validators.email]],
      whatsapp_number: [''],
      bank_accounts: ['']
    });
    this.loadConfig();
  }

  loadConfig(): void {
    this.http.get<any>(`${environment.apiUrl}/admin/config/`).subscribe({
      next: (c) => {
        this.configForm.patchValue(c);
        this.loading = false;
        this.cdr.detectChanges();
      },
      error: () => {
        this.loading = false;
        this.cdr.detectChanges();
      }
    });
  }

  saveConfig(): void {
    if (this.configForm.invalid) return;
    this.saving = true;
    this.successMsg = '';
    this.errorMsg = '';
    this.cdr.detectChanges();
    this.http.put(`${environment.apiUrl}/admin/config/`, this.configForm.value).subscribe({
      next: () => {
        this.saving = false;
        this.successMsg = 'Configuración guardada correctamente';
        this.cdr.detectChanges();
      },
      error: (err) => {
        this.saving = false;
        this.errorMsg = err.error?.msg ?? 'Error al guardar';
        this.cdr.detectChanges();
      }
    });
  }
}


