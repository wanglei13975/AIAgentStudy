import os

# 1. 核心环境配置
# 你的特殊环境约束：必须设置 NO_PROXY 才能连上本地 Ollama
os.environ["NO_PROXY"] = "localhost,127.0.0.1"

# 导入 LangChain 组件
from langchain_ollama import ChatOllama, OllamaEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate
# 专门用于加载 .txt 文件的加载器
from langchain_community.document_loaders import TextLoader

print("=== 初始化 RAG 系统 ===")

# 2. 加载本地文件
# 这一步相当于把书从书架上拿下来，打开看
# encoding="utf-8" 非常重要，否则读取中文 txt 可能会乱码
loader = TextLoader("./company_policy.txt", encoding="utf-8")
docs = loader.load()
print(f"成功加载文件，共 {len(docs)} 个文档对象")

# 3. 文本切分 (Chunking)
# 为什么要切分？
# 1. 模型一次读不了太长的书（上下文限制）。
# 2. 只有切碎了，检索时才能精准定位到“某一条规定”，而不是把整本书丢给模型。
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=200,    # 每个切片大约 200 个字符
    chunk_overlap=50   # 切片之间重叠 50 个字符（为了保持句子连贯性，防止把一句话切断）
)
splits = text_splitter.split_documents(docs)
print(f"文档已切分为 {len(splits)} 个片段。")

# 4. 向量化与存储
# 我们复用 qwen2.5:14b 模型来充当“翻译官”
# 它的工作不是生成文字，而是把文字转化成一串数字（向量）
embeddings = OllamaEmbeddings(model="qwen2.5:14b")

print("正在构建向量索引 (FAISS)... 这可能需要几秒钟")

# FAISS 是 Facebook 开发的向量数据库引擎
# .from_documents 做了两件事：
# 1. 调用 embeddings 把上面的 splits 全变成向量。
# 2. 建立索引，方便快速查找。
vectorstore = FAISS.from_documents(splits, embeddings)

# 把数据库变成一个“检索器”接口，方便后续链调用
retriever = vectorstore.as_retriever()

# 5. 构建模型与链
# 初始化负责对话的大模型
llm = ChatOllama(
    model="qwen2.5:14b",
    temperature=0, # 严谨模式：RAG 场景下我们不希望模型发挥创造力，而是忠实于原文
    timeout=600.0
)

# 定义系统提示词
# {context} 是一个特殊占位符，LangChain 会自动把检索到的文档片段填在这里
system_prompt = (
    "你是一个行政助手。必须严格基于以下上下文回答问题。"
    "如果上下文里没有提到，请回答'制度中未说明'。"
    "\n\n"
    "【上下文信息】:\n"
    "{context}"
)

prompt = ChatPromptTemplate.from_messages([
    ("system", system_prompt),
    ("human", "{input}"),
])

# 组合链条 1：文档处理链 (把文档塞进 Prompt)
question_answer_chain = create_stuff_documents_chain(llm, prompt)

# 组合链条 2：完整的 RAG 链 (检索 + 文档处理)
# 流程：用户提问 -> retriever 找文档 -> question_answer_chain 生成回答
rag_chain = create_retrieval_chain(retriever, question_answer_chain)

# 6. 交互式问答循环
print("\n=== 系统就绪，开始提问 (输入 'exit' 退出) ===")

while True:
    user_input = input("\n请提问: ")
    # 处理退出逻辑
    if user_input.lower() in ["exit", "quit", "q"]:
        break
    
    if not user_input.strip():
        continue

    print("Agent 正在查阅规章制度...")
    try:
        # invoke 触发整个 RAG 链条
        response = rag_chain.invoke({"input": user_input})
        
        # 打印结果
        # response 包含三个 key: 'input', 'context', 'answer'
        # 我们只需要打印 'answer'
        print(f"回答: {response['answer']}")
    except Exception as e:
        print(f"发生错误: {e}")

print("再见！")