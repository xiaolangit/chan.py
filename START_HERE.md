# 🚀 快速开始指南

## 📋 项目概述

您已经拥有了一个完整的**股票买卖信号提取API系统**，支持您的股票列表 `["159647.SZ", "600585.SH"]` 的缠论分析。

## ⚡ 立即开始（3步骤）

### 1️⃣ 启动API服务
```bash
cd API_System
python3 stock_signals_api.py
```

### 2️⃣ 获取您的股票信号
浏览器访问：`http://localhost:5000/api/signals/demo`

或命令行：
```bash
curl http://localhost:5000/api/signals/demo
```

### 3️⃣ 查看客户端演示
```bash
cd API_System
python3 client_demo.py
```

## 📁 项目结构

```
📁 workspace/
├── 🚀 API_System/              # 您的股票信号API（最重要）
├── 📊 Demo_Charts/             # 图表生成（图1、图2）
├── 🧪 Tests/                   # 测试验证
├── 📖 Documentation/          # 使用文档
└── 💾 DataAPI/                # 数据源模块
```

## 🎯 核心功能

✅ **股票信号API**：`/api/signals/demo` - 直接获取您的股票信号  
✅ **批量分析**：`/api/signals/batch` - 一次分析多个股票  
✅ **多时间框架**：支持1分钟到月线  
✅ **自动容错**：真实数据源失效时自动切换模拟数据  
✅ **完整买卖点**：b1, s1, b2, s2, b3a, s3b, 1p, 2s等  

## 📚 详细文档

- **`Documentation/PROJECT_SUMMARY.md`** - 项目总结
- **`Documentation/API_USAGE_GUIDE.md`** - 完整API使用指南
- **`PROJECT_STRUCTURE.md`** - 项目结构说明

## 🔧 依赖安装

如果遇到缺少依赖的问题：
```bash
pip install flask pandas matplotlib numpy requests --break-system-packages
```

## 💡 常用操作

### 获取股票信号（Python）
```python
import requests

# 获取您的股票列表信号
response = requests.post("http://localhost:5000/api/signals/batch", json={
    "codes": ["159647.SZ", "600585.SH"],
    "timeframe": "1d"
})

data = response.json()
print(f"强买入: {data['summary']['strong_buy_stocks']}")
print(f"强卖出: {data['summary']['strong_sell_stocks']}")
```

### 生成图2（4张图合一）
```bash
cd Demo_Charts
python3 demo_qmt_unified_chart_fixed.py
```

现在开始使用您的股票买卖信号API系统吧！🎉