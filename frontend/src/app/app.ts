import { Component } from '@angular/core';
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

  mensajes: Mensaje[] = [
    { texto: '¡Buen día! Soy InfoBot, dime en qué puedo ayudarte', emisor: 'bot' }
  ];

  mensajeUsuario: string = '';

  constructor(private http: HttpClient) {}

  toggleChat() {
    this.chatAbierto = !this.chatAbierto;
  }

  enviarMensaje() {
    const texto = this.mensajeUsuario.trim();
    if (!texto) return;

    this.mensajes.push({ texto, emisor: 'usuario' });
    this.mensajeUsuario = '';

    // OJO: el campo que espera Django es "pregunta", no "mensaje"
    this.http.post<any>('http://127.0.0.1:8000/api/preguntar/', { pregunta: texto })
      .subscribe({
        next: (respuesta) => {
          // Por ahora Django regresa una lista de chunks (contexto_encontrado),
          // no una respuesta ya redactada. Mostramos el primero como respuesta provisional.
          const contexto = respuesta.contexto_encontrado;

          if (contexto && contexto.length > 0) {
            this.mensajes.push({ texto: contexto[0], emisor: 'bot' });
          } else {
            this.mensajes.push({ texto: 'No encontré información sobre eso.', emisor: 'bot' });
          }
        },
        error: (err) => {
          console.error('Error al conectar con Django', err);
          this.mensajes.push({ texto: 'Ocurrió un error al conectar con el servidor', emisor: 'bot' });
        }
      });
  }
}