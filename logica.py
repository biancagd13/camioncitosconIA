from itertools import product
from datetime import datetime


def evaluar_camion_ampliado(P: bool, Q: bool, R: bool, S: bool, T: bool = False, N: bool = False):
    """
    Motor de Reglas Ampliado con Lógica Proposicional.

    Premisas:
    P = Autorización previa
    Q = Peso excedido
    R = Materiales peligrosos
    S = Certificación del conductor
    T = Certificación vencida por tiempo
    N = Horario nocturno restringido

    Reglas:
    A = P ∧ S ∧ ¬Q (Acceso estándar)
    E = P ∧ (R ∨ Q) (Inspección especial)
    V = S ∧ ¬T (Certificación vigente)
    H = ¬(R ∧ N) (Seguridad de horario nocturno)
    """

    # --------------------------------------------------------
    # REGLAS LÓGICAS
    # --------------------------------------------------------
    acceso_estandar = P and S and not Q
    inspeccion_especial = P and (R or Q)
    certificacion_vigente = S and not T
    horario_seguro = not (R and N)

    # Decisión Final: Permiso total de ingreso
    permiso_final = acceso_estandar and certificacion_vigente and horario_seguro

    # --------------------------------------------------------
    # GENERACIÓN DE EXPLICACIÓN DETALLADA (PASO A PASO)
    # --------------------------------------------------------
    explicaciones = []

    if not P:
        explicaciones.append("Rechazado: Falta autorización previa (P=False).")
    if Q:
        explicaciones.append("Alerta: El camión excede el límite de peso (Q=True). Requiere inspección (E).")
    if R:
        explicaciones.append("Alerta: Transporta materiales peligrosos (R=True).")
    if T:
        explicaciones.append("Rechazado: La certificación del conductor está vencida (T=True).")
    if R and N:
        explicaciones.append("Rechazado: Prohibido transportar materiales peligrosos en horario nocturno (R=True, N=True).")

    if permiso_final:
        explicaciones.append("Aprobado: Cumple con todas las reglas de acceso estándar, vigencia y horario.")

    explicacion_texto = " | ".join(explicaciones)

    resultado = {
        "premisas": {"P": P, "Q": Q, "R": R, "S": S, "T": T, "N": N},
        "resultados": {
            "A_acceso_estandar": acceso_estandar,
            "E_inspeccion_especial": inspeccion_especial,
            "V_certificacion_vigente": certificacion_vigente,
            "H_horario_seguro": horario_seguro,
            "PERMISO_FINAL": permiso_final
        },
        "explicacion": explicacion_texto
    }

    return resultado


def generar_tabla_verdad_ampliada():
    """Genera la tabla de verdad para las 4 reglas principales."""
    print("\n==========================================================================")
    print("                    TABLA DE VERDAD AMPLIADA (LOGISMART)")
    print("==========================================================================")
    print("P Q R S T N | A (Estándar) | E (Inspección) | V (Vigencia) | H (Horario)")
    print("-" * 74)

    # Genera combinaciones para P, Q, R, S, T, N
    for P, Q, R, S, T, N in product([False, True], repeat=6):
        res = evaluar_camion_ampliado(P, Q, R, S, T, N)["resultados"]
        print(
            f"{int(P)} {int(Q)} {int(R)} {int(S)} {int(T)} {int(N)} | "
            f"     {int(res['A_acceso_estandar'])}       | "
            f"      {int(res['E_inspeccion_especial'])}       | "
            f"      {int(res['V_certificacion_vigente'])}      | "
            f"    {int(res['H_horario_seguro'])}"
        )


if __name__ == "__main__":
    # Prueba rápida
    res = evaluar_camion_ampliado(P=True, Q=False, R=True, S=True, T=False, N=True)
    print("Explicación de la decisión:")
    print(res["explicacion"])