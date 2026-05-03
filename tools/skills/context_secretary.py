import os
import sys

# Hozzáadjuk az ENVIRONMENT_SETUP mappát a path-hoz
base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(os.path.join(base_dir, "ENVIRONMENT_SETUP"))

try:
    from agent_memory_manager import MEMORY_FILE, REPO_NAME
except ImportError as e:
    print(f"Hiba a memória manager betöltésekor: {e}")
    sys.exit(1)

def sync_memory_to_vps():
    if not os.path.exists(MEMORY_FILE):
        print(f"Nincs mit szinkronizálni, {MEMORY_FILE} nem létezik.")
        return

    # Az MCP bridge importálása
    bridge_path = os.path.join(os.path.dirname(__file__), "mcp_bridge_tool.py")
    if not os.path.exists(bridge_path):
        print("MCP híd nem található a szinkronizációhoz.")
        return

    try:
        with open(MEMORY_FILE, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"Hiba a memória olvasásakor: {e}")
        return

    import subprocess
    import json
    import base64

    # Base64 a tartalomra a bash/json escape problémák elkerülésére
    b64_content = base64.b64encode(content.encode('utf-8')).decode('utf-8')
    vps_target_dir = f"/home/misi/Jules_mx/memory_offload/{REPO_NAME}"
    vps_target_file = f"{vps_target_dir}/agent_memory.jsonl"

    # 1. Hozzuk létre a mappát a VPS-en (execute_bash)
    cmd_mkdir = f"mkdir -p {vps_target_dir}"
    args_mkdir = json.dumps({"command": cmd_mkdir})

    print(f"📡 {REPO_NAME} memória mappa létrehozása a VPS-en...")
    subprocess.run(
        [sys.executable, bridge_path, "--tool", "execute_bash", "--args", args_mkdir],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
    )

    # 2. Írjuk ki a fájlt (execute_bash a base64 tartalommal)
    cmd_write = f"echo '{b64_content}' | base64 -d > {vps_target_file}"
    args_write = json.dumps({"command": cmd_write})

    print(f"☁️ {REPO_NAME} memória szinkronizálása a VPS-re: {vps_target_file}...")
    res = subprocess.run(
        [sys.executable, bridge_path, "--tool", "execute_bash", "--args", args_write],
        capture_output=True, text=True
    )

    if res.returncode == 0:
        print("✅ Felhő-szinkronizáció kész.")
    else:
        print(f"❌ Szinkronizációs hiba: {res.stderr}")

if __name__ == "__main__":
    sync_memory_to_vps()
