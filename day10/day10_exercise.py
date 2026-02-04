import os
# 1. 环境配置
os.environ["NO_PROXY"] = "localhost,127.0.0.1"

from langchain_ollama import ChatOllama, OllamaEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import TextLoader
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate, PromptTemplate
from langchain_core.tools import tool
from langchain.agents import create_react_agent, AgentExecutor
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory

print("=== 正在启动全能 Agent 系统 ===")
print("1. 正在加载并索引知识库 (这可能需要几秒钟)...")

# --- RAG 初始化流水线 (复用 Day 9 的逻辑) ---
# 加载
loader = TextLoader("./it_manual.txt", encoding="utf-8")
docs = loader.load()

# 切分
text_splitter = RecursiveCharacterTextSplitter(chunk_size=200, chunk_overlap=50)
splits = text_splitter.split_documents(docs)

# 向量化 (Embeddings)
embeddings = OllamaEmbeddings(model="qwen2.5:14b")
vectorstore = FAISS.from_documents(splits, embeddings)
retriever = vectorstore.as_retriever()

# 构建 RAG 链 (这个链条稍后会在工具里被触发)
# 注意：这里我们用一个临时的 LLM 实例专门给 RAG 用，或者复用主 LLM 也可以
rag_llm = ChatOllama(model="qwen2.5:14b", temperature=0, timeout=600.0)

rag_system_prompt = (
    "你是一个查询助手。请严格基于以下上下文回答问题。"
    "如果上下文中没有答案，请回答'未找到相关信息'。"
    "\n\n"
    "{context}"
)
rag_prompt = ChatPromptTemplate.from_messages([
    ("system", rag_system_prompt),
    ("human", "{input}"),
])
question_answer_chain = create_stuff_documents_chain(rag_llm, rag_prompt)
# 这个 rag_chain 就是我们将要封装的核心对象
rag_chain = create_retrieval_chain(retriever, question_answer_chain)

print("   -> 知识库索引完成！")

# --- 定义工具集 ---

@tool
def lookup_it_manual(query: str) -> str:
    """
    查阅 IT 运维手册的工具。
    当用户询问 Wifi、VPN、打印机等 IT 问题时使用本工具。
    参数 query 是具体的查询问题。
    """
    # 兼容性处理：如果模型有时候发疯传了 None 进来
    if not query: 
        return "请提供具体的查询问题。"
    
    try:
        # 这里调用我们在第一步里准备好的 RAG 链
        result = rag_chain.invoke({"input": query})
        return result["answer"]
    except Exception as e:
        return f"查询出错: {e}"

@tool
def get_current_weather(dummy_arg: str = "") -> str:
    """
    查询天气的工具。当用户问天气时使用。
    """
    return "今天天气晴朗，气温 25 度，适合穿紫色衣服。"

@tool
def restart_router(dummy_arg: str = "") -> str:
    """
    当用户说“网断了”或者“重启路由器”时，返回“路由器正在重启... 重启成功！。
    """
    return "路由器正在重启... 重启成功！"

# 这里的 tools 列表包含了 RAG 工具和 普通工具
tools = [lookup_it_manual, get_current_weather, restart_router]

# --- 构建 ReAct Agent ---

# 主 LLM
llm = ChatOllama(model="qwen2.5:14b", temperature=0, timeout=600.0)

# ReAct Prompt 模板 (包含 chat_history)
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

agent = create_react_agent(llm, tools, prompt)

# 关闭 verbose 以避免 v0.3 的打印 Bug
agent_executor = AgentExecutor(
    agent=agent, 
    tools=tools, 
    verbose=False, 
    handle_parsing_errors=True
)

# 加入记忆功能
store = {}
def get_session_history(session_id: str):
    if session_id not in store:
        store[session_id] = ChatMessageHistory()
    return store[session_id]

agent_with_memory = RunnableWithMessageHistory(
    agent_executor,
    get_session_history,
    input_messages_key="input",
    history_messages_key="chat_history",
)

# --- 运行交互 ---
print("\n=== 全能 Agent 就绪 (输入 'exit' 退出) ===")
print("你可以问：'我叫小明' (测试记忆)")
print("也可以问：'公司周五要穿什么？' (测试 RAG 工具)")
print("也可以问：'今天天气咋样？' (测试普通工具)")

session_id = "user_test_001"

while True:
    user_input = input("\n请提问: ")
    if user_input.lower() in ["exit", "quit", "q"]:
        break
    
    if not user_input.strip():
        continue

    print(f">> Agent 正在思考 (Session: {session_id})...")
    try:
        response = agent_with_memory.invoke(
            {"input": user_input},
            config={"configurable": {"session_id": session_id}}
        )
        print(f"回答: {response['output']}")
    except Exception as e:
        print(f"发生错误: {e}")