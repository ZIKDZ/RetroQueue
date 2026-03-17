import docker
import time

client = docker.from_env()

CSGO_IMAGE = "cm2network/csgo:sourcemod"
STEAM_TOKEN = "YOUR_TOKEN_HERE"  # replace this

PORT = 27015
MAP = "de_dust2"

def start_container():
    print("[INFO] Starting CS:GO server...")

    try:
        container = client.containers.run(
            CSGO_IMAGE,
            detach=True,
            network_mode="host",
            environment={
                "SRCDS_TOKEN": STEAM_TOKEN,
                "SRCDS_PORT": str(PORT),
                "SRCDS_STARTMAP": MAP,
                "SRCDS_MAXPLAYERS": "10",
                "SRCDS_GAMETYPE": "0",
                "SRCDS_GAMEMODE": "1",
                "SRCDS_LAN": "0",
                "SRCDS_TICKRATE": "128",
                "SRCDS_HOSTNAME": f"Test Server {PORT}",
            },
            volumes={
                "/home/ilias/csgo-server/server": {
                    "bind": "/home/steam/csgo-dedicated",
                    "mode": "rw"
                }
            },
            name=f"csgo_test_{PORT}",
            remove=False  # keep container after stop (for debugging)
        )

        print(f"[SUCCESS] Container started: {container.id}")
        return container

    except Exception as e:
        print(f"[ERROR] Failed to start container: {e}")
        return None


def stop_container(container):
    print("[INFO] Stopping container...")
    try:
        container.stop()
        container.remove()
        print("[SUCCESS] Container stopped and removed")
    except Exception as e:
        print(f"[ERROR] Failed to stop container: {e}")


if __name__ == "__main__":
    container = start_container()

    if container:
        print("[INFO] Server is running. Try connecting now.")
        print(f"connect YOUR_IP:{PORT}")

        try:
            # Keep it alive for testing
            time.sleep(120)  # 2 minutes
        finally:
            stop_container(container)