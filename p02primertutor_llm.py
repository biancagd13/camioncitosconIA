import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
import re
import ollama

nombre_modelo_llm = "llama3.2"

instruccion_del_sistema = """
Eres LogiSmart, un Tutor Virtual y Asistente Experto EXCLUSIVAMENTE en Series de Anime y Películas de Anime.

Tu función es orientar al usuario en:
1. Recomendación de series y películas según géneros o gustos.
2. Explicación de arcos argumentales y cronologías de series/sagas de películas.
3. Comparativas entre series y películas animadas.

Reglas estrictas de contenido:
- Queda PROHIBIDO hablar de mangas, cómics, manhwua, bandas sonoras, videojuegos o mercancía. Si el usuario pregunta por eso, redirígelo amablemente a series o películas.
- Dirígete siempre a la persona como 'usuario' o por su nombre si te lo da. NUNCA uses la palabra 'estudiante'.
- NO utilices emojis bajo ninguna circunstancia.

Instrucciones de estilo y personalidad:
- Sé alegre, creativa y dinámica.
- Varía espontáneamente tus frases divertidas mexicanas. Ejemplos que puedes combinar: ¡Me late chocolate!, ¡Recórcholis!, ¡Reconchinchiles!, ¡Me late cacahuate!, ¡Me canso ganso!, ¡A todo dar!, ¡Súper chido!, ¡De a devis!
- Responde de forma compacta y clara. Evita saltos de línea innecesarios o renglones vacíos dobles.
"""

historial_conversacion = [
    {
        "role": "system",
        "content": instruccion_del_sistema
    }
]

class AplicacionTutorAnimeGUI:
    def __init__(self, ventana_principal):
        self.ventana_raiz = ventana_principal
        self.ventana_raiz.title("LogiSmart - Asistente de Series y Películas de Anime")
        self.ventana_raiz.geometry("1080x750")
        self.ventana_raiz.minsize(900, 600)
        
        self.ventana_raiz.configure(bg="#F3E8FF")

        self.configurar_estilos_tema()
        self.construir_componentes_de_pantalla()
        self.mostrar_mensaje_bienvenida_inicial()

    def configurar_estilos_tema(self):
        estilo = ttk.Style()
        estilo.theme_use("clam")
        estilo.configure("TLabelframe", background="#F3E8FF", bordercolor="#C084FC")
        estilo.configure("TLabelframe.Label", background="#F3E8FF", foreground="#5B21B6", font=("Segoe UI", 11, "bold"))
        estilo.configure("TFrame", background="#F3E8FF")

    def construir_componentes_de_pantalla(self):
        # ------------------------------------------------------------
        # PANEL CABECERA
        # ------------------------------------------------------------
        panel_cabecera = tk.Frame(self.ventana_raiz, bg="#7E22CE", height=60)
        panel_cabecera.pack(fill=tk.X, side=tk.TOP)

        etiqueta_titulo_cabecera = tk.Label(
            panel_cabecera,
            text="¡Me Late Chocolate! Asistente Virtual de Series y Películas Anime",
            font=("Segoe UI", 14, "bold"),
            fg="#FFFFFF",
            bg="#7E22CE"
        )
        etiqueta_titulo_cabecera.pack(pady=15)

        # ------------------------------------------------------------
        # DIVISOR PRINCIPAL
        # ------------------------------------------------------------
        panel_contenedor = ttk.PanedWindow(self.ventana_raiz, orient=tk.HORIZONTAL)
        panel_contenedor.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)

        # ------------------------------------------------------------
        # PANEL IZQUIERDO: CHAT TEXTUAL SIN CANVAS NI BURBUJAS
        # ------------------------------------------------------------
        marco_izquierda_chat = ttk.LabelFrame(panel_contenedor, text=" Chat de Consultas ")
        panel_contenedor.add(marco_izquierda_chat, weight=3)

        marco_izquierda_chat.grid_rowconfigure(0, weight=1)
        marco_izquierda_chat.grid_rowconfigure(1, weight=0)
        marco_izquierda_chat.grid_columnconfigure(0, weight=1)

        # CAJA DE TEXTO PRINCIPAL DEL CHAT
        self.caja_chat_principal = scrolledtext.ScrolledText(
            marco_izquierda_chat,
            wrap=tk.WORD,
            font=("Segoe UI", 10),
            bg="#FAF5FF",
            fg="#1E1B4B",
            relief="flat",
            state="disabled"
        )
        self.caja_chat_principal.grid(row=0, column=0, sticky="nsew", padx=10, pady=(10, 5))

        # Configuración de etiquetas de texto para colores y formatos
        self.caja_chat_principal.tag_config("usuario_header", font=("Segoe UI", 10, "bold"), foreground="#4338CA")
        self.caja_chat_principal.tag_config("asistente_header", font=("Segoe UI", 10, "bold"), foreground="#6B21A8")
        self.caja_chat_principal.tag_config("texto_normal", font=("Segoe UI", 10), foreground="#1E1B4B")
        self.caja_chat_principal.tag_config("texto_negrita", font=("Segoe UI", 10, "bold"), foreground="#1E1B4B")

        # ÁREA INFERIOR DE ENTRADA FIJA
        marco_entrada_usuario = tk.Frame(marco_izquierda_chat, bg="#E9D5FF", bd=1, relief="solid")
        marco_entrada_usuario.grid(row=1, column=0, sticky="ew", padx=10, pady=10)

        etiqueta_indicador = tk.Label(
            marco_entrada_usuario,
            text="Escribe tu consulta aquí:",
            font=("Segoe UI", 9, "bold"),
            fg="#5B21B6",
            bg="#E9D5FF"
        )
        etiqueta_indicador.pack(anchor="w", padx=10, pady=(6, 2))

        marco_controles = tk.Frame(marco_entrada_usuario, bg="#E9D5FF")
        marco_controles.pack(fill=tk.X, padx=10, pady=(0, 8))

        self.texto_placeholder = "Ejemplo: Recomiéndame 3 películas de anime de fantasía..."
        
        self.campo_texto_pregunta = tk.Entry(
            marco_controles,
            font=("Segoe UI", 10),
            bg="#FFFFFF",
            fg="#6B7280",
            relief="flat",
            bd=5
        )
        self.campo_texto_pregunta.insert(0, self.texto_placeholder)
        self.campo_texto_pregunta.bind("<FocusIn>", self.limpiar_placeholder)
        self.campo_texto_pregunta.bind("<FocusOut>", self.restaurar_placeholder)
        self.campo_texto_pregunta.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10), ipady=4)
        self.campo_texto_pregunta.bind("<Return>", lambda evento: self.procesar_pregunta_usuario())

        self.boton_enviar_consulta = tk.Button(
            marco_controles,
            text="Enviar Consulta",
            font=("Segoe UI", 10, "bold"),
            bg="#9333EA",
            fg="#FFFFFF",
            activebackground="#7E22CE",
            activeforeground="#FFFFFF",
            relief="flat",
            cursor="hand2",
            padx=14,
            command=self.procesar_pregunta_usuario
        )
        self.boton_enviar_consulta.pack(side=tk.RIGHT)

        # ------------------------------------------------------------
        # PANEL DERECHO: REGISTRO Y MÉTRICAS DEL USUARIO
        # ------------------------------------------------------------
        marco_derecha_historial = ttk.LabelFrame(panel_contenedor, text=" Sesión del Usuario ")
        panel_contenedor.add(marco_derecha_historial, weight=1)

        self.etiqueta_metricas_sesion = tk.Label(
            marco_derecha_historial,
            text="Mensajes: 0 | Consultas: 0",
            font=("Segoe UI", 9, "bold"),
            fg="#5B21B6",
            bg="#E9D5FF",
            pady=8
        )
        self.etiqueta_metricas_sesion.pack(fill=tk.X, padx=10, pady=8)

        self.caja_resumen_historial = scrolledtext.ScrolledText(
            marco_derecha_historial,
            wrap=tk.WORD,
            font=("Segoe UI", 9),
            bg="#FAFAF9",
            fg="#4C1D95",
            relief="flat",
            state="disabled"
        )
        self.caja_resumen_historial.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))

    def limpiar_placeholder(self, evento):
        if self.campo_texto_pregunta.get() == self.texto_placeholder:
            self.campo_texto_pregunta.delete(0, tk.END)
            self.campo_texto_pregunta.config(fg="#1E1B4B")

    def restaurar_placeholder(self, evento):
        if not self.campo_texto_pregunta.get().strip():
            self.campo_texto_pregunta.insert(0, self.texto_placeholder)
            self.campo_texto_pregunta.config(fg="#6B7280")

    def mostrar_mensaje_bienvenida_inicial(self):
        saludo_inicial = "¡Hola, usuario! Soy tu asistente de Series y Películas de Anime. Puedes pedirme recomendaciones por género, cronologías o comparativas. Escribe tu consulta abajo para empezar."
        self.agregar_mensaje_al_chat("Asistente Anime", saludo_inicial)

    def procesar_pregunta_usuario(self):
        pregunta_del_usuario = self.campo_texto_pregunta.get().strip()

        if not pregunta_del_usuario or pregunta_del_usuario == self.texto_placeholder:
            return

        self.campo_texto_pregunta.delete(0, tk.END)
        self.agregar_mensaje_al_chat("Usuario", pregunta_del_usuario)

        historial_conversacion.append({
            "role": "user",
            "content": pregunta_del_usuario
        })

        self.boton_enviar_consulta.config(state="disabled", text="Consultando...", bg="#C084FC")

        hilo_consulta = threading.Thread(target=self.obtener_respuesta_ollama_en_hilo)
        hilo_consulta.start()

    def obtener_respuesta_ollama_en_hilo(self):
        try:
            respuesta_del_modelo = ollama.chat(
                model=nombre_modelo_llm,
                messages=historial_conversacion
            )

            contenido_respuesta = respuesta_del_modelo["message"]["content"]

            historial_conversacion.append({
                "role": "assistant",
                "content": contenido_respuesta
            })

            self.ventana_raiz.after(0, self.finalizar_procesamiento_respuesta, contenido_respuesta, None)

        except Exception as error_de_conexion:
            historial_conversacion.pop()
            self.ventana_raiz.after(0, self.finalizar_procesamiento_respuesta, None, error_de_conexion)

    def finalizar_procesamiento_respuesta(self, contenido_respuesta, error):
        self.boton_enviar_consulta.config(state="normal", text="Enviar Consulta", bg="#9333EA")

        if error:
            messagebox.showerror(
                "Error de Conexión",
                f"No pudimos conectar con Ollama.\n\n"
                f"Detalle: {error}"
            )
        else:
            self.agregar_mensaje_al_chat("Asistente Anime", contenido_respuesta)
            self.actualizar_panel_resumen_historial()

    def agregar_mensaje_al_chat(self, emisor, texto_mensaje):
        texto_limpio = texto_mensaje.strip()
        texto_limpio = re.sub(r'\n\s*\n+', '\n', texto_limpio)

        self.caja_chat_principal.config(state="normal")

        # Encabezado del emisor
        etiqueta_header = "usuario_header" if emisor == "Usuario" else "asistente_header"
        self.caja_chat_principal.insert(tk.END, f"[{emisor}]\n", etiqueta_header)

        # Formato básico para markdown en el cuerpo del texto
        partes_de_texto = re.split(r'(\*\*.*?\*\*)', texto_limpio)
        for parte in partes_de_texto:
            if parte.startswith('**') and parte.endswith('**'):
                self.caja_chat_principal.insert(tk.END, parte[2:-2], "texto_negrita")
            else:
                self.caja_chat_principal.insert(tk.END, parte, "texto_normal")

        self.caja_chat_principal.insert(tk.END, "\n\n")
        self.caja_chat_principal.config(state="disabled")
        self.caja_chat_principal.see(tk.END)

    def actualizar_panel_resumen_historial(self):
        total_mensajes = len(historial_conversacion) - 1
        total_consultas = total_mensajes // 2

        self.etiqueta_metricas_sesion.config(
            text=f"Mensajes: {total_mensajes} | Consultas: {total_consultas}"
        )

        self.caja_resumen_historial.config(state="normal")
        self.caja_resumen_historial.delete("1.0", tk.END)

        for elemento in historial_conversacion[1:]:
            etiqueta_rol = "Usuario" if elemento["role"] == "user" else "Asistente"
            vista_previa = elemento["content"].strip()[:40].replace("\n", " ") + "..."

            self.caja_resumen_historial.insert(
                tk.END,
                f"[{etiqueta_rol}]: {vista_previa}\n\n"
            )

        self.caja_resumen_historial.config(state="disabled")

if __name__ == "__main__":
    ventana_raiz_aplicacion = tk.Tk()
    aplicacion_tutor = AplicacionTutorAnimeGUI(ventana_raiz_aplicacion)
    ventana_raiz_aplicacion.mainloop()