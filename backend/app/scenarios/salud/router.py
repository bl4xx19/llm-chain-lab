from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.llm.executor import ejecutar_turno
from app.llm.tools_schema import SALUD_TOOLS
from app.llm.prompts.salud import SYSTEM_PROMPT_SALUD
from app.scenarios.salud.functions import SALUD_FUNCTIONS
from app.scenarios.salud.seed_data import reset_datos_salud
from app.logging.writer import log_interaction
from app.logging.indicators import evaluate_chain_1_1, evaluate_chain_1_2, evaluate_chain_1_3, evaluate_chain_1_4

router = APIRouter(prefix="/chat/salud", tags=["salud"])

_conversations: dict[str, list[dict]] = {}

AUTHORIZED_PATIENT = "HC-1001"


class ChatRequest(BaseModel):
    session_id: str
    message: str
    intento_cadena_id: str | None = None
    tecnica: str | None = None


class ResetRequest(BaseModel):
    session_id: str


@router.post("/reset")
def reset_salud(req: ResetRequest, db: Session = Depends(get_db)):
    _conversations.pop(req.session_id, None)
    reset_datos_salud(db)
    return {"status": "reset", "session_id": req.session_id}


@router.post("")
def chat_salud(req: ChatRequest, db: Session = Depends(get_db)):
    history = _conversations.setdefault(
        req.session_id,
        [{"role": "system", "content": SYSTEM_PROMPT_SALUD}],
    )
    history.append({"role": "user", "content": req.message})

    resultado_turno = ejecutar_turno(history, SALUD_TOOLS, SALUD_FUNCTIONS, db)

    tool_calls = resultado_turno["tool_calls"]
    ultima_llamada = tool_calls[-1] if tool_calls else None
    function_called = ultima_llamada["tool_name"] if ultima_llamada else None
    function_args = ultima_llamada.get("arguments") if ultima_llamada else None
    function_result = ultima_llamada.get("result") if ultima_llamada else None
    final_message = resultado_turno["assistant_response"]

    log_entry = log_interaction(
        db=db,
        escenario="salud",
        session_id=req.session_id,
        user_input=req.message,
        llm_raw_response={"tool_calls": tool_calls, "final_response": final_message, "error": resultado_turno["error"]},
        function_called=function_called,
        function_args=function_args,
        function_result=function_result,
        cadena_id=req.intento_cadena_id,
        tecnica=req.tecnica,
    )

    indicadores = None
    if function_called == "consultar_historial":
        indicadores = {"1.1": evaluate_chain_1_1(log_entry, AUTHORIZED_PATIENT)}
    elif function_called == "buscar_en_historiales":
        indicadores = {"1.2": evaluate_chain_1_2(log_entry, AUTHORIZED_PATIENT)}
    elif function_called == "actualizar_diagnostico":
        indicadores = {"1.3": evaluate_chain_1_3(log_entry)}
    elif function_called == "exportar_historiales_completos":
        indicadores = {"1.4": evaluate_chain_1_4(log_entry)}

    return {
        "response": final_message,
        "function_called": function_called,
        "function_args": function_args,
        "function_result": function_result,
        "indicadores": indicadores,
        "log_id": log_entry.id,
    }
