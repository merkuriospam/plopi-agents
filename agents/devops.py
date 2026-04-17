# agents/devops.py
import os
import re
import json
import subprocess
from config.llm import get_llm
from models.ticket import Ticket

llm = get_llm()
SANDBOX = os.getenv("TS_SANDBOX_PATH")

def extract_code(text: str) -> str:
    match = re.search(r"```(?:typescript|ts)?\n(.*?)```", text, re.DOTALL)
    return match.group(1).strip() if match else text.strip()

def devops_agent(ticket: Ticket) -> Ticket:
    import sys
    print("[DEVOPS] Iniciando generación de servidor...", file=sys.stderr, flush=True)
    
    # Obtener sandbox path del ticket
    sandbox = ticket.get("sandbox_path", os.getenv("TS_SANDBOX_PATH", "C:\\dev\\temp\\pipa"))
    
    # Crear directorio si no existe
    os.makedirs(sandbox, exist_ok=True)
    
    prompt = f"""
Sos un DevOps engineer. Dado este código TypeScript:

{ticket['code']}

Generá un servidor Express en TypeScript que:
1. Importe la función principal del archivo ./solution
2. La exponga en un endpoint GET /run con los parámetros como query params
3. Devuelva el resultado en JSON
4. Corra en el puerto 3000
5. En el catch de errores, verifica que error sea una instancia de Error antes de acceder a .message

Devolvé solo el código del server, sin explicaciones, sin bloques markdown.
"""
    print("[DEVOPS] Llamando LLM...", file=sys.stderr, flush=True)
    response = llm.invoke(prompt)
    print("[DEVOPS] LLM respondió, extrayendo código...", file=sys.stderr, flush=True)
    server_code = extract_code(response.content)

    path = os.path.join(sandbox, "server.ts")
    print(f"[DEVOPS] Escribiendo servidor en {path}...", file=sys.stderr, flush=True)
    with open(path, "w") as f:
        f.write(server_code)

    print("[DEVOPS] ¡Completado!", file=sys.stderr, flush=True)
    return {**ticket, "server_path": path, "deployed": True}