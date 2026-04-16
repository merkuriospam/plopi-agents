#!/usr/bin/env python
# scripts/add_ticket.py
"""
Script para agregar nuevos tickets al archivo tickets.json
Uso: python scripts/add_ticket.py "Story description"
"""

import json
import sys
import os

def add_ticket(story: str) -> None:
    """Agrega un nuevo ticket al archivo tickets.json"""
    tickets_file = "tickets.json"
    
    # Crear archivo si no existe
    if not os.path.exists(tickets_file):
        data = {"tickets": []}
    else:
        with open(tickets_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
    
    # Crear nuevo ticket
    new_ticket = {
        "story": story,
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
    
    # Agregar a la lista
    data["tickets"].append(new_ticket)
    
    # Guardar archivo
    with open(tickets_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"[OK] Ticket agregado: '{story}'")
    print(f"[OK] Total de tickets: {len(data['tickets'])}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python scripts/add_ticket.py \"Story description\"")
        print("Ejemplo: python scripts/add_ticket.py \"Crear funcion para validar emails\"")
        sys.exit(1)
    
    story = sys.argv[1]
    add_ticket(story)
