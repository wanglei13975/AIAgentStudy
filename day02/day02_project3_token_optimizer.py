"""
Day 2 - 项目3: Token计数器与优化
学习Token管理和成本优化
"""

import re
from typing import List, Dict, Tuple
from dataclasses import dataclass


@dataclass
class TokenStats:
    """Token统计信息"""
    text: str
    token_count: int
    char_count: int
    word_count: int
    estimated_cost: float = 0.0
    
    def __str__(self):
        return f"""
Token统计:
- 字符数: {self.char_count}
- 单词数: {self.word_count}
- Token数: {self.token_count}
- 预估成本: ${self.estimated_cost:.6f}
        """.strip()


class TokenCounter:
    """Token计数器（简化版）"""
    
    # 中文字符通常1-2个token
    # 英文单词通常1个token
    # 特殊字符可能0.5-1个token
    
    @staticmethod
    def count_tokens(text: str) -> int:
        """
        估算token数量
        
        注意：这是简化的估算，实际token数可能有差异
        真实项目应使用tiktoken库
        """
        # 统计中文字符
        chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', text))
        
        # 统计英文单词
        english_words = len(re.findall(r'\b[a-zA-Z]+\b', text))
        
        # 统计数字
        numbers = len(re.findall(r'\d+', text))
        
        # 统计标点和其他字符
        other_chars = len(text) - chinese_chars - sum(len(w) for w in re.findall(r'\b[a-zA-Z]+\b', text)) - sum(len(n) for n in re.findall(r'\d+', text))
        
        # 估算token
        # 中文：1.5 token/字
        # 英文：1 token/词
        # 数字：1 token/数字串
        # 其他：0.5 token/字符
        
        estimated_tokens = int(
            chinese_chars * 1.5 +
            english_words * 1.0 +
            numbers * 1.0 +
            other_chars * 0.5
        )
        
        return estimated_tokens
    
    @staticmethod
    def analyze_text(text: str, cost_per_1k_tokens: float = 0.01) -> TokenStats:
        """
        分析文本并返回统计信息
        
        参数:
            text: 要分析的文本
            cost_per_1k_tokens: 每1000个token的成本（美元）
        """
        token_count = TokenCounter.count_tokens(text)
        char_count = len(text)
        word_count = len(text.split())
        estimated_cost = (token_count / 1000) * cost_per_1k_tokens
        
        return TokenStats(
            text=text,
            token_count=token_count,
            char_count=char_count,
            word_count=word_count,
            estimated_cost=estimated_cost
        )


class ConversationOptimizer:
    """对话优化器：管理对话历史的token使用"""
    
    def __init__(self, max_tokens: int = 4000):
        """
        初始化优化器
        
        参数:
            max_tokens: 最大token数限制
        """
        self.max_tokens = max_tokens
        self.messages: List[Dict[str, str]] = []
    
    def add_message(self, role: str, content: str):
        """添加消息"""
        self.messages.append({"role": role, "content": content})
    
    def get_total_tokens(self) -> int:
        """计算当前对话的总token数"""
        total = 0
        for msg in self.messages:
            total += TokenCounter.count_tokens(msg["content"])
        return total
    
    def optimize_messages(self) -> List[Dict[str, str]]:
        """
        优化消息列表，确保不超过token限制
        
        策略：
        1. 保留系统消息
        2. 保留最近的对话
        3. 移除中间较旧的对话
        """
        if not self.messages:
            return []
        
        current_tokens = self.get_total_tokens()
        
        if current_tokens <= self.max_tokens:
            return self.messages
        
        # 分离系统消息和其他消息
        system_msgs = [m for m in self.messages if m["role"] == "system"]
        other_msgs = [m for m in self.messages if m["role"] != "system"]
        
        # 计算系统消息的token
        system_tokens = sum(TokenCounter.count_tokens(m["content"]) for m in system_msgs)
        
        # 可用于对话历史的token
        available_tokens = self.max_tokens - system_tokens
        
        # 从最新消息开始，逐步添加直到达到限制
        optimized_other = []
        current = 0
        
        for msg in reversed(other_msgs):
            msg_tokens = TokenCounter.count_tokens(msg["content"])
            if current + msg_tokens <= available_tokens:
                optimized_other.insert(0, msg)
                current += msg_tokens
            else:
                break
        
        return system_msgs + optimized_other
    
    def print_optimization_report(self):
        """打印优化报告"""
        original_tokens = self.get_total_tokens()
        optimized_msgs = self.optimize_messages()
        optimized_tokens = sum(
            TokenCounter.count_tokens(m["content"]) for m in optimized_msgs
        )
        
        print(f"\n{'='*60}")
        print(f"📊 对话优化报告")
        print(f"{'='*60}")
        print(f"原始消息数: {len(self.messages)}")
        print(f"原始Token数: {original_tokens}")
        print(f"Token限制: {self.max_tokens}")
        print(f"\n优化后:")
        print(f"消息数: {len(optimized_msgs)}")
        print(f"Token数: {optimized_tokens}")
        print(f"节省Token: {original_tokens - optimized_tokens}")
        print(f"保留率: {len(optimized_msgs) / len(self.messages) * 100:.1f}%")
        print(f"{'='*60}")


class PromptOptimizer:
    """提示词优化器"""
    
    @staticmethod
    def compress_prompt(prompt: str, max_tokens: int = 500) -> str:
        """
        压缩提示词
        
        策略：
        1. 移除多余空白
        2. 简化冗余表达
        3. 使用缩写
        """
        # 移除多余空白
        compressed = re.sub(r'\s+', ' ', prompt).strip()
        
        # 如果还是太长，截断
        current_tokens = TokenCounter.count_tokens(compressed)
        if current_tokens > max_tokens:
            # 简单截断策略：保留前80%
            target_length = int(len(compressed) * 0.8)
            compressed = compressed[:target_length] + "..."
        
        return compressed
    
    @staticmethod
    def analyze_prompt_efficiency(prompt: str) -> Dict:
        """
        分析提示词效率
        
        返回优化建议
        """
        stats = TokenCounter.analyze_text(prompt)
        
        suggestions = []
        
        # 检查是否过长
        if stats.token_count > 1000:
            suggestions.append("❗ 提示词过长，建议精简")
        
        # 检查是否有大量空白
        if prompt.count('  ') > 5:
            suggestions.append("💡 存在多余空白，可以清理")
        
        # 检查是否有重复
        words = prompt.split()
        if len(words) != len(set(words)):
            suggestions.append("💡 存在重复词语，可以简化")
        
        # 检查是否太短
        if stats.token_count < 10:
            suggestions.append("💡 提示词可能过于简短，考虑添加更多上下文")
        
        return {
            "stats": stats,
            "suggestions": suggestions,
            "efficiency_score": min(100, 100 * (500 / max(stats.token_count, 1)))
        }


# ============================================================
# 演示示例
# ============================================================

def demo_token_counting():
    """演示Token计数"""
    print("\n" + "="*60)
    print("📚 演示1: Token计数")
    print("="*60)
    
    texts = [
        "Hello, how are you?",
        "你好，今天天气怎么样？",
        "This is a longer sentence with more words to demonstrate token counting.",
        "Python是一种高级编程语言，它简单易学且功能强大。",
        "混合text：Python很好用，I love it!"
    ]
    
    for text in texts:
        stats = TokenCounter.analyze_text(text)
        print(f"\n文本: {text}")
        print(f"Token数: {stats.token_count}")


def demo_conversation_optimization():
    """演示对话优化"""
    print("\n" + "="*60)
    print("📚 演示2: 对话历史优化")
    print("="*60)
    
    optimizer = ConversationOptimizer(max_tokens=200)  # 很小的限制用于演示
    
    # 添加系统消息
    optimizer.add_message("system", "你是一个helpful的AI助手")
    
    # 模拟长对话
    conversations = [
        ("user", "你好！"),
        ("assistant", "你好！有什么可以帮助你的吗？"),
        ("user", "介绍一下Python"),
        ("assistant", "Python是一种高级编程语言，由Guido van Rossum在1991年创建。它以简洁易读的语法而闻名。"),
        ("user", "Python有哪些特点？"),
        ("assistant", "Python的主要特点包括：1. 语法简洁 2. 动态类型 3. 自动内存管理 4. 丰富的标准库"),
        ("user", "Python适合做什么？"),
        ("assistant", "Python广泛应用于Web开发、数据分析、人工智能、科学计算、自动化等领域。"),
    ]
    
    for role, content in conversations:
        optimizer.add_message(role, content)
    
    # 打印优化报告
    optimizer.print_optimization_report()
    
    # 显示保留的消息
    optimized = optimizer.optimize_messages()
    print("\n保留的消息:")
    for msg in optimized:
        print(f"  [{msg['role']}] {msg['content'][:50]}...")


def demo_prompt_optimization():
    """演示提示词优化"""
    print("\n" + "="*60)
    print("📚 演示3: 提示词优化")
    print("="*60)
    
    # 差的提示词
    bad_prompt = """
    请帮我写一个Python程序     写一个Python程序    
    要求这个程序能够     能够     能够处理数据
    然后还要     还要     还要能够分析数据
    """
    
    print("\n原始提示词:")
    print(bad_prompt)
    print(f"\nToken数: {TokenCounter.count_tokens(bad_prompt)}")
    
    # 优化
    optimized = PromptOptimizer.compress_prompt(bad_prompt)
    print("\n优化后:")
    print(optimized)
    print(f"\nToken数: {TokenCounter.count_tokens(optimized)}")
    
    # 分析效率
    print("\n" + "-"*60)
    good_prompt = "用Python写一个数据处理和分析程序，包含数据清洗、统计分析和可视化功能。"
    analysis = PromptOptimizer.analyze_prompt_efficiency(good_prompt)
    
    print("\n好的提示词示例:")
    print(good_prompt)
    print(f"\n效率评分: {analysis['efficiency_score']:.1f}/100")
    print(f"Token数: {analysis['stats'].token_count}")
    
    if analysis['suggestions']:
        print("\n优化建议:")
        for suggestion in analysis['suggestions']:
            print(f"  {suggestion}")


def demo_cost_estimation():
    """演示成本估算"""
    print("\n" + "="*60)
    print("📚 演示4: 成本估算")
    print("="*60)
    
    # 模拟不同场景的使用
    scenarios = [
        {
            "name": "简单对话",
            "prompts": ["你好", "今天天气怎么样", "谢谢"],
            "responses": ["你好！", "今天天气不错，阳光明媚。", "不客气！"]
        },
        {
            "name": "代码生成",
            "prompts": ["用Python写一个快速排序"],
            "responses": ["""
def quicksort(arr):
    if len(arr) <= 1:
        return arr
    pivot = arr[len(arr) // 2]
    left = [x for x in arr if x < pivot]
    middle = [x for x in arr if x == pivot]
    right = [x for x in arr if x > pivot]
    return quicksort(left) + middle + quicksort(right)
            """]
        },
        {
            "name": "长文本分析",
            "prompts": ["分析这篇文章的主题和要点：" + "这是一篇很长的文章..." * 100],
            "responses": ["文章主要讨论..."]
        }
    ]
    
    # API定价（示例，非真实价格）
    COST_PER_1K_INPUT = 0.01
    COST_PER_1K_OUTPUT = 0.03
    
    print("\n场景成本估算 (假设价格: 输入$0.01/1K, 输出$0.03/1K):")
    print("-" * 60)
    
    for scenario in scenarios:
        input_tokens = sum(TokenCounter.count_tokens(p) for p in scenario['prompts'])
        output_tokens = sum(TokenCounter.count_tokens(r) for r in scenario['responses'])
        
        input_cost = (input_tokens / 1000) * COST_PER_1K_INPUT
        output_cost = (output_tokens / 1000) * COST_PER_1K_OUTPUT
        total_cost = input_cost + output_cost
        
        print(f"\n📊 {scenario['name']}:")
        print(f"   输入Token: {input_tokens}")
        print(f"   输出Token: {output_tokens}")
        print(f"   总Token: {input_tokens + output_tokens}")
        print(f"   预估成本: ${total_cost:.6f}")
        print(f"   每天1000次: ${total_cost * 1000:.2f}")
        print(f"   每月30天: ${total_cost * 1000 * 30:.2f}")


def main():
    """主函数"""
    print("="*60)
    print("🎓 Day 2 - 项目3: Token计数与优化")
    print("="*60)
    
    # 运行所有演示
    demo_token_counting()
    demo_conversation_optimization()
    demo_prompt_optimization()
    demo_cost_estimation()
    
    # 总结
    print("\n" + "="*60)
    print("📚 关键知识点")
    print("="*60)
    print("""
1. Token基础:
   - Token是LLM的基本计算单位
   - 中文字符 ≈ 1.5 token
   - 英文单词 ≈ 1 token
   - Token数影响成本和速度

2. 对话优化:
   - 限制历史长度
   - 保留重要上下文
   - 移除冗余信息
   - 使用滑动窗口

3. 提示词优化:
   - 精简表达
   - 移除冗余
   - 清晰结构
   - 合理长度

4. 成本控制:
   - 监控Token使用
   - 优化提示词
   - 批量处理
   - 缓存结果

💡 实用建议:
- 对话应用：限制历史在2000-4000 tokens
- 生产环境：使用真实的token计数库(tiktoken)
- 成本优化：缓存常见查询结果
- 性能优化：控制上下文窗口大小
    """)


if __name__ == "__main__":
    main()
