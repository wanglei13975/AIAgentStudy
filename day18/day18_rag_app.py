import os

# --- 核心修复：强制绕过公司代理 ---
# 1. 设置不走代理的名单
os.environ["NO_PROXY"] = "localhost,127.0.0.1,0.0.0.0"
# 2. (可选) 如果上面不管用，可以直接暴力删除代理变量
# (这只会影响当前脚本，不会影响你系统的其他软件)
if "HTTP_PROXY" in os.environ:
    del os.environ["HTTP_PROXY"]
if "HTTPS_PROXY" in os.environ:
    del os.environ["HTTPS_PROXY"]

# --- 下面才是其他的 import ---
import tempfile
import streamlit as st
from langchain_ollama import ChatOllama, OllamaEmbeddings
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

# 1. 页面设置
st.set_page_config(page_title="Day 18 - PDF 知识库助手", page_icon="📚")
st.title("📚 PDF 智能问答助手")

# 2. 侧边栏：文件上传
with st.sidebar:
    st.header("📄 文档上传")
    uploaded_file = st.file_uploader("请上传 PDF 文件", type=["pdf"])
    st.markdown("---")
    st.markdown("💡 **提示**：上传后，AI 会自动学习文档内容，然后你就可以提问了。")

# 3. 核心逻辑：处理 PDF (带缓存！)
# @st.cache_resource 是今天的 MVP。
# 它会检查：如果 uploaded_file 对象没变，就直接返回上次算好的 retriever，不跑函数体。
@st.cache_resource
def process_uploaded_file(uploaded_file):
    if not uploaded_file:
        return None
    
    # A. 因为 PyPDFLoader 需要一个真实的文件路径，
    # 而 Streamlit 上传的是内存字节流，所以我们要创建一个临时文件
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
        tmp_file.write(uploaded_file.getvalue())
        tmp_file_path = tmp_file.name

    # B. 标准 RAG 流程 (Day 10 的复习)
    loader = PyPDFLoader(tmp_file_path)
    docs = loader.load()
    
    # 删掉临时文件 (保持整洁)
    os.remove(tmp_file_path)
    
    # C. 切分
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    splits = text_splitter.split_documents(docs)
    
    # D. 向量化 & 存储
    # 注意：这里我们用 Chroma 的内存模式 (不持久化到磁盘)，因为每次重启 App 清空也没关系
    embeddings = OllamaEmbeddings(model="qwen2.5:14b") # 或者 nomic-embed-text
    vectorstore = Chroma.from_documents(documents=splits, embedding=embeddings)
    
    # E. 返回检索器
    return vectorstore.as_retriever()

# 4. 初始化 Session State (聊天记录)
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# 5. 只有当用户上传了文件，我们才开始干活
if uploaded_file:
    with st.spinner("🧠 正在阅读文档，请稍候... (首次处理可能需要几十秒)"):
        retriever = process_uploaded_file(uploaded_file)
    
    st.success("文档加载完成！请开始提问。")

    # --- 定义 RAG 链 ---
    # 我们把 Chain 定义在这里，因为 retriever 是动态生成的
    llm = ChatOllama(model="qwen2.5:14b", temperature=0)
    
    template = """基于以下已知信息回答用户的问题。
    如果无法从上下文中得到答案，请说“根据文档无法回答”。
    
    【已知信息】：
    {context}
    
    【用户问题】：
    {question}
    """
    prompt = PromptTemplate.from_template(template)
    
    # 定义简单的 RAG Chain
    def format_docs(docs):
        return "\n\n".join(doc.page_content for doc in docs)

    rag_chain = (
        {"context": retriever | format_docs, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )

    # --- 6. 聊天界面渲染 (同 Day 17) ---
    for msg in st.session_state.chat_history:
        role = "user" if msg["role"] == "user" else "assistant"
        st.chat_message(role).write(msg["content"])

    # --- 7. 处理输入 ---
    user_input = st.chat_input("在这个 PDF 里查找...")

    if user_input:
        # 显示用户输入
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        st.chat_message("user").write(user_input)

        # AI 回答
        with st.chat_message("assistant"):
            with st.spinner("🔍 正在检索文档并生成答案..."):
                try:
                    # Streamlit 的流式输出稍微复杂，今天先用 invoke 一次性输出
                    response = rag_chain.invoke(user_input)
                    st.write(response)
                    st.session_state.chat_history.append({"role": "assistant", "content": response})
                except Exception as e:
                    st.error(f"发生错误: {e}")

else:
    # 如果没上传文件，显示欢迎页
    st.info("👋 请先在左侧上传一个 PDF 文件，我才能回答你的问题。")