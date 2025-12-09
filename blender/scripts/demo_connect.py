from blender.addon.bridge_client import BridgeClient


def main():
    client = BridgeClient()
    result = client.ping()
    print("Ping response:", result)


if __name__ == "__main__":
    main()
