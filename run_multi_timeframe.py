#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
多时间框架缠论分析运行脚本
"""

import sys
import os

def install_dependencies():
    """安装必要的依赖包"""
    try:
        import pandas
        import matplotlib
        import numpy
        import requests
        print("✓ 所有依赖已安装")
        return True
    except ImportError as e:
        print(f"✗ 缺少依赖: {e}")
        print("请运行: pip install pandas matplotlib numpy requests")
        return False

def check_environment():
    """检查运行环境"""
    print("=== 环境检查 ===")
    
    # 检查Python版本
    print(f"Python版本: {sys.version}")
    
    # 检查当前目录
    print(f"当前目录: {os.getcwd()}")
    
    # 检查核心文件
    required_files = [
        'Chan.py',
        'ChanConfig.py', 
        'DataAPI/QmtStockAPI.py',
        'Common/CEnum.py',
        'Plot/PlotDriver.py'
    ]
    
    missing_files = []
    for file in required_files:
        if os.path.exists(file):
            print(f"✓ {file}")
        else:
            print(f"✗ {file}")
            missing_files.append(file)
    
    if missing_files:
        print(f"缺少关键文件: {missing_files}")
        return False
        
    return install_dependencies()

def run_simple_test():
    """运行简单测试"""
    print("\n=== 运行简单测试 ===")
    
    try:
        # 测试导入
        from DataAPI.QmtStockAPI import CQMTData
        from Common.CEnum import KL_TYPE, AUTYPE
        print("✓ 核心模块导入成功")
        
        # 测试数据源初始化
        data_source = CQMTData(
            code="159647.SZ",
            k_type=KL_TYPE.K_DAY,
            begin_date="20240101",
            autype=AUTYPE.QFQ
        )
        print("✓ QMT数据源初始化成功")
        
        return True
        
    except Exception as e:
        print(f"✗ 测试失败: {e}")
        return False

def run_multi_timeframe_demo():
    """运行多时间框架演示"""
    print("\n=== 运行多时间框架演示 ===")
    
    try:
        # 尝试运行完整统一图表版本（4个时间框架在一张图上，完整买卖点）
        print("运行完整多时间框架演示（4个时间框架在一张图上，模仿图1效果）...")
        import demo_qmt_unified_chart_complete
        return True
        
    except Exception as e:
        print(f"✗ 统一图表版本运行失败: {e}")
        
        try:
            # 尝试运行高级版本
            print("运行高级多时间框架演示（独立图表）...")
            import demo_qmt_advanced_multi
            return True
            
        except Exception as e:
            print(f"✗ 高级版本运行失败: {e}")
            
            try:
                # 尝试运行基础版本
                print("运行基础多时间框架演示...")
                import demo_qmt_multi_timeframe
                return True
                
            except Exception as e:
                print(f"✗ 基础版本运行失败: {e}")
                
                try:
                    # 尝试运行单时间框架
                    print("运行单时间框架演示...")
                    import demo_qmt
                    return True
                    
                except Exception as e:
                    print(f"✗ 单时间框架运行失败: {e}")
                    return False

def main():
    """主函数"""
    print("多时间框架缠论分析系统")
    print("=" * 50)
    
    # 检查环境
    if not check_environment():
        print("\n环境检查失败，请解决上述问题后重试")
        return
        
    # 运行测试
    if not run_simple_test():
        print("\n简单测试失败，请检查代码和依赖")
        return
        
    # 运行演示
    if run_multi_timeframe_demo():
        print("\n✓ 演示运行成功！")
        print("\n生成的文件:")
        
        possible_files = [
            "complete_multi_timeframe_159647_SZ.png",
            "unified_multi_timeframe_159647_SZ.png",
            "chart_1min.png",
            "chart_5min.png", 
            "chart_15min.png",
            "chart_1day.png",
            "summary_analysis.png",
            "unified_multi_timeframe.png",
            "test.png"
        ]
        
        for file in possible_files:
            if os.path.exists(file):
                print(f"- {file}")
                
    else:
        print("\n✗ 演示运行失败")
        
    print("\n使用说明:")
    print("1. 完整多时间框架（4个时间框架在一张图上，模仿图1效果）: python demo_qmt_unified_chart_complete.py")
    print("2. 独立多时间框架图表: python demo_qmt_advanced_multi.py")
    print("3. 单时间框架: python demo_qmt.py")
    print("4. 查看文档: cat README_MultiTimeframe.md")

if __name__ == "__main__":
    main()