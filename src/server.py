import os
from mcp.server.fastmcp import FastMCP

mcp = FastMCP(name="mock filesystem", host="0.0.0.0", port=8000)

base_path = os.getcwd() + "/filesystem/"


@mcp.resource(
    "json://files",
    name="list_file",
    description="list all available files",
    mime_type="application/json",
)
def list_file() -> list[str]:
    return os.listdir(base_path)


@mcp.resource(
    "json://files/{file_name}",
    name="read_file",
    description="read file text content",
    mime_type="application/json",
)
def read_file(file_name: str) -> str:
    with open(base_path + file_name, "r") as f:
        return f.read()


@mcp.tool(name="write_file", description="overwrite file text content")
def write_file(file_name: str, text: str):
    with open(base_path + file_name, "w") as f:
        f.write(text)
        return {"code": 200}


if __name__ == "__main__":
    mcp.run(transport="sse")
