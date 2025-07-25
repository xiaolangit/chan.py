#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单测试股票信号提取
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Chan import CChan
from ChanConfig import CChanConfig
from Common.CEnum import AUTYPE, KL_TYPE
from Plot.PlotMeta import CChanPlotMeta
from DataAPI.QmtStockAPI import CQMTData

def test_single_stock():
    """测试单个股票"""
    print("测试单个股票信号提取...")
    
    try:
        code = "159647.SZ"
        begin_time = "20240101"
        end_time = None
        data_src = "custom:QmtStockAPI.CQMTData"
        kl_type = KL_TYPE.K_DAY
        
        config = CChanConfig({
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
        
        print(f"创建CChan实例：{code}, {kl_type}, {data_src}")
        
        # 为了确保CChan能够找到CQMTData类，我们需要将其添加到全局命名空间
        globals()['CQMTData'] = CQMTData
        
        # 创建缠论分析
        chan = CChan(
            code=code,
            begin_time=begin_time,
            end_time=end_time,
            data_src=data_src,
            lv_list=[kl_type],
            config=config,
            autype=AUTYPE.QFQ,
        )
        
        print("✅ CChan实例创建成功")
        
        # 获取绘图元数据
        meta = CChanPlotMeta(chan[kl_type])
        print("✅ CChanPlotMeta创建成功")
        
        # 检查买卖点
        if hasattr(meta, 'bs_point_lst'):
            print(f"普通买卖点数量: {len(meta.bs_point_lst) if meta.bs_point_lst else 0}")
        
        if hasattr(meta, 'seg_bsp_lst'):
            print(f"段买卖点数量: {len(meta.seg_bsp_lst) if meta.seg_bsp_lst else 0}")
        
        print("✅ 测试成功")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        print(f"错误详情:\n{traceback.format_exc()}")

if __name__ == "__main__":
    test_single_stock()