import { Component, OnInit, ChangeDetectorRef } from '@angular/core'; 
import { RouterOutlet } from '@angular/router';
import { HttpClient } from '@angular/common/http';
import { FormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-root',
  imports: [RouterOutlet, FormsModule, CommonModule],
  templateUrl: './app.html',
  styleUrl: './app.css'
})
export class App implements OnInit {
  mensajeDjango: string = 'Esperando a Django...';
  mensajeDjango2: string = '';

  // --- Variables para SUMA ---
  numero1: number = 0;
  numero2: number = 0;
  resultadoSuma: number | null = null;

  // --- Variables para CONCATENAR ---
  texto1: string = '';
  texto2: string = '';
  resultadoConcatenar: string = '';

  // --- Variables para INVERTIR ARREGLO ---
  arregloTexto: string = ''; // el usuario escribe algo como: 1,2,3,4
  resultadoInvertir: any[] = [];

  constructor(private http: HttpClient, private cdr: ChangeDetectorRef) {
    console.log('1. El componente se cargó correctamente.');
  }

  ngOnInit() {
    console.log('2. Intentando contactar al puerto 8000...');
    
    this.http.get<any>('http://127.0.0.1:8000/api/mensaje/').subscribe({
      next: (respuesta) => {
        console.log('3. ¡Éxito! Datos recibidos:', respuesta);
        this.mensajeDjango = respuesta.mensaje;
        this.mensajeDjango2 = respuesta.mensaje2;
        this.cdr.detectChanges(); 
      },
      error: (error) => {
        console.error('3. ¡Error fatal al conectar!', error);
        this.mensajeDjango = 'Error de conexión con el backend';
        this.cdr.detectChanges();
      }
    });
  }

  // --- Método: SUMAR ---
  enviarSuma() {
    this.http.post<any>('http://127.0.0.1:8000/api/sumar/', {
      a: this.numero1,
      b: this.numero2
    }).subscribe({
      next: (respuesta) => {
        this.resultadoSuma = respuesta.resultado;
        this.cdr.detectChanges();
      },
      error: (error) => console.error('Error al sumar:', error)
    });
  }

  // --- Método: CONCATENAR ---
  enviarConcatenar() {
    this.http.post<any>('http://127.0.0.1:8000/api/concatenar/', {
      texto1: this.texto1,
      texto2: this.texto2
    }).subscribe({
      next: (respuesta) => {
        this.resultadoConcatenar = respuesta.resultado;
        this.cdr.detectChanges();
      },
      error: (error) => console.error('Error al concatenar:', error)
    });
  }

  // --- Método: INVERTIR ARREGLO ---
  enviarInvertir() {
    // Convertimos el texto "1,2,3,4" en un arreglo real [1,2,3,4]
    const arreglo = this.arregloTexto
      .split(',')
      .map(item => item.trim());

    this.http.post<any>('http://127.0.0.1:8000/api/invertir/', {
      arreglo: arreglo
    }).subscribe({
      next: (respuesta) => {
        this.resultadoInvertir = respuesta.resultado;
        this.cdr.detectChanges();
      },
      error: (error) => console.error('Error al invertir:', error)
    });
  }
}