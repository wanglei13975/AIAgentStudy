"""
Day 2 - 项目4: Prompt工程模板系统
学习如何写好提示词，让AI给出更好的回答
"""

import requests
import json
from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum


class PromptType(Enum):
    """提示词类型"""
    ZERO_SHOT = "zero_shot"          # 零样本
    FEW_SHOT = "few_shot"            # 少样本
    CHAIN_OF_THOUGHT = "cot"         # 思维链
    ROLE_PLAY = "role_play"          # 角色扮演
    STRUCTURED_OUTPUT = "structured" # 结构化输出


@dataclass
class PromptTemplate:
    """提示词模板"""
    name: str
    type: PromptType
    system_prompt: str
    user_template: str
    examples: Optional[List[Dict]] = None
    
    def format(self, **kwargs) -> str:
        """格式化用户提示"""
        return self.user_template.format(**kwargs)


class PromptLibrary:
    """提示词库"""
    
    def __init__(self):
        self.templates: Dict[str, PromptTemplate] = {}
        self._init_templates()
    
    def _init_templates(self):
        """初始化内置模板"""
        
        # 1. 零样本：代码生成
        self.add_template(PromptTemplate(
            name="code_generator",
            type=PromptType.ZERO_SHOT,
            system_prompt="你是一个专业的程序员，擅长写清晰、高效的代码。",
            user_template="""
请用{language}编写一个{task}。

要求：
1. 代码要有详细注释
2. 包含错误处理
3. 提供使用示例
4. 说明时间和空间复杂度
"""
        ))
        
        # 2. 少样本：文本分类
        self.add_template(PromptTemplate(
            name="text_classifier",
            type=PromptType.FEW_SHOT,
            system_prompt="你是一个文本分类专家。根据示例学习，然后对新文本进行分类。",
            user_template="""
以下是一些分类示例：

{examples}

现在，请对以下文本进行分类：
文本：{text}
分类：
""",
            examples=[
                {"text": "这个产品质量很好，非常满意！", "label": "正面"},
                {"text": "服务态度太差了，再也不来了。", "label": "负面"},
                {"text": "还行吧，凑合能用。", "label": "中性"}
            ]
        ))
        
        # 3. 思维链：数学问题
        self.add_template(PromptTemplate(
            name="math_solver",
            type=PromptType.CHAIN_OF_THOUGHT,
            system_prompt="你是一个数学老师，解题时要展示详细的思考过程。",
            user_template="""
问题：{problem}

请按以下步骤解答：
1. 理解题意
2. 列出已知条件
3. 确定解题思路
4. 逐步计算
5. 验证答案
6. 给出最终答案
"""
        ))
        
        # 4. 角色扮演：创意写作
        self.add_template(PromptTemplate(
            name="creative_writer",
            type=PromptType.ROLE_PLAY,
            system_prompt="""
你是一位获奖无数的创意作家，擅长{genre}。
你的写作风格是{style}。
你的作品总是{characteristics}。
""",
            user_template="""
主题：{theme}
要求：
- 字数：{word_count}字左右
- 包含元素：{elements}

开始创作：
"""
        ))
        
        # 5. 结构化输出：数据提取
        self.add_template(PromptTemplate(
            name="data_extractor",
            type=PromptType.STRUCTURED_OUTPUT,
            system_prompt="你是一个数据提取专家，能从文本中提取结构化信息。",
            user_template="""
从以下文本中提取信息，并以JSON格式返回。

文本：
{text}

提取字段：
{fields}

输出格式：
```json
{{
  "field1": "value1",
  "field2": "value2"
}}
```

请只返回JSON，不要有其他解释。
"""
        ))
        
        # 6. 代码审查
        self.add_template(PromptTemplate(
            name="code_reviewer",
            type=PromptType.ROLE_PLAY,
            system_prompt="""
你是一位资深的代码审查专家，拥有15年的编程经验。
你的审查关注：代码质量、性能、安全性、可维护性。
""",
            user_template="""
请审查以下代码：

```{language}
{code}
```

审查要点：
1. 代码质量和风格
2. 潜在bug和错误
3. 性能优化建议
4. 安全问题
5. 可维护性改进

请给出详细的审查意见。
"""
        ))
        
        # 7. 翻译
        self.add_template(PromptTemplate(
            name="translator",
            type=PromptType.ZERO_SHOT,
            system_prompt="""
你是一位专业翻译，精通{source_lang}和{target_lang}。
你的翻译准确、流畅、符合目标语言的表达习惯。
""",
            user_template="""
请将以下{source_lang}文本翻译成{target_lang}：

{text}

翻译要求：
- 保持原意
- 语言自然
- 适合{context}语境
"""
        ))
    
    def add_template(self, template: PromptTemplate):
        """添加模板"""
        self.templates[template.name] = template
    
    def get_template(self, name: str) -> Optional[PromptTemplate]:
        """获取模板"""
        return self.templates.get(name)
    
    def list_templates(self):
        """列出所有模板"""
        print("\n" + "="*60)
        print("📚 可用的提示词模板")
        print("="*60)
        
        for name, template in self.templates.items():
            print(f"\n🔹 {name}")
            print(f"   类型: {template.type.value}")
            print(f"   系统提示: {template.system_prompt[:50]}...")


class PromptTester:
    """提示词测试器"""
    
    def __init__(self, model: str = "qwen2.5:14b"):
        self.model = model
        self.url = "http://localhost:11434/api/chat"
    
    def test_prompt(
        self, 
        template: PromptTemplate, 
        **kwargs
    ) -> Dict:
        """测试提示词"""
        
        # 格式化系统提示
        system_prompt = template.system_prompt.format(**kwargs) if '{' in template.system_prompt else template.system_prompt
        
        # 格式化用户提示
        if template.examples and template.type == PromptType.FEW_SHOT:
            # 添加示例
            examples_text = "\n".join([
                f"文本：{ex['text']}\n分类：{ex['label']}"
                for ex in template.examples
            ])
            kwargs['examples'] = examples_text
        
        user_prompt = template.format(**kwargs)
        
        # 构建消息
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
        
        data = {
            "model": self.model,
            "messages": messages,
            "stream": False,
            "keep_alive": "5m"
        }
        
        try:
            response = requests.post(self.url, json=data, timeout=60)
            result = response.json()
            
            return {
                "success": True,
                "response": result.get("message", {}).get("content", ""),
                "system_prompt": system_prompt,
                "user_prompt": user_prompt
            }
        
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }


# ============================================================
# 演示示例
# ============================================================

def demo_code_generation():
    """演示代码生成"""
    print("\n" + "="*60)
    print("📚 演示1: 代码生成（零样本）")
    print("="*60)
    
    library = PromptLibrary()
    tester = PromptTester()
    
    template = library.get_template("code_generator")
    
    result = tester.test_prompt(
        template,
        language="Python",
        task="二分查找函数"
    )
    
    if result["success"]:
        print("\n📝 生成的代码:")
        print("-" * 60)
        print(result["response"])
    else:
        print(f"❌ 错误: {result['error']}")


def demo_few_shot_learning():
    """演示少样本学习"""
    print("\n" + "="*60)
    print("📚 演示2: 文本分类（少样本）")
    print("="*60)
    
    library = PromptLibrary()
    tester = PromptTester()
    
    template = library.get_template("text_classifier")
    
    # 测试新文本
    test_texts = [
        "这家餐厅的菜品太好吃了，环境也很棒！",
        "价格太贵了，性价比不高。",
        "还可以吧，没有特别惊艳。"
    ]
    
    print("\n测试文本分类:")
    print("-" * 60)
    
    for text in test_texts:
        result = tester.test_prompt(template, text=text)
        if result["success"]:
            print(f"\n文本: {text}")
            print(f"分类: {result['response']}")


def demo_chain_of_thought():
    """演示思维链"""
    print("\n" + "="*60)
    print("📚 演示3: 数学问题（思维链）")
    print("="*60)
    
    library = PromptLibrary()
    tester = PromptTester()
    
    template = library.get_template("math_solver")
    
    result = tester.test_prompt(
        template,
        problem="一个班级有30名学生，其中女生占40%。如果再转来5名女生，女生占比是多少？"
    )
    
    if result["success"]:
        print("\n📝 解题过程:")
        print("-" * 60)
        print(result["response"])


def demo_role_play():
    """演示角色扮演"""
    print("\n" + "="*60)
    print("📚 演示4: 创意写作（角色扮演）")
    print("="*60)
    
    library = PromptLibrary()
    tester = PromptTester()
    
    template = library.get_template("creative_writer")
    
    result = tester.test_prompt(
        template,
        genre="科幻小说",
        style="简洁有力",
        characteristics="充满想象力且引人深思",
        theme="人工智能觉醒",
        word_count="200",
        elements="一个实验室、一台超级计算机、一个科学家"
    )
    
    if result["success"]:
        print("\n📝 创作内容:")
        print("-" * 60)
        print(result["response"])


def demo_structured_output():
    """演示结构化输出"""
    print("\n" + "="*60)
    print("📚 演示5: 数据提取（结构化输出）")
    print("="*60)
    
    library = PromptLibrary()
    tester = PromptTester()
    
    template = library.get_template("data_extractor")
    
    text = """
张伟，男，28岁，毕业于清华大学计算机系。
现任某互联网公司高级工程师，年薪50万。
联系方式：zhangwei@example.com，手机：13800138000。
"""
    
    fields = """
- name: 姓名
- age: 年龄
- education: 学历
- job: 职位
- salary: 年薪
- email: 邮箱
- phone: 手机号
"""
    
    result = tester.test_prompt(
        template,
        text=text,
        fields=fields
    )
    
    if result["success"]:
        print("\n📝 提取的数据:")
        print("-" * 60)
        print(result["response"])


def demo_comparison():
    """演示不同提示词的效果对比"""
    print("\n" + "="*60)
    print("📚 演示6: 提示词效果对比")
    print("="*60)
    
    tester = PromptTester()
    
    task = "解释什么是递归"
    
    # 差的提示词
    bad_prompt = task
    
    # 好的提示词
    good_prompt = f"""
请解释编程概念：{task}

要求：
1. 用简单易懂的语言
2. 给出一个实际的代码示例
3. 说明使用场景和注意事项
4. 用类比帮助理解
"""
    
    print("\n🔴 差的提示词:")
    print(bad_prompt)
    print("\n回答:")
    print("-" * 60)
    
    result1 = tester.test_prompt(
        PromptTemplate("bad", PromptType.ZERO_SHOT, "", bad_prompt)
    )
    if result1["success"]:
        print(result1["response"][:200] + "...")
    
    print("\n\n🟢 好的提示词:")
    print(good_prompt)
    print("\n回答:")
    print("-" * 60)
    
    result2 = tester.test_prompt(
        PromptTemplate("good", PromptType.ZERO_SHOT, "", good_prompt)
    )
    if result2["success"]:
        print(result2["response"][:200] + "...")


def main():
    """主函数"""
    print("="*60)
    print("🎓 Day 2 - 项目4: Prompt工程模板系统")
    print("="*60)
    
    # 初始化库
    library = PromptLibrary()
    library.list_templates()
    
    # 选择演示
    print("\n请选择要运行的演示:")
    print("1. 代码生成")
    print("2. 文本分类（少样本）")
    print("3. 数学问题（思维链）")
    print("4. 创意写作（角色扮演）")
    print("5. 数据提取（结构化输出）")
    print("6. 提示词效果对比")
    print("7. 全部运行")
    
    choice = input("\n输入选项 (1-7): ").strip()
    
    demos = {
        "1": demo_code_generation,
        "2": demo_few_shot_learning,
        "3": demo_chain_of_thought,
        "4": demo_role_play,
        "5": demo_structured_output,
        "6": demo_comparison,
    }
    
    try:
        if choice == "7":
            for demo in demos.values():
                demo()
                input("\n按回车继续下一个演示...")
        elif choice in demos:
            demos[choice]()
        else:
            print("无效选项")
    
    except Exception as e:
        print(f"\n⚠️  演示出错: {e}")
        print("💡 请确保Ollama正在运行")
    
    # 总结
    print("\n" + "="*60)
    print("📚 Prompt工程关键技巧")
    print("="*60)
    print("""
1. 清晰具体:
   ❌ "写代码"
   ✅ "用Python写一个二分查找函数，包含注释和示例"

2. 提供上下文:
   - 角色设定：你是一个...
   - 任务背景：为了...
   - 输出要求：需要包含...

3. 使用示例（Few-shot）:
   - 给出2-5个示例
   - 示例要有代表性
   - 格式要一致

4. 分步骤思考（Chain-of-Thought）:
   - 引导AI展示思考过程
   - 提高复杂问题的准确性
   - "让我们一步一步思考"

5. 格式化输出:
   - 明确要求输出格式
   - JSON、Markdown、表格等
   - 便于后续处理

6. 迭代优化:
   - 测试不同版本
   - 收集反馈
   - 持续改进

💡 记住：好的Prompt = 清晰的任务 + 充足的上下文 + 具体的要求
    """)


if __name__ == "__main__":
    main()
