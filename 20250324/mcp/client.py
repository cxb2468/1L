import asyncio
from mcp.client.stdio import stdio_client
from mcp import ClientSession, StdioServerParameters


async def main():
    # 定义服务器参数（通过stdio连接到本地Python脚本）
    server_params = StdioServerParameters(
        command="python",
        args=["server.py"]
    )
    # 创建客户端连接
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # 初始化连接
            await session.initialize()

            # 调用服务器的"add"工具
            result = await session.call_tool(
                name="add",
                arguments={"a": 1, "b": 2}
            )
            print("Result:", result)
            if not result.isError:
                print(result.content[0].text)


asyncio.run(main())
input('')