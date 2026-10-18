from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.llm.executor import ejecutar_turno
from app.llm.tools_schema import SOPORTE_TOOLS
from app.llm.prompts.soporte import SYSTEM_PROMPT_SOPORTE
from app.scenarios.soporte.functions import SOPORTE_FUNCTIONS
from app.scenarios.soporte.seed_data import reset_datos_soporte
from app.logging.writer import log_interaction
from app.logging.indicators import evaluate_chain_3_1, evaluate_chain_3_2, evaluate_chain_3_3, evaluate_chain_3_4

router = APIRouter(prefix="/chat/soporte", tags=["soporte"])

_conversations: dict[str, list[dict]] = {}

EVALUATORS = {
    "verificar_conectividad": evaluate_chain_3_2,
    "obtener_configuracion": evaluate_chain_3_1,
    "buscar_tickets": evaluate_chain_3_3,
    "resetear_credenciales_agente": evaluate_chain_3_4,
}


class ChatRequest(BaseModel):
    session_id: str
    message: str
    intento_cadena_id: str | None = None
    tecnica: str | None = None


class ResetRequest(BaseModel):
    session_id: str


@router.post("/reset")
def reset_soporte(req: ResetRequest, db: Session = Depends(get_db)):
    _conversations.pop(req.session_id, None)
    reset_datos_soporte(db)
    return {"status": "reset", "session_id": req.session_id}


@router.post("")
def chat_soporte(req: ChatRequest, db: Session = Depends(get_db)):
    history = _conversations.setdefault(
        req.session_id,
        [{"role": "system", "content": SYSTEM_PROMPT_SOPORTE}],
    )
    history.append({"role": "user", "content": req.message})

    resultado_turno = ejecutar_turno(history, SOPORTE_TOOLS, SOPORTE_FUNCTIONS, db)

    tool_calls = resultado_turno["tool_calls"]
    ultima_llamada = tool_calls[-1] if tool_calls else None
    function_called = ultima_llamada["tool_name"] if ultima_llamada else None
    function_args = ultima_llamada.get("arguments") if ultima_llamada else None
    function_result = ultima_llamada.get("result") if ultima_llamada else None
    final_message = resultado_turno["assistant_response"]

    log_entry = log_interaction(
        db=db,
        escenario="soporte",
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
    evaluator = EVALUATORS.get(function_called)
    if evaluator:
        indicadores = evaluator(log_entry)

    return {
        "response": final_message,
        "function_called": function_called,
        "function_args": function_args,
        "function_result": function_result,
        "indicadores": indicadores,
        "log_id": log_entry.id,
    }
