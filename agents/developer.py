# agents/developer.py
from config.llm import get_llm
from models.ticket import Ticket

llm = get_llm()

def developer_agent(ticket: Ticket) -> Ticket:
    import sys
    print("[DEVELOPER] Iniciando...", file=sys.stderr, flush=True)
    prompt = f"""
Sos un desarrollador TypeScript experto. 
Escribí el código para completar estas tareas:
{chr(10).join(f'- {t}' for t in ticket['tasks'])}

Contexto de la story: {ticket['story']}

REQUISITOS IMPORTANTES:
1. Devolvé código en TypeScript (con tipos de datos)
2. Define la función principal para la story
3. AL FINAL, SIEMPRE exporta la función principal con: export {{ nombreFuncion }};
4. Incluye validaciones y manejo de errores
5. En bloques try-catch, haz type narrowing: if (error instanceof Error) {{ }} antes de acceder a .message
6. Sin comentarios de prueba (describe, it, expect)
7. Sin llamadas a main() ni código de ejecución

Devolvé solo el código, sin explicaciones ni bloques markdown.
"""
    print("[DEVELOPER] Llamando LLM...", file=sys.stderr, flush=True)
    response = llm.invoke(prompt)
    print("[DEVELOPER] Completado", file=sys.stderr, flush=True)
    return {**ticket, "code": response.content}