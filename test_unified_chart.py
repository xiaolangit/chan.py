#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速测试统一多时间框架图表
"""

import sys
import os

def test_imports():
    """测试导入"""
    try:
        print("正在测试导入...")
        from Chan import CChan
        from ChanConfig import CChanConfig
        from Common.CEnum import AUTYPE, KL_TYPE
        from Plot.PlotMeta import CChanPlotMeta
        from DataAPI.QmtStockAPI import CQMTData
        import matplotlib.pyplot as plt
        print("✓ 所有模块导入成功")
        return True
    except ImportError as e:
        print(f"✗ 导入失败: {e}")
        return False

def test_data_source():
    """测试数据源"""
    try:
        print("正在测试数据源...")
        from DataAPI.QmtStockAPI import CQMTData
        from Common.CEnum import KL_TYPE, AUTYPE
        
        # 创建数据源实例
        data_source = CQMTData(
            code="159647.SZ",
            k_type=KL_TYPE.K_DAY,
            begin_date="20240101",
            autype=AUTYPE.QFQ
        )
        print("✓ 数据源初始化成功")
        return True
    except Exception as e:
        print(f"✗ 数据源测试失败: {e}")
        return False

def test_single_timeframe():
    """测试单个时间框架"""
    try:
        print("正在测试单个时间框架...")
        from Chan import CChan
        from ChanConfig import CChanConfig
        from Common.CEnum import AUTYPE, KL_TYPE
        
        config = CChanConfig({
            "bi_strict": True,
            "trigger_step": False,
            "skip_step": 0,
            "divergence_rate": float("inf"),
            "print_warning": False,  # 关闭警告以减少输出
        })
        
        chan = CChan(
            code="159647.SZ",
            begin_time="20240601",  # 使用更短的时间范围进行测试
            end_time=None,
            data_src="custom:QmtStockAPI.CQMTData",
            lv_list=[KL_TYPE.K_DAY],
            config=config,
            autype=AUTYPE.QFQ,
        )
        
        print("✓ 单个时间框架测试成功")
        return True
    except Exception as e:
        print(f"✗ 单个时间框架测试失败: {e}")
        return False

def run_unified_chart():
    """运行统一图表"""
    try:
        print("正在运行统一多时间框架图表...")
        import demo_qmt_unified_chart_fixed
        print("✓ 统一图表运行成功")
        return True
    except Exception as e:
        print(f"✗ 统一图表运行失败: {e}")
        print(f"错误详情: {str(e)}")
        return False

def main():
    """主函数"""
    print("统一多时间框架图表测试")
    print("=" * 40)
    
    # 逐步测试
    tests = [
        ("导入测试", test_imports),
        ("数据源测试", test_data_source),
        ("单时间框架测试", test_single_timeframe),
        ("统一图表测试", run_unified_chart),
    ]
    
    for test_name, test_func in tests:
        print(f"\n{test_name}:")
        if not test_func():
            print(f"\n测试失败在: {test_name}")
            print("请根据错误信息修复问题后重试")
            return
        
    print("\n" + "=" * 40)
    print("✓ 所有测试通过！")
    print("统一多时间框架图表应该已经生成")
    print("请查看当前目录下的 unified_multi_timeframe_159647_SZ.png 文件")

if __name__ == "__main__":
    main()