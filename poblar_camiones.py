from database import DatabaseManager

# Inicializar conexión con MongoDB Atlas
db = DatabaseManager()

# Camiones de prueba con datos para evaluar las reglas P, Q, R, S
camiones_demo = [
    {
        "placa": "ABC-1234",
        "camion_id": "CAM-001",
        "empresa": "Transportes Velox",
        "autorizacion": True,
        "certificacion_conductor": True
    },
    {
        "placa": "XYZ-9876",
        "camion_id": "CAM-002",
        "empresa": "Logística del Norte",
        "autorizacion": False,
        "certificacion_conductor": True
    },
    {
        "placa": "UTVT-2026",
        "camion_id": "CAM-003",
        "empresa": "Express UTVT",
        "autorizacion": True,
        "certificacion_conductor": False
    }
]

print("\n========== POBLANDO BASE DE DATOS MONGODB ATLAS ==========")
for c in camiones_demo:
    res = db.guardar_camion(
        placa=c["placa"],
        camion_id=c["camion_id"],
        empresa=c["empresa"],
        autorizacion=c["autorizacion"],
        certificacion_conductor=c["certificacion_conductor"]
    )
    print(f"🚛 Camión registrado: Placa {c['placa']} | Empresa: {c['empresa']}")

print("\n✅ Camiones de prueba registrados exitosamente en MongoDB Atlas.")