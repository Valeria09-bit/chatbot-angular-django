import { Component, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { HttpClient, HttpClientModule } from '@angular/common/http';

interface Mensaje {
  texto: string;
  emisor: 'bot' | 'usuario';
}

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [CommonModule, FormsModule, HttpClientModule],
  templateUrl: './app.html',
  styleUrl: './app.css'
})
export class App {

  chatAbierto = false;
  escribiendo = false;   // controla si se muestra el indicador de "escribiendo..."

  mensajes: Mensaje[] = [
    { texto: '¡Buen día! Soy InfoBot, dime en qué puedo ayudarte', emisor: 'bot' }
  ];

  mensajeUsuario: string = '';

  // se agregó ChangeDetectorRef para forzar el refresco de la vista
  constructor(private http: HttpClient, private cdRef: ChangeDetectorRef) {}

  toggleChat() {
    this.chatAbierto = !this.chatAbierto;
  }

  enviarMensaje() {
    const texto = this.mensajeUsuario.trim();
    if (!texto) return;

    this.mensajes.push({ texto, emisor: 'usuario' });
    this.mensajeUsuario = '';
    this.escribiendo = true;
    this.cdRef.detectChanges();   // refresca la vista para mostrar el indicador de inmediato

    this.http.post<any>('http://127.0.0.1:8000/api/preguntar/', { pregunta: texto })
      .subscribe({
        next: (respuesta) => {
          this.escribiendo = false;
          this.mensajes.push({ texto: respuesta.respuesta, emisor: 'bot' });
          this.cdRef.detectChanges();   // refresca la vista al llegar la respuesta
        },
        error: (err) => {
          this.escribiendo = false;
          console.error('Error al conectar con Django', err);
          this.mensajes.push({ texto: 'Ocurrió un error al conectar con el servidor', emisor: 'bot' });
          this.cdRef.detectChanges();   //  refresca la vista también si hay error
        }
      });
  }
}