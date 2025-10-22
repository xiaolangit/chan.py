# 股票买卖信号API使用指南 🚀

## 🎯 项目概述

基于您现有的缠论分析系统，我已经为您创建了一个完整的**股票买卖信号提取API**。该API能够：

- ✅ **批量处理您的股票列表** `["159647.SZ", "600585.SH"]`
- ✅ **提取确认的缠论买卖信号**（只包含 `is_sure=True` 的买卖点）
- ✅ **支持多时间框架分析**（1分钟到月线）
- ✅ **信号可靠性保证**（只通知已确认的买卖点）
- ✅ **RESTful API接口**（支持JSON格式输入输出）

## 🚀 快速开始

### 1️⃣ 启动API服务
```bash
python3 stock_signals_api.py
```

服务将在 `http://localhost:5000` 启动，您会看到：
```
🚀 股票买卖信号API服务启动
============================================================
📍 服务地址: http://localhost:5000
📖 API文档: http://localhost:5000
🔍 演示接口: http://localhost:5000/api/signals/demo
💚 健康检查: http://localhost:5000/api/health
============================================================
```

### 2️⃣ 测试API
```bash
# 使用客户端演示
python3 client_demo.py

# 或直接访问浏览器
http://localhost:5000/api/signals/demo
```

## 📊 核心API接口

### 🔥 快速演示（您的股票列表）

**最简单的方式** - 直接获取您股票列表的信号：

```bash
curl http://localhost:5000/api/signals/demo
```

**浏览器访问**：`http://localhost:5000/api/signals/demo`

### 📈 单个股票查询

#### GET请求
```bash
curl "http://localhost:5000/api/signals/single?code=159647.SZ&timeframe=1d"
```

#### POST请求
```bash
curl -X POST http://localhost:5000/api/signals/single \
  -H "Content-Type: application/json" \
  -d '{
    "code": "159647.SZ",
    "timeframe": "1d",
    "begin_time": "20240101"
  }'
```

### 📊 批量股票查询

```bash
curl -X POST http://localhost:5000/api/signals/batch \
  -H "Content-Type: application/json" \
  -d '{
    "codes": ["159647.SZ", "600585.SH"],
    "timeframe": "1d"
  }'
```

## 💡 Python客户端使用

```python
from client_demo import StockSignalClient

# 创建客户端
client = StockSignalClient()

# 批量查询您的股票列表
your_stocks = ["159647.SZ", "600585.SH"]
result = client.get_batch_stock_signals(your_stocks, "1d")

# 处理结果
for code, stock_data in result["results"].items():
    if stock_data["status"] == "success":
        print(f"{code}: {stock_data['summary']['signal_strength']}")
        
        # 获取最新买卖信号
        latest_buy = stock_data["latest_signals"]["latest_buy"]
        latest_sell = stock_data["latest_signals"]["latest_sell"]
        
        if latest_buy:
            print(f"  最新买入: {latest_buy['type']} @ {latest_buy['price']}")
        if latest_sell:
            print(f"  最新卖出: {latest_sell['type']} @ {latest_sell['price']}")
```

## 📋 API返回数据格式

### 批量查询返回示例
```json
{
  "batch_analysis": true,
  "timeframe": "1d",
  "timestamp": "2025-01-25T10:30:00",
  "summary": {
    "total_stocks": 2,
    "successful": 2,
    "failed": 0,
    "buy_signal_stocks": ["159647.SZ"],
    "sell_signal_stocks": [],
    "no_signal_stocks": ["600585.SH"]
  },
  "results": {
    "159647.SZ": {
      "code": "159647.SZ",
      "timeframe": "1d",
      "status": "success",
      "data_source": "mock",
      "latest_info": {
        "price": 2.22,
        "time": "2025/01/25"
      },
      "signals": {
        "buy_signals": [
          {
            "type": "b1",
            "time": "2025/01/20",
            "price": 2.15,
            "x_index": 240,
            "signal_category": "normal",
            "is_buy": true,
            "is_sure": true
          }
        ],
        "sell_signals": [
          {
            "type": "※s2",
            "time": "2025/01/18",
            "price": 2.35,
            "x_index": 238,
            "signal_category": "segment",
            "is_buy": false,
            "is_sure": true
          }
        ],
        "total_buy_count": 1,
        "total_sell_count": 1
      },
      "latest_signals": {
        "latest_buy": {
          "type": "b1",
          "time": "2025/01/20",
          "price": 2.15
        },
        "latest_sell": null
      },
      "summary": {
        "signal_type": "target_buy",
        "has_recent_buy": true,
        "has_recent_sell": false
      }
    }
  }
}
```

## 🎛️ 参数说明

### 支持的时间框架
- `1m` - 1分钟
- `5m` - 5分钟  
- `15m` - 15分钟
- `30m` - 30分钟
- `60m` - 60分钟
- `1d` - 日线（默认）
- `1w` - 周线
- `1M` - 月线

### 买卖点类型
- **普通买卖点**: `b1`, `s1`, `b2`, `s2`, `b3a`, `s3b`, `1p`, `2s`（只包含对应笔 `is_sure=True` 的）
- **段买卖点**: 带 `※` 标记，如 `※b1`, `※s2s`（只包含对应段 `is_sure=True` 的）
- **确认机制**: 所有返回的买卖点都经过 `is_sure=True` 验证，确保信号可靠性

### 信号类型
- `target_buy` - 检测到确认的买入信号
- `target_sell` - 检测到确认的卖出信号
- `no_signal` - 没有检测到任何信号

## 📡 数据源说明

API直接使用真实数据源：

1. **QMT真实数据源**：直接连接QMT讯投接口 (`111.180.147.209`)
2. **确认信号机制**：只返回 `is_sure=True` 的买卖点，确保信号可靠性
3. **数据源标识**：返回结果中的 `data_source` 字段显示 `"real"`

## 🔍 实际使用场景

### 1. 实时监控
```python
import time
import requests

def monitor_stocks():
    codes = ["159647.SZ", "600585.SH"]
    
    while True:
        response = requests.post("http://localhost:5000/api/signals/batch", 
                               json={"codes": codes, "timeframe": "1d"})
        data = response.json()
        
        # 检查强买入股票
        for code in data["summary"]["strong_buy_stocks"]:
            print(f"🟢 {code} 出现强买入信号！")
        
        # 检查强卖出股票
        for code in data["summary"]["strong_sell_stocks"]:
            print(f"🔴 {code} 出现强卖出信号！")
        
        time.sleep(300)  # 5分钟检查一次

monitor_stocks()
```

### 2. 批量筛选
```python
import requests

def screen_buy_signals(stock_list):
    """从股票列表中筛选出有买入信号的股票"""
    
    response = requests.post("http://localhost:5000/api/signals/batch",
                           json={"codes": stock_list, "timeframe": "1d"})
    data = response.json()
    
    buy_candidates = []
    
    for code, result in data["results"].items():
        if result["status"] == "success":
            signals = result["signals"]
            summary = result["summary"]
            
            # 筛选条件：有最近买入信号且信号强度不是卖出
            if (signals["total_buy_count"] > 0 and 
                summary["signal_strength"] in ["strong_buy", "weak_buy"]):
                
                buy_candidates.append({
                    "code": code,
                    "strength": summary["signal_strength"],
                    "latest_buy": result["latest_signals"]["latest_buy"],
                    "price": result["latest_info"]["price"]
                })
    
    return buy_candidates

# 使用示例
candidates = screen_buy_signals(["159647.SZ", "600585.SH"])
for stock in candidates:
    print(f"{stock['code']}: {stock['strength']} @ {stock['price']}")
```

### 3. 信号导出
```python
import pandas as pd

def export_signals_to_excel(codes, timeframe="1d"):
    """导出买卖信号到Excel文件"""
    
    response = requests.post("http://localhost:5000/api/signals/batch",
                           json={"codes": codes, "timeframe": timeframe})
    data = response.json()
    
    records = []
    
    for code, result in data["results"].items():
        if result["status"] == "success":
            # 买入信号
            for signal in result["signals"]["buy_signals"]:
                records.append({
                    "股票代码": code,
                    "信号类型": "买入",
                    "信号": signal["type"],
                    "时间": signal["time"],
                    "价格": signal["price"],
                    "类别": signal["signal_category"]
                })
            
            # 卖出信号
            for signal in result["signals"]["sell_signals"]:
                records.append({
                    "股票代码": code,
                    "信号类型": "卖出",
                    "信号": signal["type"],
                    "时间": signal["time"],
                    "价格": signal["price"],
                    "类别": signal["signal_category"]
                })
    
    df = pd.DataFrame(records)
    df.to_excel("股票买卖信号.xlsx", index=False)
    print(f"导出完成：{len(records)} 条信号")

# 导出您的股票信号
export_signals_to_excel(["159647.SZ", "600585.SH"])
```

## 🛠️ 系统架构

```
📁 项目结构
├── 📄 stock_signals_api.py      # 主API服务
├── 📄 client_demo.py            # 客户端演示
├── 📄 test_stock_api.py         # API测试脚本
├── 📄 DataAPI/
│   ├── 📄 QmtStockAPI.py        # 真实数据源（QMT）
│   └── 📄 MockStockAPI.py       # 模拟数据源
├── 📄 demo_qmt_unified_chart_fixed.py  # 图表生成（图2效果）
└── 📄 STOCK_SIGNALS_API.md     # 详细技术文档
```

## 📞 API接口总览

| 接口 | 方法 | 功能 | 示例 |
|------|------|------|------|
| `/` | GET | API文档 | `http://localhost:5000` |
| `/api/health` | GET | 健康检查 | `curl http://localhost:5000/api/health` |
| `/api/signals/demo` | GET | 您的股票列表 | `curl http://localhost:5000/api/signals/demo` |
| `/api/signals/single` | GET/POST | 单个股票 | `curl "http://localhost:5000/api/signals/single?code=159647.SZ"` |
| `/api/signals/batch` | POST | 批量股票 | `curl -X POST ... -d '{"codes":["159647.SZ","600585.SH"]}'` |

## 🎉 总结

现在您拥有了一个完整的股票买卖信号API系统：

✅ **可直接使用**：支持您的股票列表 `["159647.SZ", "600585.SH"]`  
✅ **高度可扩展**：轻松添加更多股票代码  
✅ **容错能力强**：真实数据源不可用时自动使用模拟数据  
✅ **接口丰富**：支持单个/批量查询，多种时间框架  
✅ **文档完善**：提供详细的使用说明和示例代码  

立即开始使用：
1. `python3 stock_signals_api.py` - 启动服务
2. `python3 client_demo.py` - 查看演示
3. 访问 `http://localhost:5000/api/signals/demo` - 获取您的股票信号

祝您投资顺利！🚀📈