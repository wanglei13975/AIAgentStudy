# 练习3：温度对比实验 - 观察指南

## 📋 实验目标
理解温度参数(temperature)如何影响AI的输出

---

## 🧪 实验步骤

### 方式一：自动化实验（推荐）
```bash
python exercise3_temperature_experiment.py
```
- ✅ 自动测试3个温度
- ✅ 生成详细报告
- ✅ 自动保存结果

### 方式二：手动实验（适合仔细观察）
```bash
python exercise3_manual.py
```
- ✅ 逐步测试，方便对比
- ✅ 可以暂停思考
- ✅ 交互式体验

---

## 🔍 观察重点

### 1. 代码实现方式

**低温 (0.1)** 通常会：
- ✅ 选择最标准、最常见的实现
- ✅ 代码结构规范
- ✅ 每次运行结果高度一致

**中温 (0.5)** 通常会：
- ✅ 在标准实现基础上有小变化
- ✅ 可能添加一些优化
- ✅ 保持稳定性同时有一定变化

**高温 (0.9)** 通常会：
- ✅ 可能尝试不同的实现方式
- ✅ 代码风格更多样
- ⚠️ 可能出现不常见但有趣的写法

### 2. 注释和文档

观察每个温度下：
- 📝 注释的详细程度
- 📖 是否包含docstring
- 💬 解释的风格

**记录方法：**
```
Temperature 0.1:
- 注释数量: ____ 个
- 有docstring: 是/否
- 注释风格: 简洁/详细

Temperature 0.5:
- 注释数量: ____ 个
- 有docstring: 是/否
- 注释风格: 简洁/详细

Temperature 0.9:
- 注释数量: ____ 个
- 有docstring: 是/否
- 注释风格: 简洁/详细
```

### 3. 代码复杂度

对比分析：
- 📏 代码行数
- 🔧 函数数量
- 🎨 是否有额外的辅助函数
- 🧪 是否包含测试代码

### 4. 额外内容

检查是否包含：
- ✅ 使用示例
- ✅ 时间复杂度分析
- ✅ 空间复杂度分析
- ✅ 优化建议
- ✅ 边界情况处理

---

## 📊 记录表格

复制这个表格并填写你的观察结果：

```markdown
| 特征 | Temp 0.1 | Temp 0.5 | Temp 0.9 |
|------|----------|----------|----------|
| 回复长度(字符) | | | |
| 代码行数 | | | |
| 注释数量 | | | |
| 函数数量 | | | |
| 实现方法 | | | |
| 是否有测试 | | | |
| 是否有示例 | | | |
| 整体评分(1-5) | | | |
```

---

## 🎯 预期结果

基于大量实验，通常会观察到：

### Temperature 0.1 (低温)
```python
# 典型特征:
# - 代码简洁、标准
# - 注释适中
# - 实现最常见的版本
# - 每次运行几乎相同

def quicksort(arr):
    if len(arr) <= 1:
        return arr
    pivot = arr[len(arr) // 2]
    left = [x for x in arr if x < pivot]
    middle = [x for x in arr if x == pivot]
    right = [x for x in arr if x > pivot]
    return quicksort(left) + middle + quicksort(right)
```

### Temperature 0.5 (中温)
```python
# 典型特征:
# - 可能添加更多注释
# - 可能包含使用示例
# - 实现有小变化但仍然标准
# - 有一定随机性

def quicksort(arr):
    """
    快速排序实现
    时间复杂度: O(n log n)
    """
    if len(arr) <= 1:
        return arr
    
    pivot = arr[len(arr) // 2]
    left = [x for x in arr if x < pivot]
    middle = [x for x in arr if x == pivot]
    right = [x for x in arr if x > pivot]
    
    return quicksort(left) + middle + quicksort(right)

# 使用示例
arr = [3, 6, 8, 10, 1, 2, 1]
print(quicksort(arr))
```

### Temperature 0.9 (高温)
```python
# 典型特征:
# - 可能尝试不同的实现方式
# - 注释可能更详细或更随意
# - 可能包含多种优化
# - 每次运行差异较大

def quicksort(arr):
    """
    快速排序 - 高效的分治排序算法
    
    原理: 选择一个基准元素，将数组分为小于和大于基准的两部分
    平均时间复杂度: O(n log n)
    最坏时间复杂度: O(n²)
    空间复杂度: O(log n)
    """
    if not arr or len(arr) == 1:
        return arr
    
    # 选择中间元素作为基准
    pivot_index = len(arr) // 2
    pivot = arr[pivot_index]
    
    # 分区
    left_part = []
    equal_part = []
    right_part = []
    
    for element in arr:
        if element < pivot:
            left_part.append(element)
        elif element == pivot:
            equal_part.append(element)
        else:
            right_part.append(element)
    
    # 递归排序并合并
    return quicksort(left_part) + equal_part + quicksort(right_part)


# 测试函数
def test_quicksort():
    test_cases = [
        [3, 6, 8, 10, 1, 2, 1],
        [1],
        [],
        [5, 5, 5, 5],
    ]
    
    for test in test_cases:
        print(f"输入: {test}")
        print(f"输出: {quicksort(test.copy())}")
        print()

if __name__ == "__main__":
    test_quicksort()
```

---

## 💡 思考题

完成实验后，回答以下问题：

### Q1: 代码生成任务应该用什么温度？
**你的答案：**
```
温度: ____
理由: 




```

### Q2: 三次生成的代码，你最喜欢哪个？为什么？
**你的答案：**
```
选择: Temperature = ____
理由:




```

### Q3: 如果让你用这个代码，你会选哪个？
**你的答案：**
```
选择: Temperature = ____
理由:




```

### Q4: 温度参数在什么场景下最重要？
**你的答案：**
```
场景:




```

---

## 🎓 学到的知识

完成实验后，你应该理解：

✅ **温度参数的本质**
- 控制输出的随机性
- 影响token选择的概率分布

✅ **低温的特点**
- 输出确定、可预测
- 适合需要准确答案的任务
- 缺乏创造性

✅ **高温的特点**
- 输出多样、有创意
- 适合头脑风暴、创意写作
- 可能不够稳定

✅ **实际应用**
- 代码生成：0.1-0.3
- 日常对话：0.5-0.7
- 创意写作：0.7-0.9

---

## 🔬 进阶实验（可选）

如果你想深入探索：

### 实验4.1: 更细粒度的温度
测试: 0.0, 0.2, 0.4, 0.6, 0.8, 1.0

### 实验4.2: 多次采样
用同一个温度(如0.9)运行5次，观察结果的一致性

### 实验4.3: 不同类型的问题
- 数学题（应该用低温）
- 创意故事（应该用高温）
- 解释概念（中温即可）

---

## 📝 提交作业

完成后，准备以下内容：

1. ✅ 填写好的观察记录表
2. ✅ 回答所有思考题
3. ✅ 保存的三次实验结果
4. ✅ 你的总结（100字以上）

**总结模板：**
```
通过这次实验，我发现...

温度参数的作用是...

在实际应用中，我会...

最让我意外的发现是...
```

---

## 🚀 下一步

理解温度参数后，明天我们将学习：
- 更多的模型参数（top_p, top_k等）
- 提示工程技巧
- 如何结合参数优化输出

继续加油！💪
