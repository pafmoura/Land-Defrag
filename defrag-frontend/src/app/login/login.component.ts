import { CommonModule } from '@angular/common';
import { Component, OnInit } from '@angular/core';
import { FormControl, FormGroup, FormsModule, ReactiveFormsModule, Validators } from '@angular/forms';
import { Router } from '@angular/router';
import { AuthService } from '../services/auth.service';

@Component({
  selector: 'app-login',
  standalone: true,
  imports: [    FormsModule,
    ReactiveFormsModule,
CommonModule],
  templateUrl: './login.component.html',
  styleUrl: './login.component.css'
})
export class LoginComponent implements OnInit {
  loginForm: FormGroup;
  errorMessage: string = '';

  constructor(private authService: AuthService, private router: Router) {
    this.loginForm = new FormGroup({
      email: new FormControl('' ),
      password: new FormControl(''),
    });
  }

  ngOnInit(): void {}

  onSubmit(): void {
    console.log("olá");
    if (this.loginForm.valid) {
      const { email, password } = this.loginForm.value;

      this.authService.login(email, password).subscribe({
        next: (response: { token: any; }) => {
          this.authService.saveToken(response.token);
          this.router.navigate(['/simulator/setup']); // Redireciona após login bem-sucedido
        },
        error: (error: any) => {
          this.errorMessage = 'Login falhou. Verifique suas credenciais.';
          console.error(error);
        },
      });
    }
  }
}
