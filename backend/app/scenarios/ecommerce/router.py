from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.llm.executor import ejecutar_turno
from app.llm.tools_schema import ECOMMERCE_TOOLS
from app.llm.prompts.ecommerce import SYSTEM_PROMPT_ECOMMERCE
from app.scenarios.ecommerce.functions import ECOMMERCE_FUNCTIONS
from app.scenarios.ecommerce.seed_data import reset_datos_ecommerce
from app.logging.writer import log_interaction
from app.logging.indicators import evaluate_chain_2_1, evaluate_chain_2_2, evaluate_chain_2_3, evaluate_chain_2_4

router = APIRouter(prefix="/chat/ecommerce", tags=["ecommerce"])

_conversations: dict[str, list[dict]] = {}

EVALUATORS = {
    "aplicar_descuento": evaluate_chain_2_1,
    "crear_pedido": evaluate_chain_2_2,
    "buscar_disponibilidad": evaluate_chain_2_3,
    "actualizar_inventario_masivo": evaluate_chain_2_4,
}


class ChatRequest(BaseModel):
    session_id: str
    message: str
    intento_cadena_id: str | None = None
    tecnica: str | None = None


class ResetRequest(BaseModel):
    session_id: str


@router.post("/reset")
def reset_ecommerce(req: ResetRequest, db: Session = Depends(get_db)):
    _conversations.pop(req.session_id, None)
    reset_datos_ecommerce(db)
    return {"status": "reset", "session_id": req.session_id}


@router.post("")
def chat_ecommerce(req: ChatRequest, db: Session = Depends(get_db)):
    history = _conversations.setdefault(
        req.session_id,
        [{"role": "system", "content": SYSTEM_PROMPT_ECOMMERCE}],
    )
    history.append({"role": "user", "content": req.message})

    resultado_turno = ejecutar_turno(history, ECOMMERCE_TOOLS, ECOMMERCE_FUNCTIONS, db)

    tool_calls = resultado_turno["tool_calls"]
    ultima_llamada = tool_calls[-1] if tool_calls else None
    function_called = ultima_llamada["tool_name"] if ultima_llamada else None
    function_args = ultima_llamada.get("arguments") if ultima_llamada else None
    function_result = ultima_llamada.get("result") if ultima_llamada else None
    final_message = resultado_turno["assistant_response"]

    log_entry = log_interaction(
        db=db,
        escenario="ecommerce",
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
