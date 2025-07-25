#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
股票买卖信号API客户端演示
"""

import requests
import json
from typing import List

class StockSignalClient:
    """股票信号API客户端"""
    
    def __init__(self, base_url: str = "http://localhost:5000"):
        self.base_url = base_url
    
    def get_single_stock_signals(self, code: str, timeframe: str = "1d", 
                                begin_time: str = None, end_time: str = None):
        """获取单个股票的买卖信号"""
        url = f"{self.base_url}/api/signals/single"
        
        params = {
            "code": code,
            "timeframe": timeframe
        }
        
        if begin_time:
            params["begin_time"] = begin_time
        if end_time:
            params["end_time"] = end_time
        
        response = requests.get(url, params=params)
        return response.json()
    
    def get_batch_stock_signals(self, codes: List[str], timeframe: str = "1d",
                               begin_time: str = None, end_time: str = None):
        """批量获取多个股票的买卖信号"""
        url = f"{self.base_url}/api/signals/batch"
        
        data = {
            "codes": codes,
            "timeframe": timeframe
        }
        
        if begin_time:
            data["begin_time"] = begin_time
        if end_time:
            data["end_time"] = end_time
        
        response = requests.post(url, json=data)
        return response.json()
    
    def get_demo_signals(self):
        """获取演示信号（您的股票列表）"""
        url = f"{self.base_url}/api/signals/demo"
        response = requests.get(url)
        return response.json()
    
    def health_check(self):
        """健康检查"""
        url = f"{self.base_url}/api/health"
        response = requests.get(url)
        return response.json()

def print_signals_summary(result):
    """打印信号摘要"""
    if "batch_analysis" in result:
        # 批量分析结果
        print(f"\n📊 批量分析摘要:")
        summary = result["summary"]
        print(f"总股票数: {summary['total_stocks']}")
        print(f"成功分析: {summary['successful']}")
        print(f"失败分析: {summary['failed']}")
        
        if summary['strong_buy_stocks']:
            print(f"🟢 强买入信号: {summary['strong_buy_stocks']}")
        if summary['strong_sell_stocks']:
            print(f"🔴 强卖出信号: {summary['strong_sell_stocks']}")
        if summary['neutral_stocks']:
            print(f"⚪ 中性信号: {summary['neutral_stocks']}")
        
        # 显示各股票详细信息
        for code, stock_result in result["results"].items():
            print(f"\n📈 {code}:")
            if stock_result["status"] == "success":
                signals = stock_result["signals"]
                latest = stock_result["latest_signals"]
                
                print(f"  最新价格: {stock_result['latest_info']['price']:.2f}")
                print(f"  买入信号数: {signals['total_buy_count']}")
                print(f"  卖出信号数: {signals['total_sell_count']}")
                print(f"  信号强度: {stock_result['summary']['signal_strength']}")
                
                if latest["latest_buy"]:
                    print(f"  最新买入: {latest['latest_buy']['type']} @ {latest['latest_buy']['price']:.2f}")
                if latest["latest_sell"]:
                    print(f"  最新卖出: {latest['latest_sell']['type']} @ {latest['latest_sell']['price']:.2f}")
            else:
                print(f"  ❌ 分析失败: {stock_result['error']}")
    
    else:
        # 单股票分析结果
        if result["status"] == "success":
            signals = result["signals"]
            latest = result["latest_signals"]
            
            print(f"\n📈 {result['code']} 信号分析:")
            print(f"时间框架: {result['timeframe']}")
            print(f"最新价格: {result['latest_info']['price']:.2f}")
            print(f"买入信号数: {signals['total_buy_count']}")
            print(f"卖出信号数: {signals['total_sell_count']}")
            print(f"信号强度: {result['summary']['signal_strength']}")
            
            if latest["latest_buy"]:
                print(f"最新买入: {latest['latest_buy']['type']} @ {latest['latest_buy']['price']:.2f}")
            if latest["latest_sell"]:
                print(f"最新卖出: {latest['latest_sell']['type']} @ {latest['latest_sell']['price']:.2f}")
            
            # 显示最近5个买卖信号
            print(f"\n🔍 最近买入信号:")
            for signal in signals["buy_signals"][-5:]:
                print(f"  {signal['time']}: {signal['type']} @ {signal['price']:.2f}")
            
            print(f"\n🔍 最近卖出信号:")
            for signal in signals["sell_signals"][-5:]:
                print(f"  {signal['time']}: {signal['type']} @ {signal['price']:.2f}")
        else:
            print(f"❌ 分析失败: {result['error']}")

def main():
    """演示API调用"""
    print("🚀 股票买卖信号API客户端演示")
    print("=" * 60)
    
    # 创建客户端
    client = StockSignalClient()
    
    # 健康检查
    print("1. 健康检查...")
    try:
        health = client.health_check()
        print(f"✅ 服务状态: {health['status']}")
        print(f"支持的时间框架: {health['supported_timeframes']}")
    except Exception as e:
        print(f"❌ 服务连接失败: {e}")
        print("请确保API服务已启动: python stock_signals_api.py")
        return
    
    print("\n" + "=" * 60)
    
    # 演示1: 单个股票信号
    print("2. 单个股票信号演示...")
    try:
        result = client.get_single_stock_signals("159647.SZ", "1d")
        print_signals_summary(result)
    except Exception as e:
        print(f"❌ 单股票查询失败: {e}")
    
    print("\n" + "=" * 60)
    
    # 演示2: 批量股票信号（您的股票列表）
    print("3. 批量股票信号演示...")
    try:
        your_stocks = ["159647.SZ", "600585.SH"]
        result = client.get_batch_stock_signals(your_stocks, "1d")
        print_signals_summary(result)
    except Exception as e:
        print(f"❌ 批量查询失败: {e}")
    
    print("\n" + "=" * 60)
    
    # 演示3: 快速演示接口
    print("4. 快速演示接口...")
    try:
        result = client.get_demo_signals()
        print_signals_summary(result)
    except Exception as e:
        print(f"❌ 演示接口失败: {e}")
    
    print("\n" + "=" * 60)
    print("🎉 演示完成！")
    print("\n📖 API使用说明:")
    print("- 启动服务: python stock_signals_api.py")
    print("- 访问文档: http://localhost:5000")
    print("- 演示接口: http://localhost:5000/api/signals/demo")
    print("- 单股票查询: GET http://localhost:5000/api/signals/single?code=159647.SZ")
    print("- 批量查询: POST http://localhost:5000/api/signals/batch")

if __name__ == "__main__":
    main()