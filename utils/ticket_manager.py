# utils/ticket_manager.py
import json
import os
from typing import List, Optional
from models.ticket import Ticket

def read_tickets(file_path: str) -> List[Ticket]:
    """Lee tickets desde un archivo JSON."""
    if not os.path.exists(file_path):
        print(f"[WARN] Archivo {file_path} no existe")
        return []
    
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    tickets = data.get("tickets", [])
    print(f"[OK] Cargados {len(tickets)} tickets desde {file_path}")
    return tickets

def write_tickets(file_path: str, tickets: List[Ticket]) -> None:
    """Escribe tickets actualizados a un archivo JSON."""
    data = {"tickets": tickets}
    
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"[OK] Actualizados {len(tickets)} tickets en {file_path}")

def initialize_ticket_file(file_path: str) -> None:
    """Crea un archivo JSON de ejemplo si no existe."""
    if os.path.exists(file_path):
        return
    
    example_tickets = {
        "tickets": [
            {
                "story": "Crear función que valide emails",
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
                "status": "pending"
            },
            {
                "story": "Implementar función para generar contraseña aleatoria",
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
                "status": "pending"
            }
        ]
    }
    
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(example_tickets, f, indent=2, ensure_ascii=False)
    
    print(f"[OK] Archivo de ejemplo creado: {file_path}")
