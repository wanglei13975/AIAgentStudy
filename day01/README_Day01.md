# Day 1: Python基础复习 + LLM API使用

## 📚 学习总结

### 今日成果
✅ 复习了Python核心概念（函数、类、异常处理）  
✅ 学会了调用本地Ollama模型  
✅ 理解了LLM的输入输出机制  
✅ 创建了3个递进的实践项目

---

## 🚀 快速开始

### 1. 安装依赖
```bash
pip install -r requirements.txt
```

### 2. 确保Ollama运行
```bash
# 检查Ollama是否运行
ollama list

# 如果需要启动
ollama serve
```

### 3. 运行项目

#### 项目1：基础对话器
```bash
python project1_basic_chat.py
```
最简单的问答程序，理解基本的API调用。

#### 项目2：对话历史管理器
```bash
python project2_conversation_manager.py
```
带上下文的对话，AI能记住之前说过的内容。

#### 项目3：LLM工具类（推荐）
```bash
python project3_llm_toolkit.py
```
完整的LLM封装，支持流式输出、保存加载、温度控制等高级功能。

---

## 🎯 核心知识点

### 1. Ollama API 两种模式

**Generate API** (简单问答)
```python
# 适用于单次问答，不保留上下文
url = "http://localhost:11434/api/generate"
data = {"model": "qwen2.5:14b", "prompt": "你好"}
```

**Chat API** (对话模式)
```python
# 适用于多轮对话，保留上下文
url = "http://localhost:11434/api/chat"
data = {
    "model": "qwen2.5:14b",
    "messages": [
        {"role": "user", "content": "你好"},
        {"role": "assistant", "content": "你好！"},
        {"role": "user", "content": "我刚才说了什么？"}
    ]
}
```

### 2. 对话角色（Role）
- **system**: 系统提示词，定义AI的行为和身份
- **user**: 用户的输入
- **assistant**: AI的回复

### 3. 重要参数

| 参数 | 说明 | 取值范围 | 作用 |
|------|------|----------|------|
| temperature | 随机性 | 0.0-1.0 | 越高越随机，越低越确定 |
| stream | 流式输出 | true/false | 是否逐字输出 |
| num_predict | 最大token | 整数 | 限制回复长度 |

### 4. 流式 vs 非流式

**非流式输出**（stream=false）
- ✅ 简单，一次性获得完整回复
- ❌ 等待时间长，用户体验差

**流式输出**（stream=true）
- ✅ 实时显示，体验好
- ❌ 处理稍微复杂

---

## 💡 最佳实践

### 1. 错误处理
始终使用 try-except 处理网络请求：
```python
try:
    response = requests.post(url, json=data)
    response.raise_for_status()
except requests.exceptions.ConnectionError:
    print("无法连接到Ollama")
except requests.exceptions.RequestException as e:
    print(f"请求错误: {e}")
```

### 2. 对话历史管理
限制历史长度，避免超出上下文窗口：
```python
# 只保留最近10轮对话
if len(self.history) > 20:  # 每轮2条消息
    self.history = self.history[-20:]
```

### 3. 使用系统提示词
明确AI的角色和行为规范：
```python
system_prompt = """你是一个Python编程助手。
请遵循以下规则：
1. 回答要简洁明了
2. 提供可运行的代码示例
3. 解释关键概念
"""
```

---

## 🔧 常见问题

### Q1: 连接失败怎么办？
```bash
# 检查Ollama是否运行
curl http://localhost:11434/api/tags

# 如果没有响应，启动Ollama
ollama serve
```

### Q2: 模型响应很慢？
- qwen2.5:14b 是较大的模型，首次加载需要时间
- 考虑使用更小的模型如 qwen2.5:7b
- 检查系统资源（内存、GPU）

### Q3: 如何选择温度参数？
- **0.1-0.3**: 需要准确、一致的回答（代码生成、数学题）
- **0.5-0.7**: 平衡创造性和准确性（通用对话）
- **0.8-1.0**: 需要创意和多样性（创意写作、头脑风暴）

### Q4: 对话历史太长怎么办？
实现滑动窗口策略：
```python
MAX_HISTORY = 20  # 保留最近10轮对话

def add_message(self, role, content):
    self.history.append({"role": role, "content": content})
    # 保留系统提示词，限制其他消息
    system_msgs = [m for m in self.history if m["role"] == "system"]
    other_msgs = [m for m in self.history if m["role"] != "system"]
    if len(other_msgs) > MAX_HISTORY:
        other_msgs = other_msgs[-MAX_HISTORY:]
    self.history = system_msgs + other_msgs
```

---

## 📊 项目对比

| 特性 | 项目1 | 项目2 | 项目3 |
|------|-------|-------|-------|
| 上下文记忆 | ❌ | ✅ | ✅ |
| 流式输出 | ❌ | ❌ | ✅ |
| 温度控制 | ❌ | ❌ | ✅ |
| 保存/加载 | ❌ | ❌ | ✅ |
| 系统提示词 | ❌ | ❌ | ✅ |
| 适合场景 | 学习基础 | 简单对话 | 生产环境 |

---

## 🎓 学习建议

### 今天的重点
1. **理解API调用流程**：从构建请求到处理响应
2. **掌握对话历史管理**：这是构建Agent的基础
3. **熟悉类的封装**：良好的代码组织是关键

### 动手练习
- 运行每个项目，观察差异
- 修改参数，看看效果变化
- 完成 `day01_exercises.md` 中的练习

### 延伸阅读
- [Ollama官方文档](https://github.com/ollama/ollama/blob/main/docs/api.md)
- [HTTP请求基础](https://requests.readthedocs.io/)
- [Python类与对象](https://docs.python.org/zh-cn/3/tutorial/classes.html)

---

## 📝 今日代码统计

- **project1_basic_chat.py**: 66 行（入门级）
- **project2_conversation_manager.py**: 125 行（进阶）
- **project3_llm_toolkit.py**: 328 行（生产级）

---

## 🎯 检查清单

学完 Day 1，你应该能够：
- [ ] 成功调用本地Ollama模型
- [ ] 理解 generate 和 chat 两种API的区别
- [ ] 管理对话历史记录
- [ ] 使用系统提示词定制AI行为
- [ ] 实现流式输出
- [ ] 保存和加载对话
- [ ] 处理常见错误

---

## 🚀 下一步

明天（Day 2）我们将学习：
- **异步编程**：提升程序性能
- **批量请求处理**：高效处理多个任务
- **Token计数与优化**：控制成本
- **Prompt工程入门**：如何写好提示词

准备好了吗？继续加油！💪

---

## 📮 反馈与建议

如果你有任何问题或建议，欢迎反馈：
- 代码运行遇到问题？
- 某个概念不理解？
- 想要更多练习？

让我知道，我会帮你解决！
