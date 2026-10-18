import threading
import time

from openai import OpenAI
from app.config import settings

_kwargs_cliente = {}
if settings.llm_max_retries is not None:
    _kwargs_cliente["max_retries"] = settings.llm_max_retries

_client = OpenAI(
    base_url=settings.llm_base_url,
    api_key=settings.llm_api_key,
    **_kwargs_cliente,
)

_lock = threading.Lock()
_inicio_ultima_llamada = 0.0

_extra_content_por_llamada: dict[tuple, list] = {}

estadisticas = {"llamadas": 0, "extra_content_capturados": 0, "extra_content_reenviados": 0}


def _esperar_turno() -> None:
    global _inicio_ultima_llamada
    intervalo = settings.llm_min_interval_seconds
    if intervalo <= 0:
        return
    with _lock:
        espera = _inicio_ultima_llamada + intervalo - time.monotonic()
        if espera > 0:
            time.sleep(espera)
        _inicio_ultima_llamada = time.monotonic()


def _clave(tool_call_id, nombre, argumentos) -> tuple:
    return (tool_call_id, nombre, argumentos)


def _extra_content_de(tool_call) -> dict | None:
    extra = getattr(tool_call, "extra_content", None)
    if extra is None:
        extra = (getattr(tool_call, "model_extra", None) or {}).get("extra_content")
    return extra or None


def _capturar_extra_content(response) -> None:
    for choice in getattr(response, "choices", None) or []:
        for tc in (choice.message.tool_calls or []):
            extra = _extra_content_de(tc)
            if not extra:
                continue
            clave = _clave(tc.id, tc.function.name, tc.function.arguments)
            if len(_extra_content_por_llamada) > 5000:
                _extra_content_por_llamada.clear()
            _extra_content_por_llamada.setdefault(clave, []).append(extra)
            estadisticas["extra_content_capturados"] += 1


def _reinyectar_extra_content(messages: list[dict]) -> list[dict]:
    if not _extra_content_por_llamada:
        return messages

    total = {}
    for m in messages:
        if m.get("role") == "assistant":
            for tc in (m.get("tool_calls") or []):
                fn = tc.get("function", {})
                k = _clave(tc.get("id"), fn.get("name"), fn.get("arguments"))
                total[k] = total.get(k, 0) + 1

    vistas = {}
    salida = []
    for m in messages:
        if m.get("role") == "assistant" and m.get("tool_calls"):
            nuevos = []
            for tc in m["tool_calls"]:
                fn = tc.get("function", {})
                k = _clave(tc.get("id"), fn.get("name"), fn.get("arguments"))
                guardados = _extra_content_por_llamada.get(k)
                if guardados and "extra_content" not in tc:
                    i = vistas.get(k, 0)
                    vistas[k] = i + 1
                    inicio = max(len(guardados) - total[k], 0)
                    extra = guardados[min(inicio + i, len(guardados) - 1)]
                    tc = {**tc, "extra_content": extra}
                    estadisticas["extra_content_reenviados"] += 1
                nuevos.append(tc)
            m = {**m, "tool_calls": nuevos}
        salida.append(m)
    return salida


def chat_completion(messages: list[dict], tools: list[dict]) -> object:
    _esperar_turno()
    estadisticas["llamadas"] += 1
    response = _client.chat.completions.create(
        model=settings.llm_model,
        temperature=settings.llm_temperature,
        messages=_reinyectar_extra_content(messages),
        tools=tools,
        tool_choice="auto",
    )
    _capturar_extra_content(response)
    return response
