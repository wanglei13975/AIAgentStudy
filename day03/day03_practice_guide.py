"""
Day 3 练习指南
一步步完成3个练习，掌握Agent核心技能

运行方式：
python day03_practice_guide.py

按顺序完成每个练习，我会带着你一步步走。
"""


def show_menu():
    """显示菜单"""
    print("\n" + "="*70)
    print("🎓 Day 3 练习指南")
    print("="*70)
    print("""
选择你要完成的练习：

练习1：添加新工具 ⭐
  难度：简单
  时间：15分钟
  学习：如何扩展Agent的能力
  
练习2：多步推理任务 ⭐⭐
  难度：中等
  时间：20分钟
  学习：Agent如何链式使用工具
  
练习3：优化提示词 ⭐⭐⭐
  难度：进阶
  时间：25分钟
  学习：如何写出好的系统提示词

💡 建议：按顺序完成，难度递增
    """)


def practice1_guide():
    """练习1指导"""
    print("\n" + "="*70)
    print("📝 练习1：添加新工具")
    print("="*70)
    
    print("""
🎯 目标：
给Agent添加一个天气查询工具

📚 学习内容：
1. 如何定义工具函数
2. 如何描述工具
3. 如何添加到工具列表
4. Agent如何使用新工具

🔧 具体步骤：
1. 定义weather函数
2. 创建工具描述
3. 添加到tools列表
4. 测试Agent

⏱️  预计时间：15分钟

准备好了吗？
    """)
    
    choice = input("输入'start'开始练习，或'back'返回: ").strip().lower()
    
    if choice == 'start':
        print("\n✅ 开始练习1！")
        print("运行以下命令：")
        print("\npython practice1_add_tool.py")
        print("\n按照提示一步步完成\n")
    else:
        return


def practice2_guide():
    """练习2指导"""
    print("\n" + "="*70)
    print("📝 练习2：多步推理任务")
    print("="*70)
    
    print("""
🎯 目标：
让Agent完成需要多个步骤的复杂任务

任务："查询现在几点，然后计算距离中午12点还有多长时间"

📚 学习内容：
1. 任务分解
2. 中间结果的使用
3. 链式工具调用
4. Agent的记忆

🔧 步骤：
1. 理解多步推理
2. 手动演示过程
3. 创建支持多步的Agent
4. 自动执行任务

⏱️  预计时间：20分钟

这个练习很重要！多步推理是Agent的核心能力。
    """)
    
    choice = input("输入'start'开始练习，或'back'返回: ").strip().lower()
    
    if choice == 'start':
        print("\n✅ 开始练习2！")
        print("运行以下命令：")
        print("\npython practice2_multi_step.py")
        print("\n按照提示一步步完成\n")
    else:
        return


def practice3_guide():
    """练习3指导"""
    print("\n" + "="*70)
    print("📝 练习3：优化系统提示词")
    print("="*70)
    
    print("""
🎯 目标：
学习如何写出高质量的系统提示词

📚 学习内容：
1. 提示词的重要性
2. 好提示词 vs 差提示词
3. 提示词的关键要素
4. 优化技巧

🔧 内容：
1. 理解提示词作用
2. 对比好坏示例
3. 学习优化技巧
4. 完整模板

⏱️  预计时间：25分钟

💡 这是最重要的练习！
   好的提示词能让Agent：
   - 更准确
   - 更高效
   - 更可控
    """)
    
    choice = input("输入'start'开始练习，或'back'返回: ").strip().lower()
    
    if choice == 'start':
        print("\n✅ 开始练习3！")
        print("运行以下命令：")
        print("\npython practice3_optimize_prompt.py")
        print("\n这是理论+实践结合的练习\n")
    else:
        return


def show_summary():
    """显示总结"""
    print("\n" + "="*70)
    print("📚 练习总结")
    print("="*70)
    
    print("""
完成3个练习后，你将掌握：

✅ 练习1：工具扩展
   - 如何添加新功能
   - 工具的三要素
   - 描述的重要性

✅ 练习2：多步推理
   - 复杂任务分解
   - 链式工具调用
   - 中间结果管理

✅ 练习3：提示词优化
   - 提示词结构
   - 优化技巧
   - 最佳实践

🎯 综合能力：
构建一个：
- 能力可扩展（添加工具）
- 能处理复杂任务（多步推理）
- 行为可控（好的提示词）
的实用Agent！

💡 下一步：
- 练习添加更多工具
- 尝试更复杂的任务
- 优化提示词
- 为Day 4做准备
    """)


def check_progress():
    """检查进度"""
    print("\n" + "="*70)
    print("📊 学习进度检查")
    print("="*70)
    
    print("""
请诚实回答以下问题：

1. 你理解工具的三要素了吗？
   - name（名称）
   - description（描述）
   - function（函数）

2. 你能解释多步推理的过程吗？
   - 第一步获取信息
   - 基于结果决定下一步
   - 链式调用直到完成

3. 你知道好的提示词应该包含什么吗？
   - 角色定位
   - 工具说明
   - 工作流程
   - 输出格式
   - 注意事项

如果有不清楚的，回去重新做那个练习！
    """)


def main():
    """主函数"""
    print("="*70)
    print("🎓 Day 3 练习指南")
    print("="*70)
    print("""
欢迎来到Day 3的练习环节！

我会带你完成3个练习，每个练习都有：
- 清晰的目标
- 详细的步骤
- 实际的代码
- 知识点总结

准备好了吗？让我们开始吧！
    """)
    
    while True:
        print("\n" + "-"*70)
        print("请选择：")
        print("  1 - 练习1：添加新工具")
        print("  2 - 练习2：多步推理")
        print("  3 - 练习3：优化提示词")
        print("  4 - 查看总结")
        print("  5 - 进度检查")
        print("  0 - 退出")
        print("-"*70)
        
        choice = input("\n输入选项 (0-5): ").strip()
        
        if choice == '1':
            practice1_guide()
        elif choice == '2':
            practice2_guide()
        elif choice == '3':
            practice3_guide()
        elif choice == '4':
            show_summary()
        elif choice == '5':
            check_progress()
        elif choice == '0':
            print("\n" + "="*70)
            print("👋 练习结束！")
            print("="*70)
            print("""
记住今天学到的：
✅ 如何添加工具
✅ 如何多步推理
✅ 如何优化提示词

这些是构建实用Agent的核心技能！

明天我们会学习更多高级内容。
继续加油！💪
            """)
            break
        else:
            print("\n❌ 无效选项，请重新选择")


if __name__ == "__main__":
    main()
