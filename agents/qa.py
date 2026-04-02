# agents/qa.py
import os
import re
import subprocess
import sys
from config.llm import get_llm
from models import ticket
from models import ticket
from models.ticket import Ticket

llm = get_llm()
SANDBOX = os.getenv("TS_SANDBOX_PATH")

def extract_code(text: str) -> str:
    match = re.search(r"```(?:typescript|ts)?\n(.*?)```", text, re.DOTALL)
    return match.group(1).strip() if match else text.strip()

def qa_agent(ticket: Ticket) -> Ticket:
    import sys
    print("[QA] Iniciando...", file=sys.stderr, flush=True)
    
    prompt = f"""
Sos un QA engineer. Dado este código TypeScript:

{ticket['code']}

Story: {ticket['story']}

Generá dos bloques de código separados:
1. El código fuente en TypeScript (sin imports de jest)
2. Los tests con jest (importando desde ./solution)

Usá bloques ```typescript para cada uno, en ese orden.
"""
    print("[QA] Llamando LLM...", file=sys.stderr, flush=True)
    response = llm.invoke(prompt)
    print("[QA] LLM respondió, extrayendo bloques...", file=sys.stderr, flush=True)
    blocks = re.findall(r"```(?:typescript|ts)?\n(.*?)```", response.content, re.DOTALL)

    if len(blocks) < 2:
        print(f"[QA] ERROR: Se esperaban 2 bloques, se obtuvieron {len(blocks)}", file=sys.stderr, flush=True)
        return {**ticket, "tests": response.content, "tests_passed": False}

    solution_code = blocks[0].strip()
    test_code = blocks[1].strip()
    test_code = blocks[1].strip().replace("toThrowError", "toThrow")

    print("[QA] Escribiendo archivos...", file=sys.stderr, flush=True)
    with open(os.path.join(SANDBOX, "solution.ts"), "w") as f:
        f.write(solution_code)
    with open(os.path.join(SANDBOX, "solution.test.ts"), "w") as f:
        f.write(test_code)

    print("[QA] Ejecutando tests (npm test)...", file=sys.stderr, flush=True)
    result = subprocess.run(
        ["npm", "test"],
        cwd=SANDBOX,
        capture_output=True,
        text=True,
        shell=True,
        timeout=30,
        encoding="utf-8",
        errors="replace"
    )
    print(f"[QA] STDOUT: {result.stdout}", file=sys.stderr, flush=True)
    print(f"[QA] STDERR: {result.stderr}", file=sys.stderr, flush=True)

    passed = result.returncode == 0
    output = (result.stdout or "") + (result.stderr or "")
    print(f"[QA] Tests {'PASARON' if passed else 'FALLARON'}", file=sys.stderr, flush=True)

    # return {**ticket, "tests": test_code, "tests_passed": passed, "tests_output": output}
    return {**ticket, "tests": test_code, "tests_passed": passed, "tests_output": output, "qa_attempts": ticket.get("qa_attempts", 0) + 1}