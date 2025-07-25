# 📁 项目文件结构说明

## 🎯 整理后的目录结构

```
📁 workspace/
├── 📁 API_System/              # 🚀 核心API系统
│   ├── 📄 stock_signals_api.py     # 主API服务器
│   ├── 📄 client_demo.py           # 客户端演示
│   ├── 📄 test_stock_api.py        # API功能测试
│   └── 📄 simple_test.py           # 简单功能测试
│
├── 📁 Demo_Charts/             # 📊 图表演示系统
│   ├── 📄 demo_qmt.py                      # 原始单图演示（图1）
│   ├── 📄 demo_qmt_multi_timeframe.py      # 多时间框架演示
│   ├── 📄 demo_qmt_advanced_multi.py       # 高级多图演示
│   ├── 📄 demo_qmt_unified_chart_fixed.py  # 统一图表（图2修复版）
│   ├── 📄 demo_qmt_unified_chart_complete.py # 完整版统一图表
│   └── 📄 run_multi_timeframe.py           # 多时间框架运行器
│
├── 📁 Tests/                   # 🧪 测试文件
│   ├── 📄 test_fixed_bsp.py         # 买卖点修复测试
│   ├── 📄 test_unified_chart.py     # 统一图表测试
│   └── 📄 test_warning_fix.py       # 警告修复测试
│
├── 📁 Documentation/          # 📖 文档和配置
│   ├── 📄 PROJECT_SUMMARY.md        # 项目总结
│   ├── 📄 API_USAGE_GUIDE.md        # API使用指南
│   ├── 📄 STOCK_SIGNALS_API.md      # API技术文档
│   ├── 📄 README_MultiTimeframe.md  # 多时间框架说明
│   ├── 📄 SUMMARY.md               # 系统总结
│   ├── 📄 WARNING_FIXED.md         # 警告修复说明
│   ├── 📄 BUY_SELL_POINTS_FIXED.md # 买卖点修复说明
│   ├── 📄 quick_guide.md           # 快速指南
│   └── 📄 requirements.txt         # Python依赖
│
├── 📁 DataAPI/                # 💾 数据源模块
│   ├── 📄 QmtStockAPI.py           # QMT真实数据源
│   ├── 📄 MockStockAPI.py          # 模拟数据源
│   └── 📄 CommonStockAPI.py        # 数据源基类
│
└── 📁 [缠论核心模块]/         # 🧠 原有缠论系统
    ├── 📁 Chan/                    # 主分析模块
    ├── 📁 Plot/                    # 绘图模块
    ├── 📁 Common/                  # 公共工具
    ├── 📁 KLine/                   # K线模块
    ├── 📁 Bi/                      # 笔模块
    ├── 📁 Seg/                     # 段模块
    ├── 📁 ZS/                      # 中枢模块
    └── 📁 BuySellPoint/           # 买卖点模块
```

## 🚀 快速启动指南

### 1️⃣ 启动API服务
```bash
cd API_System
python3 stock_signals_api.py
```

### 2️⃣ 运行客户端演示
```bash
cd API_System
python3 client_demo.py
```

### 3️⃣ 生成图表演示
```bash
cd Demo_Charts
python3 demo_qmt_unified_chart_fixed.py
```

### 4️⃣ 运行测试
```bash
cd Tests
python3 test_fixed_bsp.py
```

## 📂 目录功能说明

### 🚀 API_System/ - 核心API系统
**最重要的目录**，包含您需要的股票信号API：

- **`stock_signals_api.py`** - 主API服务，提供RESTful接口
- **`client_demo.py`** - 客户端演示，展示如何调用API
- **`test_stock_api.py`** - API功能测试
- **`simple_test.py`** - 简单功能验证

### 📊 Demo_Charts/ - 图表演示系统
包含各种图表生成演示：

- **`demo_qmt_unified_chart_fixed.py`** - 🔥 **图2实现**（4张图合一+买卖点）
- **`demo_qmt.py`** - 图1原始演示
- **`run_multi_timeframe.py`** - 自动化运行脚本

### 🧪 Tests/ - 测试文件
各种功能测试和验证：

- **`test_fixed_bsp.py`** - 买卖点修复验证
- **`test_unified_chart.py`** - 统一图表测试
- **`test_warning_fix.py`** - matplotlib警告修复测试

### 📖 Documentation/ - 文档和配置
完整的项目文档：

- **`PROJECT_SUMMARY.md`** - 🔥 **项目总结**（重要）
- **`API_USAGE_GUIDE.md`** - 🔥 **API使用指南**（重要）
- **`requirements.txt`** - Python依赖包列表

### 💾 DataAPI/ - 数据源模块
数据获取相关：

- **`QmtStockAPI.py`** - 您的QMT真实数据源
- **`MockStockAPI.py`** - 模拟数据源（容错备用）

## 🎯 您最需要关注的文件

### 立即使用
1. **`API_System/stock_signals_api.py`** - 启动API服务
2. **`API_System/client_demo.py`** - 查看使用示例
3. **`Documentation/API_USAGE_GUIDE.md`** - 阅读使用指南

### 图表生成
1. **`Demo_Charts/demo_qmt_unified_chart_fixed.py`** - 生成图2效果

### 参考文档
1. **`Documentation/PROJECT_SUMMARY.md`** - 了解项目全貌
2. **`Documentation/requirements.txt`** - 安装依赖

## 🔧 维护说明

- **API系统修改**：主要在 `API_System/` 目录
- **图表功能修改**：主要在 `Demo_Charts/` 目录  
- **新增测试**：添加到 `Tests/` 目录
- **文档更新**：更新 `Documentation/` 目录
- **数据源扩展**：在 `DataAPI/` 目录添加新的数据源

## 🚀 项目亮点

✅ **清晰的模块分离**：不同功能各司其职  
✅ **易于维护**：相关文件集中管理  
✅ **快速定位**：根据需求直接找到对应目录  
✅ **扩展友好**：新功能可以清晰地添加到对应目录  

现在您可以根据需要快速找到和使用相应的功能模块！🎉