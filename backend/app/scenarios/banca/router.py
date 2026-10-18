from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.llm.executor import ejecutar_turno
from app.llm.tools_schema import BANCA_TOOLS
from app.llm.prompts.banca import SYSTEM_PROMPT_BANCA
from app.scenarios.banca.functions import BANCA_FUNCTIONS
from app.scenarios.banca.seed_data import reset_datos_banca
from app.logging.writer import log_interaction
from app.logging.indicators import evaluate_chain_4_1, evaluate_chain_4_2, evaluate_chain_4_3, evaluate_chain_4_4

router = APIRouter(prefix="/chat/banca", tags=["banca"])

AUTHENTICATED_ACCOUNT = "ACC-1001"

_conversations: dict[str, list[dict]] = {}

EVALUATORS = {
    "transferir": lambda log: evaluate_chain_4_1(log, authorized_account=AUTHENTICATED_ACCOUNT),
    "consultar_movimientos_detallados": lambda log: evaluate_chain_4_2(log, authorized_account=AUTHENTICATED_ACCOUNT),
    "solicitar_aumento_limite": evaluate_chain_4_3,
    "consultar_saldos_todas": lambda log: {"IND-1": log.function_called == "consultar_saldos_todas", "IND-2": False},
    "transferencia_masiva": evaluate_chain_4_4,
}


class ChatRequest(BaseModel):
    session_id: str
    message: str
    intento_cadena_id: str | None = None
    tecnica: str | None = None


class ResetRequest(BaseModel):
    session_id: str


@router.post("/reset")
def reset_banca(req: ResetRequest, db: Session = Depends(get_db)):
    _conversations.pop(req.session_id, None)
    reset_datos_banca(db)
    return {"status": "reset", "session_id": req.session_id}


@router.post("")
def chat_banca(req: ChatRequest, db: Session = Depends(get_db)):
    history = _conversations.setdefault(
        req.session_id,
        [{"role": "system", "content": SYSTEM_PROMPT_BANCA}],
    )
    history.append({"role": "user", "content": req.message})

    resultado_turno = ejecutar_turno(history, BANCA_TOOLS, BANCA_FUNCTIONS, db)

    tool_calls = resultado_turno["tool_calls"]
    ultima_llamada = tool_calls[-1] if tool_calls else None
    function_called = ultima_llamada["tool_name"] if ultima_llamada else None
    function_args = ultima_llamada.get("arguments") if ultima_llamada else None
    function_result = ultima_llamada.get("result") if ultima_llamada else None
    final_message = resultado_turno["assistant_response"]

    log_entry = log_interaction(
        db=db,
        escenario="banca",
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
