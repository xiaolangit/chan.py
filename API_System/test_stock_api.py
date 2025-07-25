#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
股票买卖信号API测试脚本
"""

import sys
import traceback
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from stock_signals_api import StockSignalExtractor

def test_signal_extraction():
    """测试信号提取功能"""
    print("🧪 测试股票买卖信号提取功能")
    print("=" * 50)
    
    # 创建信号提取器
    extractor = StockSignalExtractor()
    
    # 测试您的股票列表
    test_stocks = ["159647.SZ", "600585.SH"]
    
    print(f"📊 测试股票列表: {test_stocks}")
    print(f"⏰ 时间框架: 1d (日线)")
    print(f"📅 数据范围: 最近一年")
    print("-" * 50)
    
    for i, code in enumerate(test_stocks, 1):
        print(f"\n{i}. 正在分析 {code}...")
        
        try:
            # 提取单个股票信号
            result = extractor.extract_signals(code, "1d")
            
            if result["status"] == "success":
                print(f"✅ {code} 分析成功")
                
                # 显示基本信息
                latest_info = result["latest_info"]
                signals = result["signals"]
                summary = result["summary"]
                
                print(f"   📈 最新价格: {latest_info['price']:.2f}")
                print(f"   📅 最新时间: {latest_info['time']}")
                print(f"   🟢 买入信号数: {signals['total_buy_count']}")
                print(f"   🔴 卖出信号数: {signals['total_sell_count']}")
                print(f"   💪 信号强度: {summary['signal_strength']}")
                
                # 显示最新信号
                latest_signals = result["latest_signals"]
                if latest_signals["latest_buy"]:
                    latest_buy = latest_signals["latest_buy"]
                    print(f"   🆕 最新买入: {latest_buy['type']} @ {latest_buy['price']:.2f} ({latest_buy['time']})")
                
                if latest_signals["latest_sell"]:
                    latest_sell = latest_signals["latest_sell"]
                    print(f"   🆕 最新卖出: {latest_sell['type']} @ {latest_sell['price']:.2f} ({latest_sell['time']})")
                
                # 显示最近3个买卖信号
                if signals["buy_signals"]:
                    print(f"   🔍 最近买入信号:")
                    for signal in signals["buy_signals"][-3:]:
                        print(f"      {signal['time']}: {signal['type']} @ {signal['price']:.2f}")
                
                if signals["sell_signals"]:
                    print(f"   🔍 最近卖出信号:")
                    for signal in signals["sell_signals"][-3:]:
                        print(f"      {signal['time']}: {signal['type']} @ {signal['price']:.2f}")
                        
            else:
                print(f"❌ {code} 分析失败: {result['error']}")
                
        except Exception as e:
            print(f"❌ {code} 分析出错: {e}")
            print(f"详细错误: {traceback.format_exc()}")
    
    print("\n" + "=" * 50)
    
    # 测试批量分析
    print("📊 测试批量分析...")
    try:
        batch_result = extractor.extract_multiple_signals(test_stocks, "1d")
        
        if batch_result:
            summary = batch_result["summary"]
            print(f"✅ 批量分析完成")
            print(f"   📈 总股票数: {summary['total_stocks']}")
            print(f"   ✅ 成功分析: {summary['successful']}")
            print(f"   ❌ 失败分析: {summary['failed']}")
            
            if summary['strong_buy_stocks']:
                print(f"   🟢 强买入股票: {summary['strong_buy_stocks']}")
            if summary['strong_sell_stocks']:
                print(f"   🔴 强卖出股票: {summary['strong_sell_stocks']}")
            if summary['neutral_stocks']:
                print(f"   ⚪ 中性股票: {summary['neutral_stocks']}")
        else:
            print("❌ 批量分析失败")
            
    except Exception as e:
        print(f"❌ 批量分析出错: {e}")
    
    print("\n🎉 测试完成!")
    return True

def test_environment():
    """测试环境依赖"""
    print("🔧 检查环境依赖...")
    
    required_modules = [
        "pandas", "matplotlib", "numpy", "requests", "flask",
        "Chan", "ChanConfig", "Plot.PlotMeta"
    ]
    
    missing_modules = []
    
    for module in required_modules:
        try:
            __import__(module)
            print(f"✅ {module}")
        except ImportError as e:
            print(f"❌ {module}: {e}")
            missing_modules.append(module)
    
    if missing_modules:
        print(f"\n⚠️  缺少以下模块: {missing_modules}")
        print("请运行: pip install flask pandas matplotlib numpy requests")
        return False
    else:
        print("✅ 所有依赖模块都已安装")
        return True

def main():
    """主测试函数"""
    print("🚀 股票买卖信号API测试")
    print("=" * 60)
    
    # 检查环境
    if not test_environment():
        print("\n❌ 环境检查失败，请先安装缺少的依赖")
        return
    
    print("\n" + "=" * 60)
    
    # 测试信号提取
    try:
        test_signal_extraction()
    except Exception as e:
        print(f"❌ 测试过程中出现错误: {e}")
        print(f"详细错误信息:\n{traceback.format_exc()}")
    
    print("\n📖 使用说明:")
    print("1. 启动API服务: python stock_signals_api.py")
    print("2. 测试客户端: python client_demo.py") 
    print("3. 浏览器访问: http://localhost:5000/api/signals/demo")
    print("4. 查看文档: 请阅读 STOCK_SIGNALS_API.md")

if __name__ == "__main__":
    main()