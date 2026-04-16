# main.py
from dotenv import load_dotenv
load_dotenv()

import sys
import json
from langgraph.graph import StateGraph, END
from models.ticket import Ticket
from agents.task_creator import task_creator_agent
from agents.developer import developer_agent
from agents.reviewer import reviewer_agent
from agents.qa import qa_agent
from agents.devops import devops_agent
from utils.ticket_manager import read_tickets, write_tickets, initialize_ticket_file

# Argumentos de línea de comandos
FORCE_REPROCESS = "--force" in sys.argv or "-f" in sys.argv
ONLY_FAILED = "--only-failed" in sys.argv

def log(msg):
    print(f"[LOG] {msg}", file=sys.stderr, flush=True)

def route_after_task_creator(ticket: Ticket):
    """Después de generar tasks, ir a Reviewer para validarlas."""
    log("route_after_task_creator -> reviewer")
    return "reviewer"

def route_review(ticket: Ticket):
    """
    Enrutador para el Reviewer. Depending on phase:
    - Phase 1 (TASK VALIDATION): tasks_review fue seteado, code es None
    - Phase 2 (CODE REVIEW): review fue seteado, code no es None
    """
    code = ticket.get("code")
    review = ticket.get("review")
    tasks_review = ticket.get("tasks_review")
    
    log(f"route_review: code={code is not None}, review={review is not None}, tasks_review={tasks_review is not None}")
    
    # Fase 2: Después de revisar código (code y review están seteados)
    if code is not None and review is not None:
        approved = ticket.get("approved", False)
        review_attempts = ticket.get("review_attempts", 0)
        log(f"  FASE 2 (CODE): approved={approved}, attempts={review_attempts}")
        
        if not approved and review_attempts < 3:
            log("  → Reintentar Developer")
            return "developer"
        else:
            log("  → Ir a QA")
            return "qa"
    
    # Fase 1: Después de validar tasks (tasks_review está seteado, code es None)
    if tasks_review is not None and code is None:
        tasks_approved = ticket.get("tasks_approved", False)
        tasks_attempts = ticket.get("tasks_attempts", 0)
        log(f"  FASE 1 (TASKS): approved={tasks_approved}, attempts={tasks_attempts}")
        
        if not tasks_approved and tasks_attempts < 3:
            log("  → Reintentar Task Creator")
            return "task_creator"
        else:
            log("  → Ir a Developer")
            return "developer"
    
    # Fallback
    log("  → Default: QA")
    return "qa"

def route_qa(ticket: Ticket):
    attempts = ticket.get("qa_attempts", 0)
    tests_passed = ticket.get("tests_passed", False)
    log(f"route_qa: tests_passed={tests_passed}, attempts={attempts}")
    if attempts >= 3:
        log("Máximo de intentos de QA alcanzado, forzando devops...")
        return "devops"
    return "devops" if tests_passed else "developer"

builder = StateGraph(Ticket)
builder.add_node("task_creator", task_creator_agent)
builder.add_node("developer", developer_agent)
builder.add_node("reviewer", reviewer_agent)
builder.add_node("qa", qa_agent)
builder.add_node("devops", devops_agent)

builder.set_entry_point("task_creator")
builder.add_edge("task_creator", "reviewer")
builder.add_conditional_edges("reviewer", route_review)
builder.add_edge("developer", "reviewer")  # Developer siempre va a Reviewer para que valide el código
builder.add_conditional_edges("qa", route_qa)
builder.add_edge("devops", END)

graph = builder.compile()

# Inicializar archivo de tickets si no existe
TICKETS_FILE = "tickets.json"
initialize_ticket_file(TICKETS_FILE)

# Leer tickets del JSON
tickets = read_tickets(TICKETS_FILE)

if not tickets:
    print("[ERROR] No hay tickets para procesar")
    exit(1)

from langgraph.errors import GraphRecursionError

# Procesar cada ticket
skipped = 0
for idx, ticket_data in enumerate(tickets, 1):
    status = ticket_data.get("status", "pending")
    story = ticket_data.get('story', 'Sin descripción')[:60]
    
    # Determinar si debe procesarse
    should_process = True
    skip_reason = None
    
    # Si --only-failed: solo procesar tickets fallidos
    if ONLY_FAILED:
        if status != "failed":
            should_process = False
            skip_reason = "no fallido (usa --all para procesar todos)"
    # Si no --force: saltar completados
    elif not FORCE_REPROCESS:
        if status == "completed":
            should_process = False
            skip_reason = "ya completado (usa --force para reprocesar)"
        elif status == "failed":
            should_process = False
            skip_reason = "falló anteriormente (usa --force para reintentar)"
    
    if not should_process:
        print(f"[SKIP] Ticket #{idx} - {skip_reason}: {story}...")
        skipped += 1
        continue
    
    print(f"\n{'='*60}")
    print(f"[{idx}/{len(tickets)}] Procesando: {story}")
    print(f"Status anterior: {status}")
    print(f"{'='*60}\n")
    
    # Construir ticket completo con valores por defecto
    ticket: Ticket = {
        "story": ticket_data.get("story", ""),
        "tasks": ticket_data.get("tasks", []),
        "tasks_review": ticket_data.get("tasks_review"),
        "tasks_approved": ticket_data.get("tasks_approved", False),
        "tasks_attempts": ticket_data.get("tasks_attempts", 0),
        "code": ticket_data.get("code"),
        "review": ticket_data.get("review"),
        "approved": ticket_data.get("approved", False),
        "review_attempts": ticket_data.get("review_attempts", 0),
        "tests": ticket_data.get("tests"),
        "tests_passed": ticket_data.get("tests_passed"),
        "tests_output": ticket_data.get("tests_output"),
        "qa_attempts": ticket_data.get("qa_attempts", 0),
        "server_path": ticket_data.get("server_path"),
        "deployed": ticket_data.get("deployed", False),
    }
    
    try:
        result = graph.invoke(ticket, {"recursion_limit": 15})
        
        # Actualizar estado del ticket con resultado del flujo
        ticket_data.update({
            "tasks": result.get("tasks", []),
            "tasks_review": result.get("tasks_review"),
            "tasks_approved": result.get("tasks_approved", False),
            "tasks_attempts": result.get("tasks_attempts", 0),
            "code": result.get("code"),
            "review": result.get("review"),
            "approved": result.get("approved", False),
            "review_attempts": result.get("review_attempts", 0),
            "tests": result.get("tests"),
            "tests_passed": result.get("tests_passed"),
            "tests_output": result.get("tests_output"),
            "qa_attempts": result.get("qa_attempts", 0),
            "server_path": result.get("server_path"),
            "deployed": result.get("deployed", False),
            "status": "completed" if result.get("tests_passed") else "failed"
        })
        
        # Mostrar resumen del ticket
        print(f"\n[SUMMARY] TICKET #{idx}")
        print(f"  Story: {result['story'][:60]}...")
        print(f"  Tasks: {len(result.get('tasks', []))} generadas")
        print(f"  Tasks Aprobadas: {'[OK] SI' if result.get('tasks_approved') else '[NO]'}")
        print(f"  Codigo Aprobado: {'[OK] SI' if result.get('approved') else '[NO]'}")
        print(f"  Tests Pasados: {'[OK] SI' if result.get('tests_passed') else '[NO]'}")
        print(f"  Deployed: {'[OK] SI' if result.get('deployed') else '[NO]'}")
        print(f"  Server: {result.get('server_path', 'N/A')}")
        
    except GraphRecursionError:
        print(f"[ERROR] Ticket #{idx} alcanzo limite de iteraciones")
        ticket_data["status"] = "error"
    except Exception as e:
        print(f"[ERROR] Ticket #{idx} - {str(e)}")
        ticket_data["status"] = "error"

# Guardar tickets actualizados
write_tickets(TICKETS_FILE, tickets)

print(f"\n{'='*60}")
print("[OK] Procesamiento completado")
if skipped > 0:
    print(f"     {skipped} ticket(s) saltado(s) (ya completado/fallido)")
    print(f"     Opciones:")
    print(f"       --force: Reprocesar todos los tickets")
    print(f"       --only-failed: Solo reprocesar tickets fallidos")
print(f"{'='*60}")