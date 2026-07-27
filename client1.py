import asyncio
from langchain_mcp_adapters.client import MultiServerMCPClient
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.messages import ToolMessage , HumanMessage
import json


load_dotenv()



SERVERS={
    "math":{
        "transport":"stdio",
        "command":"C:/Users/Lenovo/AppData/Roaming/Python/Python314/Scripts/uv.exe",
        "args":[
            "run",
            "fastmcp",
            "run",
            "/Users/Lenovo/Desktop/MCP-Multi-Context-Protocol-/Math_MCP_Server/main.py"
        ]
    },
    'expense':{
        "transport":"streamable_http",
        "url":"https://test-antardhwani.fastmcp.app/mcp"
    }
}

async def main():
    client=MultiServerMCPClient(SERVERS)
    tools=await client.get_tools()
    named_tools={}
    for tool in tools :
        named_tools[tool.name]=tool

    llm=ChatGroq(model='llama-3.3-70b-versatile')
    llm_with_tools=llm.bind_tools(tools)

    prompt="What is the product of 799484 +94911 "
    response=await llm_with_tools.ainvoke(prompt)

    if not getattr(response ,"tool_calls",None):
        print("\n LLM : ",response.content)
        return 
    tool_messages=[]
    for tc in response.tool_calls:
        selected_tool=tc[0]['name']
        selected_tool_args=tc.get('args') or {}
        selected_tool_id=tc[0]['id']

        tool_result=await named_tools[selected_tool].ainvoke(selected_tool_args)

        tool_messages.append(ToolMessage(tool_call_id=selected_tool_id, content=json.dumps(result)))

    final_response=await llm_with_tools.ainvoke([prompt,response , tool_message])
    print(f"Final Response:,{final_response.content}")


if __name__=='__main__':
    asyncio.run(main())