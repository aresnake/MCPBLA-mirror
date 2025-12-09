from blender.addon.bridge_client import BridgeClient


def main():
    client = BridgeClient()
    result = client.send_dummy_snapshot()
    print("Snapshot response:", result)


if __name__ == "__main__":
    main()
