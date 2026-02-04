import os

# --- 1. 必不可少的网络配置（防止 504/443 报错）---
os.environ["NO_PROXY"] = "localhost,127.0.0.1"
if "HTTP_PROXY" in os.environ: del os.environ["HTTP_PROXY"]
if "HTTPS_PROXY" in os.environ: del os.environ["HTTPS_PROXY"]

from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# --- 2. 初始化模型 ---
print("--- 正在初始化模型 (怼人模式) ---")
llm = ChatOllama(
    model="qwen2.5:14b", 
    temperature=0.7, #稍微调高一点，让它说话更有个性
    timeout=600.0 
)

# ==========================================
# 第一步：情绪分析链 (Chain A)
# ==========================================
prompt_analyze = ChatPromptTemplate.from_template(
    """
    任务：分析用户输入的情感倾向。
    用户输入："{user_text}"
    
    请只输出“正面”或“负面”这两个词中的一个，不要包含任何其他分析或标点符号。
    """
)
chain_analyze = prompt_analyze | llm | StrOutputParser()

# ==========================================
# 第二步：回复生成链 (Chain B)
# ==========================================
prompt_reply = ChatPromptTemplate.from_template(
    """
    背景：你是一个性格古怪的机器人。
    
    用户说："{user_text}"
    检测到的情绪是："{sentiment}"
    
    请根据情绪生成回复：
    1. 如果情绪是【负面】：请用极其温柔、暖心的语气安慰用户，像一个知心大姐姐/大哥哥。
    2. 如果情绪是【正面】：请用幽默、毒舌、泼冷水的方式回复，打击一下用户的嚣张气焰（但在开玩笑的范围内）。
    
    直接输出你的回复即可。
    """
)
chain_reply = prompt_reply | llm | StrOutputParser()

# ==========================================
# 主程序
# ==========================================
def run_bot(text):
    print(f"\n[用户]: {text}")
    print(">>> 正在分析情绪...")
    
    # 1. 运行第一条链：获取情绪
    sentiment = chain_analyze.invoke({"user_text": text})
    # 清理一下可能多余的空格
    sentiment = sentiment.strip()
    print(f"[分析结果]: {sentiment}")
    
    print(">>> 正在生成回复...")
    
    # 2. 运行第二条链：传入 原文 + 情绪
    # 注意：这里我们把两个变量传给了 Prompt
    reply = chain_reply.invoke({
        "user_text": text,
        "sentiment": sentiment
    })
    
    print(f"[机器人]: {reply}")

if __name__ == "__main__":
    # 测试案例 1：负面情绪（应该被安慰）
    run_bot("我今天被老板骂了一顿，感觉好想哭，工作太难了。")
    
    print("-" * 50)
    
    # 测试案例 2：正面情绪（应该被怼）
    run_bot("哈哈哈！我今天中了彩票，还升职加薪了，我简直是世界之王！")