# 多时间框架缠论分析

本项目基于chan.py库实现了多时间框架的缠论分析，可以同时分析1分钟、5分钟、15分钟、1天四个时间维度的K线数据。

## 文件说明

### 核心文件

1. **DataAPI/QmtStockAPI.py** - 自定义的QMT数据源API
   - 实现了从QMT接口获取K线数据的功能
   - 支持多种时间周期：1分钟、5分钟、15分钟、30分钟、60分钟、日线、周线、月线
   - 处理时间戳转换和数据格式化

2. **demo_qmt.py** - 原始单时间框架演示
   - 基础的缠论分析演示，生成图1效果
   - 单一时间框架（默认日线）的缠论分析

3. **demo_qmt_multi_timeframe.py** - 多时间框架演示（方案1）
   - 生成4个独立的时间框架图表
   - 包含组合图表功能（实验性）

4. **demo_qmt_advanced_multi.py** - 高级多时间框架演示（方案2，推荐）
   - 生成独立的时间框架图表文件
   - 包含汇总分析图表
   - 尝试统一多时间框架显示

## 使用方法

### 运行单时间框架分析（图1效果）

```bash
python demo_qmt.py
```

这将生成：
- `test.png` - 单一时间框架的缠论分析图表

### 运行多时间框架分析（图2效果）

推荐使用高级版本：

```bash
python demo_qmt_advanced_multi.py
```

这将生成：
- `chart_1min.png` - 1分钟级别缠论分析
- `chart_5min.png` - 5分钟级别缠论分析  
- `chart_15min.png` - 15分钟级别缠论分析
- `chart_1day.png` - 日线级别缠论分析
- `summary_analysis.png` - 汇总分析图表
- `unified_multi_timeframe.png` - 统一多时间框架图表（如果成功）

或使用基础版本：

```bash
python demo_qmt_multi_timeframe.py
```

## 配置说明

### 时间框架配置

目前支持的时间框架：
- `KL_TYPE.K_1M` - 1分钟
- `KL_TYPE.K_5M` - 5分钟
- `KL_TYPE.K_15M` - 15分钟
- `KL_TYPE.K_30M` - 30分钟
- `KL_TYPE.K_60M` - 60分钟
- `KL_TYPE.K_DAY` - 日线
- `KL_TYPE.K_WEEK` - 周线
- `KL_TYPE.K_MON` - 月线

### 缠论参数配置

```python
config = CChanConfig({
    "bi_strict": True,          # 严格笔的定义
    "trigger_step": False,      # 是否开启逐步触发模式
    "skip_step": 0,            # 跳过的步数
    "divergence_rate": float("inf"),  # 背驰率
    "bsp2_follow_1": False,    # 二类买卖点是否跟一类走
    "bsp3_follow_1": False,    # 三类买卖点是否跟一类走
    "min_zs_cnt": 0,           # 最小中枢数量
    "bs1_peak": False,         # 一类买卖点是否在分型处
    "macd_algo": "peak",       # MACD算法
    "bs_type": '1,2,3a,1p,2s,3b',  # 买卖点类型
    "print_warning": True,     # 是否打印警告
    "zs_algo": "normal",       # 中枢算法
})
```

### 绘图配置

```python
plot_config = {
    "plot_kline": True,        # 绘制K线
    "plot_kline_combine": True, # 绘制合并K线
    "plot_bi": True,           # 绘制笔
    "plot_seg": True,          # 绘制段
    "plot_eigen": False,       # 绘制特征序列
    "plot_zs": True,           # 绘制中枢
    "plot_macd": True,         # 绘制MACD
    "plot_mean": False,        # 绘制均线
    "plot_channel": False,     # 绘制通道
    "plot_bsp": True,          # 绘制买卖点
    "plot_extrainfo": False,   # 绘制额外信息
    "plot_demark": False,      # 绘制德马克指标
    "plot_marker": False,      # 绘制标记
    "plot_rsi": False,         # 绘制RSI
    "plot_kdj": False,         # 绘制KDJ
}
```

## 数据源配置

### QMT数据接口

数据接口地址：`http://111.180.147.209/chan/stock`

请求参数：
- `code` - 股票代码（如：159647.SZ）
- `period` - 时间周期（1m, 5m, 15m, 30m, 60m, 1d, 1w, 1M）
- `start_time` - 开始时间（格式：20240101）
- `end_time` - 结束时间（可选）

### 自定义数据源

如需使用其他数据源，可以参考`QmtStockAPI.py`的实现方式：

1. 继承`CCommonStockApi`类
2. 实现`get_kl_data()`方法
3. 实现`SetBasicInfo()`方法
4. 实现时间戳转换和数据格式化

## 注意事项

1. **网络连接** - 确保能够访问QMT数据接口
2. **数据量控制** - 1分钟级别数据量较大，建议适当调整时间范围
3. **内存使用** - 多时间框架同时分析会占用较多内存
4. **图表文件** - 生成的PNG文件较大，注意磁盘空间

## 错误处理

如果遇到以下错误：

1. **网络连接错误** - 检查网络连接和数据接口地址
2. **数据格式错误** - 检查API返回的数据格式
3. **内存不足** - 减少分析的K线数量或时间范围
4. **绘图错误** - 检查matplotlib和相关依赖库

## 扩展功能

可以进一步扩展的功能：

1. **实时数据更新** - 添加实时数据获取和图表更新
2. **更多技术指标** - 集成更多技术分析指标
3. **策略回测** - 基于缠论信号进行策略回测
4. **预警系统** - 基于买卖点信号设置价格预警
5. **Web界面** - 开发Web版本的多时间框架分析工具

## 技术支持

如有问题，请检查：
1. 所有依赖库是否正确安装
2. 数据接口是否可访问
3. 股票代码格式是否正确
4. 时间格式是否符合要求