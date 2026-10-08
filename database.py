import os
import logging
from datetime import datetime
from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError, PyMongoError

# Cargar variables de entorno desde .env
load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("LogiSmartDB")


class DatabaseManager:
    """
    Administrador de persistencia MongoDB Atlas conectado vía .env.
    """

    def __init__(self):
        user = os.getenv("MONGO_USER")
        password = os.getenv("MONGO_PASSWORD")
        cluster = os.getenv("MONGO_CLUSTER")
        self.db_name = os.getenv("MONGO_DB_NAME", "velox_utvt")

        if user and password and cluster:
            self.uri = f"mongodb+srv://{user}:{password}@{cluster}/?retryWrites=true&w=majority"
        else:
            self.uri = "mongodb://localhost:27017/"

        self.client = None
        self.db = None
        self.conectar()

    def conectar(self):
        try:
            self.client = MongoClient(self.uri, serverSelectionTimeoutMS=5000)
            self.client.admin.command("ping")
            self.db = self.client[self.db_name]
            logger.info(f"✅ Conexión exitosa a MongoDB Atlas (DB: [{self.db_name}])")
        except Exception as e:
            logger.error(f"❌ Error de conexión: {e}")
            self.db = None

    def esta_conectado(self) -> bool:
        if self.client is None:
            return False
        try:
            self.client.admin.command("ping")
            return True
        except PyMongoError:
            return False

    # ========================================================
    # CONSULTAS DE CAMIONES Y ACCESOS REALES
    # ========================================================

    def obtener_camion_por_placa(self, placa: str) -> dict:
        """Busca un camión específico en MongoDB Atlas por su placa."""
        if not self.esta_conectado():
            return None
        return self.db.camiones.find_one({"placa": placa.upper()})

    def guardar_camion(self, placa: str, camion_id: str, empresa: str, autorizacion: bool, certificacion_conductor: bool):
        if not self.esta_conectado():
            return None
        doc = {
            "placa": placa.upper(),
            "camion_id": camion_id,
            "empresa": empresa,
            "autorizacion": autorizacion,
            "certificacion_conductor": certificacion_conductor,
            "actualizado_en": datetime.now().isoformat()
        }
        return self.db.camiones.update_one({"placa": doc["placa"]}, {"$set": doc}, upsert=True)

    def registrar_acceso(self, placa: str, P: bool, Q: bool, R: bool, S: bool, A: bool, E: bool, operador: str, explicacion: str = ""):
        if not self.esta_conectado():
            return None
        doc = {
            "placa": placa.upper(),
            "premisas": {"P": P, "Q": Q, "R": R, "S": S},
            "resultados": {"A_acceso_estandar": A, "E_inspeccion_especial": E},
            "explicacion": explicacion,
            "timestamp": datetime.now().isoformat(),
            "operador": operador
        }
        return self.db.accesos.insert_one(doc)

    def registrar_incidente(self, correo_original: str, clasificacion: str, prioridad: str, datos_extraidos: dict, estado: str = "nuevo"):
        if not self.esta_conectado():
            return None
        doc = {
            "correo_original": correo_original,
            "clasificacion": clasificacion,
            "prioridad": prioridad,
            "datos_extraidos": datos_extraidos,
            "estado": estado,
            "fecha_creacion": datetime.now(),
            "timestamp_iso": datetime.now().isoformat()
        }
        return self.db.incidentes.insert_one(doc)

    def registrar_riesgo(self, modulo: str, descripcion: str, categoria: str, probabilidad: str, impacto: str, mitigacion: str, riesgo_residual: int) -> str:
        if not self.esta_conectado():
            return None
        doc = {
            "modulo": modulo,
            "descripcion": descripcion,
            "categoria": categoria,
            "probabilidad": probabilidad,
            "impacto": impacto,
            "mitigacion": mitigacion,
            "riesgo_residual": riesgo_residual,
            "timestamp": datetime.now().isoformat()
        }
        res = self.db.riesgos_eticos.update_one({"modulo": modulo, "descripcion": descripcion}, {"$set": doc}, upsert=True)
        return str(res.upserted_id) if res.upserted_id else "Actualizado"

    def listar_riesgos(self) -> list:
        if not self.esta_conectado():
            return []
        return list(self.db.riesgos_eticos.find({}, {"_id": 0}))


if __name__ == "__main__":
    db = DatabaseManager()
    print("Estado de conexión:", db.esta_conectado())