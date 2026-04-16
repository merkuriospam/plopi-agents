#!/usr/bin/env python
# main.py - Opciones de línea de comandos

"""
Opciones disponibles para procesar tickets:

1. Procesamiento normal (saltando ya completados):
   python main.py
   
   - Procesa solo tickets con status "pending"
   - Saltea tickets con status "completed" o "failed"
   - Ideal para procesar nuevos tickets

2. Reprocesar todos (incluyendo completados):
   python main.py --force
   o
   python main.py -f
   
   - Reprocesa TODOS los tickets, incluyendo completados
   - Útil para reintentar fallidos o revisar completados
   - Sobrescribe resultados anteriores

3. Solo reprocesar fallidos:
   python main.py --only-failed
   
   - Procesa solo tickets con status "failed"
   - Ignora "pending" y "completed"
   - Útil para reintentar solo los que fallaron

Combinaciones:
   python main.py --force --only-failed
   → Reprocesa solo los tickets fallidos

Ejemplos:

# Procesar nuevos tickets
$ python main.py
[SKIP] Ticket #1 - ya completado: Necesito una función...
[SKIP] Ticket #2 - ya completado: Crear función que...
[OK] Procesamiento completado

# Reintentar solo los fallidos
$ python main.py --only-failed
[PROCESANDO] Ticket #1 - Necesito una función...
[SKIP] Ticket #2 - no fallido: Crear función que...
[OK] Procesamiento completado

# Reprocesar TODO
$ python main.py --force
[PROCESANDO] Ticket #1 - Necesito una función...
[PROCESANDO] Ticket #2 - Crear función que...
[OK] Procesamiento completado
"""

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] in ["--help", "-h", "help"]:
        print(__doc__)
    else:
        print("Para ver opciones: python main.py --help")
