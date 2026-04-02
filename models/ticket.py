# models/ticket.py
from typing import TypedDict, Optional

class Ticket(TypedDict):
    story: str                    # descripción de la tarea
    tasks: list[str]              # tareas técnicas (las define Tech Lead)
    code: Optional[str]           # código generado por Developer
    review: Optional[str]         # feedback del Reviewer
    approved: bool                # si pasó el review
    tests: Optional[str]          # tests generados por QA, si el código fue aprobado
    tests_passed: Optional[bool]
    tests_output: Optional[str]
    server_path: Optional[str]
    deployed: Optional[bool]