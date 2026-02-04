import os

# 1. 环境配置
os.environ["NO_PROXY"] = "localhost,127.0.0.1"

from langchain_ollama import ChatOllama
from langchain.agents import create_react_agent, AgentExecutor
from langchain_core.tools import tool
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables.history import RunnableWithMessageHistory

# 【新组件】导入 SQL 历史记录管理模块
from langchain_community.chat_message_histories import SQLChatMessageHistory

# 2. 初始化模型
llm = ChatOllama(
    model="qwen2.5:14b", # 或者 7b
    temperature=0,
    timeout=600.0,
)

# 3. 定义简单工具
@tool
def calculate_salary(dummy_arg: str = "") -> str:
    """
    计算工资的工具。当用户问工资、薪水时使用。
    """
    return "根据数据库，你的月薪是 50,000 元 (税前)。"

tools = [calculate_salary]

# 4. 定义 Prompt (标准 ReAct)
template = """Answer the following questions as best you can. You have access to the following tools:

{tools}

Use the following format:

Question: the input question you must answer
Thought: you should always think about what to do
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I now know the final answer
Final Answer: the final answer to the original input question

Begin!

Previous conversation history:
{chat_history}

Question: {input}
Thought:{agent_scratchpad}"""

prompt = PromptTemplate.from_template(template)

# 5. 构建 Agent
agent = create_react_agent(llm, tools, prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=False, handle_parsing_errors=True)

# 6. 【核心修改】定义持久化记忆获取函数
# 以前我们用 store = {}，现在我们连接数据库

def get_session_history(session_id: str):
    """
    根据 session_id 从本地 SQLite 数据库中加载聊天记录。
    如果数据库文件不存在，会自动创建。
    """
    # connection_string 指向当前目录下的 memory.db 文件
    return SQLChatMessageHistory(
        session_id=session_id,
        connection="sqlite:///memory.db" 
    )

# 7. 包装 Agent
agent_with_memory = RunnableWithMessageHistory(
    agent_executor,
    get_session_history,
    input_messages_key="input",
    history_messages_key="chat_history",
)

# 8. 交互逻辑
print("=== 持久化记忆 Agent (即使重启程序，我也记得你) ===")
print("当前 Session ID: user_001")
print("你可以先告诉我要记住什么，然后退出程序，再重新运行看看。")

session_id = "user_001"

while True:
    print("=== 持久化记忆 Agent (即使重启程序，我也记得你) ===")
    #请输入你的姓名
    name = input("请输入你的姓名: ")
    session_id = name
    user_input = input("\n请提问 (输入 'exit' 退出): ")
    if user_input.lower() in ["exit", "quit", "q"]:
        break
    
    if not user_input.strip():
        continue

    print(f">> Agent 正在思考...")
    try:
        response = agent_with_memory.invoke(
            {"input": user_input},
            config={"configurable": {"session_id": session_id}}
        )
        print(f"回答: {response['output']}")
    except Exception as e:
        print(f"发生错误: {e}")