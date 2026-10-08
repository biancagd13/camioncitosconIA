import json
import logging
from typing import List, Optional
from pydantic import BaseModel, Field
import ollama

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ClasificadorHibrido")


# ============================================================
# 1. ESQUEMA PYDANTIC PARA VALIDACIÓN
# ============================================================

class IncidenteJSON(BaseModel):
    categoria: str = Field(description="Categoría del incidente: Acceso, Peso, Materiales, Seguridad, Emergencia, Otro")
    prioridad: str = Field(description="Prioridad asignada: BAJA, MEDIA, ALTA, CRITICA")
    entidades: List[str] = Field(default_factory=list, description="Placas, nombres, IDs o empresas mencionadas")
    resumen: str = Field(description="Resumen breve del incidente en una oración")


# Prioridades ordenadas para la fusión de seguridad
MAPA_PRIORIDADES = {"BAJA": 1, "MEDIA": 2, "ALTA": 3, "CRITICA": 4}


# ============================================================
# 2. CLASIFICADOR POR REGLAS (RESPALDO Y SEGURIDAD CRÍTICA)
# ============================================================

def clasificar_por_reglas(texto_correo: str) -> IncidenteJSON:
    """Clasificador determinista basado en palabras clave para respaldo y emergencias."""
    texto = texto_correo.lower()
    
    # 🚨 DETECCIÓN DE EMERGENCIAS CRÍTICAS (Violencia, Homicidios, Asaltos, Accidentes)
    palabras_criticas = ["mataron", "muerto", "homicidio", "asaltado", "asalto", "arma", "disparo", "secuestro", "herido", "balacera"]
    if any(palabra in texto for palabra in palabras_criticas):
        return IncidenteJSON(
            categoria="Emergencia",
            prioridad="CRITICA",
            entidades=[],
            resumen="Alerta crítica: Evento de alto riesgo, violencia o pérdida humana detectado."
        )

    # ⚠️ REGLAS LOGÍSTICAS HABITUALES
    elif "peso" in texto or "excede" in texto or "báscula" in texto:
        return IncidenteJSON(
            categoria="Peso",
            prioridad="ALTA",
            entidades=[],
            resumen="Incidente detectado por exceso de peso o problemas en báscula."
        )
    elif "no autorizado" in texto or "acceso" in texto or "barrera" in texto:
        return IncidenteJSON(
            categoria="Acceso",
            prioridad="CRITICA",
            entidades=[],
            resumen="Intento o anomalía de acceso no autorizado."
        )
    elif "peligroso" in texto or "químico" in texto or "fuga" in texto:
        return IncidenteJSON(
            categoria="Materiales",
            prioridad="ALTA",
            entidades=[],
            resumen="Transporte o manejo no adecuado de materiales peligrosos."
        )
    elif "retraso" in texto or "tarde" in texto or "demora" in texto:
        return IncidenteJSON(
            categoria="Seguridad",
            prioridad="MEDIA",
            entidades=[],
            resumen="Aviso o reporte de retraso logístico."
        )
    else:
        return IncidenteJSON(
            categoria="Otro",
            prioridad="BAJA",
            entidades=[],
            resumen="Reporte general o incidente sin categoría crítica explícita."
        )


# ============================================================
# 3. CLASIFICADOR HÍBRIDO (LLM + REGLAS)
# ============================================================

def clasificar_incidente_hibrido(texto_correo: str, modelo_ollama: str = "llama3") -> dict:
    """
    Clasifica un correo usando Ollama con salida JSON validada por Pydantic.
    Aplica plan de respaldo y regla de fusión de seguridad.
    """
    
    # SYSTEM PROMPT MEJORADO CON REGLAS DE EVALUACIÓN
    prompt = f"""
    Eres un oficial de seguridad y control logístico en un centro de distribución. 
    Analiza el siguiente correo y clasifica su nivel de riesgo y categoría.

    REGLAS DE PRIORIZACIÓN CRÍTICA:
    - CRITICA: Asaltos, homicidios, violencia, heridos, personas armadas, accesos no autorizados o amenazas a la vida.
    - ALTA: Exceso de peso, derrames de materiales peligrosos o fallas en barreras principales.
    - MEDIA: Retrasos logísticos, fallas mecánicas menores o discrepancias menores.
    - BAJA: Informes de rutina, consultas generales o avisos informativos.

    Responde EXCLUSIVAMENTE con un JSON válido respetando este esquema:
    {{
        "categoria": "Acceso" | "Peso" | "Materiales" | "Seguridad" | "Emergencia" | "Otro",
        "prioridad": "BAJA" | "MEDIA" | "ALTA" | "CRITICA",
        "entidades": ["lista de placas, nombres, IDs o empresas mencionadas"],
        "resumen": "Resumen conciso en una frase"
    }}

    Correo a analizar:
    "{texto_correo}"
    """

    incidente_llm: Optional[IncidenteJSON] = None

    # Intentos de llamada a Ollama
    for intento in range(2):
        try:
            respuesta = ollama.chat(
                model=modelo_ollama,
                messages=[{"role": "user", "content": prompt}],
                format="json"
            )
            contenido = respuesta['message']['content']
            
            # Validación con Pydantic
            datos_json = json.loads(contenido)
            incidente_llm = IncidenteJSON(**datos_json)
            logger.info("✅ Clasificación exitosa con Ollama (LLM).")
            break
        except Exception as e:
            logger.warning(f"⚠️ Intento {intento + 1} fallido con Ollama: {e}")

    # Clasificación paralela basada en reglas
    incidente_reglas = clasificar_por_reglas(texto_correo)

    # Fallback si el LLM falla
    if incidente_llm is None:
        logger.info("🔄 Usando clasificador de reglas como respaldo.")
        return {
            "resultado": incidente_reglas.model_dump(),
            "fuente": "REGLAS_FALLBACK",
            "requiere_revision_humana": True
        }

    # ============================================================
    # FUSIÓN Y LÓGICA DE SEGURIDAD (Capa de Protección)
    # ============================================================
    prio_llm = MAPA_PRIORIDADES.get(incidente_llm.prioridad.upper(), 1)
    prio_reglas = MAPA_PRIORIDADES.get(incidente_reglas.prioridad.upper(), 1)

    requiere_revision = prio_llm != prio_reglas
    
    # Prevalece siempre la prioridad más alta por seguridad
    if prio_reglas > prio_llm:
        incidente_final = incidente_llm
        incidente_final.prioridad = incidente_reglas.prioridad
        if incidente_reglas.prioridad == "CRITICA":
            incidente_final.categoria = incidente_reglas.categoria
    else:
        incidente_final = incidente_llm

    return {
        "resultado": incidente_final.model_dump(),
        "fuente": "HIBRIDO",
        "requiere_revision_humana": requiere_revision,
        "comparativa": {
            "prioridad_llm": incidente_llm.prioridad,
            "prioridad_reglas": incidente_reglas.prioridad
        }
    }


if __name__ == "__main__":
    # Prueba rápida con el caso que falló anteriormente
    correo_critico = "Al chofer lo mataron durante el trayecto a la planta."
    res = clasificar_por_reglas(correo_critico)
    print("\n========== PRUEBA DE EMERGENCIAS CRÍTICAS ==========")
    print(json.dumps(res.model_dump(), indent=4, ensure_ascii=False))