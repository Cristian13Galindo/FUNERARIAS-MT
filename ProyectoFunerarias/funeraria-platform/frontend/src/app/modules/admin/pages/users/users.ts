import { Component, OnInit, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { ReactiveFormsModule, FormBuilder, FormGroup, Validators } from '@angular/forms';
import { HttpClient } from '@angular/common/http';
import { environment } from '../../../../../environments/environment';

@Component({
  selector: 'app-users',
  standalone: true,
  imports: [CommonModule, RouterModule, ReactiveFormsModule],
  templateUrl: './users.html',
  styleUrl: './users.css'
})
export class Users implements OnInit {
  users: any[] = [];
  loading = true;
  showForm = false;
  userForm!: FormGroup;
  saving = false;
  errorMsg = '';

  constructor(
    private http: HttpClient,
    private fb: FormBuilder,
    private cdr: ChangeDetectorRef
  ) {}

  ngOnInit(): void {
    this.buildForm();
    this.loadUsers();
  }

  buildForm(): void {
    this.userForm = this.fb.group({
      first_name: ['', Validators.required],
      last_name: ['', Validators.required],
      email: ['', [Validators.required, Validators.email]],
      password: ['', [Validators.required, Validators.minLength(6)]],
      role: ['operario', Validators.required]
    });
  }

  loadUsers(): void {
    this.loading = true;
    this.http.get<any[]>(`${environment.apiUrl}/admin/users/`).subscribe({
      next: (u) => {
        this.users = u;
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
    this.buildForm();
    this.showForm = true;
    this.errorMsg = '';
    this.cdr.detectChanges();
  }

  cancelForm(): void {
    this.showForm = false;
    this.cdr.detectChanges();
  }

  saveUser(): void {
    if (this.userForm.invalid) return;
    this.saving = true;
    this.cdr.detectChanges();
    this.http.post(`${environment.apiUrl}/admin/users/`, this.userForm.value).subscribe({
      next: () => {
        this.saving = false;
        this.showForm = false;
        this.cdr.detectChanges();
        this.loadUsers();
      },
      error: (err) => {
        this.saving = false;
        this.errorMsg = err.error?.msg ?? 'Error al crear usuario';
        this.cdr.detectChanges();
      }
    });
  }
}


