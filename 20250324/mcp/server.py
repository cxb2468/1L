from mcp.server.fastmcp import FastMCP

# 创建MCP服务器实例
mcp = FastMCP("My Simple Server")


# 定义一个工具：加法函数
@mcp.tool()
def add(a: int, b: int) -> int:
    """将两个整数相加"""
    return a + b + 67


if __name__ == "__main__":
    # 直接运行服务器
    mcp.run()