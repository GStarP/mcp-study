import json
import os
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import HumanMessage, BaseMessage
from mcp import ClientSession
from mcp.client.sse import sse_client
from langchain_core.tools import tool
from dotenv import load_dotenv


load_dotenv()


async def convert_mcp_client_to_langchain_tools(mcp_client: ClientSession):
    """
    TODO real impl
    Convert mcp client resources/tools to langchain tools.
    """

    @tool
    async def list_file() -> list[str]:
        """
        list all files
        """
        res = await mcp_client.read_resource("json://files")
        return json.loads(res.contents[0].text)

    @tool
    async def read_file(file_name: str) -> str:
        """
        read file text content
        """
        res = await mcp_client.read_resource(f"json://files/{file_name}")
        return res.contents[0].text

    @tool
    async def write_file(file_name: str, text: str) -> str:
        """
        write file text content
        """
        res = await mcp_client.call_tool(
            "write_file", {"file_name": file_name, "text": text}
        )
        ret = json.loads(res.content[0].text)
        if ret["code"] == 200:
            return "success"
        else:
            return "fail"

    tools = [list_file, read_file, write_file]

    return tools


async def run():
    async with sse_client(url="http://localhost:8000/sse") as (read, write):
        async with ClientSession(read, write) as mcp_client:
            await mcp_client.initialize()
            print("mcp client initialized")

            tools = await convert_mcp_client_to_langchain_tools(mcp_client)
            print("tools prepared")

            llm = ChatOpenAI(
                # ! deepseek will cause agent loop
                # base_url="https://api.deepseek.com/v1",
                # model="deepseek-chat",
                model="gpt-4o-mini",
                temperature=0.3,
            )

            system_prompt = "You are a coding assistant. The user provides you with some tools to access workspace, use these tools to help user solve problems. "
            agent_executor = create_react_agent(
                model=llm, tools=tools, state_modifier=system_prompt
            )

            res = await agent_executor.ainvoke(
                {
                    "messages": [
                        HumanMessage(
                            content="what's wrong with my main.js file? it cannot print anything! please correct the code for me."
                        ),
                    ]
                },
                debug=True,
            )

            messages: list[BaseMessage] = res["messages"]
            for m in messages:
                m.pretty_print()


if __name__ == "__main__":
    import asyncio

    asyncio.run(run())
