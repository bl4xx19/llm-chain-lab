import csv
import io
import json
from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse, JSONResponse
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.db.models import InteractionLog

router = APIRouter(prefix="/logs", tags=["logs"])


def _query_logs(db: Session, escenario: str | None, cadena_id: str | None):
    q = db.query(InteractionLog)
    if escenario:
        q = q.filter(InteractionLog.escenario == escenario)
    if cadena_id:
        q = q.filter(InteractionLog.cadena_id == cadena_id)
    return q.order_by(InteractionLog.timestamp.asc()).all()


@router.get("/export")
def export_logs(
    escenario: str | None = Query(default=None),
    cadena_id: str | None = Query(default=None),
    formato: str = Query(default="json", pattern="^(json|csv)$"),
    db: Session = Depends(get_db),
):
    logs = _query_logs(db, escenario, cadena_id)

    if formato == "json":
        data = [
            {
                "id": l.id,
                "escenario": l.escenario,
                "cadena_id": l.cadena_id,
                "tecnica": l.tecnica,
                "session_id": l.session_id,
                "user_input": l.user_input,
                "llm_raw_response": l.llm_raw_response,
                "function_called": l.function_called,
                "function_args": l.function_args,
                "function_result": l.function_result,
                "timestamp": l.timestamp.isoformat() if l.timestamp else None,
            }
            for l in logs
        ]
        return JSONResponse(content=data)

    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(
        [
            "id", "escenario", "cadena_id", "tecnica", "session_id", "user_input",
            "function_called", "function_args", "function_result", "timestamp",
        ]
    )
    for l in logs:
        writer.writerow(
            [
                l.id,
                l.escenario,
                l.cadena_id,
                l.tecnica,
                l.session_id,
                l.user_input,
                l.function_called,
                json.dumps(l.function_args, ensure_ascii=False),
                json.dumps(l.function_result, ensure_ascii=False),
                l.timestamp.isoformat() if l.timestamp else None,
            ]
        )
    buffer.seek(0)
    filename = f"logs_{escenario or 'todos'}_{cadena_id or 'todas'}.csv"
    return StreamingResponse(
        buffer,
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )


@router.get("/reproducibilidad")
def reproducibilidad(
    escenario: str,
    cadena_id: str,
    expected_function: str = Query(..., description="Nombre de la función esperada, ej. 'transferir'"),
    db: Session = Depends(get_db),
):
    logs = _query_logs(db, escenario, cadena_id)
    total = len(logs)
    exitosos = sum(1 for l in logs if l.function_called == expected_function)
    tasa = (exitosos / total) if total else 0.0

    por_tecnica: dict[str, dict] = {}
    for l in logs:
        clave = l.tecnica or "sin_especificar"
        stats = por_tecnica.setdefault(clave, {"total": 0, "exitosos": 0})
        stats["total"] += 1
        if l.function_called == expected_function:
            stats["exitosos"] += 1

    for clave, stats in por_tecnica.items():
        t = stats["exitosos"] / stats["total"] if stats["total"] else 0.0
        stats["tasa_exito"] = round(t, 3)
        stats["validada_ind5"] = t >= 0.8

    return {
        "escenario": escenario,
        "cadena_id": cadena_id,
        "total_intentos": total,
        "intentos_exitosos": exitosos,
        "tasa_exito": round(tasa, 3),
        "validada_ind5": tasa >= 0.8,
        "por_tecnica": por_tecnica,
    }
