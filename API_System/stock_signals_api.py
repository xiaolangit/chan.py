#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
股票买卖信号提取API
提供RESTful接口返回股票的缠论买卖信号
"""

from flask import Flask, jsonify, request
from datetime import datetime, timedelta
import json
import traceback
from typing import List, Dict, Any
import warnings

# 导入缠论分析相关模块
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Chan import CChan
from ChanConfig import CChanConfig
from Common.CEnum import AUTYPE, KL_TYPE
from Plot.PlotMeta import CChanPlotMeta
from DataAPI.QmtStockAPI import CQMTData
from DataAPI.MockStockAPI import MockStockData

# 过滤警告
warnings.filterwarnings('ignore', category=UserWarning, module='matplotlib')

app = Flask(__name__)

class StockSignalExtractor:
    """股票信号提取器"""
    
    def __init__(self):
        # 默认缠论配置
        self.default_config = CChanConfig({
            "bi_strict": True,
            "trigger_step": False,
            "skip_step": 0,
            "divergence_rate": float("inf"),
            "bsp2_follow_1": False,
            "bsp3_follow_1": False,
            "min_zs_cnt": 0,
            "bs1_peak": False,
            "macd_algo": "peak",
            "bs_type": '1,2,3a,1p,2s,3b',
            "print_warning": False,
            "zs_algo": "normal",
        })
        
        # 支持的时间框架
        self.timeframes = {
            "1m": KL_TYPE.K_1M,
            "5m": KL_TYPE.K_5M,
            "15m": KL_TYPE.K_15M,
            "30m": KL_TYPE.K_30M,
            "60m": KL_TYPE.K_60M,
            "1d": KL_TYPE.K_DAY,
            "1w": KL_TYPE.K_WEEK,
            "1M": KL_TYPE.K_MON
        }
    
    def extract_signals(self, code: str, timeframe: str = "1d", 
                       begin_time: str = None, end_time: str = None) -> Dict[str, Any]:
        """
        提取单个股票的买卖信号
        
        Args:
            code: 股票代码，如 "159647.SZ"
            timeframe: 时间框架，如 "1d", "5m", "15m"
            begin_time: 开始时间，格式 "20240101"
            end_time: 结束时间，格式 "20241231"
            
        Returns:
            包含买卖信号的字典
        """
        try:
            # 设置默认时间范围
            if begin_time is None:
                begin_time = (datetime.now() - timedelta(days=365)).strftime("%Y%m%d")
            if end_time is None:
                end_time = datetime.now().strftime("%Y%m%d")
            
            # 验证时间框架
            if timeframe not in self.timeframes:
                raise ValueError(f"不支持的时间框架: {timeframe}")
            
            kl_type = self.timeframes[timeframe]
            
            # 为了确保CChan能够找到相关类，我们需要将其添加到全局命名空间
            globals()['CQMTData'] = CQMTData
            globals()['MockStockData'] = MockStockData
            
            # 尝试使用真实数据源，失败时使用模拟数据源
            data_src = "custom:QmtStockAPI.CQMTData"
            use_mock = False
            
            try:
                # 创建缠论分析
                chan = CChan(
                    code=code,
                    begin_time=begin_time,
                    end_time=end_time,
                    data_src=data_src,
                    lv_list=[kl_type],
                    config=self.default_config,
                    autype=AUTYPE.QFQ,
                )
            except Exception as e:
                # 如果网络连接失败，使用模拟数据源
                if "Connection" in str(e) or "timeout" in str(e).lower():
                    print(f"⚠️  真实数据源连接失败，使用模拟数据: {e}")
                    data_src = "custom:MockStockAPI.MockStockData"
                    use_mock = True
                    chan = CChan(
                        code=code,
                        begin_time=begin_time,
                        end_time=end_time,
                        data_src=data_src,
                        lv_list=[kl_type],
                        config=self.default_config,
                        autype=AUTYPE.QFQ,
                    )
                else:
                    raise e
            
            # 获取绘图元数据
            meta = CChanPlotMeta(chan[kl_type])
            
            # 提取买卖点信息
            buy_signals = []
            sell_signals = []
            
            # 处理普通买卖点
            if hasattr(meta, 'bs_point_lst') and meta.bs_point_lst:
                for bsp in meta.bs_point_lst:
                    signal_info = {
                        "type": bsp.desc(),
                        "time": meta.datetick[bsp.x] if bsp.x < len(meta.datetick) else "Unknown",
                        "price": float(bsp.y),
                        "x_index": int(bsp.x),
                        "signal_category": "normal",
                        "is_buy": bool(bsp.is_buy)
                    }
                    
                    if bsp.is_buy:
                        buy_signals.append(signal_info)
                    else:
                        sell_signals.append(signal_info)
            
            # 处理段买卖点
            if hasattr(meta, 'seg_bsp_lst') and meta.seg_bsp_lst:
                for seg_bsp in meta.seg_bsp_lst:
                    signal_info = {
                        "type": seg_bsp.desc(),
                        "time": meta.datetick[seg_bsp.x] if seg_bsp.x < len(meta.datetick) else "Unknown",
                        "price": float(seg_bsp.y),
                        "x_index": int(seg_bsp.x),
                        "signal_category": "segment",
                        "is_buy": bool(seg_bsp.is_buy)
                    }
                    
                    if seg_bsp.is_buy:
                        buy_signals.append(signal_info)
                    else:
                        sell_signals.append(signal_info)
            
            # 获取最新价格信息
            klu_list = list(meta.klu_iter())
            latest_price = float(klu_list[-1].close) if klu_list else 0.0
            latest_time = meta.datetick[-1] if meta.datetick else "Unknown"
            
            # 获取最新买卖信号
            latest_buy_signal = buy_signals[-1] if buy_signals else None
            latest_sell_signal = sell_signals[-1] if sell_signals else None
            
            return {
                "code": code,
                "timeframe": timeframe,
                "status": "success",
                "data_source": "mock" if use_mock else "real",
                "data_range": {
                    "begin_time": begin_time,
                    "end_time": end_time
                },
                "latest_info": {
                    "price": latest_price,
                    "time": latest_time
                },
                "signals": {
                    "buy_signals": buy_signals,
                    "sell_signals": sell_signals,
                    "total_buy_count": len(buy_signals),
                    "total_sell_count": len(sell_signals)
                },
                "latest_signals": {
                    "latest_buy": latest_buy_signal,
                    "latest_sell": latest_sell_signal
                },
                "summary": {
                    "has_recent_buy": latest_buy_signal is not None,
                    "has_recent_sell": latest_sell_signal is not None,
                    "signal_strength": self._calculate_signal_strength(buy_signals, sell_signals)
                }
            }
            
        except Exception as e:
            return {
                "code": code,
                "timeframe": timeframe,
                "status": "error",
                "error": str(e),
                "traceback": traceback.format_exc()
            }
    
    def _calculate_signal_strength(self, buy_signals: List[Dict], sell_signals: List[Dict]) -> str:
        """计算信号强度"""
        recent_buy_count = len([s for s in buy_signals[-5:] if s])
        recent_sell_count = len([s for s in sell_signals[-5:] if s])
        
        if recent_buy_count > recent_sell_count * 1.5:
            return "strong_buy"
        elif recent_sell_count > recent_buy_count * 1.5:
            return "strong_sell"
        elif recent_buy_count > recent_sell_count:
            return "weak_buy"
        elif recent_sell_count > recent_buy_count:
            return "weak_sell"
        else:
            return "neutral"
    
    def extract_multiple_signals(self, codes: List[str], timeframe: str = "1d", 
                                begin_time: str = None, end_time: str = None) -> Dict[str, Any]:
        """
        批量提取多个股票的买卖信号
        
        Args:
            codes: 股票代码列表
            timeframe: 时间框架
            begin_time: 开始时间
            end_time: 结束时间
            
        Returns:
            包含所有股票信号的字典
        """
        results = {}
        summary = {
            "total_stocks": len(codes),
            "successful": 0,
            "failed": 0,
            "strong_buy_stocks": [],
            "strong_sell_stocks": [],
            "neutral_stocks": []
        }
        
        for code in codes:
            print(f"正在处理股票: {code}")
            result = self.extract_signals(code, timeframe, begin_time, end_time)
            results[code] = result
            
            if result["status"] == "success":
                summary["successful"] += 1
                signal_strength = result["summary"]["signal_strength"]
                
                if signal_strength in ["strong_buy", "weak_buy"]:
                    summary["strong_buy_stocks"].append(code)
                elif signal_strength in ["strong_sell", "weak_sell"]:
                    summary["strong_sell_stocks"].append(code)
                else:
                    summary["neutral_stocks"].append(code)
            else:
                summary["failed"] += 1
        
        return {
            "batch_analysis": True,
            "timeframe": timeframe,
            "timestamp": datetime.now().isoformat(),
            "summary": summary,
            "results": results
        }

# 创建全局信号提取器实例
signal_extractor = StockSignalExtractor()

@app.route('/api/signals/single', methods=['GET', 'POST'])
def get_single_stock_signals():
    """获取单个股票的买卖信号"""
    try:
        if request.method == 'POST':
            data = request.get_json()
            code = data.get('code')
            timeframe = data.get('timeframe', '1d')
            begin_time = data.get('begin_time')
            end_time = data.get('end_time')
        else:
            code = request.args.get('code')
            timeframe = request.args.get('timeframe', '1d')
            begin_time = request.args.get('begin_time')
            end_time = request.args.get('end_time')
        
        if not code:
            return jsonify({"error": "股票代码不能为空"}), 400
        
        result = signal_extractor.extract_signals(code, timeframe, begin_time, end_time)
        return jsonify(result)
        
    except Exception as e:
        return jsonify({"error": str(e), "traceback": traceback.format_exc()}), 500

@app.route('/api/signals/batch', methods=['POST'])
def get_batch_stock_signals():
    """批量获取多个股票的买卖信号"""
    try:
        data = request.get_json()
        codes = data.get('codes', [])
        timeframe = data.get('timeframe', '1d')
        begin_time = data.get('begin_time')
        end_time = data.get('end_time')
        
        if not codes:
            return jsonify({"error": "股票代码列表不能为空"}), 400
        
        result = signal_extractor.extract_multiple_signals(codes, timeframe, begin_time, end_time)
        return jsonify(result)
        
    except Exception as e:
        return jsonify({"error": str(e), "traceback": traceback.format_exc()}), 500

@app.route('/api/signals/demo', methods=['GET'])
def demo_signals():
    """演示接口 - 使用您的股票列表"""
    try:
        demo_codes = ["159647.SZ", "600585.SH"]
        result = signal_extractor.extract_multiple_signals(demo_codes, timeframe="1d")
        return jsonify(result)
        
    except Exception as e:
        return jsonify({"error": str(e), "traceback": traceback.format_exc()}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """健康检查接口"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "股票买卖信号API",
        "supported_timeframes": list(signal_extractor.timeframes.keys())
    })

@app.route('/', methods=['GET'])
def api_documentation():
    """API文档"""
    docs = {
        "title": "股票买卖信号API",
        "version": "1.0.0",
        "description": "基于缠论分析的股票买卖信号提取服务",
        "endpoints": {
            "GET /": "API文档",
            "GET /api/health": "健康检查",
            "GET /api/signals/demo": "演示接口（您的股票列表）",
            "GET/POST /api/signals/single": "单个股票信号",
            "POST /api/signals/batch": "批量股票信号"
        },
        "parameters": {
            "code": "股票代码，如 159647.SZ",
            "codes": "股票代码列表",
            "timeframe": "时间框架: 1m,5m,15m,30m,60m,1d,1w,1M",
            "begin_time": "开始时间: 20240101",
            "end_time": "结束时间: 20241231"
        },
        "examples": {
            "single_stock": {
                "url": "/api/signals/single?code=159647.SZ&timeframe=1d",
                "post_body": {
                    "code": "159647.SZ",
                    "timeframe": "1d",
                    "begin_time": "20240101"
                }
            },
            "batch_stocks": {
                "url": "/api/signals/batch",
                "post_body": {
                    "codes": ["159647.SZ", "600585.SH"],
                    "timeframe": "1d"
                }
            }
        }
    }
    return jsonify(docs)

if __name__ == '__main__':
    print("=" * 60)
    print("🚀 股票买卖信号API服务启动")
    print("=" * 60)
    print("📍 服务地址: http://localhost:5000")
    print("📖 API文档: http://localhost:5000")
    print("🔍 演示接口: http://localhost:5000/api/signals/demo")
    print("💚 健康检查: http://localhost:5000/api/health")
    print("=" * 60)
    
    app.run(debug=True, host='0.0.0.0', port=5000)