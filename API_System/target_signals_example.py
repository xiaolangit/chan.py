#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
目标买卖点信号示例
只在出现 b1, b2, s1, s2 信号时进行通知
"""

import requests
import json
import time

def check_target_signals():
    """检查买卖点信号"""
    print("🎯 检查确认的买卖点信号 (is_sure=True)")
    print("=" * 50)
    
    # 您的股票列表
    stocks = ["159647.SZ", "600585.SH"]
    
    try:
        # 调用批量分析API
        response = requests.post("http://localhost:5000/api/signals/batch", json={
            "codes": stocks,
            "timeframe": "1d"
        })
        
        if response.status_code == 200:
            data = response.json()
            
            # 检查买入信号
            buy_signal_stocks = data["summary"]["buy_signal_stocks"]
            if buy_signal_stocks:
                print("🟢 买入信号:")
                for code in buy_signal_stocks:
                    stock_data = data["results"][code]
                    latest_buy = stock_data["latest_signals"]["latest_buy"]
                    if latest_buy:
                        print(f"  📈 {code}: {latest_buy['type']} @ {latest_buy['price']} ({latest_buy['time']})")
            else:
                print("⚪ 无买入信号")
            
            # 检查卖出信号
            sell_signal_stocks = data["summary"]["sell_signal_stocks"]
            if sell_signal_stocks:
                print("\n🔴 卖出信号:")
                for code in sell_signal_stocks:
                    stock_data = data["results"][code]
                    latest_sell = stock_data["latest_signals"]["latest_sell"]
                    if latest_sell:
                        print(f"  📉 {code}: {latest_sell['type']} @ {latest_sell['price']} ({latest_sell['time']})")
            else:
                print("⚪ 无卖出信号")
            
            # 显示无信号股票
            no_signal_stocks = data["summary"]["no_signal_stocks"]
            if no_signal_stocks:
                print(f"\n⚫ 无信号股票: {no_signal_stocks}")
                
        else:
            print(f"❌ API调用失败: {response.status_code}")
            
    except Exception as e:
        print(f"❌ 检查失败: {e}")

def monitor_target_signals():
    """持续监控目标信号"""
    print("🚨 开始监控目标买卖点信号...")
    print("按 Ctrl+C 停止监控")
    print("-" * 50)
    
    try:
        while True:
            check_target_signals()
            print("\n" + "=" * 50)
            print("⏰ 等待5分钟后重新检查...")
            time.sleep(300)  # 5分钟检查一次
            
    except KeyboardInterrupt:
        print("\n🛑 监控已停止")

def get_single_stock_target_signal(code):
    """获取单个股票的目标信号"""
    print(f"🔍 检查 {code} 的目标信号...")
    
    try:
        response = requests.get(f"http://localhost:5000/api/signals/single?code={code}")
        
        if response.status_code == 200:
            data = response.json()
            
            if data["status"] == "success":
                signal_type = data["summary"]["signal_type"]
                
                if signal_type == "target_buy":
                    latest_buy = data["latest_signals"]["latest_buy"]
                    print(f"🟢 {code} 出现买入信号: {latest_buy['type']} @ {latest_buy['price']}")
                    return True
                    
                elif signal_type == "target_sell":
                    latest_sell = data["latest_signals"]["latest_sell"]
                    print(f"🔴 {code} 出现卖出信号: {latest_sell['type']} @ {latest_sell['price']}")
                    return True
                    
                else:
                    print(f"⚪ {code} 无信号")
                    return False
            else:
                print(f"❌ {code} 分析失败: {data['error']}")
                return False
                
    except Exception as e:
        print(f"❌ 检查 {code} 失败: {e}")
        return False

if __name__ == "__main__":
    print("🎯 买卖点信号检查工具")
    print("检查所有确认的缠论买卖点信号 (只包含is_sure=True的信号)")
    print("=" * 60)
    
    # 选择运行模式
    mode = input("选择模式 [1]单次检查 [2]持续监控 [3]单个股票: ")
    
    if mode == "1":
        check_target_signals()
    elif mode == "2":
        monitor_target_signals()
    elif mode == "3":
        code = input("输入股票代码 (如: 159647.SZ): ")
        get_single_stock_target_signal(code)
    else:
        print("❌ 无效选择")