# Day 2: 异步编程 + Prompt工程基础

## 📚 学习总结

### 今日成果
✅ 掌握了Python异步编程基础（async/await）  
✅ 学会了批量请求处理  
✅ 理解了Token计数和优化  
✅ 掌握了Prompt工程基础技巧

---

## 🚀 快速开始

### 1. 安装依赖
```bash
pip install -r day02_requirements.txt
```

主要依赖：
- `requests` - 同步HTTP请求
- `aiohttp` - 异步HTTP请求

### 2. 运行项目

#### 项目1：异步编程基础
```bash
python day02_project1_async_basics.py
```
**学习内容：**
- 同步 vs 异步对比
- async/await 语法
- asyncio.gather() 并发执行
- 异步HTTP请求
- 错误处理

#### 项目2：批量请求处理器
```bash
python day02_project2_batch_processor.py
```
**学习内容：**
- 批量任务管理
- 并发控制（Semaphore）
- 进度追踪
- 结果聚合

#### 项目3：Token计数与优化
```bash
python day02_project3_token_optimizer.py
```
**学习内容：**
- Token计数方法
- 对话历史优化
- 成本估算
- Prompt压缩

#### 项目4：Prompt工程
```bash
python day02_project4_prompt_engineering.py
```
**学习内容：**
- 零样本（Zero-shot）
- 少样本（Few-shot）
- 思维链（Chain-of-Thought）
- 角色扮演（Role-play）
- 结构化输出

---

## 🎯 核心知识点

### 1. 异步编程

#### 为什么需要异步？
```python
# ❌ 同步：串行执行，慢
结果1 = 调用API("问题1")  # 3秒
结果2 = 调用API("问题2")  # 3秒
结果3 = 调用API("问题3")  # 3秒
# 总共：9秒

# ✅ 异步：并发执行，快
结果 = await asyncio.gather(
    调用API("问题1"),
    调用API("问题2"),
    调用API("问题3")
)
# 总共：约3秒！
```

#### 基本语法
```python
# 1. 定义异步函数
async def fetch_data():
    await asyncio.sleep(1)  # 异步等待
    return "数据"

# 2. 并发执行
async def main():
    tasks = [fetch_data() for _ in range(5)]
    results = await asyncio.gather(*tasks)

# 3. 运行
asyncio.run(main())
```

#### 异步HTTP请求
```python
import aiohttp

async def async_request(url, data):
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=data) as response:
            return await response.json()
```

### 2. 批量处理

#### 并发控制
```python
# 使用Semaphore限制并发数
semaphore = asyncio.Semaphore(5)  # 最多5个并发

async def limited_task(task):
    async with semaphore:
        return await execute_task(task)
```

#### 进度追踪
```python
@dataclass
class Task:
    id: int
    status: str  # pending, running, success, failed
    start_time: float
    end_time: float
```

### 3. Token优化

#### Token计数（简化版）
```python
def count_tokens(text):
    chinese = len(re.findall(r'[\u4e00-\u9fff]', text))
    english = len(re.findall(r'\b[a-zA-Z]+\b', text))
    
    # 中文 ≈ 1.5 token/字
    # 英文 ≈ 1 token/词
    return int(chinese * 1.5 + english)
```

#### 对话历史优化
```python
class ConversationOptimizer:
    def optimize_messages(self):
        # 保留系统消息
        # 保留最近N条消息
        # 移除中间较旧消息
        return optimized_messages
```

### 4. Prompt工程

#### 基本原则
```python
# ❌ 差的Prompt
"写代码"

# ✅ 好的Prompt
"""
用Python写一个快速排序函数

要求：
1. 包含详细注释
2. 包含时间复杂度分析
3. 提供使用示例
4. 处理边界情况
"""
```

#### 提示词类型

| 类型 | 说明 | 适用场景 |
|------|------|----------|
| Zero-shot | 不提供示例 | 简单、通用任务 |
| Few-shot | 提供2-5个示例 | 分类、格式化 |
| Chain-of-Thought | 引导思考过程 | 复杂推理 |
| Role-play | 设定角色 | 创意、专业任务 |
| Structured | 指定输出格式 | 数据提取 |

#### Few-shot示例
```python
prompt = """
以下是一些示例：

文本：这个产品很好用
分类：正面

文本：服务太差了
分类：负面

现在分类：
文本：还可以，凑合
分类：
"""
```

#### Chain-of-Thought示例
```python
prompt = """
问题：小明有10个苹果，吃了3个，又买了5个，现在有几个？

让我们一步一步思考：
1. 初始有10个苹果
2. 吃了3个：10 - 3 = 7个
3. 又买了5个：7 + 5 = 12个
4. 最终答案：12个苹果
"""
```

---

## 📊 性能对比

### 同步 vs 异步

| 场景 | 同步耗时 | 异步耗时 | 加速比 |
|------|---------|---------|--------|
| 5个简单问题 | 15秒 | 3秒 | 5x |
| 10个问题 | 30秒 | 3秒 | 10x |
| 批量翻译100句 | 300秒 | 30秒 | 10x |

### 并发控制影响

| 并发数 | 耗时 | CPU使用 | 稳定性 |
|-------|------|---------|--------|
| 1 | 慢 | 低 | 高 |
| 3-5 | 适中 | 中 | 高 |
| 10+ | 快 | 高 | 中 |
| 无限制 | 最快 | 很高 | 低 |

**推荐：3-10的并发数，平衡速度和稳定性**

---

## 💡 最佳实践

### 1. 异步编程
```python
# ✅ 好习惯
async def main():
    async with aiohttp.ClientSession() as session:
        # 复用session
        tasks = [fetch(session, url) for url in urls]
        return await asyncio.gather(*tasks)

# ❌ 坏习惯
async def main():
    results = []
    for url in urls:
        # 每次创建新session，慢
        async with aiohttp.ClientSession() as session:
            result = await fetch(session, url)
            results.append(result)
```

### 2. 错误处理
```python
# 使用 return_exceptions=True
results = await asyncio.gather(
    *tasks,
    return_exceptions=True  # 收集异常而不抛出
)

# 分别处理成功和失败
successes = [r for r in results if not isinstance(r, Exception)]
failures = [r for r in results if isinstance(r, Exception)]
```

### 3. Token管理
```python
# 设置合理的上限
MAX_TOKENS = 4000

# 定期清理历史
if current_tokens > MAX_TOKENS:
    messages = optimize_messages(messages)

# 使用滑动窗口
def keep_recent(messages, max_count=20):
    system_msgs = [m for m in messages if m['role'] == 'system']
    other_msgs = [m for m in messages if m['role'] != 'system']
    return system_msgs + other_msgs[-max_count:]
```

### 4. Prompt编写
```python
# 结构化模板
template = """
[系统角色]
你是一个{role}

[任务]
{task}

[要求]
1. {requirement1}
2. {requirement2}

[输出格式]
{format}
"""

# 使用变量填充
prompt = template.format(
    role="Python专家",
    task="写一个排序函数",
    requirement1="包含注释",
    requirement2="处理边界情况",
    format="Python代码 + 说明"
)
```

---

## 🔧 常见问题

### Q1: 异步代码出现 "RuntimeError: Event loop is closed"
**原因：** 在已关闭的事件循环中运行异步代码

**解决：**
```python
# ❌ 错误
loop = asyncio.get_event_loop()
loop.run_until_complete(main())
loop.close()
loop.run_until_complete(other())  # 错误！

# ✅ 正确
asyncio.run(main())
asyncio.run(other())  # 每次创建新的事件循环
```

### Q2: 并发太高导致连接错误
**解决：** 使用Semaphore限制并发数
```python
semaphore = asyncio.Semaphore(5)

async def limited_request():
    async with semaphore:
        return await make_request()
```

### Q3: Token计数不准确
**说明：** 简化版计数器只是估算

**解决：** 生产环境使用tiktoken
```python
# pip install tiktoken
import tiktoken

encoding = tiktoken.encoding_for_model("gpt-4")
tokens = encoding.encode(text)
count = len(tokens)
```

### Q4: Prompt太长被截断
**解决：**
1. 精简表达，去除冗余
2. 使用简洁的示例
3. 分步骤处理
```python
# ❌ 一次性处理
"分析这个100页的文档..."

# ✅ 分步处理
"第1步：总结前10页..."
"第2步：总结11-20页..."
```

---

## 🎓 学习建议

### Day 2的重点
1. **理解异步的本质**：不是让任务更快，而是让多个任务同时进行
2. **掌握基本语法**：async/await/gather
3. **学会错误处理**：return_exceptions、try/except
4. **理解Token概念**：计量单位、影响成本
5. **掌握Prompt技巧**：清晰、具体、结构化

### 动手练习
- 完成 `day02_exercises.md` 中的练习1-3
- 对比同步和异步的性能差异
- 尝试不同的Prompt写法
- 优化一个真实的对话应用

### 延伸阅读
- [Python asyncio文档](https://docs.python.org/3/library/asyncio.html)
- [aiohttp文档](https://docs.aiohttp.org/)
- [Prompt Engineering Guide](https://www.promptingguide.ai/)

---

## 📈 进步检查

Day 1 → Day 2 的提升：

| 能力 | Day 1 | Day 2 |
|------|-------|-------|
| API调用 | ✅ 同步 | ✅ 异步 |
| 批量处理 | ❌ | ✅ |
| 性能优化 | ❌ | ✅ |
| Token管理 | ❌ | ✅ |
| Prompt技巧 | ⭐ | ⭐⭐⭐ |

---

## 📝 今日代码统计

- **project1_async_basics.py**: 385行（异步基础）
- **project2_batch_processor.py**: 450行（批量处理）
- **project3_token_optimizer.py**: 420行（Token优化）
- **project4_prompt_engineering.py**: 580行（Prompt工程）

**总计：** 1,835行高质量代码！

---

## 🎯 检查清单

学完 Day 2，你应该能够：
- [ ] 使用async/await编写异步代码
- [ ] 使用asyncio.gather()并发执行任务
- [ ] 使用aiohttp进行异步HTTP请求
- [ ] 控制并发数避免过载
- [ ] 计算和优化Token使用
- [ ] 管理对话历史
- [ ] 编写结构化的Prompt
- [ ] 使用Few-shot提升效果
- [ ] 引导AI进行思维链推理
- [ ] 设定角色和上下文

---

## 🚀 下一步：Day 3

明天我们将学习：
- **ReAct模式**：Reasoning + Acting
- **工具调用（Tool Use）**：让AI使用工具
- **Function Calling**：函数调用机制
- **构建第一个Tool-using Agent**

这是走向真正Agent的关键一步！💪

---

## 💬 反馈

Day 2内容量较大，如果遇到困难：
1. 先掌握异步基础（项目1）
2. 然后学习批量处理（项目2）
3. Token和Prompt可以之后慢慢理解
4. 多动手实践，一定会掌握的！

继续加油！明天见！🚀
