# 📋 API返回字段详细说明

## 🎯 概述

本文档详细说明股票买卖信号API返回的每个字段的含义和用途。

## 📊 批量查询返回结构

### 🏷️ 顶层字段

| 字段名 | 类型 | 说明 |
|--------|------|------|
| `batch_analysis` | boolean | 是否为批量分析，批量查询时为 `true` |
| `timeframe` | string | 分析的时间框架，如 `"1d"`(日线), `"5m"`(5分钟) |
| `timestamp` | string | API响应的时间戳，ISO格式 |
| `summary` | object | 批量分析汇总信息 |
| `results` | object | 各个股票的详细分析结果 |

### 📈 Summary 汇总字段

| 字段名 | 类型 | 说明 |
|--------|------|------|
| `total_stocks` | integer | 总共分析的股票数量 |
| `successful` | integer | 成功分析的股票数量 |
| `failed` | integer | 分析失败的股票数量 |
| `buy_signal_stocks` | array | 有确认买入信号的股票代码列表 |
| `sell_signal_stocks` | array | 有确认卖出信号的股票代码列表 |
| `no_signal_stocks` | array | 没有任何确认信号的股票代码列表 |

**示例：**
```json
{
  "summary": {
    "total_stocks": 2,
    "successful": 2,
    "failed": 0,
    "buy_signal_stocks": ["159647.SZ"],
    "sell_signal_stocks": [],
    "no_signal_stocks": ["600585.SH"]
  }
}
```

## 🔍 单个股票结果结构

### 🏷️ 股票基本信息

| 字段名 | 类型 | 说明 |
|--------|------|------|
| `code` | string | 股票代码，如 `"159647.SZ"` |
| `timeframe` | string | 分析时间框架 |
| `status` | string | 分析状态：`"success"` 或 `"error"` |
| `data_source` | string | 数据源类型：`"real"`(真实数据) |
| `error_message` | string | 错误信息(仅在 `status` 为 `"error"` 时出现) |

### 📊 Latest Info 最新价格信息

| 字段名 | 类型 | 说明 |
|--------|------|------|
| `price` | number | 最新价格 |
| `time` | string | 最新价格对应的时间，格式 `"YYYY/MM/DD"` |

**示例：**
```json
{
  "latest_info": {
    "price": 25.67,
    "time": "2024/07/25"
  }
}
```

### 🎯 Signals 信号详情

#### 📈 买入信号 (buy_signals)
每个买入信号包含以下字段：

| 字段名 | 类型 | 说明 |
|--------|------|------|
| `type` | string | 买入点类型：`"b1"`, `"b2"`, `"b3a"`, `"1p"`, `"※b1"` 等 |
| `time` | string | 信号出现时间，格式 `"YYYY/MM/DD"` |
| `price` | number | 买入点对应的价格 |
| `x_index` | integer | 在K线序列中的位置索引 |
| `signal_category` | string | 信号类别：`"normal"`(普通买卖点) 或 `"segment"`(段买卖点) |
| `is_buy` | boolean | 是否为买入信号，买入信号固定为 `true` |
| `is_sure` | boolean | 是否为确认信号，API只返回 `true` 的信号 |

#### 📉 卖出信号 (sell_signals)
结构与买入信号相同，但：
- `type` 为卖出点类型：`"s1"`, `"s2"`, `"s3b"`, `"2s"`, `"※s1"` 等
- `is_buy` 固定为 `false`

**示例：**
```json
{
  "signals": {
    "buy_signals": [
      {
        "type": "b1",
        "time": "2024/07/20",
        "price": 24.5,
        "x_index": 156,
        "signal_category": "normal",
        "is_buy": true,
        "is_sure": true
      }
    ],
    "sell_signals": [
      {
        "type": "※s2",
        "time": "2024/07/18",
        "price": 26.2,
        "x_index": 154,
        "signal_category": "segment",
        "is_buy": false,
        "is_sure": true
      }
    ],
    "total_buy_count": 3,
    "total_sell_count": 2
  }
}
```

#### 📊 信号统计
| 字段名 | 类型 | 说明 |
|--------|------|------|
| `total_buy_count` | integer | 总买入信号数量 |
| `total_sell_count` | integer | 总卖出信号数量 |

### 🕐 Latest Signals 最新信号

| 字段名 | 类型 | 说明 |
|--------|------|------|
| `latest_buy` | object/null | 最新的买入信号详情，无买入信号时为 `null` |
| `latest_sell` | object/null | 最新的卖出信号详情，无卖出信号时为 `null` |

**最新信号对象结构：**
| 字段名 | 类型 | 说明 |
|--------|------|------|
| `type` | string | 信号类型 |
| `time` | string | 信号时间 |
| `price` | number | 信号价格 |

**示例：**
```json
{
  "latest_signals": {
    "latest_buy": {
      "type": "b1",
      "time": "2024/07/20",
      "price": 24.5
    },
    "latest_sell": null
  }
}
```

### 📋 Summary 个股汇总

| 字段名 | 类型 | 说明 |
|--------|------|------|
| `signal_type` | string | 信号类型：`"target_buy"`, `"target_sell"`, `"no_signal"` |
| `has_recent_buy` | boolean | 是否有最新买入信号 |
| `has_recent_sell` | boolean | 是否有最新卖出信号 |

**signal_type 详解：**
- `"target_buy"`: 检测到确认的买入信号
- `"target_sell"`: 检测到确认的卖出信号  
- `"no_signal"`: 没有检测到任何确认信号

## 🎯 信号类型详解

### 📈 普通买卖点类型

| 类型 | 说明 | 含义 |
|------|------|------|
| `b1` | 第一类买点 | 趋势类背驰后的买点 |
| `b2` | 第二类买点 | 回调不创新低的买点 |
| `b3a` | 第三类买点A | 突破前高的买点 |
| `s1` | 第一类卖点 | 趋势类背驰后的卖点 |
| `s2` | 第二类卖点 | 反弹不创新高的卖点 |
| `s3b` | 第三类卖点B | 跌破前低的卖点 |
| `1p` | 第一类买点(笔) | 基于笔的第一类买点 |
| `2s` | 第二类卖点(笔) | 基于笔的第二类卖点 |

### 📊 段买卖点类型

段买卖点前缀带 `※` 符号：

| 类型 | 说明 | 含义 |
|------|------|------|
| `※b1` | 段第一类买点 | 基于段级别的第一类买点 |
| `※s1` | 段第一类卖点 | 基于段级别的第一类卖点 |
| `※b2` | 段第二类买点 | 基于段级别的第二类买点 |
| `※s2` | 段第二类卖点 | 基于段级别的第二类卖点 |

## 🛡️ 确认机制说明

### ✅ is_sure 字段
- **含义**: 表示该信号是否已确认
- **值**: API只返回 `is_sure: true` 的信号
- **保证**: 确认的信号不会因后续数据而改变

### 🔍 确认逻辑
- **普通买卖点**: 对应的笔(bi)必须 `is_sure=true`
- **段买卖点**: 对应的段(segment)必须 `is_sure=true`

## 📝 完整示例

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
      "data_source": "real",
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
        "sell_signals": [],
        "total_buy_count": 1,
        "total_sell_count": 0
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

## 🚀 使用建议

### 💡 关键字段优先级
1. **`summary.buy_signal_stocks`** - 快速识别有买入信号的股票
2. **`latest_signals.latest_buy`** - 获取最新买入信号详情
3. **`signals.buy_signals`** - 查看完整买入信号历史
4. **`is_sure`** - 确认信号可靠性(所有返回信号都是 `true`)

### 🔍 监控策略
```python
# 重点关注的字段
for code in response["summary"]["buy_signal_stocks"]:
    stock = response["results"][code]
    signal = stock["latest_signals"]["latest_buy"]
    print(f"🟢 {code}: {signal['type']} @ {signal['price']}")
```

现在您可以清楚了解API返回的每个字段的具体含义！🎯