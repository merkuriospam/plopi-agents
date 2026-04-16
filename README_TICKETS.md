# Sistema de Procesamiento Automático de Tickets Ágiles

## Descripción General

El sistema procesa tickets desde un archivo JSON, ejecutando un flujo completo de agentes ágiles:
1. **Task Creator** - Genera tareas técnicas desde la story
2. **Reviewer** - Valida tasks (fase 1) y código (fase 2)
3. **Developer** - Implementa código según las tasks
4. **QA** - Crea y ejecuta tests validando cada task
5. **DevOps** - Genera servidor Express listo para deploy

## Estructura del Archivo JSON

El archivo `tickets.json` debe contener un array de tickets con esta estructura:

```json
{
  "tickets": [
    {
      "story": "Descripción de la funcionalidad a implementar",
      "tasks": [],
      "tasks_review": null,
      "tasks_approved": false,
      "tasks_attempts": 0,
      "code": null,
      "review": null,
      "approved": false,
      "review_attempts": 0,
      "tests": null,
      "tests_passed": null,
      "tests_output": null,
      "qa_attempts": 0,
      "server_path": null,
      "deployed": false,
      "status": "pending"
    }
  ]
}
```

## Campos del Ticket

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `story` | string | Descripción de la funcionalidad (REQUERIDO) |
| `tasks` | list[str] | Tareas técnicas generadas por Task Creator |
| `tasks_review` | string | Feedback del Reviewer sobre tasks |
| `tasks_approved` | bool | Si las tasks fueron aprobadas |
| `tasks_attempts` | int | Contador de reintentos (máx 3) |
| `code` | string | Código JavaScript generado |
| `review` | string | Feedback del Reviewer sobre código |
| `approved` | bool | Si el código fue aprobado |
| `review_attempts` | int | Contador de reintentos (máx 3) |
| `tests` | string | Tests TypeScript generados |
| `tests_passed` | bool | Si todos los tests pasaron |
| `tests_output` | string | Logs de ejecución de tests |
| `qa_attempts` | int | Contador de reintentos (máx 3) |
| `server_path` | string | Ruta donde se guardó el servidor |
| `deployed` | bool | Si el servidor fue generado |
| `status` | string | Estado final: "pending", "completed", "failed", "error" |

## Cómo Usar

### 1. Preparar tickets.json

Crear un archivo `tickets.json` con los tickets que deseas procesar:

```json
{
  "tickets": [
    {
      "story": "Crear función que valide emails",
      "tasks": [],
      "tasks_review": null,
      "tasks_approved": false,
      "tasks_attempts": 0,
      "code": null,
      "review": null,
      "approved": false,
      "review_attempts": 0,
      "tests": null,
      "tests_passed": null,
      "tests_output": null,
      "qa_attempts": 0,
      "server_path": null,
      "deployed": false,
      "status": "pending"
    }
  ]
}
```

### 2. Ejecutar el procesamiento

**Opción 1: Procesar solo nuevos tickets (recomendado)**

```bash
python main.py
```

✅ Procesa tickets con status "pending"
✅ Salta "completed" y "failed" automáticamente
✅ Rápido y eficiente

**Opción 2: Reprocesar solo fallidos**

```bash
python main.py --only-failed
```

✅ Procesa solo tickets con status "failed"
✅ Salta "pending" y "completed"
✅ Útil para reintentar después de correcciones

**Opción 3: Reprocesar todos**

```bash
python main.py --force
```

✅ Reprocesa TODOS los tickets
✅ Incluyendo "completed" y "failed"
✅ Sobrescribe resultados anteriores (úsalo con cuidado)

**Opción 4: Reprocesar fallidos con force**

```bash
python main.py --force --only-failed
```

✅ Reprocesa solo "failed" incluso si están marcados diferente

### 3. Revisar los resultados

Después de la ejecución, el archivo `tickets.json` contendrá:
- Todas las tasks generadas
- El código implementado
- Los tests creados y sus resultados
- El estado final de cada ticket

## Ejemplo de Ejecución

```
[OK] Cargados 2 tickets desde tickets.json

============================================================
[1/2] Procesando: Crear función que valide emails
============================================================

[TASK_CREATOR] Tareas generadas: 6
[REVIEWER] Tasks validadas: APROBADO
[DEVELOPER] Código implementado
[REVIEWER] Código validado: APROBADO
[QA] 6 tests generados y ejecutados
[QA] Tests PASARON
[DEVOPS] Servidor generado: C:\dev\temp\pipa\server.ts

[SUMMARY] TICKET #1
  Story: Crear función que valide emails...
  Tasks: 6 generadas
  Tasks Aprobadas: [OK] SI
  Codigo Aprobado: [OK] SI
  Tests Pasados: [OK] SI
  Deployed: [OK] SI
  Server: C:\dev\temp\pipa\server.ts

...

[OK] Procesamiento completado
[OK] Actualizados 2 tickets en tickets.json
```

## Configuración Requerida

Asegúrate de tener configuradas las variables de entorno en `.env`:

```bash
# LLM Configuration
LLM_PROVIDER=groq
LLM_MODEL=llama-3.3-70b-versatile
LLM_API_KEY=your_api_key_here

# Sandbox TypeScript
TS_SANDBOX_PATH=C:\dev\temp\pipa
```

## Reintentos Automáticos

El sistema reintentar automáticamente hasta 3 veces en cada fase:
- **Tasks**: Si el Reviewer rechaza las tasks
- **Código**: Si el Reviewer rechaza el código
- **Tests**: Si los tests fallan

Después de 3 reintentos, continúa al siguiente paso o marca como error.

## Estados Posibles de Tickets

- **pending**: Ticket sin procesar aún
- **completed**: Ticket procesado exitosamente (tests pasaron)
- **failed**: Ticket procesado pero tests fallaron
- **error**: Error durante el procesamiento

## Integración con Jira (Futuro)

En el futuro, el sistema podrá:
1. Leer tickets directamente desde Jira
2. Actualizar el estado del ticket en Jira después del procesamiento
3. Agregar comentarios con los resultados
4. Generar enlaces a los servidores deployed

## Archivos del Sistema

```
plopi-agents/
├── main.py                      # Orquestador principal
├── agents/
│   ├── task_creator.py         # Genera tasks desde story
│   ├── developer.py            # Implementa código
│   ├── reviewer.py             # Valida tasks y código
│   ├── qa.py                   # Genera y ejecuta tests
│   └── devops.py               # Genera servidor
├── models/
│   └── ticket.py               # Estructura Ticket TypedDict
├── config/
│   └── llm.py                  # Configuración de LLM
├── utils/
│   └── ticket_manager.py       # Lee/escribe JSON de tickets
├── tickets.json                # Archivo con tickets a procesar
└── .env                        # Configuración (API keys, paths)
```

## Troubleshooting

### Error: "Archivo tickets.json no existe"
- Crear el archivo con la estructura correcta
- O ejecutar `python main.py` una vez para que genere el archivo de ejemplo

### Error: "Se alcanzó el límite de iteraciones"
- Aumentar el `recursion_limit` en `main.py` (línea ~108)
- Revisar los logs para identificar loops infinitos

### Tests fallan constantemente
- Revisar que el LLM esté generando código válido
- Aumentar el timeout de npm test en `agents/qa.py` (línea ~60)
- Revisar la configuración del sandbox en `.env`

## Próximas Mejoras

1. Integración con Jira API
2. Persistencia en base de datos
3. Dashboard web para visualizar progreso
4. Webhooks para notificaciones
5. Soporte para múltiples lenguajes de programación
6. Configuración granular de reintentos por agente
