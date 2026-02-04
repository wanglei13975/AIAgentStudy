import os

# 1. 网络与环境配置
os.environ["NO_PROXY"] = "localhost,127.0.0.1"

from langchain_ollama import ChatOllama, OllamaEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.documents import Document

# 2. 模拟加载“私有数据”
# 假设这是公司内网的一份机密文档，模型训练时绝对没见过
raw_text = """
【机密文档：代号 "Project X" 技术规格书】
1. 项目概述："Project X" 是公司 2024 年开发的下一代全息投影设备。
2. 核心参数：
   - 亮度：5000 流明
   - 分辨率：16K 超清
   - 续航：采用核钻电池，单次充电可续航 5 年。
3. 负责人：首席科学家 Dr. Brown。
4. 注意事项：该设备在温度低于 -273 度时会停止工作，且不能接触强磁场。
5. 发布日期：预计 2025 年 12 月 31 日。
6. 暗号：芝麻开门。
"""

# 将文本封装为 Document 对象
docs = [Document(page_content=raw_text)]

# 3. 文本切分
# 将长文本切成小块，方便检索
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=100,  # 每一块的大小
    chunk_overlap=20 # 块与块之间的重叠量，防止切断上下文
)
splits = text_splitter.split_documents(docs)
print(f"文档已切分为 {len(splits)} 个片段。")

# 4. 初始化模型
# 对话模型
llm = ChatOllama(
    model="qwen2.5:14b",
    temperature=0,
    timeout=600.0
)

# 向量化模型 (Embedding Model)
# 我们直接复用 qwen2.5 来做向量化，虽然比专用小模型慢一点，但不需要下载新模型
embeddings = OllamaEmbeddings(
    model="qwen2.5:14b",
)

print("正在生成向量索引 (这可能需要几秒钟)...")

# 5. 构建向量数据库 (Vector Store)
# 使用 FAISS 将切分后的文本转换成向量并存入内存
vectorstore = FAISS.from_documents(documents=splits, embedding=embeddings)

# 6. 构建检索器 (Retriever)
retriever = vectorstore.as_retriever()

# 7. 构建 RAG 链
# 7.1 定义 Prompt：告诉 LLM 必须基于 context 回答
system_prompt = (
    "你是一个企业助手。请根据下方提供的【上下文信息】回答用户的问题。"
    "如果你在上下文中找不到答案，就诚实地说不知道，不要编造。"
    "\n\n"
    "【上下文信息】:\n"
    "{context}"
)

prompt = ChatPromptTemplate.from_messages([
    ("system", system_prompt),
    ("human", "{input}"),
])

# 7.2 创建文档组合链 (将检索到的片段塞进 Prompt)
question_answer_chain = create_stuff_documents_chain(llm, prompt)

# 7.3 创建最终的检索增强链
rag_chain = create_retrieval_chain(retriever, question_answer_chain)

# 8. 测试提问
# print("\n=== 测试 1: 询问文档内的具体参数 ===")
# query1 = "Project X 的续航时间是多久？由谁负责？"
# print(f"用户提问: {query1}")
# response1 = rag_chain.invoke({"input": query1})
# print(f"Agent回答: {response1['answer']}")

# print("\n=== 测试 2: 询问文档外的内容 (测试幻觉) ===")
# query2 = "Project X 的售价是多少？"
# print(f"用户提问: {query2}")
# response2 = rag_chain.invoke({"input": query2})
# print(f"Agent回答: {response2['answer']}")
print("\n=== 测试 3: 询问文档内的内容 (自定义) ===")
query2 = "暗号是什么？"
print(f"用户提问: {query2}")
response2 = rag_chain.invoke({"input": query2})
print(f"Agent回答: {response2['answer']}")