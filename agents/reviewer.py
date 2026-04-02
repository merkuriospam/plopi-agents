# agents/reviewer.py
from config.llm import get_llm
from models.ticket import Ticket

llm = get_llm()

def reviewer_agent(ticket: Ticket) -> Ticket:
    import sys
    print("[REVIEWER] Iniciando...", file=sys.stderr, flush=True)
    prompt = f"""
Sos un code reviewer senior. Revisá este código Javascript:

{ticket['code']}

Criterios: calidad, manejo de errores, buenas prácticas.
Respondé SOLO con uno de estos formatos:
- APROBADO
- RECHAZADO: <motivo concreto>
"""
    print("[REVIEWER] Llamando LLM...", file=sys.stderr, flush=True)
    response = llm.invoke(prompt)
    print("[REVIEWER] Completado", file=sys.stderr, flush=True)
    content = response.content.strip()
    approved = content.startswith("APROBADO")
    attempts = ticket.get("review_attempts", 0)
    return {**ticket, "review": content, "approved": approved, "review_attempts": attempts + 1}