from Chan import CChan
from ChanConfig import CChanConfig
from Common.CEnum import AUTYPE, DATA_SRC, KL_TYPE
from Plot.PlotDriver import CPlotDriver
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.patches import Rectangle
import numpy as np

def create_advanced_multi_timeframe():
    """
    创建高级多时间框架缠论分析图表
    在单个图表中同时显示1分钟、5分钟、15分钟、1天的缠论分析
    """
    
    code = "159647.SZ"
    begin_time = "20240101"
    end_time = None
    data_src = "custom:QmtStockAPI.CQMTData"
    
    # 定义四个时间框架
    timeframes = [
        ("1分钟", KL_TYPE.K_1M),
        ("5分钟", KL_TYPE.K_5M),
        ("15分钟", KL_TYPE.K_15M),
        ("1天", KL_TYPE.K_DAY)
    ]
    
    # 缠论配置
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
        "print_warning": True,
        "zs_algo": "normal",
    })

    # 绘图配置
    plot_config = {
        "plot_kline": True,
        "plot_kline_combine": True,
        "plot_bi": True,
        "plot_seg": True,
        "plot_eigen": False,
        "plot_zs": True,
        "plot_macd": True,  # 启用MACD显示
        "plot_mean": False,
        "plot_channel": False,
        "plot_bsp": True,
        "plot_extrainfo": False,
        "plot_demark": False,
        "plot_marker": False,
        "plot_rsi": False,
        "plot_kdj": False,
    }

    # 创建主图和子图
    fig = plt.figure(figsize=(32, 24))
    gs = gridspec.GridSpec(2, 2, hspace=0.3, wspace=0.2)
    
    # 设置主标题
    fig.suptitle(f'{code} 多时间框架缠论分析 - 1分钟/5分钟/15分钟/日线', 
                fontsize=20, fontweight='bold', y=0.98)
    
    # 存储所有缠论分析实例
    chan_instances = {}
    
    print("开始创建多时间框架缠论分析...")
    
    for i, (name, kl_type) in enumerate(timeframes):
        print(f"正在处理 {name} 时间框架...")
        
        try:
            # 调整绘图参数
            plot_para = {
                "seg": {},
                "bi": {},
                "figure": {
                    "w": 15,
                    "h": 10,
                    "macd_h": 0.3,  # MACD子图高度比例
                },
                "marker": {}
            }
            
            # 根据时间框架调整显示的K线数量
            if kl_type == KL_TYPE.K_1M:
                plot_para["figure"]["x_range"] = 500  # 1分钟显示更多K线
            elif kl_type == KL_TYPE.K_5M:
                plot_para["figure"]["x_range"] = 300
            elif kl_type == KL_TYPE.K_15M:
                plot_para["figure"]["x_range"] = 200
            else:  # 日线
                plot_para["figure"]["x_range"] = 120
            
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
            
            # 保存实例
            chan_instances[name] = chan
            
            # 创建独立的图表
            plot_driver = CPlotDriver(
                chan,
                plot_config=plot_config,
                plot_para=plot_para,
            )
            
            # 设置子图标题
            plot_driver.figure.suptitle(f'{name} 时间框架', fontsize=16, fontweight='bold')
            
            # 保存独立图表
            filename = f"./chart_{name.replace('分钟', 'min').replace('天', 'day')}.png"
            plot_driver.save2img(filename)
            
            print(f"{name} 时间框架处理完成，已保存为 {filename}")
            
        except Exception as e:
            print(f"处理 {name} 时间框架时出错: {str(e)}")
            continue
    
    # 创建汇总信息图表
    create_summary_chart(chan_instances, code)
    
    print("所有时间框架处理完成！")
    print("\n生成的文件:")
    print("- chart_1min.png (1分钟图表)")
    print("- chart_5min.png (5分钟图表)")  
    print("- chart_15min.png (15分钟图表)")
    print("- chart_1day.png (日线图表)")
    print("- summary_analysis.png (汇总分析)")


def create_summary_chart(chan_instances, code):
    """
    创建汇总分析图表，显示各时间框架的关键信息
    """
    if not chan_instances:
        print("没有可用的缠论分析实例，跳过汇总图表创建")
        return
        
    try:
        fig, axes = plt.subplots(2, 2, figsize=(20, 16))
        fig.suptitle(f'{code} 多时间框架缠论分析汇总', fontsize=16, fontweight='bold')
        
        timeframes = list(chan_instances.keys())
        
        for i, (name, chan) in enumerate(chan_instances.items()):
            row = i // 2
            col = i % 2
            ax = axes[row, col]
            
            # 获取缠论分析结果
            try:
                kl_data = chan[list(chan.lv_list)[0]]
                
                # 绘制简化的K线图
                if hasattr(kl_data, 'lst') and len(kl_data.lst) > 0:
                    # 获取最近的数据
                    recent_data = kl_data.lst[-50:] if len(kl_data.lst) > 50 else kl_data.lst
                    
                    # 绘制简化的价格走势
                    closes = [k.close for k in recent_data]
                    highs = [k.high for k in recent_data]
                    lows = [k.low for k in recent_data]
                    
                    x = range(len(closes))
                    ax.plot(x, closes, 'b-', linewidth=1, label='收盘价')
                    ax.fill_between(x, lows, highs, alpha=0.3, color='gray', label='高低区间')
                    
                    # 设置标题和标签
                    ax.set_title(f'{name} - 最近趋势', fontsize=12, fontweight='bold')
                    ax.set_ylabel('价格')
                    ax.legend()
                    ax.grid(True, alpha=0.3)
                    
                    # 添加统计信息
                    current_price = closes[-1] if closes else 0
                    price_change = ((closes[-1] - closes[0]) / closes[0] * 100) if len(closes) > 1 and closes[0] != 0 else 0
                    
                    info_text = f'当前价: {current_price:.2f}\n变化: {price_change:+.2f}%'
                    ax.text(0.02, 0.98, info_text, transform=ax.transAxes, 
                           verticalalignment='top', fontsize=10,
                           bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.8))
                
                else:
                    ax.text(0.5, 0.5, f'{name}\n暂无数据', ha='center', va='center',
                           transform=ax.transAxes, fontsize=12)
                    ax.set_title(f'{name} - 无数据', fontsize=12)
                    
            except Exception as e:
                ax.text(0.5, 0.5, f'{name}\n数据处理错误:\n{str(e)}', ha='center', va='center',
                       transform=ax.transAxes, fontsize=10, color='red')
                ax.set_title(f'{name} - 错误', fontsize=12, color='red')
        
        plt.tight_layout()
        plt.savefig('./summary_analysis.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        print("汇总分析图表已保存为 summary_analysis.png")
        
    except Exception as e:
        print(f"创建汇总图表时出错: {str(e)}")


def create_unified_multi_timeframe():
    """
    创建统一的多时间框架图表（所有时间框架在一个图中）
    这个版本尝试将所有时间框架的数据合并到一个图表中
    """
    
    code = "159647.SZ" 
    begin_time = "20240101"
    end_time = None
    data_src = "custom:QmtStockAPI.CQMTData"
    
    # 使用多个时间级别创建一个CChan实例
    lv_list = [KL_TYPE.K_1M, KL_TYPE.K_5M, KL_TYPE.K_15M, KL_TYPE.K_DAY]
    
    # 缠论配置
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
        "print_warning": True,
        "zs_algo": "normal",
    })

    # 多级别绘图配置
    plot_config = {
        KL_TYPE.K_1M: {
            "plot_kline": True,
            "plot_bi": True,
            "plot_seg": True,
            "plot_zs": True,
            "plot_bsp": True,
            "plot_macd": True,
        },
        KL_TYPE.K_5M: {
            "plot_kline": True,
            "plot_bi": True,
            "plot_seg": True,
            "plot_zs": True,
            "plot_bsp": True,
            "plot_macd": True,
        },
        KL_TYPE.K_15M: {
            "plot_kline": True,
            "plot_bi": True,
            "plot_seg": True,
            "plot_zs": True,
            "plot_bsp": True,
            "plot_macd": True,
        },
        KL_TYPE.K_DAY: {
            "plot_kline": True,
            "plot_bi": True,
            "plot_seg": True,
            "plot_zs": True,
            "plot_bsp": True,
            "plot_macd": True,
        }
    }

    # 绘图参数
    plot_para = {
        "figure": {
            "x_range": 200,
            "w": 32,
            "h": 8,
            "macd_h": 0.3,
        }
    }
    
    try:
        print("正在创建统一多时间框架缠论分析...")
        
        # 创建多级别缠论分析
        chan = CChan(
            code=code,
            begin_time=begin_time,
            end_time=end_time,
            data_src=data_src,
            lv_list=lv_list,
            config=config,
            autype=AUTYPE.QFQ,
        )
        
        # 创建绘图驱动器
        plot_driver = CPlotDriver(
            chan,
            plot_config=plot_config,
            plot_para=plot_para,
        )
        
        # 设置图表标题
        plot_driver.figure.suptitle(f'{code} 统一多时间框架缠论分析\n1分钟/5分钟/15分钟/日线', 
                                   fontsize=16, fontweight='bold')
        
        # 保存图表
        plot_driver.save2img("./unified_multi_timeframe.png")
        print("统一多时间框架图表已保存为 unified_multi_timeframe.png")
        
        # 显示图表
        plot_driver.figure.show()
        
    except Exception as e:
        print(f"创建统一多时间框架图表时出错: {str(e)}")
        print("建议使用独立图表模式")


if __name__ == "__main__":
    print("=== 多时间框架缠论分析系统 ===")
    print("将生成以下时间框架的缠论分析:")
    print("- 1分钟级别")
    print("- 5分钟级别") 
    print("- 15分钟级别")
    print("- 1天级别")
    print()
    
    # 方法1：创建独立的多时间框架图表（推荐）
    print("1. 创建独立时间框架图表...")
    create_advanced_multi_timeframe()
    
    print("\n" + "="*50)
    
    # 方法2：创建统一的多时间框架图表（实验性）
    print("2. 尝试创建统一多时间框架图表...")
    try:
        create_unified_multi_timeframe()
    except Exception as e:
        print(f"统一图表创建失败: {str(e)}")
        print("这是正常的，因为多时间框架统一显示比较复杂")
    
    print("\n分析完成！请检查生成的图表文件。")