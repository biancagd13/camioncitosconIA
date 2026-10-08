import logging
from database import DatabaseManager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("RiesgosEticos")

# Matriz para convertir niveles a puntaje numérico (Probabilidad x Impacto)
VALORES = {"Bajo": 1, "Baja": 1, "Medio": 2, "Media": 2, "Alto": 3, "Alta": 3}


class MatrizRiesgosEticos:
    """
    Gestor de Riesgos Éticos de la IA con evaluación de Riesgo Residual
    y persistencia en MongoDB Atlas.
    """

    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
        self.inicializar_riesgos_base()

    def calcular_puntaje(self, probabilidad: str, impacto: str) -> int:
        """Calcula el puntaje de riesgo multiplicando probabilidad x impacto."""
        p = VALORES.get(probabilidad, 2)
        i = VALORES.get(impacto, 2)
        return p * i

    def inicializar_riesgos_base(self):
        """Carga en MongoDB los 4 riesgos éticos propios del sistema si la colección está vacía."""
        if not self.db.esta_conectado():
            return

        # Si ya hay datos en la colección, no duplicar
        if self.db.db.riesgos_eticos.count_documents({}) > 0:
            return

        riesgos_base = [
            {
                "modulo": "Asistente LLM (RAG)",
                "descripcion": "Alucinaciones del LLM generando respuestas inventadas o engañosas.",
                "categoria": "Fiabilidad / Exactitud",
                "probabilidad": "Media",
                "impacto": "Alto",
                "mitigacion": "Implementación de filtro RAG estricto: responder 'no tengo información' si no hay coincidencia en MongoDB.",
                "probabilidad_residual": "Baja",
                "impacto_residual": "Bajo"
            },
            {
                "modulo": "Clasificador Híbrido",
                "descripcion": "Sesgo en la clasificación de correos que contienen ortografía informal o modismos.",
                "categoria": "Equidad / Sesgo",
                "probabilidad": "Alta",
                "impacto": "Medio",
                "mitigacion": "Uso de clasificador determinista por palabras clave como respaldo y regla de prioridad máxima.",
                "probabilidad_residual": "Baja",
                "impacto_residual": "Medio"
            },
            {
                "modulo": "Registro de Accesos",
                "descripcion": "Vulnerabilidad en la privacidad de datos personales del conductor.",
                "categoria": "Privacidad",
                "probabilidad": "Media",
                "impacto": "Alto",
                "mitigacion": "Anonimización de datos en bitácoras y políticas de retención de información.",
                "probabilidad_residual": "Baja",
                "impacto_residual": "Bajo"
            },
            {
                "modulo": "Motor de Reglas",
                "descripcion": "Dependencia excesiva de la automatización en la toma de decisiones críticas de seguridad.",
                "categoria": "Autonomía Humana",
                "probabilidad": "Alta",
                "impacto": "Alto",
                "mitigacion": "Marcado automático de flag 'requiere_revision_humana' cuando existan discrepancias.",
                "probabilidad_residual": "Media",
                "impacto_residual": "Bajo"
            }
        ]

        for r in riesgos_base:
            self.registrar_riesgo(
                modulo=r["modulo"],
                descripcion=r["descripcion"],
                categoria=r["categoria"],
                probabilidad=r["probabilidad"],
                impacto=r["impacto"],
                mitigacion=r["mitigacion"],
                prob_res=r["probabilidad_residual"],
                imp_res=r["impacto_residual"]
            )
        logger.info("✅ Riesgos éticos base inicializados en MongoDB.")

    def registrar_riesgo(self, modulo: str, descripcion: str, categoria: str,
                         probabilidad: str, impacto: str, mitigacion: str,
                         prob_res: str = "Baja", imp_res: str = "Bajo"):
        """Calcula el riesgo inherente vs. residual y guarda en MongoDB."""
        puntaje_inherente = self.calcular_puntaje(probabilidad, impacto)
        puntaje_residual = self.calcular_puntaje(prob_res, imp_res)

        return self.db.registrar_riesgo(
            modulo=modulo,
            descripcion=descripcion,
            categoria=categoria,
            probabilidad=probabilidad,
            impacto=impacto,
            mitigacion=mitigacion,
            riesgo_residual=puntaje_residual
        )

    def obtener_resumen_matriz(self) -> list:
        """Obtiene la lista completa de riesgos de MongoDB."""
        return self.db.listar_riesgos()


if __name__ == "__main__":
    # Prueba del módulo e inserción de datos iniciales en MongoDB Atlas
    db = DatabaseManager()
    matriz = MatrizRiesgosEticos(db)

    print("\n========== MATRIZ DE RIESGOS ÉTICOS (DESDE MONGODB) ==========")
    lista = matriz.obtener_resumen_matriz()
    for item in lista:
        print(f"\nModulo: {item.get('modulo')} | Categoria: {item.get('categoria')}")
        print(f"Riesgo: {item.get('descripcion')}")
        print(f"Mitigación: {item.get('mitigacion')}")
        print(f"Puntaje Riesgo Residual: {item.get('riesgo_residual')}")