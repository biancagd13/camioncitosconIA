import logging
from database import DatabaseManager
import ollama

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("AsistenteRAG")


class AsistenteLogiSmart:
    """
    Asistente conversacional con patrón RAG sencillo (MongoDB + Ollama).
    Responde consultas operativas citando fuentes y evitando alucinaciones.
    """

    def __init__(self, db_manager: DatabaseManager, modelo_ollama: str = "llama3"):
        self.db = db_manager
        self.modelo = modelo_ollama

    def buscar_contexto(self, consulta: str) -> list:
        """Busca registros relevantes en MongoDB por placa o palabra clave."""
        contexto = []
        
        if not self.db.esta_conectado():
            return contexto

        # Extraer posibles palabras/placas en mayúsculas (ej: CAM-102, ABC-1234)
        palabras = consulta.upper().split()

        # 1. Buscar en bitácora de accesos
        for palabra in palabras:
            accesos = list(self.db.db.accesos.find({"placa": palabra}, {"_id": 0}))
            for acc in accesos:
                contexto.append({
                    "origen": "Colección 'accesos'",
                    "placa": acc.get("placa"),
                    "explicacion": acc.get("explicacion"),
                    "timestamp": acc.get("timestamp")
                })

        # 2. Buscar en incidentes
        incidentes = list(self.db.db.incidentes.find({}, {"_id": 0}))
        for inc in incidentes:
            texto = str(inc).lower()
            if any(p.lower() in texto for p in palabras if len(p) > 3):
                contexto.append({
                    "origen": "Colección 'incidentes'",
                    "clasificacion": inc.get("clasificacion"),
                    "prioridad": inc.get("prioridad"),
                    "resumen": inc.get("datos_extraidos", {}).get("resumen", "Sin resumen"),
                    "estado": inc.get("estado")
                })

        return contexto

    def responder_consulta(self, pregunta_usuario: str) -> dict:
        """Procesa la pregunta, recupera contexto y genera respuesta grounded."""
        registros_encontrados = self.buscar_contexto(pregunta_usuario)

        # Regla Anti-Alucinación: Si no hay información en MongoDB, no inventar
        if not registros_encontrados:
            return {
                "respuesta": "No tengo información registrada en el sistema sobre esa consulta.",
                "fuentes": [],
                "tiene_datos": False
            }

        prompt = f"""
        Eres el Asistente Oficial del sistema de control LogiSmart.
        Responde la siguiente pregunta del operador utilizando ÚNICAMENTE la siguiente información recuperada de la base de datos:

        INFORMACIÓN DE BASE DE DATOS (CONTEXTO):
        {registros_encontrados}

        PREGUNTA DEL OPERADOR:
        "{pregunta_usuario}"

        REGLAS OBLIGATORIAS:
        1. Responde de forma clara y concisa.
        2. Cita la fuente de los datos (por ejemplo, 'Según la colección accesos...').
        3. No inventes ningún dato que no esté en el contexto proporcionado.
        """

        try:
            respuesta = ollama.chat(
                model=self.modelo,
                messages=[{"role": "user", "content": prompt}]
            )
            contenido = respuesta['message']['content']
        except Exception as e:
            logger.warning(f"⚠️ Error al conectar con Ollama: {e}. Respondiendo con respaldo directo.")
            contenido = f"Información recuperada del sistema:\n{registros_encontrados}"

        return {
            "respuesta": contenido,
            "fuentes": registros_encontrados,
            "tiene_datos": True
        }


if __name__ == "__main__":
    # Prueba del filtro anti-alucinación sin Ollama o sin datos previa
    db = DatabaseManager()
    asistente = AsistenteLogiSmart(db)

    print("\n========== PRUEBA ASISTENTE RAG (SIN DATOS) ==========")
    res = asistente.responder_consulta("¿Por qué el camión XYZ-9999 fue rechazado?")
    print("Respuesta:", res["respuesta"])