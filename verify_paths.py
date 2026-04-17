import json

with open('tickets.json', encoding='utf-8') as f:
    tickets = json.load(f)

print("\n" + "="*60)
print("VERIFICACION DE SANDBOX PATHS")
print("="*60)

for i, ticket in enumerate(tickets['tickets'], 1):
    print(f"\n[TICKET #{i}]")
    print(f"  Story: {ticket['story'][:50]}...")
    print(f"  sandbox_path: {ticket.get('sandbox_path', 'NO DEFINIDO')}")
    print(f"  server_path: {ticket.get('server_path', 'NO DEFINIDO')}")
    print(f"  Status: {ticket.get('status', 'NO DEFINIDO')}")

print("\n" + "="*60)
print("[OK] Verificación completada")
print("="*60 + "\n")
