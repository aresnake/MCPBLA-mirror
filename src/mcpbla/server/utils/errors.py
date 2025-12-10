class MCPError(Exception):
    """Base exception for MCP server errors."""


class ToolExecutionError(MCPError):
    """Raised when a tool fails during execution."""
