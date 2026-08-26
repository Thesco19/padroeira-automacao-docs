import subprocess
import json

def get_stats():
    # Coleta dados reais dos containers
    cmd = "docker stats --no-stream --format '{{json .}}'"
    result = subprocess.check_output(cmd, shell=True).decode('utf-8')
    return [json.loads(line) for line in result.splitlines()]

# Monta o relatório para a IA
relatorio = {
    "host": "MacMini-Paulo",
    "status_containers": get_stats()
}
print(json.dumps(relatorio, indent=2))
