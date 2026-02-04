"""
练习3：温度对比实验
自动测试不同温度参数对AI回复的影响
"""

import requests
import json
import time
from datetime import datetime


class TemperatureExperiment:
    """温度对比实验类"""
    
    def __init__(self, model: str = "qwen2.5:14b"):
        self.model = model
        self.url = "http://localhost:11434/api/chat"
        self.session = requests.Session()
    
    def test_temperature(self, question: str, temperature: float) -> dict:
        """
        测试指定温度下的回复
        
        返回:
            {
                'temperature': float,
                'response': str,
                'time': float,
                'tokens': int (如果可用)
            }
        """
        print(f"\n{'='*70}")
        print(f"🌡️  测试温度: {temperature}")
        print(f"{'='*70}")
        
        data = {
            "model": self.model,
            "messages": [{"role": "user", "content": question}],
            "stream": False,
            "keep_alive": "5m",
            "options": {
                "temperature": temperature,
                "num_ctx": 2048,
            }
        }
        
        print("🤔 思考中...")
        start_time = time.time()
        
        try:
            response = self.session.post(self.url, json=data, timeout=120)
            response.raise_for_status()
            
            result = response.json()
            elapsed = time.time() - start_time
            
            assistant_message = result.get("message", {}).get("content", "")
            
            print(f"\n🤖 AI回复:")
            print("-" * 70)
            print(assistant_message)
            print("-" * 70)
            print(f"⏱️  耗时: {elapsed:.2f}秒")
            
            return {
                'temperature': temperature,
                'response': assistant_message,
                'time': elapsed,
                'length': len(assistant_message)
            }
        
        except Exception as e:
            print(f"❌ 错误: {e}")
            return {
                'temperature': temperature,
                'response': f"错误: {str(e)}",
                'time': 0,
                'length': 0
            }
    
    def run_experiment(self, question: str, temperatures: list):
        """
        运行完整实验
        
        参数:
            question: 测试问题
            temperatures: 温度列表，如 [0.1, 0.5, 0.9]
        """
        print("\n" + "="*70)
        print("🔬 温度对比实验开始")
        print("="*70)
        print(f"📝 测试问题: {question}")
        print(f"🌡️  测试温度: {temperatures}")
        print(f"🤖 使用模型: {self.model}")
        print("="*70)
        
        # 收集所有结果
        results = []
        
        for temp in temperatures:
            result = self.test_temperature(question, temp)
            results.append(result)
            
            # 等待一下，避免请求过快
            if temp != temperatures[-1]:
                print("\n⏸️  等待3秒...")
                time.sleep(3)
        
        # 生成对比报告
        self.generate_report(question, results)
        
        return results
    
    def generate_report(self, question: str, results: list):
        """生成详细的对比报告"""
        
        print("\n" + "="*70)
        print("📊 实验报告")
        print("="*70)
        
        # 基本统计
        print(f"\n📝 测试问题: {question}")
        print(f"🔢 测试次数: {len(results)}")
        print(f"⏱️  总耗时: {sum(r['time'] for r in results):.2f}秒")
        
        # 每个温度的统计
        print("\n" + "-"*70)
        print("各温度参数对比:")
        print("-"*70)
        
        for result in results:
            temp = result['temperature']
            response_length = result['length']
            time_taken = result['time']
            
            print(f"\n🌡️  Temperature: {temp}")
            print(f"   📏 回复长度: {response_length} 字符")
            print(f"   ⏱️  耗时: {time_taken:.2f}秒")
            print(f"   📝 回复预览: {result['response'][:100]}...")
        
        # 分析差异
        print("\n" + "-"*70)
        print("🔍 差异分析:")
        print("-"*70)
        
        lengths = [r['length'] for r in results]
        print(f"📏 回复长度变化: {min(lengths)} → {max(lengths)} 字符")
        print(f"   差异: {max(lengths) - min(lengths)} 字符 ({(max(lengths) - min(lengths)) / min(lengths) * 100:.1f}%)")
        
        # 保存报告
        self.save_report(question, results)
    
    def save_report(self, question: str, results: list):
        """保存实验报告到文件"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"temperature_experiment_{timestamp}.md"
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write("# 温度对比实验报告\n\n")
            f.write(f"**实验时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write(f"**测试问题**: {question}\n\n")
            f.write(f"**使用模型**: {self.model}\n\n")
            
            f.write("---\n\n")
            
            for i, result in enumerate(results, 1):
                f.write(f"## 测试 {i}: Temperature = {result['temperature']}\n\n")
                f.write(f"- **回复长度**: {result['length']} 字符\n")
                f.write(f"- **耗时**: {result['time']:.2f}秒\n\n")
                f.write("### 完整回复:\n\n")
                f.write("```python\n" if "def " in result['response'] or "import " in result['response'] else "```\n")
                f.write(result['response'])
                f.write("\n```\n\n")
                f.write("---\n\n")
            
            f.write("## 观察总结\n\n")
            f.write("### 温度参数的影响:\n\n")
            f.write("1. **Temperature = 0.1 (低温)**\n")
            f.write("   - 回复更加确定和一致\n")
            f.write("   - 代码风格更规范\n")
            f.write("   - 创造性较低\n\n")
            
            f.write("2. **Temperature = 0.5 (中温)**\n")
            f.write("   - 平衡了确定性和多样性\n")
            f.write("   - 适合大多数场景\n\n")
            
            f.write("3. **Temperature = 0.9 (高温)**\n")
            f.write("   - 回复更加多样化\n")
            f.write("   - 可能出现更创新的方法\n")
            f.write("   - 但也可能不太稳定\n\n")
        
        print(f"\n✅ 报告已保存到: {filename}")


def analyze_code_differences(results: list):
    """深入分析代码的差异"""
    print("\n" + "="*70)
    print("🔬 代码差异深度分析")
    print("="*70)
    
    for i, result in enumerate(results, 1):
        response = result['response']
        temp = result['temperature']
        
        print(f"\n🌡️  Temperature {temp}:")
        
        # 检查是否包含注释
        comment_count = response.count('#')
        print(f"   💬 注释数量: {comment_count}")
        
        # 检查是否包含文档字符串
        docstring_count = response.count('"""') + response.count("'''")
        print(f"   📖 文档字符串: {docstring_count // 2}")
        
        # 检查函数定义
        func_count = response.count('def ')
        print(f"   🔧 函数定义: {func_count}")
        
        # 代码行数估计
        lines = len(response.split('\n'))
        print(f"   📏 代码行数: {lines}")


def main():
    """主函数"""
    print("🔬 温度对比实验 - 练习3")
    print()
    
    # 创建实验对象
    experiment = TemperatureExperiment()
    
    # 实验问题
    question = "用Python写一个快速排序"
    
    # 测试的温度
    temperatures = [0.1, 0.5, 0.9]
    
    # 运行实验
    results = experiment.run_experiment(question, temperatures)
    
    # 深度分析
    analyze_code_differences(results)
    
    # 总结
    print("\n" + "="*70)
    print("📚 学习总结")
    print("="*70)
    print("""
温度参数(temperature)的作用:

🌡️  Temperature 控制模型输出的随机性

📉 低温 (0.1 - 0.3):
   ✅ 输出更确定、一致
   ✅ 适合需要准确答案的任务（代码生成、数学计算）
   ❌ 缺乏创造性和多样性
   
🌡️  中温 (0.5 - 0.7):
   ✅ 平衡了准确性和创造性
   ✅ 适合大多数对话场景
   ✅ 这是推荐的默认值
   
🔥 高温 (0.8 - 1.0):
   ✅ 输出更多样化和创造性
   ✅ 适合创意写作、头脑风暴
   ❌ 可能不够准确或稳定
   ❌ 代码可能出现语法错误

💡 实用建议:
   - 代码生成: 0.1 - 0.3
   - 日常对话: 0.5 - 0.7
   - 创意写作: 0.7 - 0.9
   - 多次采样: 0.8 - 1.0
    """)
    
    print("\n✅ 实验完成！查看保存的报告文件了解更多细节。")


if __name__ == "__main__":
    main()
