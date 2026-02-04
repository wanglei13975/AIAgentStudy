"""
Day 2 - 项目2: 批量请求处理器
高效处理多个LLM请求
"""

import asyncio
import aiohttp
import time
from typing import List, Dict, Optional
from dataclasses import dataclass
from enum import Enum


class TaskStatus(Enum):
    """任务状态"""
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"


@dataclass
class Task:
    """任务数据类"""
    id: int
    prompt: str
    status: TaskStatus = TaskStatus.PENDING
    response: Optional[str] = None
    error: Optional[str] = None
    start_time: Optional[float] = None
    end_time: Optional[float] = None
    
    @property
    def duration(self) -> float:
        """获取任务耗时"""
        if self.start_time and self.end_time:
            return self.end_time - self.start_time
        return 0.0


class BatchProcessor:
    """批量请求处理器"""
    
    def __init__(
        self, 
        model: str = "qwen2.5:14b",
        max_concurrent: int = 3,
        timeout: int = 60
    ):
        """
        初始化批量处理器
        
        参数:
            model: 模型名称
            max_concurrent: 最大并发数
            timeout: 单个请求超时时间
        """
        self.model = model
        self.max_concurrent = max_concurrent
        self.timeout = timeout
        self.url = "http://localhost:11434/api/chat"
        self.tasks: List[Task] = []
    
    def add_task(self, prompt: str) -> int:
        """添加任务"""
        task_id = len(self.tasks)
        task = Task(id=task_id, prompt=prompt)
        self.tasks.append(task)
        return task_id
    
    def add_tasks(self, prompts: List[str]) -> List[int]:
        """批量添加任务"""
        return [self.add_task(p) for p in prompts]
    
    async def _execute_task(self, task: Task, session: aiohttp.ClientSession):
        """执行单个任务"""
        task.status = TaskStatus.RUNNING
        task.start_time = time.time()
        
        print(f"🟢 任务{task.id} 开始: {task.prompt[:30]}...")
        
        data = {
            "model": self.model,
            "messages": [{"role": "user", "content": task.prompt}],
            "stream": False,
            "keep_alive": "5m",
            "options": {
                "temperature": 0.7,
                "num_ctx": 2048
            }
        }
        
        try:
            async with session.post(
                self.url, 
                json=data, 
                timeout=aiohttp.ClientTimeout(total=self.timeout)
            ) as response:
                result = await response.json()
                task.response = result.get("message", {}).get("content", "")
                task.status = TaskStatus.SUCCESS
                task.end_time = time.time()
                
                print(f"✅ 任务{task.id} 完成 ({task.duration:.1f}秒)")
                
        except asyncio.TimeoutError:
            task.error = "超时"
            task.status = TaskStatus.FAILED
            task.end_time = time.time()
            print(f"❌ 任务{task.id} 超时")
            
        except Exception as e:
            task.error = str(e)
            task.status = TaskStatus.FAILED
            task.end_time = time.time()
            print(f"❌ 任务{task.id} 失败: {str(e)[:50]}")
    
    async def process_all(self, show_progress: bool = True):
        """
        处理所有任务
        
        参数:
            show_progress: 是否显示进度
        """
        if not self.tasks:
            print("⚠️  没有任务需要处理")
            return
        
        print(f"\n{'='*60}")
        print(f"🚀 开始批量处理")
        print(f"{'='*60}")
        print(f"📊 任务总数: {len(self.tasks)}")
        print(f"🔢 最大并发: {self.max_concurrent}")
        print(f"⏱️  超时设置: {self.timeout}秒")
        print(f"{'='*60}\n")
        
        start_time = time.time()
        
        # 使用信号量控制并发数
        semaphore = asyncio.Semaphore(self.max_concurrent)
        
        async def limited_task(task: Task, session: aiohttp.ClientSession):
            async with semaphore:
                await self._execute_task(task, session)
        
        # 创建会话并执行所有任务
        async with aiohttp.ClientSession() as session:
            await asyncio.gather(
                *[limited_task(task, session) for task in self.tasks],
                return_exceptions=True
            )
        
        total_time = time.time() - start_time
        
        # 统计结果
        self._print_summary(total_time)
    
    def _print_summary(self, total_time: float):
        """打印处理摘要"""
        success_count = sum(1 for t in self.tasks if t.status == TaskStatus.SUCCESS)
        failed_count = sum(1 for t in self.tasks if t.status == TaskStatus.FAILED)
        
        print(f"\n{'='*60}")
        print(f"📊 处理完成")
        print(f"{'='*60}")
        print(f"✅ 成功: {success_count}/{len(self.tasks)}")
        print(f"❌ 失败: {failed_count}/{len(self.tasks)}")
        print(f"⏱️  总耗时: {total_time:.2f}秒")
        
        if success_count > 0:
            avg_time = sum(t.duration for t in self.tasks if t.status == TaskStatus.SUCCESS) / success_count
            print(f"📈 平均耗时: {avg_time:.2f}秒")
            print(f"🚀 吞吐量: {success_count / total_time:.2f} 任务/秒")
        
        print(f"{'='*60}\n")
    
    def get_results(self) -> List[Dict]:
        """获取所有结果"""
        return [
            {
                "id": task.id,
                "prompt": task.prompt,
                "response": task.response,
                "status": task.status.value,
                "duration": task.duration,
                "error": task.error
            }
            for task in self.tasks
        ]
    
    def get_successful_results(self) -> List[Dict]:
        """只获取成功的结果"""
        return [
            {
                "id": task.id,
                "prompt": task.prompt,
                "response": task.response,
                "duration": task.duration
            }
            for task in self.tasks
            if task.status == TaskStatus.SUCCESS
        ]
    
    def print_results(self, verbose: bool = False):
        """打印结果"""
        print("\n" + "="*60)
        print("📋 任务结果")
        print("="*60)
        
        for task in self.tasks:
            status_emoji = "✅" if task.status == TaskStatus.SUCCESS else "❌"
            print(f"\n{status_emoji} 任务{task.id}: {task.prompt}")
            print(f"   状态: {task.status.value} | 耗时: {task.duration:.2f}秒")
            
            if task.status == TaskStatus.SUCCESS:
                response_preview = task.response[:100] if not verbose else task.response
                print(f"   回答: {response_preview}...")
            elif task.error:
                print(f"   错误: {task.error}")


# ============================================================
# 使用示例
# ============================================================

async def demo_basic():
    """演示基本用法"""
    print("\n" + "="*60)
    print("📚 演示1: 基本批量处理")
    print("="*60)
    
    processor = BatchProcessor(max_concurrent=3)
    
    # 添加任务
    questions = [
        "什么是Python?",
        "解释一下快速排序",
        "机器学习和深度学习的区别",
        "什么是API?",
        "解释REST架构"
    ]
    
    processor.add_tasks(questions)
    
    # 处理所有任务
    await processor.process_all()
    
    # 查看结果
    processor.print_results()


async def demo_concurrent_control():
    """演示并发控制"""
    print("\n" + "="*60)
    print("📚 演示2: 并发控制对比")
    print("="*60)
    
    questions = [f"用一句话解释概念{i}" for i in range(1, 7)]
    
    # 测试1：低并发
    print("\n🔵 测试1: 最大并发=2")
    processor1 = BatchProcessor(max_concurrent=2)
    processor1.add_tasks(questions)
    
    start = time.time()
    await processor1.process_all()
    time1 = time.time() - start
    
    # 测试2：高并发
    print("\n🟢 测试2: 最大并发=6")
    processor2 = BatchProcessor(max_concurrent=6)
    processor2.add_tasks(questions)
    
    start = time.time()
    await processor2.process_all()
    time2 = time.time() - start
    
    # 对比
    print("\n" + "="*60)
    print("📊 对比结果")
    print("="*60)
    print(f"并发=2: {time1:.2f}秒")
    print(f"并发=6: {time2:.2f}秒")
    print(f"加速比: {time1/time2:.2f}x")


async def demo_error_handling():
    """演示错误处理"""
    print("\n" + "="*60)
    print("📚 演示3: 错误处理")
    print("="*60)
    
    processor = BatchProcessor(max_concurrent=3, timeout=5)  # 短超时
    
    # 添加一些可能超时的复杂任务
    tasks = [
        "简单问题：1+1=?",
        "写一个完整的Web应用（这个可能超时）",
        "另一个简单问题：2+2=?",
    ]
    
    processor.add_tasks(tasks)
    await processor.process_all()
    
    # 只获取成功的结果
    successful = processor.get_successful_results()
    print(f"\n✅ 成功完成 {len(successful)} 个任务")


async def demo_practical_use():
    """演示实际应用场景"""
    print("\n" + "="*60)
    print("📚 演示4: 实际应用 - 批量翻译")
    print("="*60)
    
    processor = BatchProcessor(max_concurrent=5)
    
    # 批量翻译任务
    sentences = [
        "Hello, how are you?",
        "Good morning!",
        "Thank you very much.",
        "See you later.",
        "Have a nice day!"
    ]
    
    # 创建翻译提示
    prompts = [f"将以下英文翻译成中文，只返回翻译结果：{s}" for s in sentences]
    processor.add_tasks(prompts)
    
    await processor.process_all()
    
    # 展示翻译结果
    print("\n翻译结果:")
    print("-" * 60)
    for i, task in enumerate(processor.tasks):
        if task.status == TaskStatus.SUCCESS:
            print(f"{sentences[i]:30} → {task.response}")


async def main():
    """主函数"""
    print("="*60)
    print("🎓 Day 2 - 项目2: 批量请求处理器")
    print("="*60)
    
    try:
        # 运行所有演示
        await demo_basic()
        
        # 其他演示（可选）
        choice = input("\n是否运行其他演示？(y/n): ")
        if choice.lower() == 'y':
            await demo_concurrent_control()
            await demo_error_handling()
            await demo_practical_use()
    
    except Exception as e:
        print(f"\n⚠️  演示出错: {e}")
        print("💡 请确保Ollama正在运行")
    
    # 总结
    print("\n" + "="*60)
    print("📚 关键知识点")
    print("="*60)
    print("""
1. 批量处理的优势:
   - 提高吞吐量
   - 更好的资源利用
   - 统一的错误处理

2. 并发控制:
   - 使用Semaphore限制并发数
   - 避免过载服务器
   - 平衡速度和稳定性

3. 实际应用:
   - 批量翻译
   - 批量内容生成
   - 并行数据处理
   - 多任务自动化

4. 最佳实践:
   - 合理设置并发数（3-10）
   - 设置超时避免卡死
   - 优雅处理失败任务
   - 记录和监控进度
    """)


if __name__ == "__main__":
    asyncio.run(main())
