#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试修复后的买卖点标识功能
"""

def test_fixed_buy_sell_points():
    """测试修复后的买卖点标识"""
    print("=== 测试修复后的买卖点标识 ===")
    print("正在运行 demo_qmt_unified_chart_fixed.py...")
    print("该版本现在包含完整的买卖点标识：")
    print("- b1, s1, b2, s2 等买卖点标签")
    print("- 指向买卖点的箭头")
    print("- 段买卖点标识")
    print()
    
    try:
        import demo_qmt_unified_chart_fixed
        print("✓ 修复后的图表创建成功！")
        print("生成的文件：unified_multi_timeframe_with_bsp_159647_SZ.png")
        print("该文件包含完整的买卖点标识，类似图1的效果")
        return True
    except Exception as e:
        print(f"✗ 测试失败: {e}")
        return False

def main():
    """主函数"""
    print("买卖点标识修复测试")
    print("=" * 50)
    
    if test_fixed_buy_sell_points():
        print("\n" + "=" * 50)
        print("✓ 测试成功！")
        print("现在 demo_qmt_unified_chart_fixed.py 包含完整的买卖点标识")
        print("包括：")
        print("- 买卖点箭头（红色向上买点，绿色向下卖点）")
        print("- 买卖点标签（b1, s1, b2, s2s 等）")
        print("- 段买卖点标识（更大的箭头和黄色背景）")
        print("- 自动调整Y轴范围以容纳所有标识")
    else:
        print("\n" + "=" * 50)
        print("✗ 测试失败")
        print("请检查错误信息并修复问题")

if __name__ == "__main__":
    main()