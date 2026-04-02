# agents/developer.py
from config.llm import get_llm
from models.ticket import Ticket

llm = get_llm()

def developer_agent(ticket: Ticket) -> Ticket:
    import sys
    print("[DEVELOPER] Iniciando...", file=sys.stderr, flush=True)
    prompt = f"""
Sos un desarrollador Javascript. 
Escribí el código para completar estas tareas:
{chr(10).join(f'- {t}' for t in ticket['tasks'])}

Contexto de la story: {ticket['story']}

Devolvé solo el código, sin explicaciones.
"""
    print("[DEVELOPER] Llamando LLM...", file=sys.stderr, flush=True)
    response = llm.invoke(prompt)
    print("[DEVELOPER] Completado", file=sys.stderr, flush=True)
    return {**ticket, "code": response.content}