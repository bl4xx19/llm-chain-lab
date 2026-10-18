import argparse
import csv
import json
import os
import re
import sys
import time
import types
from datetime import datetime, timezone

import httpx
from openai import OpenAI

from app.config import settings
from app.db.session import SessionLocal, init_db
import app.llm.executor as executor_module
from app.scripts.chains_matrix import CHAINS
from app.scripts.run_experiment import ejecutar_intento, TECNICA_A_NIVEL

PILOT_CHAINS = ["1.2", "2.3", "3.4", "4.1"]

FALLOS_EXTERNOS = {"rate_limit", "timeout", "api_error", "provider_error"}
PILOT_ATTEMPTS_POR_DEFECTO = 5
PILOT_TECHNIQUE = "forzada"

MODELOS_PILOTO_MANUAL = [
    ("groq", "openai/gpt-oss-20b", "https://api.groq.com/openai/v1", "GROQ_API_KEY"),
    ("groq", "openai/gpt-oss-120b", "https://api.groq.com/openai/v1", "GROQ_API_KEY"),
    ("groq", "qwen/qwen3.8-27b", "https://api.groq.com/openai/v1", "GROQ_API_KEY"),
    ("gemini", "gemini-3.1-flash-lite", "https://generativelanguage.googleapis.com/v1beta/interactions", "GEMINI_API_KEY"),
    ("openrouter", "cohere/north-mini-code:free", "https://openrouter.ai/api/v1", "OPENROUTER_API_KEY"),
    ("openrouter", "inclusionai/ling-3.0-flash-sante:free", "https://openrouter.ai/api/v1", "OPENROUTER_API_KEY"),
    ("openrouter", "nvidia/nemotron-3.5-lightning:free", "https://openrouter.ai/api/v1", "OPENROUTER_API_KEY"),
]
MODELOS_PILOTO = MODELOS_PILOTO_MANUAL

CONFIG_POR_PROVEEDOR = {
    "groq": ("https://api.groq.com/openai/v1", "GROQ_API_KEY"),
    "gemini": ("https://generativelanguage.googleapis.com/v1beta/interactions", "GEMINI_API_KEY"),
    "openrouter": ("https://openrouter.ai/api/v1", "OPENROUTER_API_KEY"),
}


class ModelosFase3Error(Exception):
    pass


def cargar_modelos_desde_fase3(path: str) -> list[tuple]:
    if not os.path.exists(path):
        raise ModelosFase3Error(f"no existe el archivo de la fase 3: {path!r}")
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    resumen = data.get("resumen") or []
    aptos = [x for x in resumen if x.get("apto_function_calling")]
    if not aptos:
        raise ModelosFase3Error(f"{path!r} no tiene ningún modelo con apto_function_calling=true "
                                f"({len(resumen)} modelos evaluados, 0 aptos). No hay con qué correr la fase 4.")
    modelos, sin_config = [], []
    for x in aptos:
        prov, mod = x["provider"], x["model"]
        cfg = CONFIG_POR_PROVEEDOR.get(prov)
        if cfg is None:
            sin_config.append(f"{prov}:{mod}")
            continue
        base_url, api_key_env = cfg
        modelos.append((prov, mod, base_url, api_key_env))
    if sin_config:
        raise ModelosFase3Error(
            f"la fase 3 aprobó {len(sin_config)} modelo(s) cuyo proveedor no tiene configuración "
            f"(base_url/api_key_env) en pilot_multi_model.py: {sin_config}. Agrega su entrada en "
            f"CONFIG_POR_PROVEEDOR antes de continuar -- no se omiten en silencio.")
    return modelos

PILOT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "pilot_runs")
GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/interactions"
GEMINI_API_REVISION = "2026-05-20"
OPENROUTER_TITLE = "LLM Chain Lab - Screening multi-modelo"

_PATRON_SECRETO = re.compile(r"gsk_[A-Za-z0-9]{8,}|sk-or-v1-[A-Za-z0-9\-_]{8,}|AIza[0-9A-Za-z_\-]{20,}")


def redactar(texto: str, secretos: list[str]) -> str:
    if not texto:
        return texto
    for s in secretos:
        if s and len(s) >= 6:
            texto = texto.replace(s, "***")
    return _PATRON_SECRETO.sub("***", texto)


class RateLimitError(Exception):
    pass


def _tools_a_gemini(tools: list[dict] | None) -> list[dict] | None:
    if not tools:
        return None
    salida = []
    for t in tools:
        fn = t.get("function", t)
        salida.append({
            "type": "function", "name": fn["name"],
            "description": fn.get("description", ""),
            "parameters": fn.get("parameters", {"type": "object", "properties": {}}),
        })
    return salida


class GeminiChatCompletionAdapter:

    def __init__(self, http_client: httpx.Client, api_key: str, model: str):
        self.http_client = http_client
        self.api_key = api_key
        self.model = model
        self.interaction_id = None
        self.pendientes = {}
        self._contador = 0

    def _post(self, body: dict) -> dict:
        headers = {"x-goog-api-key": self.api_key, "Content-Type": "application/json",
                   "Api-Revision": GEMINI_API_REVISION}
        resp = self.http_client.post(GEMINI_URL, headers=headers, json=body)
        if resp.status_code == 429:
            raise RateLimitError(resp.text[:300])
        resp.raise_for_status()
        return resp.json()

    def __call__(self, messages: list[dict], tools: list[dict]) -> object:
        tools_gemini = _tools_a_gemini(tools)

        if messages and messages[-1]["role"] == "tool":
            id_ficticio = messages[-1]["tool_call_id"]
            call_id_real, nombre_funcion = self.pendientes.get(id_ficticio, (id_ficticio, "desconocida"))
            body = {
                "model": self.model,
                "previous_interaction_id": self.interaction_id,
                "input": [{
                    "type": "function_result", "call_id": call_id_real, "name": nombre_funcion,
                    "result": [{"type": "text", "text": messages[-1]["content"]}],
                }],
            }
        else:
            texto_usuario = messages[-1]["content"]
            body = {"model": self.model, "input": texto_usuario}
            if self.interaction_id:
                body["previous_interaction_id"] = self.interaction_id
            elif messages and messages[0]["role"] == "system":
                body["system_instruction"] = messages[0]["content"]
            if tools_gemini:
                body["tools"] = tools_gemini

        data = self._post(body)
        self.interaction_id = data.get("id", self.interaction_id)

        nombre_llamado, argumentos, call_id_real, texto = None, None, None, None
        for step in data.get("steps") or []:
            if step.get("type") == "function_call":
                nombre_llamado = step.get("name")
                argumentos = step.get("arguments") or {}
                call_id_real = step.get("id")
                break
            if step.get("type") == "model_output":
                for c in step.get("content") or []:
                    if c.get("type") == "text":
                        texto = (texto or "") + c.get("text", "")

        msg = types.SimpleNamespace(content=texto, tool_calls=None)
        if nombre_llamado is not None:
            self._contador += 1
            id_ficticio = f"fc_{self._contador}"
            self.pendientes[id_ficticio] = (call_id_real, nombre_llamado)
            tool_call = types.SimpleNamespace(
                id=id_ficticio,
                function=types.SimpleNamespace(name=nombre_llamado, arguments=json.dumps(argumentos)),
            )
            msg.tool_calls = [tool_call]

        return types.SimpleNamespace(choices=[types.SimpleNamespace(message=msg)])


def hacer_chat_completion_openai(base_url: str, api_key: str, model: str, extra_headers: dict | None):
    client = OpenAI(base_url=base_url, api_key=api_key)

    def _chat_completion(messages: list[dict], tools: list[dict]) -> object:
        kwargs = {"extra_headers": extra_headers} if extra_headers else {}
        return client.chat.completions.create(
            model=model, temperature=settings.llm_temperature,
            messages=messages, tools=tools, tool_choice="auto", **kwargs,
        )
    return _chat_completion


def construir_chat_completion(provider: str, model: str, base_url: str, api_key: str):
    if provider == "gemini":
        def fabrica():
            return GeminiChatCompletionAdapter(httpx.Client(timeout=httpx.Timeout(30.0)), api_key, model)
        return fabrica
    extra_headers = {"X-OpenRouter-Title": OPENROUTER_TITLE} if provider == "openrouter" else None
    funcion = hacer_chat_completion_openai(base_url, api_key, model, extra_headers)
    return lambda: funcion


def construir_plan(modelos, chains, attempts, order: str = "block") -> list[dict]:
    def fila(provider, model, base_url, api_key_env, chain_id, attempt):
        cfg = CHAINS[chain_id]
        return {
            "provider": provider, "model": model, "base_url": base_url, "api_key_env": api_key_env,
            "chain_id": chain_id, "scenario": cfg["scenario"], "level": cfg["level"],
            "turn_type": cfg["turn_type"], "attempt": attempt, "technique": PILOT_TECHNIQUE,
        }

    if order == "round_robin":
        plan = []
        for attempt in range(1, attempts + 1):
            for chain_id in chains:
                for provider, model, base_url, api_key_env in modelos:
                    plan.append(fila(provider, model, base_url, api_key_env, chain_id, attempt))
        return plan

    plan = []
    for provider, model, base_url, api_key_env in modelos:
        for chain_id in chains:
            for attempt in range(1, attempts + 1):
                plan.append(fila(provider, model, base_url, api_key_env, chain_id, attempt))
    return plan


def _banner(titulo: str) -> None:
    print("=" * 50)
    print(titulo)
    print("=" * 50)


def imprimir_resumen_plan(n_modelos: int, chains: list[str], attempts: int, plan: list[dict], etiqueta: str = "") -> None:
    print(f"Modelos recibidos: {n_modelos}")
    print(f"Cadenas: {len(chains)} ({', '.join(chains)})")
    print(f"Intentos por cadena: {attempts}")
    print(f"Ejecuciones planificadas: {n_modelos} x {len(chains)} x {attempts} = {len(plan)}{etiqueta}\n")


def imprimir_plan(plan: list[dict]):
    print(f"{'#':<5}{'provider':<12}{'model':<44}{'chain':<7}{'esc.':<12}{'nivel':<6}{'tipo':<8}{'intento'}")
    for i, p in enumerate(plan, 1):
        print(f"{i:<5}{p['provider']:<12}{p['model']:<44}{p['chain_id']:<7}{p['scenario']:<12}"
              f"{p['level']:<6}{p['turn_type']:<8}{p['attempt']}")
    por_modelo = {}
    for p in plan:
        por_modelo[(p["provider"], p["model"])] = por_modelo.get((p["provider"], p["model"]), 0) + 1
    print("\nPor modelo:")
    for (prov, mod), n in por_modelo.items():
        print(f"  {prov}:{mod} -> {n} ejecuciones")


def normalizar_ids_para_proveedor(valor):
    if isinstance(valor, dict):
        nuevo = {}
        for k, v in valor.items():
            if k == "id" and isinstance(v, (int, float)) and not isinstance(v, bool):
                nuevo[k] = str(v)
            else:
                nuevo[k] = normalizar_ids_para_proveedor(v)
        return nuevo
    if isinstance(valor, list):
        return [normalizar_ids_para_proveedor(x) for x in valor]
    return valor


def envolver_funciones_para_normalizacion(functions: dict) -> dict:
    envueltas = {}
    for nombre, fn in functions.items():
        def _wrapper(db, __fn=fn, **kwargs):
            return normalizar_ids_para_proveedor(__fn(db, **kwargs))
        envueltas[nombre] = _wrapper
    return envueltas


def ejecutar_item(provider: str, model: str, base_url: str, chat_completion_o_fabrica,
                  chain_id: str, attempt: int, run_seq: int, secretos: list[str]) -> dict:
    cfg_original = CHAINS[chain_id]
    cfg = dict(cfg_original)
    cfg["functions"] = envolver_funciones_para_normalizacion(cfg_original["functions"])
    nivel_tecnica = TECNICA_A_NIVEL[PILOT_TECHNIQUE]

    original = executor_module.chat_completion
    settings_model_original, settings_base_url_original = settings.llm_model, settings.llm_base_url
    settings.llm_model = model
    settings.llm_base_url = base_url
    executor_module.chat_completion = chat_completion_o_fabrica()

    try:
        registro = ejecutar_intento(chain_id, cfg, nivel_tecnica, attempt, run_seq)
        integracion_ok = True
        error_integracion = None
    except Exception as e:
        integracion_ok = False
        error_integracion = redactar(f"{type(e).__name__}: {e}", secretos)
        registro = {
            "run_id": f"PILOT-ERROR-{run_seq:04d}", "chain_id": chain_id, "scenario": cfg["scenario"],
            "level": cfg["level"], "turn_type": cfg["turn_type"], "attempt": attempt,
            "persuasion_technique": PILOT_TECHNIQUE, "ind_1": False, "ind_2": False,
            "attempt_success": False, "execution_valid": False, "failure_mode": "integration_error",
            "tool_calls": [], "turns": [], "started_at": datetime.now(timezone.utc).isoformat(),
            "finished_at": datetime.now(timezone.utc).isoformat(),
        }
    finally:
        executor_module.chat_completion = original
        settings.llm_model, settings.llm_base_url = settings_model_original, settings_base_url_original

    registro["provider"] = provider
    registro["model"] = model
    registro["fase"] = "piloto"
    registro["integracion_ok"] = integracion_ok
    if error_integracion:
        registro["error_integracion"] = error_integracion
    registro["success"] = registro.get("attempt_success")
    registro["indicators"] = {"ind_1": registro.get("ind_1"), "ind_2": registro.get("ind_2")}
    registro["timestamp"] = registro.get("finished_at")
    registro["attempt_number"] = registro.get("attempt")
    registro["expected_tool_invoked"] = registro.get("ind_1")
    registro["out_of_scope_achieved"] = registro.get("ind_2")
    return registro


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Screening multi-modelo sobre un subconjunto de cadenas.")
    modo = ap.add_mutually_exclusive_group()
    modo.add_argument("--dry-run", action="store_true", help="Solo muestra el plan, no ejecuta nada (por defecto).")
    modo.add_argument("--smoke-test", action="store_true", help="Corre 1 modelo x 1 cadena x 1 intento.")
    modo.add_argument("--confirm-full-run", action="store_true", help="Corre el screening completo.")
    ap.add_argument("--smoke-model", choices=list(CONFIG_POR_PROVEEDOR), help="Proveedor a usar en --smoke-test.")
    ap.add_argument("--smoke-chain", choices=PILOT_CHAINS, help="Cadena a usar en --smoke-test.")
    ap.add_argument("--order", choices=["block", "round_robin"], default="block",
                    help="block (por defecto): todos los intentos de un modelo seguidos. "
                         "round_robin: intercala modelos y cadenas, para que si la cuota de un "
                         "proveedor se agota a mitad de camino, no penalice solo a los modelos "
                         "que quedaron al final del bloque.")
    ap.add_argument("--output-dir", help="Carpeta PADRE donde crear la carpeta PILOT-<fecha>/ "
                    "(por defecto: pilot_runs/ junto a este script).")
    ap.add_argument("--official", action="store_true",
                    help="Marca esta corrida como la comparación OFICIAL de modelos (fase 04, no piloto): "
                         "agrega metadata.json y resumen.md con esa fase.")
    ap.add_argument("--models-from", metavar="PATH",
                    help="Ruta a un function_calling_result.json de la fase 3 (--official). La lista de "
                         "modelos de esta corrida es la de los aptos (apto_function_calling=true) ahí. "
                         "En modo --official es OBLIGATORIO usar esto o --manual-models -- no hay default "
                         "implícito, para que la fuente de la lista quede siempre trazable.")
    ap.add_argument("--manual-models", action="store_true",
                    help="Usar la lista fija MODELOS_PILOTO_MANUAL en vez de leerla de la fase 3 "
                         "(modo manual explícito, para pruebas o si la fase 3 no está disponible).")
    ap.add_argument("--attempts", type=int, default=PILOT_ATTEMPTS_POR_DEFECTO,
                    help=f"Intentos por modelo/cadena (por defecto {PILOT_ATTEMPTS_POR_DEFECTO}, "
                         "intentos por cadena).")
    args = ap.parse_args(argv)
    if args.attempts < 1:
        ap.error("--attempts debe ser >= 1")

    if args.manual_models:
        modelos_efectivos = MODELOS_PILOTO_MANUAL
        fuente_modelos = "manual_fijo"
        fuente_modelos_detalle = "lista fija de modelos candidatos, definida en el código (modo manual explícito)"
    elif args.models_from:
        try:
            modelos_efectivos = cargar_modelos_desde_fase3(args.models_from)
        except ModelosFase3Error as e:
            print(f"[FAIL] {e}")
            return 1
        fuente_modelos = "fase_3"
        fuente_modelos_detalle = args.models_from
    elif args.official:
        ap.error("en modo --official hace falta indicar --models-from PATH (la salida de la fase 3) "
                 "o --manual-models de forma explícita -- no hay una fuente de modelos por defecto.")
    else:
        modelos_efectivos = MODELOS_PILOTO_MANUAL
        fuente_modelos = "manual_fijo (modo piloto, sin --official)"
        fuente_modelos_detalle = "lista fija de modelos candidatos, definida en el código (modo manual explícito)"

    _titulo = "FASE 04 - SCREENING MULTI-MODELO" if args.official else "SCREENING MULTI-MODELO (PILOTO)"
    _banner(_titulo + (" - DRY-RUN" if (not args.smoke_test and not args.confirm_full_run) else ""))
    print("Fuente de modelos: " + ("Fase 03" if args.models_from and not args.manual_models else "lista manual"))
    for p, m, _, _ in modelos_efectivos:
        print(f"  - {p}:{m}")
    print(f"Orden: {args.order}\n")

    plan_completo = construir_plan(modelos_efectivos, PILOT_CHAINS, args.attempts, args.order)

    if not args.smoke_test and not args.confirm_full_run:
        imprimir_resumen_plan(len(modelos_efectivos), PILOT_CHAINS, args.attempts, plan_completo)
        imprimir_plan(plan_completo)
        return 0

    if args.smoke_test:
        modelos = [m for m in modelos_efectivos if m[0] == args.smoke_model][:1] if args.smoke_model else modelos_efectivos[:1]
        chains = [args.smoke_chain] if args.smoke_chain else PILOT_CHAINS[:1]
        attempts = 1
        etiqueta = "SMOKE TEST"
    else:
        modelos, chains, attempts = modelos_efectivos, PILOT_CHAINS, args.attempts
        etiqueta = "SCREENING MULTI-MODELO"

    plan = construir_plan(modelos, chains, attempts, args.order)
    imprimir_resumen_plan(len(modelos), chains, attempts, plan, " (smoke test)" if args.smoke_test else "")

    init_db()
    _prefijo_id = "COMPARISON" if args.official else "PILOT"
    pilot_id = f"{_prefijo_id}-{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')}"
    pilot_dir = os.path.join(args.output_dir or PILOT_DIR, pilot_id)
    evidence_dir = os.path.join(pilot_dir, "evidence")
    exports_dir = os.path.join(pilot_dir, "exports")
    os.makedirs(exports_dir, exist_ok=True)

    secretos = [os.environ.get(env, "") for _, _, _, env in modelos_efectivos]
    secretos = [s for s in secretos if s]

    fabrica_por_modelo = {}
    modelos_omitidos = set()

    resultados = []
    run_seq = 0
    for fila in plan:
        provider, model = fila["provider"], fila["model"]
        clave_modelo = (provider, model)

        if clave_modelo in modelos_omitidos:
            continue
        if clave_modelo not in fabrica_por_modelo:
            api_key = os.environ.get(fila["api_key_env"], "").strip()
            if not api_key:
                print(f"Modelo omitido: {provider}:{model} (falta {fila['api_key_env']})")
                modelos_omitidos.add(clave_modelo)
                continue
            fabrica_por_modelo[clave_modelo] = construir_chat_completion(provider, model, fila["base_url"], api_key)

        run_seq += 1
        registro = ejecutar_item(provider, model, fila["base_url"], fabrica_por_modelo[clave_modelo],
                                 fila["chain_id"], fila["attempt"], run_seq, secretos)
        run_id = registro.get("run_id", f"PILOT-{run_seq:04d}")
        evidencia_modelo_dir = os.path.join(evidence_dir, f"{provider}__{model.replace('/', '_')}", fila["chain_id"])
        os.makedirs(evidencia_modelo_dir, exist_ok=True)
        ruta_evidencia = os.path.join(evidencia_modelo_dir, f"{run_id}.json")
        registro["evidence_path"] = os.path.relpath(ruta_evidencia, pilot_dir)
        with open(ruta_evidencia, "w", encoding="utf-8") as f:
            json.dump(registro, f, indent=2, ensure_ascii=False, default=str)
        resultados.append(registro)

        estado = "OK" if registro["success"] else f"FALLO ({registro.get('failure_mode')})"
        print(f"[{provider}:{model}] {fila['chain_id']} intento {fila['attempt']}/{attempts}: {estado}")
        time.sleep(2)

    columnas = ["fase", "provider", "model", "chain_id", "scenario", "level", "turn_type", "attempt",
                "persuasion_technique", "success", "ind_1", "ind_2", "execution_valid", "failure_mode",
                "integracion_ok", "evidence_path", "timestamp"]
    with open(os.path.join(exports_dir, "attempts.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=columnas, extrasaction="ignore")
        w.writeheader()
        for r in resultados:
            w.writerow(r)
    with open(os.path.join(exports_dir, "attempts.json"), "w", encoding="utf-8") as f:
        json.dump(resultados, f, indent=2, ensure_ascii=False, default=str)

    resumen_modelo = {}
    resumen_cadena = {}
    for r in resultados:
        es_externo = r.get("failure_mode") in FALLOS_EXTERNOS
        k1 = (r["provider"], r["model"])
        s1 = resumen_modelo.setdefault(k1, {"provider": r["provider"], "model": r["model"],
                                            "attempts": 0, "successes": 0, "external_failures": 0})
        s1["attempts"] += 1
        s1["successes"] += int(bool(r["success"]))
        s1["external_failures"] += int(es_externo)
        s2 = resumen_cadena.setdefault(r["chain_id"], {"chain_id": r["chain_id"],
                                                        "attempts": 0, "successes": 0, "external_failures": 0})
        s2["attempts"] += 1
        s2["successes"] += int(bool(r["success"]))
        s2["external_failures"] += int(es_externo)

    print("\nResumen por modelo")
    print(f"{'Proveedor':<12}{'Modelo':<44}{'Éxitos':<10}{'Válidos':<10}{'Fallos ext.':<13}%")
    with open(os.path.join(exports_dir, "summary_by_model.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["provider", "model", "attempts", "successes", "success_rate",
                                          "valid_attempts", "external_failures", "success_rate_validos"])
        w.writeheader()
        for s in resumen_modelo.values():
            pct = s["successes"] / s["attempts"] if s["attempts"] else 0
            s["success_rate"] = round(pct, 3)
            validos = s["attempts"] - s["external_failures"]
            s["valid_attempts"] = validos
            s["success_rate_validos"] = round(s["successes"] / validos, 3) if validos else None
            w.writerow(s)
            resultado_txt = f"{s['successes']}/{s['attempts']}"
            validos_txt = f"{validos}/{s['attempts']}"
            print(f"{s['provider']:<12}{s['model']:<44}{resultado_txt:<10}{validos_txt:<10}{s['external_failures']:<13}{pct:.0%}")

    print("\nResumen por cadena")
    print(f"{'Cadena':<10}{'Éxitos':<10}{'Válidos':<10}{'Fallos ext.':<13}%")
    with open(os.path.join(exports_dir, "summary_by_chain.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["chain_id", "attempts", "successes", "success_rate",
                                          "valid_attempts", "external_failures", "success_rate_validos"])
        w.writeheader()
        for cid in PILOT_CHAINS:
            if cid not in resumen_cadena:
                continue
            s = resumen_cadena[cid]
            pct = s["successes"] / s["attempts"] if s["attempts"] else 0
            s["success_rate"] = round(pct, 3)
            validos = s["attempts"] - s["external_failures"]
            s["valid_attempts"] = validos
            s["success_rate_validos"] = round(s["successes"] / validos, 3) if validos else None
            w.writerow(s)
            resultado_txt = f"{s['successes']}/{s['attempts']}"
            validos_txt = f"{validos}/{s['attempts']}"
            print(f"{cid:<10}{resultado_txt:<10}{validos_txt:<10}{s['external_failures']:<13}{pct:.0%}")

    manifest = {
        "fase": ("04_model_screening" if args.official else "piloto"),
        "pilot_id": pilot_id, "es_evidencia_oficial": False,
        "es_comparacion_oficial_modelos": args.official, "es_campana_final_cadenas": False,
        "fuente_modelos": fuente_modelos, "fuente_modelos_detalle": fuente_modelos_detalle,
        "run_id": pilot_id, "comando_usado": " ".join(["python3", "-m", "app.scripts.pilot_multi_model"] + (argv if argv is not None else sys.argv[1:])),
        "proveedores_evaluados": sorted({prov for prov, _, _, _ in modelos_efectivos}),
        "temperature": settings.llm_temperature,
        "politica_ejecucion": ("Sin fallback automático entre modelos. Sin reintentos silenciosos: cada intento corre exactamente una vez y su resultado (éxito o failure_mode) queda registrado tal cual, incluidos los errores externos de proveedor/cuota."),
        "execution_order": args.order,
        "tool_result_id_normalization": {
            "aplicada": True,
            "descripcion": ("Normalización de compatibilidad para proveedores estrictos en tool results: "
                            "los campos 'id' numéricos en el resultado de una función se convierten a string "
                            "antes de llegar al proveedor. No altera la lógica de negocio de las funciones "
                            "reales ni la evaluación de IND-1/IND-2 (confirmado por revisión de solo lectura: "
                            "ningún evaluador de estas 4 cadenas depende del tipo del campo 'id'). Solo cambia "
                            "el formato del resultado. Motivada por un hallazgo real: Cohere (vía OpenRouter) "
                            "rechaza un tool result con 'id' numérico -- 'A tool result's output's id field "
                            "must be a string'. Ver provider-key-test/diagnose_cohere_multiturn.py."),
            "funciones_afectadas": ["buscar_disponibilidad (2.3)", "leer_ticket (3.4)"],
            "funciones_revisadas_sin_riesgo": ["buscar_en_historiales (1.2)", "resetear_credenciales_agente (3.4)", "transferir (4.1)"],
            "se_aplica_solo_en": "app/scripts/pilot_multi_model.py (capa auxiliar)",
            "no_modifica": ["chains_matrix.py", "app/scenarios/*/functions.py", "executor.py", "run_experiment.py"],
        },
        "modelos": [{"provider": p, "model": m} for p, m, _, _ in modelos],
        "chains": chains, "attempts_por_combinacion": attempts, "technique": PILOT_TECHNIQUE,
        "total_planificado": len(plan), "total_ejecutado": len(resultados),
        "started_at": resultados[0]["started_at"] if resultados else None,
        "finished_at": resultados[-1]["finished_at"] if resultados else None,
        "advertencia_3_4": ("El payload de la cadena 3.4 fue calibrado en iteraciones previas "
                            "específicamente contra openai/gpt-oss-20b. Un fallo de otro modelo en "
                            "esta cadena no debe interpretarse automáticamente como una limitación "
                            "del modelo: puede ser que el payload esté ajustado al primero."),
    }
    with open(os.path.join(pilot_dir, "pilot_manifest.json"), "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)

    if args.official:
        metadata = {
            "fase": manifest["fase"], "objetivo": "Screening de los modelos aptos (ESTABLE en API_OK y function "
                     "calling) frente a 4 cadenas representativas. Reporta resultados y no selecciona finalistas.",
            "es_comparacion_oficial_modelos": True, "es_campana_final_cadenas": False,
            "fecha_hora": manifest["started_at"],
            "comando_usado": manifest["comando_usado"], "proveedores_evaluados": manifest["proveedores_evaluados"],
            "modelos_incluidos": [f"{prov}:{mod}" for prov, mod, _, _ in modelos],
            "cadenas": chains, "intentos_por_combinacion": attempts, "execution_order": args.order,
            "total_planificado": len(plan), "total_ejecutado": len(resultados),
            "archivos_resultado": ["pilot_manifest.json", "exports/attempts.csv", "exports/attempts.json",
                                   "exports/summary_by_model.csv", "exports/summary_by_chain.csv"],
        }
        with open(os.path.join(pilot_dir, "metadata.json"), "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
        with open(os.path.join(pilot_dir, "resumen.md"), "w", encoding="utf-8") as f:
            f.write(f"# {manifest['fase']}\n\n**Fecha:** {metadata['fecha_hora']}\n\n"
                    f"**Objetivo:** {metadata['objetivo']}\n\n"
                    f"**Modelos incluidos ({len(metadata['modelos_incluidos'])}):**\n\n"
                    + "".join(f"- `{m}`\n" for m in metadata["modelos_incluidos"]) +
                    f"\n**Cadenas:** {', '.join(chains)} | **Intentos/combinación:** {attempts} "
                    f"| **Orden:** {args.order}\n\n"
                    f"**Total ejecutado:** {len(resultados)}/{len(plan)}\n\n"
                    "Ver `exports/summary_by_model.csv` y `exports/summary_by_chain.csv` para los resultados.\n")
        print(f"Metadata guardada en: {os.path.relpath(pilot_dir)}")

    print(f"\nResultado guardado en: {os.path.relpath(pilot_dir)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
