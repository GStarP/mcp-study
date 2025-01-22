from mcp import ClientSession
from mcp.client.sse import sse_client


async def run():
    async with sse_client(url="http://localhost:8000/sse") as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            print("Initialized")

            """
            Test Key Concepts: Resources & Tools
            """
            resources = await session.list_resources()
            print("Resources:", resources)

            tools = await session.list_tools()
            print("Tools:", tools)

            """
            Read Resources
            """
            file_list = await session.read_resource("json://files")
            print("File list:", file_list)

            file_name = "example.js"
            file_content = await session.read_resource(f"json://files/{file_name}")
            print(f"{file_name}: {file_content}")

            """
            Call Tools
            """
            tool_name = "write_file"
            result = await session.call_tool(
                tool_name,
                {
                    "file_name": file_name,
                    "text": "function example() {\n"
                    'print("run example");\n'
                    "}\n"
                    "example();",
                },
            )
            print(f"call {tool_name}: {result}")


if __name__ == "__main__":
    import asyncio

    asyncio.run(run())
