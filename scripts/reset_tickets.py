#!/usr/bin/env python
# scripts/reset_tickets.py
"""
Script para resetear todos los tickets al estado 'pending'
Borra el código, tests, reviews pero mantiene las stories
"""

import json
import sys

def reset_tickets() -> None:
    """Resetea todos los tickets al estado inicial"""
    tickets_file = "tickets.json"
    
    try:
        with open(tickets_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"[ERROR] Archivo {tickets_file} no encontrado")
        sys.exit(1)
    
    # Resetear cada ticket
    for ticket in data.get("tickets", []):
        ticket.update({
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
        })
    
    # Guardar archivo
    with open(tickets_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"[OK] {len(data.get('tickets', []))} tickets reseteados a estado pending")

if __name__ == "__main__":
    reset_tickets()
