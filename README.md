# Equipo de Agentes Ágiles Inteligentes (PLOPI)

Sistema automatizado que procesa historias/tickets técnicas a través de un flujo completo de agentes ágiles utilizando LLMs. Cada ticket se convierte automáticamente en tareas técnicas claras, código implementado, tests validadores y servidores listos para deploy.

## 🎯 Objetivo

Automatizar el ciclo completo de desarrollo ágil:
1. **Desglose de requisitos** → Generación automática de tasks técnicas
2. **Validación de diseño** → Reviewer aprueba tasks
3. **Implementación** → Developer escribe código según tasks
4. **Validación de calidad** → Reviewer revisa código + QA ejecuta tests
5. **Deployment** → DevOps genera servidor Express

## 🏗️ Arquitectura

```
Story (JSON)
    ↓
[Task Creator] → Genera 5-7 tasks específicas desde story
    ↓
[Reviewer] (Fase 1) → Valida tasks
    ├→ Rechazado → Reintentar Task Creator (máx 3)
    └→ Aprobado ↓
[Developer] → Implementa código según tasks
    ↓
[Reviewer] (Fase 2) → Valida código
    ├→ Rechazado → Reintentar Developer (máx 3)
    └→ Aprobado ↓
[QA] → Genera tests para cada task + ejecuta
    ├→ Fallados → Reintentar Developer (máx 3)
    └→ Pasados ↓
[DevOps] → Genera servidor Express TypeScript
    ↓
[Output] → Ticket completado con todo actualizado en JSON
```

### 📁 Sandbox Separados por Ticket

Cada ticket genera su solución en un directorio único dentro de TS_SANDBOX_PATH:

```
TS_SANDBOX_PATH (default: C:\dev\temp\pipa)
├── node_modules/               (dependencias compartidas)
├── ticket_1/                   (solución ticket #1)
│   ├── solution.ts             (código generado)
│   ├── solution.test.ts        (tests generados)
│   └── server.ts               (servidor Express)
├── ticket_2/                   (solución ticket #2)
│   ├── solution.ts
│   ├── solution.test.ts
│   └── server.ts
└── ticket_N/                   (solución ticket #N)
    ├── solution.ts
    ├── solution.test.ts
    └── server.ts
```

**Ventajas:**
- ✅ No hay conflictos entre soluciones de diferentes tickets
- ✅ Cada ticket es completamente independiente
- ✅ Fácil de debuggear, testear y auditar
- ✅ El path se guarda en `tickets.json` para trazabilidad completa
- ✅ Tests de diferentes tickets se ejecutan sin interferencias

## 📁 Estructura del Proyecto

```
plopi-agents/
├── main.py                      # Orquestador principal
├── agents/                      # Módulos de agentes
│   ├── task_creator.py         # Genera tasks técnicas
│   ├── developer.py            # Implementa código
│   ├── reviewer.py             # Valida tasks y código
│   ├── qa.py                   # Crea y ejecuta tests
│   └── devops.py               # Genera servidor Express
├── models/
│   └── ticket.py               # Estructura TypedDict de Ticket
├── config/
│   └── llm.py                  # Factory de LLMs (Groq, OpenAI, etc)
├── utils/
│   └── ticket_manager.py       # Lee/escribe JSON de tickets
├── scripts/
│   ├── add_ticket.py           # Agregar nuevo ticket
│   └── reset_tickets.py        # Resetear tickets a pending
├── tickets.json                # Archivo con tickets
├── README.md                   # Este archivo
├── README_TICKETS.md           # Documentación de tickets.json
└── .env                        # Variables de entorno (API keys, paths)
```

## 🚀 Quick Start

### 1. Instalación

```bash
# Clonar o descargar el proyecto
cd plopi-agents

# Crear venv (si no existe)
python -m venv venv
source venv/Scripts/activate  # Windows
# o
source venv/bin/activate       # macOS/Linux

# Instalar dependencias
pip install python-dotenv langgraph langchain-core langchain-groq
```

### 2. Configurar LLM

Crear archivo `.env`:

```bash
# Usar Groq (recomendado para desarrollo, más rápido)
LLM_PROVIDER=groq
LLM_MODEL=llama-3.3-70b-versatile
LLM_API_KEY=gsk_xxxxx

# O usar otros proveedores:
# LLM_PROVIDER=openai
# LLM_PROVIDER=anthropic
# LLM_PROVIDER=gemini
# LLM_PROVIDER=azure

# Sandbox para ejecutar tests
TS_SANDBOX_PATH=C:\dev\temp\pipa
```

### 3. Crear tickets

Opción A: Editar `tickets.json` manualmente

```json
{
  "tickets": [
    {
      "story": "Crear función que valide emails",
      "tasks": [],
      "tasks_review": null,
      "tasks_approved": false,
      ...
    }
  ]
}
```

Opción B: Usar script

```bash
python scripts/add_ticket.py "Crear función que valide emails"
python scripts/add_ticket.py "Implementar generador de contraseñas"
```

### 4. Procesar tickets

```bash
python main.py
```

El sistema:
- Lee tickets del JSON
- **Salta automáticamente tickets ya completados o fallidos**
- Procesa solo nuevos tickets (status: "pending")
- Actualiza estados en el JSON
- Muestra resumen

**Opciones de línea de comandos:**

```bash
# Procesamiento normal (saltea completados/fallidos)
python main.py

# Reprocesar todos (incluyendo completados)
python main.py --force
python main.py -f

# Solo reprocesar fallidos
python main.py --only-failed

# Reprocesar solo fallidos (versión larga)
python main.py --force --only-failed
```

**Ejemplos de uso:**

```bash
# Procesar nuevos tickets, saltear completados
$ python main.py
[SKIP] Ticket #1 - ya completado: Necesito una función...
[PROCESANDO] Ticket #3 - Nuevo ticket: Crear API REST...

# Reintentar solo los que fallaron
$ python main.py --only-failed
[SKIP] Ticket #1 - no fallido: Necesito una función...
[PROCESANDO] Ticket #2 - fallido anteriormente: Crear función...
[SKIP] Ticket #3 - no fallido: Crear API REST...

# Reprocesar TODO desde cero
$ python main.py --force
[PROCESANDO] Ticket #1 - Necesito una función...
[PROCESANDO] Ticket #2 - Crear función...
[PROCESANDO] Ticket #3 - Crear API REST...
```

### 5. Ver resultados

Abrir `tickets.json` para ver:
- Tasks generadas
- Código implementado
- Tests y resultados
- Ruta del servidor deployado
- Estado final (completed/failed/error)

## 📊 Flujo Detallado

### Fase 1: Task Creation & Validation

```
Story: "Crear función que valide emails"
    ↓
[Task Creator]
    ├→ Tarea 1: Definir estructura de validación de email
    ├→ Tarea 2: Implementar regex para validar formato
    ├→ Tarea 3: Manejo de casos especiales
    ├→ Tarea 4: Crear pruebas unitarias
    ├→ Tarea 5: Validar contra estándares RFC
    └→ Tarea 6: Documentar función y ejemplos
    ↓
[Reviewer - FASE 1]
    Criterios:
    ✓ ¿Cubren completamente la story?
    ✓ ¿Son específicas y verificables?
    ✓ ¿Evitan ambigüedad?
    ✓ ¿Evitan duplicados?
    ✓ ¿Son técnicamente factibles?
    ↓
Resultado: APROBADO ← o ← RECHAZADO (reintentar, máx 3)
```

### Fase 2: Development & Code Review

```
[Developer]
    Recibe: tasks aprobadas + story
    Genera: Código JavaScript que cumple cada task
    ↓
[Reviewer - FASE 2]
    Criterios:
    ✓ Calidad del código
    ✓ Manejo de errores
    ✓ Buenas prácticas
    ✓ Cumple cada task
    ↓
Resultado: APROBADO ← o ← RECHAZADO (reintentar, máx 3)
```

### Fase 3: QA & Testing

```
[QA]
    Recibe: tasks + código
    Genera:
        1. solution.ts (código limpio)
        2. solution.test.ts (tests Jest)
    
    Cada test incluye:
    // Task: [nombre de la task que valida]
    
    Ejecuta: npm test
    ↓
Resultado: PASARON (7/7 tests) ← o ← FALLARON (reintentar, máx 3)
```

### Fase 4: Deployment

```
[DevOps]
    Genera: server.ts (Express + TypeScript)
    - Importa función desde solution
    - Expone endpoint GET /run
    - Responde JSON
    - Puerto 3000
    ↓
Resultado: server.ts en C:\dev\temp\pipa\server.ts
```

## 🔧 Configuración Avanzada

### Variables de Entorno

```bash
# LLM Provider (groq, openai, anthropic, gemini, azure)
LLM_PROVIDER=groq
LLM_MODEL=llama-3.3-70b-versatile
LLM_API_KEY=your_key_here

# Sandbox TypeScript
TS_SANDBOX_PATH=/path/to/sandbox

# Reintentos (opcional, por defecto 3)
MAX_RETRY_ATTEMPTS=3

# Recursion limit (por defecto 15)
RECURSION_LIMIT=15
```

### Limitar Reintentos

En `main.py`, ajustar condiciones en `route_review()` y `route_qa()`:

```python
if not approved and review_attempts < 3:  # Cambiar a 5 para permitir más
    return "developer"
```

### Aumentar Timeout de Tests

En `agents/qa.py`, línea ~60:

```python
timeout=120,  # Aumentar a 180 si necesario
```

## 📈 Monitoreo y Logs

Todos los agentes imprimen logs con prefix:
- `[TASK_CREATOR]` - Task Creator
- `[DEVELOPER]` - Developer
- `[REVIEWER]` - Reviewer
- `[QA]` - QA
- `[DEVOPS]` - DevOps
- `[LOG]` - Logs de orquestación

Ejemplo:
```
[TASK_CREATOR] Iniciando...
[TASK_CREATOR] Llamando LLM...
[TASK_CREATOR] Completado
[TASK_CREATOR] Tareas generadas: 7
```

## 🔄 Reintentos Automáticos

Cada validación reintentar automáticamente hasta 3 veces:

| Fase | Validador | Máx Intentos | Al Fallar |
|------|-----------|-------------|----------|
| 1 | Reviewer (tasks) | 3 | → Task Creator |
| 2 | Reviewer (code) | 3 | → Developer |
| 3 | QA (tests) | 3 | → Developer |

Después del 3er intento fallido, continúa al siguiente paso.

## ⏭️ Skip Automático de Tickets Completados

El sistema evita reprocesar tickets que ya fueron completados:

```
Status | Comportamiento
-------|----------------
pending | Siempre se procesa
completed | Se salta (usa --force para reprocesar)
failed | Se salta (usa --force o --only-failed para reprocesar)
error | Se salta (usa --force para reprocesar)
```

**Ventajas:**
- ✅ No desperdicia créditos de API reintentando
- ✅ Procesa rápidamente solo nuevos tickets
- ✅ Permite reintentar específicamente los fallidos

**Flags disponibles:**
- `--force` o `-f`: Reprocesa TODOS los tickets
- `--only-failed`: Reprocesa SOLO los fallidos

## 📦 Dependencias

- **LangGraph** - Orquestación de agentes
- **LangChain** - Framework para LLMs
- **Groq/OpenAI/Anthropic** - LLM providers
- **Jest** - Framework de testing (en sandbox)
- **TypeScript** - En sandbox para tests

## 🌐 Próximas Mejoras

1. **Integración con Jira**
   - Leer tickets directamente desde Jira
   - Actualizar estados en Jira
   - Agregar comentarios con resultados

2. **Persistencia en BD**
   - Guardar histórico de tickets
   - Métricas de éxito/fallos
   - Análisis de patrones

3. **Dashboard Web**
   - Visualizar tickets en progreso
   - Ver flujo en tiempo real
   - Descargar artefactos

4. **Webhooks**
   - Notificaciones por email/Slack
   - Triggers para acciones externas

5. **Multi-lenguaje**
   - Python, Go, Java, etc
   - No solo JavaScript/TypeScript

6. **Configuración Granular**
   - Ajustes por agente
   - Estrategias de reintentos personalizadas
   - Criterios de validación custom

## ❓ FAQ

**P: ¿Cuánto tiempo tarda procesar un ticket?**
R: Típicamente 2-3 minutos por ticket (depende de LLM). Con 10 tickets: ~30 min.

**P: ¿Puedo procesar tickets mientras el sistema está ejecutando?**
R: No recomendado. Espera a que termine un ciclo completo de `main.py`.

**P: ¿Qué pasa si falla el LLM?**
R: El sistema captura excepciones y marca el ticket como "error". Puedes reintentar manualmente.

**P: ¿Los tests realmente se ejecutan?**
R: Sí. El QA genera código TypeScript y ejecuta `npm test` en el sandbox con Jest.

**P: ¿Puedo ver el código generado antes de guardar?**
R: Actualmente no, pero puedes agregar logs en `main.py` para inspeccionar.

**P: ¿Cómo integro con Jira?**
R: Próxima versión. Por ahora usa JSON como fuente de verdad.

## 📞 Soporte

Para problemas:
1. Verificar logs en consola
2. Revisar archivo `.env` está bien configurado
3. Resguardar tickets con `scripts/reset_tickets.py`
4. Aumentar logs temporalmente en código

## 📄 Licencia

Proyecto abierto para uso educativo y comercial.

## ✨ Créditos

Sistema desarrollado para automatizar flujos ágiles con IA.
