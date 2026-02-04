"""
Day 2 - 项目2: 批量请求处理器（修复超时版）
使用流式输出和keep_alive避免超时
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
    """批量请求处理器（优化版）"""
    
    def __init__(
        self, 
        model: str = "qwen2.5:14b",
        max_concurrent: int = 3,
        timeout: int = 180  # 增加到3分钟
    ):
        """
        初始化批量处理器
        
        参数:
            model: 模型名称
            max_concurrent: 最大并发数
            timeout: 单个请求超时时间（秒）
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
    
    async def _execute_task_stream(self, task: Task, session: aiohttp.ClientSession):
        """
        执行单个任务（流式输出，避免超时）
        """
        task.status = TaskStatus.RUNNING
        task.start_time = time.time()
        
        print(f"🟢 任务{task.id} 开始: {task.prompt[:40]}...")
        
        data = {
            "model": self.model,
            "messages": [{"role": "user", "content": task.prompt}],
            "stream": True,  # 关键：使用流式输出
            "keep_alive": "10m",  # 关键：保持模型在内存
            "options": {
                "temperature": 0.7,
                "num_ctx": 2048,
                "num_predict": 500  # 限制输出长度，加快速度
            }
        }
        
        try:
            async with session.post(
                self.url, 
                json=data,
                timeout=aiohttp.ClientTimeout(total=self.timeout)
            ) as response:
                # 流式接收
                full_response = ""
                first_chunk = True
                
                async for line in response.content:
                    if line:
                        try:
                            import json
                            chunk = json.loads(line)
                            content = chunk.get("message", {}).get("content", "")
                            
                            if first_chunk and content:
                                elapsed = time.time() - task.start_time
                                print(f"   ⚡ 任务{task.id} 首次响应: {elapsed:.1f}秒")
                                first_chunk = False
                            
                            full_response += content
                            
                        except json.JSONDecodeError:
                            continue
                
                task.response = full_response
                task.status = TaskStatus.SUCCESS
                task.end_time = time.time()
                
                print(f"✅ 任务{task.id} 完成 ({task.duration:.1f}秒) - {len(full_response)} 字符")
                
        except asyncio.TimeoutError:
            task.error = "超时"
            task.status = TaskStatus.FAILED
            task.end_time = time.time()
            print(f"❌ 任务{task.id} 超时 ({task.duration:.0f}秒)")
            
        except Exception as e:
            task.error = str(e)
            task.status = TaskStatus.FAILED
            task.end_time = time.time()
            print(f"❌ 任务{task.id} 失败: {str(e)[:50]}")
    
    async def process_all(self, show_progress: bool = True):
        """处理所有任务"""
        if not self.tasks:
            print("⚠️  没有任务需要处理")
            return
        
        print(f"\n{'='*70}")
        print(f"🚀 开始批量处理（优化版）")
        print(f"{'='*70}")
        print(f"📊 任务总数: {len(self.tasks)}")
        print(f"🔢 最大并发: {self.max_concurrent}")
        print(f"⏱️  超时设置: {self.timeout}秒")
        print(f"💡 使用流式输出 + keep_alive 优化")
        print(f"{'='*70}\n")
        
        start_time = time.time()
        
        # 使用信号量控制并发数
        semaphore = asyncio.Semaphore(self.max_concurrent)
        
        async def limited_task(task: Task, session: aiohttp.ClientSession):
            async with semaphore:
                await self._execute_task_stream(task, session)
        
        # 创建会话并执行所有任务
        connector = aiohttp.TCPConnector(limit=10)  # 连接池
        async with aiohttp.ClientSession(connector=connector) as session:
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
        
        print(f"\n{'='*70}")
        print(f"📊 处理完成")
        print(f"{'='*70}")
        print(f"✅ 成功: {success_count}/{len(self.tasks)}")
        print(f"❌ 失败: {failed_count}/{len(self.tasks)}")
        print(f"⏱️  总耗时: {total_time:.2f}秒")
        
        if success_count > 0:
            avg_time = sum(t.duration for t in self.tasks if t.status == TaskStatus.SUCCESS) / success_count
            print(f"📈 平均耗时: {avg_time:.2f}秒/任务")
            print(f"🚀 吞吐量: {success_count / total_time:.2f} 任务/秒")
            
            # 首次响应时间
            first_responses = [
                t.duration for t in self.tasks 
                if t.status == TaskStatus.SUCCESS
            ]
            if first_responses:
                print(f"⚡ 平均响应: {sum(first_responses)/len(first_responses):.1f}秒")
        
        print(f"{'='*70}\n")
    
    def print_results(self, verbose: bool = False):
        """打印结果"""
        print("\n" + "="*70)
        print("📋 任务结果详情")
        print("="*70)
        
        for task in self.tasks:
            status_emoji = "✅" if task.status == TaskStatus.SUCCESS else "❌"
            print(f"\n{status_emoji} 任务{task.id}: {task.prompt[:50]}")
            print(f"   状态: {task.status.value} | 耗时: {task.duration:.2f}秒")
            
            if task.status == TaskStatus.SUCCESS:
                preview_len = 150 if not verbose else 500
                response_preview = task.response[:preview_len] if task.response else ""
                print(f"   回答: {response_preview}...")
            elif task.error:
                print(f"   错误: {task.error}")


# ============================================================
# 使用示例
# ============================================================

async def demo_basic():
    """演示基本用法"""
    print("\n" + "="*70)
    print("📚 演示1: 基本批量处理（优化版）")
    print("="*70)
    
    processor = BatchProcessor(max_concurrent=3, timeout=180)
    
    # 添加任务（使用更简单的问题）
    questions = [
        "1+1等于几？",
        "什么是Python？用一句话回答。",
        "快速排序的时间复杂度是？",
        "什么是API？用一句话回答。",
        "HTTP和HTTPS的区别？用一句话回答。"
    ]
    
    processor.add_tasks(questions)
    
    # 处理所有任务
    await processor.process_all()
    
    # 查看结果
    processor.print_results()


async def demo_simple_questions():
    """演示简单问题（应该很快）"""
    print("\n" + "="*70)
    print("📚 演示2: 简单问题批处理")
    print("="*70)
    
    processor = BatchProcessor(max_concurrent=5, timeout=120)
    
    # 非常简单的问题
    questions = [
        "2+2=?",
        "Python是什么语言？",
        "AI是什么？",
        "1+1=?",
        "什么是编程？",
        "什么是变量？",
        "什么是函数？",
        "什么是循环？"
    ]
    
    print(f"\n准备处理 {len(questions)} 个简单问题...")
    processor.add_tasks(questions)
    
    await processor.process_all()
    
    # 显示结果
    success = [t for t in processor.tasks if t.status == TaskStatus.SUCCESS]
    print(f"\n✅ 成功完成 {len(success)}/{len(questions)} 个问题")
    
    if success:
        print("\n前3个成功的回答:")
        for task in success[:3]:
            print(f"\nQ: {task.prompt}")
            print(f"A: {task.response[:100]}...")


async def demo_with_progress():
    """演示带详细进度的处理"""
    print("\n" + "="*70)
    print("📚 演示3: 实时进度监控")
    print("="*70)
    
    processor = BatchProcessor(max_concurrent=2, timeout=150)
    
    questions = [
        "解释递归（50字以内）",
        "解释迭代（50字以内）",
        "解释面向对象（50字以内）"
    ]
    
    processor.add_tasks(questions)
    await processor.process_all()
    
    processor.print_results(verbose=True)


async def check_ollama():
    """检查Ollama状态"""
    print("🔍 检查Ollama连接...")
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                "http://localhost:11434/api/tags",
                timeout=aiohttp.ClientTimeout(total=5)
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    models = data.get('models', [])
                    print(f"✅ Ollama运行正常")
                    print(f"📦 可用模型: {len(models)} 个")
                    for model in models[:3]:
                        print(f"   - {model.get('name', 'unknown')}")
                    return True
    except Exception as e:
        print(f"❌ 无法连接Ollama: {e}")
        print("💡 请确保Ollama正在运行: ollama serve")
        return False
    
    return False


async def main():
    """主函数"""
    print("="*70)
    print("🎓 Day 2 - 项目2: 批量请求处理器（修复版）")
    print("="*70)
    
    # 检查Ollama
    if not await check_ollama():
        print("\n⚠️  请先启动Ollama")
        return
    
    print("\n" + "="*70)
    
    try:
        # 先运行简单演示
        await demo_simple_questions()
        
        # 询问是否继续
        print("\n" + "="*70)
        choice = input("\n是否运行其他演示？(y/n): ")
        
        if choice.lower() == 'y':
            await demo_basic()
            
            choice2 = input("\n继续运行详细演示？(y/n): ")
            if choice2.lower() == 'y':
                await demo_with_progress()
    
    except KeyboardInterrupt:
        print("\n\n⚠️  用户中断")
    except Exception as e:
        print(f"\n⚠️  演示出错: {e}")
        import traceback
        traceback.print_exc()
    
    # 总结
    print("\n" + "="*70)
    print("📚 批量处理关键技巧")
    print("="*70)
    print("""
✅ 优化要点:

1. 使用流式输出（stream=True）
   - 避免长时间等待
   - 实时看到进度
   - 不容易超时

2. 使用keep_alive
   - 保持模型在内存
   - 后续请求更快
   - 减少加载时间

3. 控制并发数
   - 2-5个并发较稳定
   - 避免过载
   - 根据系统资源调整

4. 增加超时时间
   - 首次请求较慢（加载模型）
   - 建议150-180秒
   - 后续请求会快很多

5. 简化问题
   - 测试时用简单问题
   - 确保基本功能正常
   - 再处理复杂任务

💡 如果还是超时:
   - 使用更小的模型（qwen2.5:7b）
   - 减少并发数到1-2
   - 增加超时到300秒
   - 限制输出长度（num_predict）
    """)


if __name__ == "__main__":
    asyncio.run(main())
