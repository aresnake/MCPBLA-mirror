"""Minimal end-to-end stub."""
from mcpbla.server.mcp_server import create_app


def main():
    app = create_app()
    print(app.title)


if __name__ == "__main__":
    main()

