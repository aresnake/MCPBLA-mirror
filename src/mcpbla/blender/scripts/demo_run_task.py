from mcpbla.blender.addon.bridge_client import BridgeClient


def main():
    client = BridgeClient()
    instruction = "create a cube and move it 2 meters up"
    result = client.run_task(instruction)
    print("Instruction:", instruction)
    print("Plan + execution result:")
    print(result)
    state = client.run_tool("get_scene_state", {})
    print("Scene state after run_task:")
    print(state)


if __name__ == "__main__":
    main()

