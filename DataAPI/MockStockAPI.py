#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
模拟股票数据API
用于演示买卖信号提取功能
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Iterable
from Common.CEnum import AUTYPE, DATA_FIELD, KL_TYPE
from Common.CTime import CTime
from KLine.KLine_Unit import CKLine_Unit
from .CommonStockAPI import CCommonStockApi

class MockStockData(CCommonStockApi):
    """模拟股票数据源"""
    
    def __init__(self, code, k_type=KL_TYPE.K_DAY, begin_date=None, end_date=None, autype=AUTYPE.QFQ):
        super(MockStockData, self).__init__(code, k_type, begin_date, end_date, autype)
        self._generate_mock_data()
    
    def get_kl_data(self):
        """获取K线数据"""
        for _, row in self.mock_data.iterrows():
            item_dict = {
                DATA_FIELD.FIELD_TIME: self.parse_timestamp(row['time']),
                DATA_FIELD.FIELD_OPEN: float(row['open']),
                DATA_FIELD.FIELD_CLOSE: float(row['close']),
                DATA_FIELD.FIELD_LOW: float(row['low']),
                DATA_FIELD.FIELD_HIGH: float(row['high']),
                DATA_FIELD.FIELD_VOLUME: float(row['volume']),
            }
            yield CKLine_Unit(item_dict)
    
    def SetBasicInfo(self):
        """设置股票基本信息"""
        stock_names = {
            "159647.SZ": "华泰柏瑞科创50ETF",
            "600585.SH": "海螺水泥"
        }
        self.stock_name = stock_names.get(self.code, f"股票{self.code}")
    
    def _generate_mock_data(self):
        """生成模拟数据"""
        # 确定时间范围
        if self.begin_date:
            start_date = datetime.strptime(self.begin_date, "%Y%m%d")
        else:
            start_date = datetime.now() - timedelta(days=365)
        
        if self.end_date:
            end_date = datetime.strptime(self.end_date, "%Y%m%d")
        else:
            end_date = datetime.now()
        
        # 根据K线类型确定时间间隔
        freq_map = {
            KL_TYPE.K_1M: timedelta(minutes=1),
            KL_TYPE.K_5M: timedelta(minutes=5),
            KL_TYPE.K_15M: timedelta(minutes=15),
            KL_TYPE.K_30M: timedelta(minutes=30),
            KL_TYPE.K_60M: timedelta(hours=1),
            KL_TYPE.K_DAY: timedelta(days=1),
            KL_TYPE.K_WEEK: timedelta(weeks=1),
            KL_TYPE.K_MON: timedelta(days=30)
        }
        
        freq = freq_map.get(self.k_type, timedelta(days=1))
        
        # 生成时间序列
        current_time = start_date
        times = []
        while current_time <= end_date:
            times.append(int(current_time.timestamp() * 1000))  # 毫秒时间戳
            current_time += freq
        
        # 生成价格数据（模拟股票走势）
        np.random.seed(hash(self.code) % (2**32))  # 基于股票代码设置种子，保证每次生成相同数据
        
        # 基础价格
        base_prices = {
            "159647.SZ": 2.5,  # ETF价格较低
            "600585.SH": 45.0  # 个股价格较高
        }
        base_price = base_prices.get(self.code, 25.0)
        
        n_points = len(times)
        
        # 生成随机游走价格，增加波动性以产生更多买卖信号
        returns = np.random.normal(0.001, 0.03, n_points)  # 增加波动率
        returns[0] = 0  # 第一天收益率为0
        
        # 添加更强的趋势和周期性
        trend = np.linspace(-0.15, 0.15, n_points)
        cycle = 0.08 * np.sin(np.linspace(0, 6 * np.pi, n_points))  # 更多周期
        
        # 添加一些突发事件（急涨急跌）
        events = np.zeros(n_points)
        n_events = max(3, n_points // 100)  # 每100个点有3个事件
        event_indices = np.random.choice(range(20, n_points-20), n_events, replace=False)
        for idx in event_indices:
            event_magnitude = np.random.choice([-0.05, 0.05])  # 5%的突发涨跌
            events[idx:idx+3] = event_magnitude / 3  # 分散到3天
        
        returns += trend + cycle + events
        
        # 计算累积价格
        close_prices = base_price * np.exp(np.cumsum(returns))
        
        # 生成OHLV数据
        data = []
        for i, (time_ms, close) in enumerate(zip(times, close_prices)):
            # 增加日内波动性，让缠论更容易识别形态
            volatility = 0.025 * close  # 日内波动2.5%
            high = close + np.random.uniform(volatility/2, volatility)
            low = close - np.random.uniform(volatility/2, volatility)
            
            # 生成开盘价
            if i == 0:
                open_price = close
            else:
                prev_close = close_prices[i-1]
                gap = np.random.uniform(-volatility/3, volatility/3)
                open_price = prev_close + gap
            
            # 确保OHLC逻辑正确
            high = max(high, open_price, close)
            low = min(low, open_price, close)
            
            # 生成成交量
            volume = np.random.uniform(1000000, 5000000)
            
            data.append({
                'time': time_ms,
                'open': round(open_price, 2),
                'high': round(high, 2),
                'low': round(low, 2),
                'close': round(close, 2),
                'volume': int(volume)
            })
        
        self.mock_data = pd.DataFrame(data)
    
    @staticmethod
    def parse_timestamp(timestamp):
        """将毫秒级时间戳转换为CTime对象"""
        dt = datetime.fromtimestamp(timestamp / 1000)
        return CTime(dt.year, dt.month, dt.day, dt.hour, dt.minute)
    
    def __convert_type(self):
        """转换K线类型"""
        _dict = {
            KL_TYPE.K_DAY: '1d',
            KL_TYPE.K_WEEK: '1w',
            KL_TYPE.K_MON: '1M',
            KL_TYPE.K_5M: '5m',
            KL_TYPE.K_15M: '15m',
            KL_TYPE.K_30M: '30m',
            KL_TYPE.K_60M: '60m',
            KL_TYPE.K_1M: '1m',
        }
        return _dict[self.k_type]