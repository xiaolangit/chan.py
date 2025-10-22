# 股票买卖信号API使用指南

## 🎯 功能概述

基于您现有的缠论分析系统，我创建了一个RESTful API来提取股票买卖信号。支持您的股票列表 `["159647.SZ", "600585.SH"]` 的批量分析。

## 🚀 快速开始

### 1. 安装依赖
```bash
pip install flask pandas matplotlib numpy requests
```

### 2. 启动API服务
```bash
python stock_signals_api.py
```

服务将在 `http://localhost:5000` 启动

### 3. 测试API
```bash
# 方法1: 使用演示客户端
python client_demo.py

# 方法2: 直接访问浏览器
http://localhost:5000/api/signals/demo
```

## 📖 API接口说明

### 🔍 主要接口

| 接口 | 方法 | 说明 |
|------|------|------|
| `/` | GET | API文档 |
| `/api/health` | GET | 健康检查 |
| `/api/signals/demo` | GET | 演示接口（您的股票列表） |
| `/api/signals/single` | GET/POST | 单个股票信号 |
| `/api/signals/batch` | POST | 批量股票信号 |

### 📊 您的股票列表快速查询

最简单的方式，直接获取您股票列表的信号：

```bash
curl http://localhost:5000/api/signals/demo
```

或在浏览器中访问：`http://localhost:5000/api/signals/demo`

### 📈 单个股票查询

#### GET方式
```bash
curl "http://localhost:5000/api/signals/single?code=159647.SZ&timeframe=1d"
```

#### POST方式
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

## 🎛️ 参数说明

### 时间框架 (timeframe)
- `1m` - 1分钟
- `5m` - 5分钟  
- `15m` - 15分钟
- `30m` - 30分钟
- `60m` - 60分钟
- `1d` - 日线（默认）
- `1w` - 周线
- `1M` - 月线

### 时间范围
- `begin_time` - 开始时间，格式：`20240101`
- `end_time` - 结束时间，格式：`20241231`
- 默认：最近一年的数据

## 📋 返回数据格式

### 单个股票返回示例
```json
{
  "code": "159647.SZ",
  "timeframe": "1d",
  "status": "success",
  "latest_info": {
    "price": 25.67,
    "time": "2024/07/25"
  },
  "signals": {
    "buy_signals": [
      {
        "type": "b1",
        "time": "2024/07/20",
        "price": 24.5,
        "x_index": 156,
        "signal_category": "normal",
        "is_buy": true
      }
    ],
    "sell_signals": [
      {
        "type": "s2s",
        "time": "2024/07/18",
        "price": 26.2,
        "x_index": 154,
        "signal_category": "segment",
        "is_buy": false
      }
    ],
    "total_buy_count": 5,
    "total_sell_count": 3
  },
  "latest_signals": {
    "latest_buy": {
      "type": "b1",
      "time": "2024/07/20",
      "price": 24.5
    },
    "latest_sell": null
  },
  "summary": {
    "signal_strength": "weak_buy",
    "has_recent_buy": true,
    "has_recent_sell": false
  }
}
```

### 批量分析返回示例
```json
{
  "batch_analysis": true,
  "timeframe": "1d",
  "timestamp": "2024-07-25T10:30:00",
  "summary": {
    "total_stocks": 2,
    "successful": 2,
    "failed": 0,
    "strong_buy_stocks": ["159647.SZ"],
    "strong_sell_stocks": [],
    "neutral_stocks": ["600585.SH"]
  },
  "results": {
    "159647.SZ": { /* 详细信号数据 */ },
    "600585.SH": { /* 详细信号数据 */ }
  }
}
```

## 📊 信号类型说明

### 买卖点类型
- **普通买卖点**: `b1`, `s1`, `b2`, `s2`, `b3a`, `s3b`, `1p`, `2s` 等
- **段买卖点**: 带 `※` 标记，如 `※b1`, `※s2s`

### 信号强度
- `strong_buy` - 强买入
- `weak_buy` - 弱买入  
- `neutral` - 中性
- `weak_sell` - 弱卖出
- `strong_sell` - 强卖出

## 🔧 Python客户端使用

```python
from client_demo import StockSignalClient

# 创建客户端
client = StockSignalClient()

# 查询您的股票列表
your_stocks = ["159647.SZ", "600585.SH"]
result = client.get_batch_stock_signals(your_stocks, "1d")

# 处理结果
for code, stock_data in result["results"].items():
    if stock_data["status"] == "success":
        print(f"{code}: {stock_data['summary']['signal_strength']}")
        latest_buy = stock_data["latest_signals"]["latest_buy"]
        if latest_buy:
            print(f"最新买入信号: {latest_buy['type']} @ {latest_buy['price']}")
```

## 🌐 Web界面访问

访问 `http://localhost:5000` 查看完整的API文档和示例。

## ⚡ 性能特点

- ✅ **实时分析**: 基于最新的K线数据
- ✅ **多时间框架**: 支持1分钟到月线的所有时间框架
- ✅ **批量处理**: 一次请求分析多个股票
- ✅ **完整信号**: 包含所有缠论买卖点类型
- ✅ **信号强度**: 自动计算信号强度评级
- ✅ **错误处理**: 完善的异常处理和错误信息

## 🔍 使用场景

1. **实时监控**: 定期查询股票池的最新信号
2. **批量筛选**: 从大量股票中筛选有信号的股票
3. **策略回测**: 获取历史买卖信号进行策略验证
4. **信号预警**: 集成到预警系统中
5. **数据分析**: 导出信号数据进行进一步分析

## 🛠️ 扩展功能

如需添加更多功能，可以扩展：
- 添加更多技术指标
- 支持更多数据源
- 增加信号过滤条件
- 添加实时推送功能
- 集成数据库存储

现在您可以通过API接口方便地获取 `["159647.SZ", "600585.SH"]` 这些股票的买卖信号了！🎉