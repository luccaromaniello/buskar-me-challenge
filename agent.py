# agent.py

import os
import time
import uuid
import requests
import subprocess

SERVER_URL = os.getenv("SERVER_URL", "http://localhost:8000")
MACHINE_NAME = os.getenv("MACHINE_NAME", "default-machine")
MACHINE_ID = os.getenv("MACHINE_ID", str(uuid.uuid4()))
INTERVAL = 300  # 5 minutos


def ping():
    try:
        resp = requests.post(
            f"{SERVER_URL}/register_machine",
            json={"id": MACHINE_ID, "name": MACHINE_NAME},
        )
        print(f"[PING] Status: {resp.status_code}")
    except Exception as e:
        print(f"[ERRO PING] {e}")


def get_pending_commands():
    try:
        resp = requests.get(f"{SERVER_URL}/commands/{MACHINE_ID}")
        if resp.status_code == 200:
            return resp.json()
        return []
    except Exception as e:
        print(f"[ERRO GET COMMANDS] {e}")
        return []


def send_result(command_id, output):
    try:
        resp = requests.post(
            f"{SERVER_URL}/commands/{command_id}/result", json={"output": output}
        )
        print(f"[RESULTADO] Comando {command_id} enviado. Status: {resp.status_code}")
    except Exception as e:
        print(f"[ERRO RESULTADO] {e}")


def execute_script(script_content):
    try:
        result = subprocess.run(
            script_content,
            shell=True,
            check=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        return result.stdout + "\n" + result.stderr
    except Exception as e:
        return f"[ERRO EXECUÇÃO] {e}"


def main():
    print(f"[INICIANDO AGENTE] {MACHINE_NAME} ({MACHINE_ID})")
    while True:
        ping()
        commands = get_pending_commands()
        for cmd in commands:
            print(f"[EXECUTANDO] Script: {cmd['script_name']}")
            output = execute_script(cmd["script_content"])
            send_result(cmd["id"], output)
        time.sleep(INTERVAL)


if __name__ == "__main__":
    main()
