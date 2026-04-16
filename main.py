# main.py
from dotenv import load_dotenv
load_dotenv()

import sys
from langgraph.graph import StateGraph, END
from models.ticket import Ticket
from agents.task_creator import task_creator_agent
from agents.developer import developer_agent
from agents.reviewer import reviewer_agent
from agents.qa import qa_agent
from agents.devops import devops_agent

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

ticket: Ticket = {
    "story": "Necesito una función que calcule el factorial de un número",
    "tasks": [],
    "tasks_review": None,
    "tasks_approved": False,
    "tasks_attempts": 0,
    "code": None,
    "review": None,
    "approved": False,
    "review_attempts": 0,
    "tests": None,
    "tests_passed": None,
    "tests_output": None,
    "qa_attempts": 0,
    "server_path": None,
    "deployed": False,
}

from langgraph.errors import GraphRecursionError

try:
    result = graph.invoke(ticket, {"recursion_limit": 15})
except GraphRecursionError:
    print("❌ ERROR: Se alcanzó el límite de iteraciones. Proceso abortado para no consumir más créditos.")
    exit(1)

print("=== TASKS ===")
print("\n".join(result["tasks"]))
print("=== TASKS REVIEW ===")
print(result["tasks_review"])
print("=== CÓDIGO ===")
print(result["code"])
print("=== REVIEW ===")
print(result["review"])
print("=== TESTS ===")
print(result["tests"])
print("=== RESULTADO ===")
passed = result.get("tests_passed", False)
print("PASARON" if passed else "FALLARON")
try:
    sys.stdout.write(result["tests_output"] + "\n")
except:
    pass
print("=== DEPLOY ===")
print(f"server.ts generado en: {result['server_path']}")
print("Para levantar: npx ts-node server.ts")