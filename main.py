# main.py
from dotenv import load_dotenv
load_dotenv()

import sys
from langgraph.graph import StateGraph, END
from models.ticket import Ticket
from agents.developer import developer_agent
from agents.reviewer import reviewer_agent
from agents.qa import qa_agent
from agents.devops import devops_agent

def log(msg):
    print(f"[LOG] {msg}", file=sys.stderr, flush=True)

def route_review(ticket: Ticket):
    attempts = ticket.get("review_attempts", 0)
    log(f"route_review: approved={ticket['approved']}, attempts={attempts}")
    if attempts >= 3:
        log("Máximo de intentos de review alcanzado, forzando QA...")
        return "qa"
    return "qa" if ticket["approved"] else "developer"

def route_qa(ticket: Ticket):
    attempts = ticket.get("qa_attempts", 0)
    log(f"route_qa: tests_passed={ticket['tests_passed']}, attempts={attempts}")
    if attempts >= 3:
        log("Máximo de intentos de QA alcanzado, forzando devops...")
        return "devops"
    return "devops" if ticket["tests_passed"] else "developer"

builder = StateGraph(Ticket)
builder.add_node("developer", developer_agent)
builder.add_node("reviewer", reviewer_agent)
builder.add_node("qa", qa_agent)
builder.add_node("devops", devops_agent)

builder.set_entry_point("developer")
builder.add_edge("developer", "reviewer")
builder.add_conditional_edges("reviewer", route_review)
builder.add_conditional_edges("qa", route_qa)
builder.add_edge("devops", END)

graph = builder.compile()

ticket: Ticket = {
    "story": "Necesito una función que calcule el factorial de un número",
    "tasks": ["Crear función factorial(n)", "Validar n negativo"],
    "code": None,
    "review": None,
    "approved": False,
    "review_attempts": 0,
    "tests": None,
    "tests_passed": None,
    "tests_output": None,
    "server_path": None,
    "deployed": False,
    "review_attempts": 0,
    "qa_attempts": 0
}

from langgraph.errors import GraphRecursionError

try:
    result = graph.invoke(ticket, {"recursion_limit": 15})
except GraphRecursionError:
    print("❌ ERROR: Se alcanzó el límite de iteraciones. Proceso abortado para no consumir más créditos.")
    exit(1)

print("=== CÓDIGO ===")
print(result["code"])
print("=== REVIEW ===")
print(result["review"])
print("=== TESTS ===")
print(result["tests"])
print("=== RESULTADO ===")
print("✓ PASARON" if result["tests_passed"] else "✗ FALLARON")
print(result["tests_output"])
print("=== DEPLOY ===")
print(f"server.ts generado en: {result['server_path']}")
print("Para levantar: npx ts-node server.ts")