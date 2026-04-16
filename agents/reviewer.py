# agents/reviewer.py
from config.llm import get_llm
from models.ticket import Ticket

llm = get_llm()

def reviewer_agent(ticket: Ticket) -> Ticket:
    import sys
    print("[REVIEWER] Iniciando...", file=sys.stderr, flush=True)
    
    # Fase 1: Validar tasks (si no hay código aún)
    if not ticket.get("code"):
        print("[REVIEWER] Modo TASK VALIDATION", file=sys.stderr, flush=True)
        prompt = f"""
Sos un Tech Lead senior. Valida estas tareas técnicas generadas a partir de una story:

Story: {ticket['story']}

Tasks:
{chr(10).join(f'- {t}' for t in ticket['tasks'])}

Criterios de validación:
1. ¿Cubren completamente la story?
2. ¿Son específicas y libres de ambigüedad?
3. ¿Son independientes o bien secuenciadas?
4. ¿Evitan duplicados?
5. ¿Son técnicamente factibles?

Respondé SOLO con uno de estos formatos:
- APROBADO
- RECHAZADO: <motivo concreto y actionable>
"""
        print("[REVIEWER] Llamando LLM para validar tasks...", file=sys.stderr, flush=True)
        response = llm.invoke(prompt)
        print("[REVIEWER] Validación de tasks completada", file=sys.stderr, flush=True)
        content = response.content.strip()
        tasks_approved = content.startswith("APROBADO")
        attempts = ticket.get("tasks_attempts", 0)
        return {
            **ticket,
            "tasks_review": content,
            "tasks_approved": tasks_approved,
            "tasks_attempts": attempts + 1
        }
    
    # Fase 2: Validar código (después de que Developer implementa)
    else:
        print("[REVIEWER] Modo CODE VALIDATION", file=sys.stderr, flush=True)
        prompt = f"""
Sos un code reviewer senior. Revisá este código Javascript:

{ticket['code']}

Story context: {ticket['story']}

Tareas que debería cumplir:
{chr(10).join(f'- {t}' for t in ticket['tasks'])}

Criterios: calidad, manejo de errores, buenas prácticas, cumplimiento de tareas.
Respondé SOLO con uno de estos formatos:
- APROBADO
- RECHAZADO: <motivo concreto>
"""
        print("[REVIEWER] Llamando LLM para revisar código...", file=sys.stderr, flush=True)
        response = llm.invoke(prompt)
        print("[REVIEWER] Revisión de código completada", file=sys.stderr, flush=True)
        content = response.content.strip()
        approved = content.startswith("APROBADO")
        attempts = ticket.get("review_attempts", 0)
        return {**ticket, "review": content, "approved": approved, "review_attempts": attempts + 1}
