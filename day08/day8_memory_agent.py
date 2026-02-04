import os

# 1. 网络与环境配置 (必须在 import langchain 之前设置)
# 针对公司内网环境，确保能连上本地 Ollama
os.environ["NO_PROXY"] = "localhost,127.0.0.1"

from langchain_ollama import ChatOllama
from langchain.agents import create_react_agent, AgentExecutor
from langchain_core.tools import tool
from langchain_core.prompts import PromptTemplate
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory

# 2. 初始化模型 (遵守超时与模型约束)
llm = ChatOllama(
    model="qwen2.5:14b",
    temperature=0,
    timeout=600.0,  # 关键设置
)

# 3. 定义工具 (Dummy Tool)
@tool
def check_server_status(dummy_arg: str = "") -> str:
    """
    检查服务器状态的工具。
    如果是查询 'db_server'，返回 'Online'。
    其他情况返回 'Unknown'。
    """
    # 兼容模型可能传入 None 或空字符串的情况
    query = dummy_arg if dummy_arg else ""
    
    if "db" in query.lower():
        return "Database Server is ONLINE (CPU: 15%)"
    return "Web Server is ONLINE (CPU: 5%)"

tools = [check_server_status]

# 4. 定义 ReAct Prompt 模板 (关键步骤)
# 我们需要在模板中显式加入 {chat_history}
# 这是一个经典的 ReAct 模板，适配 Qwen
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

# 5. 构建 Agent (Legacy ReAct)
agent = create_react_agent(llm, tools, prompt)

# 创建 AgentExecutor
agent_executor = AgentExecutor(
    agent=agent, 
    tools=tools, 
    verbose=True,
    handle_parsing_errors=True # 防止模型输出格式微小错误导致崩溃
)

# 6. 加入记忆功能 (RunnableWithMessageHistory)
# 创建一个字典来存储不同 session 的历史记录 (内存中)
store = {}

def get_session_history(session_id: str):
    if session_id not in store:
        store[session_id] = ChatMessageHistory()
    return store[session_id]

# 包装 AgentExecutor
agent_with_memory = RunnableWithMessageHistory(
    agent_executor,
    get_session_history,
    input_messages_key="input",
    history_messages_key="chat_history", # 对应 Prompt 中的 {chat_history}
)

# 7. 测试对话
print("=== 开始第一轮对话 (自我介绍) ===")
response1 = agent_with_memory.invoke(
    {"input": "你好，我是工程师小王。请帮我检查一下数据库服务器的状态。"},
    config={"configurable": {"session_id": "session_123"}}
)
print(f"Agent回答: {response1['output']}\n")

print("=== 开始第二轮对话 (测试记忆) ===")
# 这里我们不再提名字，也不提具体要查什么服务器（如果它记得上下文）
# 但为了测试名字记忆，我们直接问它
response2 = agent_with_memory.invoke(
    {"input": "我刚才说我是谁？还有，web服务器状态怎么样？"},
    config={"configurable": {"session_id": "session_123"}}
)
print(f"Agent回答: {response2['output']}")