import json
from app.llm.client import chat_completion

MAX_TOOL_ROUNDS = 6


def ejecutar_turno(history: list[dict], tools: list[dict], functions: dict, db) -> dict:
    tool_calls_registrados = []
    error = None

    for _ in range(MAX_TOOL_ROUNDS):
        try:
            response = chat_completion(messages=history, tools=tools)
        except Exception as e:
            error = {"error_type": type(e).__name__, "error_message": str(e)}
            break

        choice = response.choices[0].message

        if not choice.tool_calls:
            history.append({"role": "assistant", "content": choice.content})
            break

        tool_call = choice.tool_calls[0]
        function_called = tool_call.function.name

        try:
            function_args = json.loads(tool_call.function.arguments)
        except json.JSONDecodeError as e:
            tool_calls_registrados.append({
                "tool_name": function_called, "arguments_raw": tool_call.function.arguments,
                "status": "error", "error_type": "invalid_tool_arguments", "error_message": str(e),
            })
            break

        fn = functions.get(function_called)
        if fn:
            try:
                function_result = fn(db, **function_args)
                status = "success"
            except Exception as e:
                function_result = {"error": str(e)}
                status = "error"
        else:
            function_result = {"error": f"función desconocida: {function_called}"}
            status = "error"

        tool_calls_registrados.append({
            "tool_name": function_called, "arguments": function_args,
            "result": function_result, "status": status,
        })

        assistant_msg = {
            "role": "assistant", "content": choice.content,
            "tool_calls": [{
                "id": tool_call.id, "type": "function",
                "function": {"name": tool_call.function.name, "arguments": tool_call.function.arguments},
            }],
        }
        history.append(assistant_msg)
        history.append({"role": "tool", "tool_call_id": tool_call.id, "content": json.dumps(function_result)})

    ultimo_msg = history[-1] if history else {}
    respuesta_final = (
        ultimo_msg.get("content")
        if ultimo_msg.get("role") == "assistant" and not ultimo_msg.get("tool_calls")
        else None
    )

    return {
        "tool_calls": tool_calls_registrados,
        "assistant_response": respuesta_final,
        "error": error,
    }
