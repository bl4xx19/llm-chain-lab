import argparse
import csv
import glob
import json
import os

BASE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "experiment_runs")


def cargar_attempts(carpeta: str) -> list[dict]:
    path = os.path.join(carpeta, "exports", "attempts.json")
    if not os.path.exists(path):
        print(f"  (sin exports/attempts.json en {carpeta}, se omite)")
        return []
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def resumir_por_modelo(registros: list[dict]) -> dict:
    por_modelo = {}
    for r in registros:
        modelo = r.get("model", "desconocido")
        por_modelo.setdefault(modelo, []).append(r)

    resumen = {}
    for modelo, regs in por_modelo.items():
        total = len(regs)
        exitosos = sum(1 for r in regs if r["attempt_success"])
        rechazos = sum(1 for r in regs if r.get("failure_mode") == "llm_refusal")
        args_invalidos = sum(1 for r in regs if r.get("failure_mode") == "invalid_tool_arguments")
        errores_proveedor = sum(1 for r in regs if not r.get("execution_valid", True))

        por_escenario = {}
        for r in regs:
            esc = r["scenario"]
            s = por_escenario.setdefault(esc, {"exitosos": 0, "intentos": 0})
            s["intentos"] += 1
            s["exitosos"] += int(r["attempt_success"])

        resumen[modelo] = {
            "model": modelo,
            "provider": regs[0].get("provider", "desconocido"),
            "total_intentos": total,
            "success_rate": round(exitosos / total, 3) if total else None,
            "refusal_rate": round(rechazos / total, 3) if total else None,
            "invalid_tool_arguments_rate": round(args_invalidos / total, 3) if total else None,
            "provider_error_rate": round(errores_proveedor / total, 3) if total else None,
            "reproducibilidad_por_escenario": {
                esc: round(s["exitosos"] / s["intentos"], 3) if s["intentos"] else None
                for esc, s in por_escenario.items()
            },
        }
    return resumen


def main():
    parser = argparse.ArgumentParser(description="Comparación entre modelos/proveedores")
    parser.add_argument("carpetas", nargs="*", help="Carpetas experiment_runs/<experiment_id>/ a comparar")
    parser.add_argument("--all", action="store_true", help="Comparar todas las carpetas existentes en experiment_runs/")
    args = parser.parse_args()

    if args.all:
        carpetas = sorted(glob.glob(os.path.join(BASE_DIR, "LLM-CHAIN-LAB-*")))
    else:
        carpetas = args.carpetas

    if len(carpetas) < 2:
        print("Se necesitan al menos 2 carpetas de campaña (corridas con modelos/proveedores distintos) para comparar.")
        print("Uso: python -m app.scripts.compare_experiment_runs <carpeta1> <carpeta2> [...]")
        print("     python -m app.scripts.compare_experiment_runs --all")
        return

    print(f"Comparando {len(carpetas)} carpetas de campaña:")
    todos_los_registros = []
    for c in carpetas:
        registros = cargar_attempts(c)
        print(f"  {c}: {len(registros)} intentos")
        todos_los_registros.extend(registros)

    if not todos_los_registros:
        print("No se encontraron intentos en ninguna carpeta. Nada que comparar.")
        return

    resumen = resumir_por_modelo(todos_los_registros)
    modelos_encontrados = sorted(resumen.keys())

    if len(modelos_encontrados) < 2:
        print(f"\nSolo se encontró 1 modelo distinto ({modelos_encontrados[0]}) entre las carpetas dadas.")
        print("Verifica que cada carpeta corresponda a una corrida con LLM_MODEL distinto.")

    print("\n=== Comparación por modelo ===")
    print(f"{'Modelo':<28}{'Proveedor':<16}{'Intentos':<10}{'Éxito':<9}{'Rechazo':<10}{'Args inválidos':<16}{'Error proveedor'}")
    for modelo in modelos_encontrados:
        s = resumen[modelo]
        txt_exito = f"{s['success_rate']:.0%}"
        txt_rechazo = f"{s['refusal_rate']:.0%}"
        txt_args = f"{s['invalid_tool_arguments_rate']:.0%}"
        txt_provider_err = f"{s['provider_error_rate']:.0%}"
        print(
            f"{modelo:<28}{s['provider']:<16}{s['total_intentos']:<10}"
            f"{txt_exito:<9}{txt_rechazo:<10}{txt_args:<16}{txt_provider_err}"
        )

    os.makedirs(BASE_DIR, exist_ok=True)
    out_path = os.path.join(BASE_DIR, "model_comparison.csv")
    with open(out_path, "w", newline="", encoding="utf-8") as f:
        columnas = ["model", "provider", "total_intentos", "success_rate", "refusal_rate",
                    "invalid_tool_arguments_rate", "provider_error_rate"]
        writer = csv.DictWriter(f, fieldnames=columnas, extrasaction="ignore")
        writer.writeheader()
        for modelo in modelos_encontrados:
            writer.writerow(resumen[modelo])

    out_json = os.path.join(BASE_DIR, "model_comparison.json")
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(resumen, f, indent=2, ensure_ascii=False)

    print(f"\nGuardado: {out_path}")
    print(f"Guardado: {out_json} (incluye reproducibilidad por escenario, por modelo)")


if __name__ == "__main__":
    main()
