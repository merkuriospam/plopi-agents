# agents/task_creator.py
import re
import sys
from config.llm import get_llm
from models.ticket import Ticket

llm = get_llm()

def task_creator_agent(ticket: Ticket) -> Ticket:
    print("[TASK_CREATOR] Iniciando...", file=sys.stderr, flush=True)
    
    prompt = f"""
Sos un Tech Lead experto. Analiza esta story y genera 3-7 tareas técnicas específicas y alcanzables:

Story: {ticket['story']}

Devuelve una lista de tareas, cada una en una línea, con formato:
- [Tarea 1]
- [Tarea 2]
- etc.

Criterios:
- Cada tarea debe ser específica y verificable
- Deben cubrir completamente la story
- Evita ambigüedad y duplicados
- Ordena por dependencias lógicas (lo más independiente primero)

Devuelve SOLO la lista de tareas, sin explicaciones adicionales.
"""
    
    print("[TASK_CREATOR] Llamando LLM...", file=sys.stderr, flush=True)
    response = llm.invoke(prompt)
    print("[TASK_CREATOR] Completado", file=sys.stderr, flush=True)
    
    content = response.content.strip()
    
    # Parsear tareas: buscar líneas que comiencen con "- "
    tasks = []
    for line in content.split("\n"):
        line = line.strip()
        if line.startswith("- "):
            task = line[2:].strip()
            if task:
                tasks.append(task)
    
    # Fallback: si no se encontraron tareas con formato "- ", usar cualquier línea no vacía
    if not tasks:
        tasks = [line.strip() for line in content.split("\n") if line.strip() and not line.startswith("#")]
    
    print(f"[TASK_CREATOR] Tareas generadas: {len(tasks)}", file=sys.stderr, flush=True)
    
    attempts = ticket.get("tasks_attempts", 0)
    return {**ticket, "tasks": tasks, "tasks_attempts": attempts + 1}
