# models/ticket.py
from typing import TypedDict, Optional

class Ticket(TypedDict):
    story: str                        # descripción de la tarea
    tasks: list[str]                  # tareas técnicas generadas por Task Creator
    tasks_review: Optional[str]       # feedback del Reviewer sobre tasks
    tasks_approved: bool              # si las tasks fueron aprobadas
    tasks_attempts: int               # contador de reintentos de tasks (máx 3)
    code: Optional[str]               # código generado por Developer
    review: Optional[str]             # feedback del Reviewer sobre código
    approved: bool                    # si el código pasó el review
    review_attempts: int              # contador de reintentos de review
    tests: Optional[str]              # tests generados por QA, si el código fue aprobado
    tests_passed: Optional[bool]      # si los tests pasaron
    tests_output: Optional[str]       # logs de ejecución de tests
    qa_attempts: int                  # contador de reintentos de QA
    server_path: Optional[str]        # ruta del servidor generado por DevOps
    deployed: Optional[bool]          # si el servidor fue deployado