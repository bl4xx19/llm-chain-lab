from sqlalchemy.orm import Session
from app.db.models import InteractionLog


def log_interaction(
    db: Session,
    escenario: str,
    session_id: str,
    user_input: str,
    llm_raw_response: dict | None = None,
    function_called: str | None = None,
    function_args: dict | None = None,
    function_result: dict | None = None,
    cadena_id: str | None = None,
    tecnica: str | None = None,
) -> InteractionLog:
    entry = InteractionLog(
        escenario=escenario,
        cadena_id=cadena_id,
        tecnica=tecnica,
        session_id=session_id,
        user_input=user_input,
        llm_raw_response=llm_raw_response,
        function_called=function_called,
        function_args=function_args,
        function_result=function_result,
    )
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry
