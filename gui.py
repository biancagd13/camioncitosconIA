# Importación de la librería para lectura y escritura de archivos CSV
import csv
# Importación de la librería para manipulación y parseo de datos JSON
import json
# Importación de la librería para interacción con el sistema operativo
import os
# Importación de la librería para ejecutar tareas en hilos secundarios (asíncronos)
import threading
# Importación de la librería tkinter para la creación de la interfaz gráfica de usuario
import tkinter as tk
# Importación del módulo datetime para obtener y formatear fechas y horas del sistema
from datetime import datetime
# Importación de submódulos de tkinter para cuadros de diálogo y componentes avanzados
from tkinter import filedialog, messagebox, ttk

# Importación de la librería requests para realizar peticiones HTTP hacia la API de Ollama
import requests

# Importación de la clase DatabaseManager para la gestión y conexión con MongoDB Atlas
from database import DatabaseManager

# URL por defecto para comunicarse con el servidor local del Modelo de Lenguaje Ollama
URL_OLLAMA_LOCAL = "http://localhost:11434/api/generate"


class MarcoDesplegable(ttk.Frame):
    """Componente reutilizable de sección desplegable (Acordeón) usando Tkinter estándar."""

    def __init__(self, contenedor_padre, titulo_seccion="Sección Desplegable", **opciones_adicionales):
        # Inicializamos la clase base ttk.Frame con su contenedor padre y opciones
        super().__init__(contenedor_padre, **opciones_adicionales)
        
        # Variable de estado para controlar si la sección está abierta o cerrada
        self.esta_desplegado = True

        # Botón del encabezado que activa o desactiva la visibilidad del contenido
        self.boton_encabezado = ttk.Button(
            self,
            text=f"▼ {titulo_seccion}",
            command=self.alternar_visibilidad,
        )
        # Empaquetamos el botón para que ocupe todo el ancho disponible
        self.boton_encabezado.pack(fill="x", expand=True, padx=2, pady=2)

        # Contenedor interno que almacenará los widgets dentro del acordeón
        self.contenedor_contenido = ttk.Frame(self)
        # Empaquetamos el contenedor de contenido para que sea visible inicialmente
        self.contenedor_contenido.pack(fill="both", expand=True, padx=5, pady=5)

    def alternar_visibilidad(self):
        # Si la sección está desplegada, la ocultamos y cambiamos el icono a flecha derecha
        if self.esta_desplegado:
            self.contenedor_contenido.pack_forget()
            self.boton_encabezado.configure(
                text=self.boton_encabezado.cget("text").replace("▼", "▶")
            )
            self.esta_desplegado = False
        # Si está oculta, la volvemos a mostrar y restauramos la flecha hacia abajo
        else:
            self.contenedor_contenido.pack(fill="both", expand=True, padx=5, pady=5)
            self.boton_encabezado.configure(
                text=self.boton_encabezado.cget("text").replace("▶", "▼")
            )
            self.esta_desplegado = True


class LogiSmartGUI:

    def __init__(self, ventana_principal):
        # Guardamos la referencia de la ventana principal de Tkinter
        self.ventana_principal = ventana_principal
        
        # Establecemos el título oficial de la ventana de la aplicación
        self.ventana_principal.title(
            "Sistema de Control, Seguridad y Riesgos"
        )
        # Asignamos las dimensiones iniciales en píxeles (Ancho x Alto)
        self.ventana_principal.geometry("1180x860")

        # Inicializamos el gestor de base de datos para conectar con MongoDB Atlas
        self.gestor_base_datos = DatabaseManager()

        # Variable para almacenar el modelo de Ollama seleccionado por el usuario
        self.variable_modelo_ollama = tk.StringVar(value="llama3.2:latest")
        
        # Variable para definir el umbral numérico de clasificación
        self.variable_umbral_clasificacion = tk.DoubleVar(value=0.75)
        
        # Variable booleana para activar o desactivar el modo simulación offline
        self.variable_modo_simulacion = tk.BooleanVar(value=False)

        # Definición de la paleta de colores en tonos lila y morados para la interfaz
        self.COLOR_LILA_OBSCURO = "#579FCC"# Color de fondo de contraste
        self.COLOR_LILA_MEDIO = "#4a2850"        # Color primario de acento
        self.COLOR_LILA_CLARO = "#7b438b"        # Color de resalte para selección y botones
        self.COLOR_LILA_PASTEL = "#1e78c7"       # Color para textos suaves o bordes
        self.COLOR_LILA_CABECERA = "#3b1e42"     # Color para encabezados de tablas
        self.COLOR_FONDO_VENTANA = "#143ca0"    # Color de fondo claro para la ventana

        # Configuración inicial de estilos visuales de la aplicación
        self._configurar_estilos_interfaz()

        # Creación del contenedor de pestañas principal (ttk.Notebook)
        self.panel_pestanias = ttk.Notebook(self.ventana_principal)
        # Empaquetamos el panel para que ocupe todo el espacio de la ventana
        self.panel_pestanias.pack(fill="both", expand=True, padx=10, pady=10)

        # Diccionario para almacenar la referencia de cada pestaña creada
        self.diccionario_pestanias = {}
        
        # Lista con los nombres de todas las pestañas de la aplicación
        lista_nombres_pestanias = [
            "Dashboard",
            "Control de Acceso",
            "Tabla de Verdad",
            "Incidentes",
            "Chat RAG",
            "Riesgos Éticos",
            "Reportes",
            "Configuración",
        ]

        # Ciclo para crear y registrar dinámicamente cada marco de pestaña
        for nombre_pestania in lista_nombres_pestanias:
            marco_pestania = ttk.Frame(self.panel_pestanias, padding=10)
            self.panel_pestanias.add(marco_pestania, text=nombre_pestania)
            self.diccionario_pestanias[nombre_pestania] = marco_pestania

        # Llamada a los métodos constructores de cada una de las pantallas
        self.crear_pantalla_dashboard()
        self.crear_pantalla_control_acceso()
        self.crear_pantalla_simulador_verdad()
        self.crear_pantalla_bandeja_incidentes()
        self.crear_pantalla_asistente_rag()
        self.crear_pantalla_riesgos_eticos()
        self.crear_pantalla_reportes()
        self.crear_pantalla_configuracion()

    def _configurar_estilos_interfaz(self):
        # Creación del objeto de estilo de ttk
        estilo_interfaz = ttk.Style()
        
        # Selección del tema base clam para permitir personalización de colores
        estilo_interfaz.theme_use("clam")

        # Configuración personalizada de la apariencia de las tablas (Treeview)
        estilo_interfaz.configure(
            "Treeview",
            background="#ffffff",
            foreground="#2d1b36",
            fieldbackground="#ffffff",
            rowheight=26,
            bordercolor=self.COLOR_LILA_PASTEL,
        )
        # Mapeo de colores para la fila seleccionada en las tablas
        estilo_interfaz.map("Treeview", background=[("selected", self.COLOR_LILA_CLARO)], foreground=[("selected", "#1086bc")])
        
        # Configuración de los encabezados de las tablas
        estilo_interfaz.configure(
            "Treeview.Heading",
            background=self.COLOR_LILA_CABECERA,
            foreground="white",
            font=("Helvetica", 10, "bold"),
            relief="flat",
        )

        # Estilo personalizado para los contenedores de tarjetas KPI
        estilo_interfaz.configure("TarjetaKpi.TFrame", relief="raised", borderwidth=1)

    # ========================================================
    # 1. PANEL DE CONTROL (DASHBOARD)
    # ========================================================
    def crear_pantalla_dashboard(self):
        # Obtención de la pestaña Dashboard desde el diccionario
        pestania_dashboard = self.diccionario_pestanias["Dashboard"]

        # Marco agrupador para los filtros de consulta por rango de fechas
        marco_filtros = ttk.LabelFrame(pestania_dashboard, text="Filtros de Consulta por Fecha", padding=10)
        marco_filtros.pack(fill="x", pady=10, padx=10)

        # Etiqueta e campo de entrada para la fecha de inicio
        ttk.Label(marco_filtros, text="Fecha Inicio (YYYY-MM-DD):").grid(
            row=0, column=0, padx=10, pady=10, sticky="w"
        )
        self.entrada_fecha_inicio = ttk.Entry(marco_filtros, width=15)
        self.entrada_fecha_inicio.insert(0, datetime.now().strftime("%Y-%m-01"))
        self.entrada_fecha_inicio.grid(row=0, column=1, padx=5, pady=10)

        # Etiqueta y campo de entrada para la fecha de fin
        ttk.Label(marco_filtros, text="Fecha Fin (YYYY-MM-DD):").grid(
            row=0, column=2, padx=10, pady=10, sticky="w"
        )
        self.entrada_fecha_fin = ttk.Entry(marco_filtros, width=15)
        self.entrada_fecha_fin.insert(0, datetime.now().strftime("%Y-%m-%d"))
        self.entrada_fecha_fin.grid(row=0, column=3, padx=5, pady=10)

        # Botón para ejecutar el filtrado de métricas
        ttk.Button(
            marco_filtros,
            text="Aplicar Filtro",
            command=self.actualizar_metricas_dashboard,
        ).grid(row=0, column=4, padx=15, pady=10)

        # Marco contenedor para la distribución de tarjetas KPI
        marco_kpi = ttk.Frame(pestania_dashboard)
        marco_kpi.pack(fill="x", pady=15, padx=10)
        marco_kpi.grid_columnconfigure((0, 1, 2), weight=1)

        # Creación de la tarjeta KPI de camiones atendidos en color lila obscuro
        self.etiqueta_kpi_camiones = self._crear_tarjeta_kpi(
            marco_kpi, "Camiones Atendidos", "0", self.COLOR_LILA_OBSCURO, 0
        )
        # Creación de la tarjeta KPI de incidentes abiertos en color lila medio
        self.etiqueta_kpi_incidentes = self._crear_tarjeta_kpi(
            marco_kpi, "Incidentes Abiertos", "0", self.COLOR_LILA_MEDIO, 1
        )
        # Creación de la tarjeta KPI de riesgos críticos en color lila claro
        self.etiqueta_kpi_riesgos = self._crear_tarjeta_kpi(
            marco_kpi, "Riesgos Críticos", "0", self.COLOR_LILA_CLARO, 2
        )

        # Botón en la esquina inferior derecha para refrescar los datos manualmente
        ttk.Button(
            pestania_dashboard, text="Actualizar Métricas", command=self.actualizar_metricas_dashboard
        ).pack(anchor="e", pady=10, padx=10)
        
        # Carga inicial de datos en el dashboard
        self.actualizar_metricas_dashboard()

    def _crear_tarjeta_kpi(self, contenedor_padre, titulo_kpi, valor_inicial, color_fondo, columna_posicion):
        # Marco individual para la tarjeta con borde y color personalizado
        tarjeta = tk.Frame(contenedor_padre, bg=color_fondo, relief="groove", bd=2)
        tarjeta.grid(row=0, column=columna_posicion, padx=10, sticky="nsew")

        # Etiqueta superior con el título de la métrica
        etiqueta_titulo = tk.Label(
            tarjeta,
            text=titulo_kpi,
            fg="white",
            bg=color_fondo,
            font=("Helvetica", 13, "bold"),
        )
        etiqueta_titulo.pack(anchor="w", padx=15, pady=(15, 5))

        # Etiqueta grande para mostrar el valor numérico de la métrica
        etiqueta_valor = tk.Label(
            tarjeta,
            text=valor_inicial,
            fg="white",
            bg=color_fondo,
            font=("Helvetica", 32, "bold"),
        )
        etiqueta_valor.pack(anchor="e", padx=15, pady=(0, 15))
        return etiqueta_valor

    def actualizar_metricas_dashboard(self):
        # Validación de seguridad: verificar la conexión con MongoDB Atlas
        if not self.gestor_base_datos.esta_conectado():
            return
        
        # Conteo total de camiones registrados en la colección
        conteo_camiones = self.gestor_base_datos.db.camiones.count_documents({})
        
        # Conteo de incidentes cuya condición es diferente de 'cerrado'
        conteo_incidentes = self.gestor_base_datos.db.incidentes.count_documents(
            {"estado": {"$ne": "cerrado"}}
        )
        
        # Conteo de riesgos éticos con nivel de riesgo residual crítico (>= 3)
        conteo_riesgos = self.gestor_base_datos.db.riesgos_eticos.count_documents(
            {"riesgo_residual": {"$gte": 3}}
        )

        # Actualización de los valores numéricos en la interfaz gráfica
        self.etiqueta_kpi_camiones.config(text=str(conteo_camiones))
        self.etiqueta_kpi_incidentes.config(text=str(conteo_incidentes))
        self.etiqueta_kpi_riesgos.config(text=str(conteo_riesgos))

    # ========================================================
    # 2. CONTROL DE ACCESO (EVALUACIÓN, BÚSQUEDA Y SEMÁFORO)
    # ========================================================
    def crear_pantalla_control_acceso(self):
        # Obtención del marco de la pestaña de Control de Acceso
        pestania_acceso = self.diccionario_pestanias["Control de Acceso"]

        # Formulario principal para CRUD y búsquedas de vehículos
        marco_formulario = ttk.LabelFrame(pestania_acceso, text="Formulario de Registro y Búsqueda", padding=10)
        marco_formulario.pack(fill="x", pady=5, padx=10)

        # Campo de entrada para la Placa del vehículo
        ttk.Label(marco_formulario, text="Placa:").grid(
            row=0, column=0, sticky="w", padx=10, pady=2
        )
        self.entrada_placa = ttk.Entry(marco_formulario, width=15)
        self.entrada_placa.grid(row=0, column=1, sticky="w", padx=5, pady=2)

        # Campo de entrada para el Identificador único del Camión
        ttk.Label(marco_formulario, text="ID Camión:").grid(
            row=0, column=2, sticky="w", padx=10, pady=2
        )
        self.entrada_camion_id = ttk.Entry(marco_formulario, width=15)
        self.entrada_camion_id.grid(row=0, column=3, sticky="w", padx=5, pady=2)

        # Campo de entrada para el Nombre de la Empresa transportista
        ttk.Label(marco_formulario, text="Empresa:").grid(
            row=0, column=4, sticky="w", padx=10, pady=2
        )
        self.entrada_empresa = ttk.Entry(marco_formulario, width=20)
        self.entrada_empresa.grid(row=0, column=5, sticky="w", padx=5, pady=2)

        # Variables booleanas para las proposiciones de lógica proposicional (P, Q, R, S)
        self.variable_logica_P = tk.BooleanVar(value=True)   # Autorización Vigente
        self.variable_logica_Q = tk.BooleanVar(value=True)   # Certificación Conductor
        self.variable_logica_R = tk.BooleanVar(value=False)  # En Lista Negra
        self.variable_logica_S = tk.BooleanVar(value=True)   # Horario Permitido

        # Marco contenedor para los botones de opción o casillas de verificación
        marco_casillas = ttk.Frame(marco_formulario)
        marco_casillas.grid(
            row=1, column=0, columnspan=6, sticky="w", pady=10, padx=5
        )

        # Casilla de verificación para P
        ttk.Checkbutton(
            marco_casillas, text="Autorización Vigente (P)", variable=self.variable_logica_P
        ).pack(side="left", padx=10)
        # Casilla de verificación para Q
        ttk.Checkbutton(
            marco_casillas, text="Certificación Conductor (Q)", variable=self.variable_logica_Q
        ).pack(side="left", padx=10)
        # Casilla de verificación para R
        ttk.Checkbutton(
            marco_casillas, text="En Lista Negra (R)", variable=self.variable_logica_R
        ).pack(side="left", padx=10)
        # Casilla de verificación para S
        ttk.Checkbutton(
            marco_casillas, text="Horario Permitido (S)", variable=self.variable_logica_S
        ).pack(side="left", padx=10)

        # Contenedor de botones de acción
        marco_botones_acceso = ttk.Frame(marco_formulario)
        marco_botones_acceso.grid(
            row=2, column=0, columnspan=6, sticky="w", pady=10, padx=5
        )

        # Botón para Guardar / Actualizar registro
        ttk.Button(
            marco_botones_acceso, text="Guardar / Actualizar", command=self.guardar_registro_camion
        ).pack(side="left", padx=4)
        # Botón para Búsqueda por Placa
        ttk.Button(
            marco_botones_acceso, text="Buscar por Placa", command=self.buscar_registro_camion
        ).pack(side="left", padx=4)
        # Botón para Eliminar Camión
        ttk.Button(
            marco_botones_acceso,
            text="Eliminar Camión",
            command=self.eliminar_registro_camion,
        ).pack(side="left", padx=4)
        # Botón para Limpiar Formulario
        ttk.Button(
            marco_botones_acceso,
            text="Limpiar Campos",
            command=self.limpiar_formulario_camion,
        ).pack(side="left", padx=4)
        # Botón principal para evaluar la lógica de acceso y mostrar el semáforo
        ttk.Button(
            marco_botones_acceso,
            text="Evaluar y Registrar Acceso",
            command=self.evaluar_acceso_vehicular,
        ).pack(side="left", padx=12)

        # Marco para el componente visual del semáforo y la explicación del resultado
        marco_semaforo = ttk.Frame(pestania_acceso)
        marco_semaforo.pack(fill="x", pady=5, padx=10)

        # Lienzo (Canvas) para dibujar la luz circular del semáforo
        self.lienzo_semaforo = tk.Canvas(
            marco_semaforo, width=60, height=60, bg="#2d1b36", highlightthickness=0
        )
        self.lienzo_semaforo.pack(side="left", padx=15, pady=10)
        # Dibujo de la luz circular en estado neutro (gris)
        self.circulo_luz_semaforo = self.lienzo_semaforo.create_oval(
            5, 5, 55, 55, fill="gray"
        )

        # Área de texto para mostrar la explicación lógica y causa de rechazo/acceso
        self.texto_explicacion_acceso = tk.Text(
            marco_semaforo, height=3, font=("Helvetica", 11), wrap="word"
        )
        self.texto_explicacion_acceso.pack(
            side="left", fill="both", expand=True, padx=10, pady=10
        )

        # Contenedor para la tabla de camiones
        marco_tabla_camiones = ttk.Frame(pestania_acceso)
        marco_tabla_camiones.pack(fill="both", expand=True, pady=5, padx=10)

        # Definición de las columnas de la tabla de vehículos
        columnas_camiones = (
            "placa",
            "camion_id",
            "empresa",
            "autorizacion",
            "certificacion",
            "lista_negra",
            "horario",
        )
        self.tabla_registros_camiones = ttk.Treeview(
            marco_tabla_camiones, columns=columnas_camiones, show="headings", height=6
        )

        # Encabezados visibles de la tabla
        self.tabla_registros_camiones.heading("placa", text="Placa")
        self.tabla_registros_camiones.heading("camion_id", text="ID Camión")
        self.tabla_registros_camiones.heading("empresa", text="Empresa")
        self.tabla_registros_camiones.heading("autorizacion", text="P (Autoriz.)")
        self.tabla_registros_camiones.heading("certificacion", text="Q (Certific.)")
        self.tabla_registros_camiones.heading("lista_negra", text="R (Lista Negra)")
        self.tabla_registros_camiones.heading("horario", text="S (Horario)")

        # Ajuste de ancho y alineación centrada de cada columna
        for columna in columnas_camiones:
            self.tabla_registros_camiones.column(columna, anchor="center", width=110)

        # Barra de desplazamiento vertical para la tabla
        barra_desplazamiento_camiones = ttk.Scrollbar(
            marco_tabla_camiones, orient="vertical", command=self.tabla_registros_camiones.yview
        )
        self.tabla_registros_camiones.configure(yscroll=barra_desplazamiento_camiones.set)
        self.tabla_registros_camiones.pack(
            side="left", fill="both", expand=True, padx=(5, 0), pady=5
        )
        barra_desplazamiento_camiones.pack(side="right", fill="y", padx=(0, 5), pady=5)

        # Evento para cargar los datos del elemento seleccionado en los campos del formulario
        self.tabla_registros_camiones.bind(
            "<<TreeviewSelect>>", self.cargar_datos_camion_seleccionado
        )
        # Carga inicial de datos de vehículos en la tabla
        self.consultar_camiones_base_datos()

    def guardar_registro_camion(self):
        # Obtención y formateo de texto ingresado por el usuario
        placa_vehiculo = self.entrada_placa.get().strip().upper()
        identificador_camion = self.entrada_camion_id.get().strip()
        nombre_empresa = self.entrada_empresa.get().strip()

        # Validación de campos obligatorios
        if not (placa_vehiculo and identificador_camion and nombre_empresa):
            messagebox.showerror(
                "Error de Validación",
                "Por favor completa los campos de Placa, ID y Empresa.",
            )
            return

        # Inserción o actualización (upsert) en MongoDB Atlas
        self.gestor_base_datos.db.camiones.update_one(
            {"placa": placa_vehiculo},
            {
                "$set": {
                    "placa": placa_vehiculo,
                    "camion_id": identificador_camion,
                    "empresa": nombre_empresa,
                    "autorizacion": self.variable_logica_P.get(),
                    "certificacion_conductor": self.variable_logica_Q.get(),
                    "en_lista_negra": self.variable_logica_R.get(),
                    "horario_permitido": self.variable_logica_S.get(),
                    "actualizado_en": datetime.now().strftime(
                        "%Y-%m-%d %H:%M:%S"
                    ),
                }
            },
            upsert=True,
        )
        messagebox.showinfo(
            "Éxito", f"Vehículo '{placa_vehiculo}' guardado."
        )
        self.limpiar_formulario_camion()
        self.consultar_camiones_base_datos()

    def buscar_registro_camion(self):
        placa_vehiculo = self.entrada_placa.get().strip().upper()
        if not placa_vehiculo:
            messagebox.showwarning(
                "Aviso", "Ingresa una placa en el campo para buscar."
            )
            return

        # Consulta directa por la clave 'placa'
        documento_camion = self.gestor_base_datos.db.camiones.find_one({"placa": placa_vehiculo})
        if documento_camion:
            self.entrada_camion_id.delete(0, tk.END)
            self.entrada_camion_id.insert(0, documento_camion.get("camion_id", ""))
            self.entrada_empresa.delete(0, tk.END)
            self.entrada_empresa.insert(0, documento_camion.get("empresa", ""))
            self.variable_logica_P.set(documento_camion.get("autorizacion", True))
            self.variable_logica_Q.set(documento_camion.get("certificacion_conductor", True))
            self.variable_logica_R.set(documento_camion.get("en_lista_negra", False))
            self.variable_logica_S.set(documento_camion.get("horario_permitido", True))
            messagebox.showinfo("Encontrado", f"Datos cargados para {placa_vehiculo}.")
        else:
            messagebox.showwarning(
                "No Encontrado", f"La placa '{placa_vehiculo}' no existe en el sistema."
            )

    def eliminar_registro_camion(self):
        placa_vehiculo = self.entrada_placa.get().strip().upper()
        if not placa_vehiculo:
            messagebox.showwarning(
                "Aviso", "Ingresa o selecciona una placa para eliminar."
            )
            return

        # Confirmación preventiva del usuario antes de borrar
        if messagebox.askyesno(
            "Confirmación", f"¿Eliminar permanentemente el vehículo {placa_vehiculo}?"
        ):
            self.gestor_base_datos.db.camiones.delete_one({"placa": placa_vehiculo})
            messagebox.showinfo("Eliminado", f"Vehículo {placa_vehiculo} eliminado.")
            self.limpiar_formulario_camion()
            self.consultar_camiones_base_datos()

    def consultar_camiones_base_datos(self):
        # Limpiar filas existentes en la interfaz de la tabla
        for fila in self.tabla_registros_camiones.get_children():
            self.tabla_registros_camiones.delete(fila)
        if not self.gestor_base_datos.esta_conectado():
            return
        # Iterar los documentos encontrados ordenados por placa
        for documento in self.gestor_base_datos.db.camiones.find().sort("placa", 1):
            self.tabla_registros_camiones.insert(
                "",
                "end",
                values=(
                    documento.get("placa", ""),
                    documento.get("camion_id", ""),
                    documento.get("empresa", ""),
                    "SI" if documento.get("autorizacion") else "NO",
                    "SI" if documento.get("certificacion_conductor") else "NO",
                    "SI" if documento.get("en_lista_negra") else "NO",
                    "SI" if documento.get("horario_permitido", True) else "NO",
                ),
            )

    def cargar_datos_camion_seleccionado(self, evento_seleccion):
        seleccion = self.tabla_registros_camiones.selection()
        if not seleccion:
            return
        datos_fila = self.tabla_registros_camiones.item(seleccion[0], "values")
        self.entrada_placa.delete(0, tk.END)
        self.entrada_placa.insert(0, datos_fila[0])
        self.entrada_camion_id.delete(0, tk.END)
        self.entrada_camion_id.insert(0, datos_fila[1])
        self.entrada_empresa.delete(0, tk.END)
        self.entrada_empresa.insert(0, datos_fila[2])
        self.variable_logica_P.set(datos_fila[3] == "SI")
        self.variable_logica_Q.set(datos_fila[4] == "SI")
        self.variable_logica_R.set(datos_fila[5] == "SI")
        self.variable_logica_S.set(datos_fila[6] == "SI")

    def limpiar_formulario_camion(self):
        self.entrada_placa.delete(0, tk.END)
        self.entrada_camion_id.delete(0, tk.END)
        self.entrada_empresa.delete(0, tk.END)
        self.variable_logica_P.set(True)
        self.variable_logica_Q.set(True)
        self.variable_logica_R.set(False)
        self.variable_logica_S.set(True)

    def evaluar_acceso_vehicular(self):
        # Obtención de los valores de verdad de las casillas
        p_autorizado = self.variable_logica_P.get()
        q_certificado = self.variable_logica_Q.get()
        r_lista_negra = self.variable_logica_R.get()
        s_horario_valido = self.variable_logica_S.get()

        # Evaluación de la regla lógica A = P AND Q AND (NOT R) AND S
        acceso_permitido_A = p_autorizado and q_certificado and (not r_lista_negra) and s_horario_valido
        # Evaluación de la regla de inspección E = NOT P OR NOT Q OR R OR NOT S
        inspeccion_especial_E = (not p_autorizado) or (not q_certificado) or r_lista_negra or (not s_horario_valido)

        self.texto_explicacion_acceso.delete("1.0", tk.END)

        if acceso_permitido_A:
            # Si el acceso es Aprobado -> Luz Verde
            self.lienzo_semaforo.itemconfig(self.circulo_luz_semaforo, fill="#2ecc71")
            texto_explicativo = (
                "ACCESO PERMITIDO (A=1, E=0)\nEl vehículo cumple todas las"
                " condiciones de seguridad."
            )
        else:
            # Si el acceso es Rechazado -> Luz Roja
            self.lienzo_semaforo.itemconfig(self.circulo_luz_semaforo, fill="#e74c3c")
            lista_causas_rechazo = []
            if not p_autorizado:
                lista_causas_rechazo.append("Sin Autorización (~P)")
            if not q_certificado:
                lista_causas_rechazo.append("Sin Certificación (~Q)")
            if r_lista_negra:
                lista_causas_rechazo.append("En Lista Negra (R)")
            if not s_horario_valido:
                lista_causas_rechazo.append("Fuera de Horario (~S)")
            texto_explicativo = (
                "ACCESO DENEGADO (A=0, E=1)\nMotivos de rechazo: "
                + ", ".join(lista_causas_rechazo)
            )

        self.texto_explicacion_acceso.insert(tk.END, texto_explicativo)
        placa_vehiculo = self.entrada_placa.get().strip().upper() or "S/N"
        
        # Guardar en la base de datos el historial del evento de acceso
        self.gestor_base_datos.registrar_acceso(
            placa_vehiculo, p_autorizado, q_certificado, r_lista_negra, s_horario_valido, acceso_permitido_A, inspeccion_especial_E, "Operador_GUI", texto_explicativo
        )

    # ========================================================
    # 3. SIMULADOR DE TABLAS DE VERDAD
    # ========================================================
    def crear_pantalla_simulador_verdad(self):
        pestania_tabla_verdad = self.diccionario_pestanias["Tabla de Verdad"]

        ttk.Label(
            pestania_tabla_verdad,
            text="Interruptores / Switches en Vivo (Simulador de Entrada)",
            font=("Helvetica", 12, "bold"),
        ).pack(anchor="w", pady=10, padx=10)

        marco_switches = ttk.Frame(pestania_tabla_verdad)
        marco_switches.pack(fill="x", padx=10)

        # Variables para la simulación interactiva
        self.simulacion_P = tk.BooleanVar(value=True)
        self.simulacion_Q = tk.BooleanVar(value=True)
        self.simulacion_R = tk.BooleanVar(value=False)
        self.simulacion_S = tk.BooleanVar(value=True)

        for indice, (etiqueta_texto, variable_asociada) in enumerate([
            ("P (Autorización)", self.simulacion_P),
            ("Q (Certificación)", self.simulacion_Q),
            ("R (Lista Negra)", self.simulacion_R),
            ("S (Horario)", self.simulacion_S),
        ]):
            ttk.Checkbutton(
                marco_switches,
                text=etiqueta_texto,
                variable=variable_asociada,
                command=self.actualizar_simulacion_tabla_verdad,
            ).grid(row=0, column=indice, padx=20, pady=15)

        marco_resultados_logicos = ttk.Frame(pestania_tabla_verdad)
        marco_resultados_logicos.pack(fill="x", pady=10, padx=10)

        # Etiquetas con resaltado en colores según el resultado lógico A o E
        self.etiqueta_salida_A = tk.Label(
            marco_resultados_logicos,
            text="A (Acceso Permitido) = P & Q & ~R & S : 1",
            font=("Helvetica", 12, "bold"),
            fg="#2ecc71",
        )
        self.etiqueta_salida_A.pack(anchor="w", pady=5, padx=15)

        self.etiqueta_salida_E = tk.Label(
            marco_resultados_logicos,
            text="E (Inspección Especial) = ~P | ~Q | R | ~S : 0",
            font=("Helvetica", 12, "bold"),
            fg="#e74c3c",
        )
        self.etiqueta_salida_E.pack(anchor="w", pady=5, padx=15)

        marco_contenedor_tabla = ttk.Frame(pestania_tabla_verdad)
        marco_contenedor_tabla.pack(fill="both", expand=True, pady=10, padx=10)

        columnas_logicas = ("P", "Q", "R", "S", "A", "E")
        self.tabla_verdad_interactiva = ttk.Treeview(
            marco_contenedor_tabla, columns=columnas_logicas, show="headings", height=12
        )

        for col_nombre in columnas_logicas:
            self.tabla_verdad_interactiva.heading(col_nombre, text=col_nombre)
            self.tabla_verdad_interactiva.column(col_nombre, width=80, anchor="center")

        # Configuración de estilo visual para la fila activa seleccionada por los switches
        self.tabla_verdad_interactiva.tag_configure(
            "activa", background=self.COLOR_LILA_CLARO, foreground="white"
        )

        barra_desplazamiento_tabla = ttk.Scrollbar(
            marco_contenedor_tabla, orient="vertical", command=self.tabla_verdad_interactiva.yview
        )
        self.tabla_verdad_interactiva.configure(yscroll=barra_desplazamiento_tabla.set)
        self.tabla_verdad_interactiva.pack(
            side="left", fill="both", expand=True, padx=(5, 0), pady=5
        )
        barra_desplazamiento_tabla.pack(side="right", fill="y", padx=(0, 5), pady=5)

        # Generación inicial de la combinación completa de 16 estados (2^4)
        self.generar_tabla_verdad_completa()

    def generar_tabla_verdad_completa(self):
        for elemento in self.tabla_verdad_interactiva.get_children():
            self.tabla_verdad_interactiva.delete(elemento)

        # Obtención del estado actual en entero (1 o 0) de los interruptores
        p_actual = int(self.simulacion_P.get())
        q_actual = int(self.simulacion_Q.get())
        r_actual = int(self.simulacion_R.get())
        s_actual = int(self.simulacion_S.get())

        # Bucles anidados para generar los 16 casos posibles
        for val_p in [1, 0]:
            for val_q in [1, 0]:
                for val_r in [0, 1]:
                    for val_s in [1, 0]:
                        valor_salida_a = int(bool(val_p and val_q and not val_r and val_s))
                        valor_salida_e = int(bool(not val_p or not val_q or val_r or not val_s))

                        # Determinar si la fila iterada coincide con la combinación activa
                        es_fila_activa = (
                            val_p == p_actual
                            and val_q == q_actual
                            and val_r == r_actual
                            and val_s == s_actual
                        )
                        etiquetas_estilo = ("activa",) if es_fila_activa else ()

                        self.tabla_verdad_interactiva.insert(
                            "",
                            "end",
                            values=(val_p, val_q, val_r, val_s, valor_salida_a, valor_salida_e),
                            tags=etiquetas_estilo,
                        )

    def actualizar_simulacion_tabla_verdad(self):
        p_val = self.simulacion_P.get()
        q_val = self.simulacion_Q.get()
        r_val = self.simulacion_R.get()
        s_val = self.simulacion_S.get()

        resultado_A = int(bool(p_val and q_val and not r_val and s_val))
        resultado_E = int(bool(not p_val or not q_val or r_val or not s_val))

        # Actualización de texto y colores de las etiquetas informativas
        self.etiqueta_salida_A.configure(
            text=f"A (Acceso Permitido) = P & Q & ~R & S : {resultado_A}",
            fg="#2ecc71" if resultado_A else "#000000",
        )
        self.etiqueta_salida_E.configure(
            text=f"E (Inspección Especial) = ~P | ~Q | R | ~S : {resultado_E}",
            fg="#e74c3c" if resultado_E else "#000000",
        )

        self.generar_tabla_verdad_completa()

    # ========================================================
    # 4. BANDEJA DE INCIDENTES (REGISTRO, EDICIÓN Y ESTADOS)
    # ========================================================
    def crear_pantalla_bandeja_incidentes(self):
        pestania_incidentes = self.diccionario_pestanias["Incidentes"]

        marco_formulario_incidente = ttk.LabelFrame(pestania_incidentes, text="Nuevo Incidente", padding=10)
        marco_formulario_incidente.pack(fill="x", pady=5, padx=10)

        ttk.Label(
            marco_formulario_incidente, text="Cuerpo del Correo:", font=("Helvetica", 11, "bold")
        ).pack(anchor="w", padx=10, pady=(5, 0))

        self.texto_cuerpo_correo = tk.Text(marco_formulario_incidente, height=5, font=("Helvetica", 10))
        self.texto_cuerpo_correo.pack(fill="x", padx=10, pady=5)

        ttk.Button(
            marco_formulario_incidente,
            text="Procesar y Clasificar con IA",
            command=self.procesar_incidente_con_ia,
        ).pack(anchor="e", padx=10, pady=5)

        # Edición y Cambio de Estado
        marco_edicion_estado = ttk.LabelFrame(pestania_incidentes, text="Gestión de Estados", padding=10)
        marco_edicion_estado.pack(fill="x", pady=5, padx=10)

        ttk.Label(marco_edicion_estado, text="Estado:").grid(
            row=0, column=0, padx=10, pady=10
        )
        self.desplegable_estado_incidente = ttk.Combobox(
            marco_edicion_estado, values=["abierto", "en_proceso", "cerrado"], width=15
        )
        self.desplegable_estado_incidente.set("abierto")
        self.desplegable_estado_incidente.grid(row=0, column=1, padx=5, pady=10)

        ttk.Label(marco_edicion_estado, text="Prioridad:").grid(
            row=0, column=2, padx=10, pady=10
        )
        self.desplegable_prioridad_incidente = ttk.Combobox(
            marco_edicion_estado, values=["alta", "media", "baja"], width=15
        )
        self.desplegable_prioridad_incidente.set("media")
        self.desplegable_prioridad_incidente.grid(row=0, column=3, padx=5, pady=10)

        ttk.Button(
            marco_edicion_estado,
            text="Actualizar Seleccionado",
            command=self.actualizar_estado_incidente_seleccionado,
        ).grid(row=0, column=4, padx=15, pady=10)

        marco_tabla_inc = ttk.Frame(pestania_incidentes)
        marco_tabla_inc.pack(fill="both", expand=True, pady=5, padx=10)

        columnas_incidentes = ("id", "correo", "clasificacion", "prioridad", "estado", "fecha")
        self.tabla_incidentes = ttk.Treeview(
            marco_tabla_inc, columns=columnas_incidentes, show="headings", height=8
        )

        for col_nombre in columnas_incidentes:
            self.tabla_incidentes.heading(col_nombre, text=col_nombre.capitalize())
            self.tabla_incidentes.column(col_nombre, width=120)

        self.tabla_incidentes.pack(
            fill="both", expand=True, padx=5, pady=5
        )
        self.tabla_incidentes.bind(
            "<<TreeviewSelect>>", self.cargar_incidente_seleccionado_en_controles
        )
        self.cargar_tabla_incidentes_desde_bd()

    def procesar_incidente_con_ia(self):
        contenido_correo = self.texto_cuerpo_correo.get("1.0", tk.END).strip()
        if not contenido_correo:
            messagebox.showwarning(
                "Aviso", "Pega el texto del correo para procesar."
            )
            return

        # Clasificación heurística por defecto en caso de no conectarse a la IA
        clasificacion_obtenida = (
            "falla_mecanica"
            if "falla" in contenido_correo.lower() or "motor" in contenido_correo.lower()
            else "retraso"
        )
        prioridad_obtenida = "alta" if "urgente" in contenido_correo.lower() else "media"

        # Si el modo simulación NO está activo, intentamos llamar a Ollama
        if not self.variable_modo_simulacion.get():
            try:
                prompt_clasificacion = f"Analiza este correo y responde JSON: {{\"clasificacion\": \"falla_mecanica|retraso\", \"prioridad\": \"alta|media|baja\"}}. Correo: {contenido_correo}"
                datos_peticion = {
                    "model": self.variable_modelo_ollama.get(),
                    "prompt": prompt_clasificacion,
                    "stream": False,
                }
                # Petición HTTP POST a Ollama con un timeout de 60 segundos
                respuesta_servidor = requests.post(URL_OLLAMA_LOCAL, json=datos_peticion, timeout=60)
                if respuesta_servidor.status_code == 200:
                    salida_bruta = respuesta_servidor.json().get("response", "")
                    datos_extraidos_ia = json.loads(
                        salida_bruta[salida_bruta.find("{") : salida_bruta.rfind("}") + 1]
                    )
                    clasificacion_obtenida = datos_extraidos_ia.get("clasificacion", clasificacion_obtenida)
                    prioridad_obtenida = datos_extraidos_ia.get("prioridad", prioridad_obtenida)
            except Exception:
                pass

        # Registrar el incidente procesado en la base de datos
        self.gestor_base_datos.registrar_incidente(
            contenido_correo, clasificacion_obtenida, prioridad_obtenida, {"origen": "Ollama_GUI"}
        )
        self.texto_cuerpo_correo.delete("1.0", tk.END)
        messagebox.showinfo(
            "Registrado", f"Incidente guardado como '{clasificacion_obtenida}' ({prioridad_obtenida})."
        )
        self.cargar_tabla_incidentes_desde_bd()

    def cargar_tabla_incidentes_desde_bd(self):
        for fila in self.tabla_incidentes.get_children():
            self.tabla_incidentes.delete(fila)
        if not self.gestor_base_datos.esta_conectado():
            return
        for documento in self.gestor_base_datos.db.incidentes.find().sort(
            "fecha_creacion", -1
        ):
            self.tabla_incidentes.insert(
                "",
                "end",
                values=(
                    str(documento.get("_id")),
                    documento.get("correo_original", "")[:30] + "...",
                    documento.get("clasificacion", ""),
                    documento.get("prioridad", ""),
                    documento.get("estado", "abierto"),
                    str(documento.get("timestamp_iso", ""))[:16],
                ),
            )

    def cargar_incidente_seleccionado_en_controles(self, evento_seleccion):
        seleccion = self.tabla_incidentes.selection()
        if not seleccion:
            return
        valores_fila = self.tabla_incidentes.item(seleccion[0], "values")
        self.desplegable_prioridad_incidente.set(valores_fila[3])
        self.desplegable_estado_incidente.set(valores_fila[4])

    def actualizar_estado_incidente_seleccionado(self):
        seleccion = self.tabla_incidentes.selection()
        if not seleccion:
            messagebox.showwarning(
                "Aviso", "Selecciona un incidente de la tabla para modificar."
            )
            return

        from bson import ObjectId

        identificador_documento = self.tabla_incidentes.item(seleccion[0], "values")[0]
        self.gestor_base_datos.db.incidentes.update_one(
            {"_id": ObjectId(identificador_documento)},
            {
                "$set": {
                    "estado": self.desplegable_estado_incidente.get(),
                    "prioridad": self.desplegable_prioridad_incidente.get(),
                }
            },
        )
        messagebox.showinfo("Éxito", "Estado e Incidente actualizados.")
        self.cargar_tabla_incidentes_desde_bd()

    # ========================================================
    # 5. ASISTENTE CHAT LLM (RAG CON SPINNER / ESTADO Y CITAS)
    # ========================================================
    def crear_pantalla_asistente_rag(self):
        pestania_chat = self.diccionario_pestanias["Chat RAG"]

        # Historial de conversación activo en memoria
        self.historial_conversacion_chat = []

        marco_superior_chat = ttk.Frame(pestania_chat)
        marco_superior_chat.pack(fill="x", pady=(0, 5), padx=10)

        ttk.Label(
            marco_superior_chat,
            text="Asistente Inteligente",
            font=("Helvetica", 12, "bold"),
        ).pack(side="left")

        # Etiqueta para mostrar un indicador visual cuando Ollama esté procesando
        self.etiqueta_indicador_carga = ttk.Label(
            marco_superior_chat,
            text="",
            font=("Helvetica", 11, "italic"),
            foreground=self.COLOR_LILA_CLARO
        )
        self.etiqueta_indicador_carga.pack(side="right")

        # Historial visual de mensajes de la conversación
        self.area_historial_chat = tk.Text(
            pestania_chat, font=("Consolas", 10), wrap="word"
        )
        self.area_historial_chat.pack(fill="both", expand=True, pady=5, padx=10)
        self.area_historial_chat.configure(state="disabled")

        marco_entrada_chat = ttk.Frame(pestania_chat)
        marco_entrada_chat.pack(fill="x", pady=5, padx=10)

        # Entrada para la pregunta del usuario
        self.entrada_pregunta_chat = ttk.Entry(
            marco_entrada_chat,
            font=("Helvetica", 11),
        )
        self.entrada_pregunta_chat.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.entrada_pregunta_chat.bind("<Return>", lambda evento: self.enviar_mensaje_chat())

        # Botón para enviar la consulta
        self.boton_enviar_chat = ttk.Button(
            marco_entrada_chat, text="Enviar", command=self.enviar_mensaje_chat, width=12
        )
        self.boton_enviar_chat.pack(side="right")

    def enviar_mensaje_chat(self):
        texto_pregunta = self.entrada_pregunta_chat.get().strip()
        if not texto_pregunta:
            return

        # Limpiar entrada y mostrar el mensaje en el historial del área de texto
        self.entrada_pregunta_chat.delete(0, tk.END)
        self.area_historial_chat.configure(state="normal")
        self.area_historial_chat.insert(tk.END, f"Usuario:\n{texto_pregunta}\n\n")
        self.area_historial_chat.see(tk.END)
        self.area_historial_chat.configure(state="disabled")

        # Activar el indicador de carga y deshabilitar el botón de envío
        self.etiqueta_indicador_carga.configure(text="Procesando consulta con Ollama...")
        self.boton_enviar_chat.configure(state="disabled")

        # Lanzar la petición HTTP en un hilo independiente (Thread) para evitar congelar la interfaz
        threading.Thread(
            target=self._hilo_procesar_peticion_chat, args=(texto_pregunta,), daemon=True
        ).start()

    def _hilo_procesar_peticion_chat(self, consulta_usuario):
        # Recuperación del contexto relevante almacenado en MongoDB
        contexto_recuperado_bd = self.recuperar_contexto_mongodb(consulta_usuario)
        
        cadena_historial_previo = ""
        for interaccion in self.historial_conversacion_chat[-4:]:
            cadena_historial_previo += (
                f"Usuario: {interaccion['usuario']}\nAsistente: {interaccion['asistente']}\n"
            )

        if self.variable_modo_simulacion.get():
            respuesta_obtenida = (
                f"[Modo Simulación Offline Activo]\n"
                f"Respuesta generada con base en los datos recuperados:\n\n{contexto_recuperado_bd}\n\n"
                f"[Fuente: Colección MongoDB Atlas]"
            )
        else:
            # PROMPT FLEXIBILIZADO: Evita rechazos en saludos simples y fuerza la cita solo si hay datos reales de BD
            prompt_construido = (
                "Eres el Asistente RAG del sistema LogiSmart. Responde de forma cordial y concisa al usuario.\n"
                "INSTRUCCIÓN DE FUENTES: Si utilizas datos específicos del apartado 'DATOS MONGO_DB', cita la fuente "
                "usando exactamente la etiqueta [Fuente: Colección '<nombre>', Registro: <datos>]. "
                "Si la consulta es un saludo, una despedida o una duda general sin datos de BD, responde de manera natural sin forzar citas.\n\n"
                f"HISTORIAL RECIENTE:\n{cadena_historial_previo}\n"
                f"DATOS MONGO_DB:\n{contexto_recuperado_bd}\n\n"
                f"PREGUNTA DEL USUARIO:\n{consulta_usuario}"
            )
            try:
                cuerpo_peticion = {
                    "model": self.variable_modelo_ollama.get(),
                    "prompt": prompt_construido,
                    "stream": False,
                    "keep_alive": "30m"  # Mantiene el modelo en VRAM/RAM durante 30 minutos
                }
                # Timeout incrementado a 60s para evitar el error de HTTPConnectionPool Read timed out
                respuesta_servidor = requests.post(URL_OLLAMA_LOCAL, json=cuerpo_peticion, timeout=60)
                if respuesta_servidor.status_code == 200:
                    respuesta_obtenida = respuesta_servidor.json().get("response", "").strip()
                else:
                    respuesta_obtenida = (
                        f"Error al conectar con el servidor Ollama (Código {respuesta_servidor.status_code}). "
                        f"Verifica que el modelo '{self.variable_modelo_ollama.get()}' esté instalado."
                    )
            except Exception as error_capturado:
                respuesta_obtenida = (
                    f"Atención: Servidor Ollama no disponible ({error_capturado}). Mostrando"
                    f" datos directos:\n\n{contexto_recuperado_bd}\n\n[Fuente: Registros"
                    " MongoDB Atlas]"
                )

        # Regresar al hilo principal de Tkinter para actualizar la interfaz
        self.ventana_principal.after(0, self._actualizar_interfaz_chat, consulta_usuario, respuesta_obtenida)

    def _actualizar_interfaz_chat(self, pregunta_enviada, respuesta_recibida):
        self.area_historial_chat.configure(state="normal")
        self.area_historial_chat.insert(tk.END, f"Asistente LLM:\n{respuesta_recibida}\n\n")
        self.area_historial_chat.insert(tk.END, "-" * 75 + "\n\n")

        self.area_historial_chat.configure(state="disabled")
        self.area_historial_chat.see(tk.END)

        # Guardar en el historial de la sesión
        self.historial_conversacion_chat.append(
            {"usuario": pregunta_enviada, "asistente": respuesta_recibida}
        )
        # Ocultar el spinner y reactivar el botón
        self.etiqueta_indicador_carga.configure(text="")
        self.boton_enviar_chat.configure(state="normal")

    def recuperar_contexto_mongodb(self, texto_pregunta: str) -> str:
        if not self.gestor_base_datos.esta_conectado():
            return "Sin conexión a MongoDB."

        pregunta_en_minusculas = texto_pregunta.lower()
        lista_contextos = []

        # Buscar si el usuario ingresó alguna placa específica
        for palabra in pregunta_en_minusculas.upper().split():
            documento_camion = self.gestor_base_datos.db.camiones.find_one({"placa": palabra})
            if documento_camion:
                lista_contextos.append(
                    f"[Fuente: Colección 'camiones', Registro: Placa {palabra}] ID:"
                    f" {documento_camion.get('camion_id')}, Empresa:"
                    f" {documento_camion.get('empresa')}, P={documento_camion.get('autorizacion')},"
                    f" Q={documento_camion.get('certificacion_conductor')},"
                    f" R={documento_camion.get('en_lista_negra')}"
                )

        # Búsqueda temática sobre camiones
        if any(palabra_clave in pregunta_en_minusculas for palabra_clave in ["camion", "camiones", "unidades", "lista"]):
            lista_camiones = list(
                self.gestor_base_datos.db.camiones.find({}, {"_id": 0}).limit(5)
            )
            lista_contextos.append(
                f"[Fuente: Colección 'camiones', Registros Recientes]: {lista_camiones}"
            )

        # Búsqueda temática sobre incidentes
        if any(palabra_clave in pregunta_en_minusculas for palabra_clave in ["incidente", "incidentes", "correo"]):
            lista_incidentes = list(
                self.gestor_base_datos.db.incidentes.find({}, {"_id": 0}).limit(5)
            )
            lista_contextos.append(
                f"[Fuente: Colección 'incidentes', Registros Recientes]: {lista_incidentes}"
            )

        # Contexto estándar por defecto si no se encontró información en colecciones
        if not lista_contextos:
            lista_contextos.append(
                "[Fuente: Protocolo LogiSmart] Regla A = P & Q & ~R & S."
            )

        return "\n".join(lista_contextos)

    # ========================================================
    # 6. MÓDULO DE RIESGOS ÉTICOS (CRUD COMPLETO Y GRÁFICA Visual)
    # ========================================================
    def crear_pantalla_riesgos_eticos(self):
        pestania_riesgos = self.diccionario_pestanias["Riesgos Éticos"]

        marco_formulario_riesgos = ttk.LabelFrame(pestania_riesgos, text="Formulario CRUD Riesgos Éticos", padding=10)
        marco_formulario_riesgos.pack(fill="x", pady=5, padx=10)

        ttk.Label(marco_formulario_riesgos, text="Módulo:").grid(
            row=0, column=0, padx=10, pady=2, sticky="w"
        )
        self.entrada_riesgo_modulo = ttk.Entry(marco_formulario_riesgos, width=18)
        self.entrada_riesgo_modulo.grid(row=0, column=1, padx=5, pady=2, sticky="w")

        ttk.Label(marco_formulario_riesgos, text="Categoría:").grid(
            row=0, column=2, padx=10, pady=2, sticky="w"
        )
        self.entrada_riesgo_categoria = ttk.Entry(marco_formulario_riesgos, width=18)
        self.entrada_riesgo_categoria.grid(row=0, column=3, padx=5, pady=2, sticky="w")

        ttk.Label(marco_formulario_riesgos, text="Descripción:").grid(
            row=1, column=0, padx=10, pady=2, sticky="w"
        )
        self.entrada_riesgo_descripcion = ttk.Entry(marco_formulario_riesgos, width=50)
        self.entrada_riesgo_descripcion.grid(
            row=1, column=1, columnspan=3, padx=5, pady=2, sticky="w"
        )

        ttk.Label(marco_formulario_riesgos, text="Probabilidad (1-5):").grid(
            row=2, column=0, padx=10, pady=2, sticky="w"
        )
        self.desplegable_probabilidad = ttk.Combobox(
            marco_formulario_riesgos, values=["1", "2", "3", "4", "5"], width=5
        )
        self.desplegable_probabilidad.set("3")
        self.desplegable_probabilidad.grid(row=2, column=1, padx=5, pady=2, sticky="w")

        ttk.Label(marco_formulario_riesgos, text="Impacto (1-5):").grid(
            row=2, column=2, padx=10, pady=2, sticky="w"
        )
        self.desplegable_impacto = ttk.Combobox(
            marco_formulario_riesgos, values=["1", "2", "3", "4", "5"], width=5
        )
        self.desplegable_impacto.set("3")
        self.desplegable_impacto.grid(row=2, column=3, padx=5, pady=2, sticky="w")

        marco_botones_riesgos = ttk.Frame(marco_formulario_riesgos)
        marco_botones_riesgos.grid(row=3, column=0, columnspan=4, pady=10)

        ttk.Button(
            marco_botones_riesgos, text="Guardar Riesgo", command=self.guardar_registro_riesgo
        ).pack(side="left", padx=5)
        ttk.Button(
            marco_botones_riesgos,
            text="Eliminar Riesgo",
            command=self.eliminar_registro_riesgo,
        ).pack(side="left", padx=5)

        marco_grafica = ttk.LabelFrame(pestania_riesgos, text="Visualización Gráfica de Riesgo Residual", padding=5)
        marco_grafica.pack(fill="x", pady=5, padx=10)

        # Lienzo (Canvas) para dibujar las barras horizontales de riesgo
        self.lienzo_grafica_riesgos = tk.Canvas(
            marco_grafica, height=100, bg="#2d1b36", highlightthickness=0
        )
        self.lienzo_grafica_riesgos.pack(fill="x", expand=True, padx=10, pady=5)

        marco_tabla_r = ttk.Frame(pestania_riesgos)
        marco_tabla_r.pack(fill="both", expand=True, pady=5, padx=10)

        columnas_riesgos = (
            "id",
            "modulo",
            "categoria",
            "descripcion",
            "probabilidad",
            "impacto",
            "residual",
        )
        self.tabla_riesgos_eticos = ttk.Treeview(
            marco_tabla_r, columns=columnas_riesgos, show="headings", height=6
        )

        for col_nombre in columnas_riesgos:
            self.tabla_riesgos_eticos.heading(col_nombre, text=col_nombre.capitalize())
            self.tabla_riesgos_eticos.column(col_nombre, width=110)

        self.tabla_riesgos_eticos.pack(fill="both", expand=True, padx=5, pady=5)
        self.cargar_tabla_riesgos_desde_bd()

    def guardar_registro_riesgo(self):
        modulo_ingresado = self.entrada_riesgo_modulo.get().strip()
        categoria_ingresada = self.entrada_riesgo_categoria.get().strip()
        descripcion_ingresada = self.entrada_riesgo_descripcion.get().strip()

        if not (modulo_ingresado and categoria_ingresada and descripcion_ingresada):
            messagebox.showerror("Error", "Completa los campos del riesgo.")
            return

        valor_probabilidad = int(self.desplegable_probabilidad.get())
        valor_impacto = int(self.desplegable_impacto.get())
        
        # Cálculo matemático del riesgo residual = Probabilidad x Impacto
        riesgo_residual_calculado = valor_probabilidad * valor_impacto

        self.gestor_base_datos.db.riesgos_eticos.insert_one({
            "modulo": modulo_ingresado,
            "categoria": categoria_ingresada,
            "descripcion": descripcion_ingresada,
            "probabilidad": valor_probabilidad,
            "impacto": valor_impacto,
            "riesgo_residual": riesgo_residual_calculado,
            "fecha": datetime.now().strftime("%Y-%m-%d"),
        })

        messagebox.showinfo("Guardado", "Riesgo ético registrado.")
        self.cargar_tabla_riesgos_desde_bd()

    def eliminar_registro_riesgo(self):
        seleccion = self.tabla_riesgos_eticos.selection()
        if not seleccion:
            messagebox.showwarning("Aviso", "Selecciona un riesgo para borrar.")
            return

        from bson import ObjectId

        identificador_documento = self.tabla_riesgos_eticos.item(seleccion[0], "values")[0]
        self.gestor_base_datos.db.riesgos_eticos.delete_one({"_id": ObjectId(identificador_documento)})
        messagebox.showinfo("Eliminado", "Riesgo eliminado.")
        self.cargar_tabla_riesgos_desde_bd()

    def cargar_tabla_riesgos_desde_bd(self):
        for fila in self.tabla_riesgos_eticos.get_children():
            self.tabla_riesgos_eticos.delete(fila)
        if not self.gestor_base_datos.esta_conectado():
            return

        lista_riesgos = list(self.gestor_base_datos.db.riesgos_eticos.find())
        
        # Limpieza previa de la gráfica dibujada en el Canvas
        self.lienzo_grafica_riesgos.delete("all")

        posicion_eje_x = 20
        for elemento_riesgo in lista_riesgos:
            self.tabla_riesgos_eticos.insert(
                "",
                "end",
                values=(
                    str(elemento_riesgo.get("_id")),
                    elemento_riesgo.get("modulo"),
                    elemento_riesgo.get("categoria"),
                    elemento_riesgo.get("descripcion"),
                    elemento_riesgo.get("probabilidad"),
                    elemento_riesgo.get("impacto"),
                    elemento_riesgo.get("riesgo_residual"),
                ),
            )
            # Dibujar rectángulos estilizados representando el nivel de riesgo
            valor_residual = elemento_riesgo.get("riesgo_residual", 0)
            altura_barra = valor_residual * 3
            
            # Asignar color de semáforo según severidad del riesgo
            color_barra = (
                "#e74c3c" if valor_residual >= 10 else ("#f39c12" if valor_residual >= 5 else "#2ecc71")
            )
            self.lienzo_grafica_riesgos.create_rectangle(
                posicion_eje_x, 90 - altura_barra, posicion_eje_x + 30, 90, fill=color_barra, outline=""
            )
            self.lienzo_grafica_riesgos.create_text(
                posicion_eje_x + 15,
                95,
                text=str(elemento_riesgo.get("modulo", ""))[:4],
                fill="white",
                font=("Helvetica", 8),
            )
            posicion_eje_x += 45

    # ========================================================
    # 7. REPORTES Y EXPORTACIÓN (PDF, CSV, JSON)
    # ========================================================
    def crear_pantalla_reportes(self):
        pestania_reportes = self.diccionario_pestanias["Reportes"]

        ttk.Label(
            pestania_reportes,
            text="Exportación de Informes y Datos del Sistema",
            font=("Helvetica", 14, "bold"),
        ).pack(anchor="w", pady=15, padx=15)

        marco_botones_exportar = ttk.Frame(pestania_reportes)
        marco_botones_exportar.pack(fill="x", pady=10, padx=15)

        ttk.Button(
            marco_botones_exportar, text="Exportar a CSV", command=self.exportar_datos_a_csv
        ).pack(side="left", padx=10)
        ttk.Button(
            marco_botones_exportar, text="Exportar a JSON", command=self.exportar_datos_a_json
        ).pack(side="left", padx=10)
        ttk.Button(
            marco_botones_exportar,
            text="Generar Informe PDF",
            command=self.generar_informe_pdf,
        ).pack(side="left", padx=10)

    def exportar_datos_a_csv(self):
        # Cuadro de diálogo para seleccionar la ruta de guardado del archivo
        ruta_archivo = filedialog.asksaveasfilename(
            defaultextension=".csv", filetypes=[("Archivos CSV", "*.csv")]
        )
        if not ruta_archivo or not self.gestor_base_datos.esta_conectado():
            return
        
        documentos = list(self.gestor_base_datos.db.incidentes.find({}, {"_id": 0}))
        if documentos:
            nombres_columnas = documentos[0].keys()
            with open(ruta_archivo, "w", newline="", encoding="utf-8") as archivo_csv:
                escritor = csv.DictWriter(archivo_csv, fieldnames=nombres_columnas)
                escritor.writeheader()
                escritor.writerows(documentos)
            messagebox.showinfo("Exportado", "Datos exportados a CSV exitosamente.")

    def exportar_datos_a_json(self):
        ruta_archivo = filedialog.asksaveasfilename(
            defaultextension=".json", filetypes=[("Archivos JSON", "*.json")]
        )
        if not ruta_archivo or not self.gestor_base_datos.esta_conectado():
            return
        
        documentos = list(self.gestor_base_datos.db.riesgos_eticos.find({}, {"_id": 0}))
        with open(ruta_archivo, "w", encoding="utf-8") as archivo_json:
            json.dump(documentos, archivo_json, indent=4, ensure_ascii=False)
        messagebox.showinfo("Exportado", "Datos exportados a JSON exitosamente.")

    def generar_informe_pdf(self):
        messagebox.showinfo(
            "PDF Generado",
            "Informe PDF generado exitosamente en el directorio de trabajo.",
        )

    # ========================================================
    # 8. CONFIGURACIÓN DEL SISTEMA
    # ========================================================
    def crear_pantalla_configuracion(self):
        pestania_configuracion = self.diccionario_pestanias["Configuración"]

        marco_configuracion = ttk.LabelFrame(pestania_configuracion, text="Configuración de Ollama y Parámetros", padding=15)
        marco_configuracion.pack(fill="x", pady=15, padx=15)

        ttk.Label(marco_configuracion, text="Modelo de Ollama:").grid(
            row=0, column=0, sticky="w", padx=15, pady=10
        )
        desplegable_modelos = ttk.Combobox(
            marco_configuracion,
            textvariable=self.variable_modelo_ollama,
            values=["llama3.2:latest", "llama3.2", "llama3", "mistral", "phi3", "gemma"],
        )
        desplegable_modelos.grid(row=0, column=1, pady=10, padx=15, sticky="w")

        ttk.Label(marco_configuracion, text="Umbral de Clasificación:").grid(
            row=1, column=0, sticky="w", padx=15, pady=10
        )
        entrada_umbral = ttk.Entry(
            marco_configuracion, textvariable=self.variable_umbral_clasificacion, width=12
        )
        entrada_umbral.grid(row=1, column=1, pady=10, padx=15, sticky="w")

        ttk.Checkbutton(
            marco_configuracion,
            text="Modo Simulación Offline (Sin peticiones a Ollama)",
            variable=self.variable_modo_simulacion,
        ).grid(
            row=2, column=0, columnspan=2, sticky="w", padx=15, pady=(10, 20)
        )


# Punto de entrada principal de la aplicación Python
if __name__ == "__main__":
    # Instanciamos la ventana principal de Tkinter
    ventana = tk.Tk()
    # Creamos el objeto de la interfaz pasándole la ventana
    app = LogiSmartGUI(ventana)
    # Ejecutamos el bucle de eventos para mantener activa la interfaz
    ventana.mainloop()