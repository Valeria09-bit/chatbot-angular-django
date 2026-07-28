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

  // Controla si se muestra u oculta la ventana del chat
  chatAbierto = false;

  mensajes: Mensaje[] = [
    { texto: '¡Buen día! Soy InfoBot, dime en qué puedo ayudarte', emisor: 'bot' }
  ];

  mensajeUsuario: string = '';

  constructor(private http: HttpClient) {}

  // Abre o cierra la ventana del chat al hacer clic en la burbuja
  toggleChat() {
    this.chatAbierto = !this.chatAbierto;
  }

  enviarMensaje() {
    const texto = this.mensajeUsuario.trim();
    if (!texto) return;

    // 1. Mostramos el mensaje del emisor usuario
    this.mensajes.push({ texto, emisor: 'usuario' });
    this.mensajeUsuario = '';

    // 2. Lo mandamos a Django para que responda
    this.http.post<any>('http://127.0.0.1:8000/api/chatbot/', { mensaje: texto })
      .subscribe({
        next: (respuesta) => {
          this.mensajes.push({ texto: respuesta.mensaje, emisor: 'bot' });
        },
        error: (err) => {
          console.error('Error al conectar con Django', err);
          this.mensajes.push({ texto: 'Ocurrió un error al conectar con el servidor', emisor: 'bot' });
        }
      });
  }
}