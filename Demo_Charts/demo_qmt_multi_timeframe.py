from Chan import CChan
from ChanConfig import CChanConfig
from Common.CEnum import AUTYPE, DATA_SRC, KL_TYPE
from Plot.PlotDriver import CPlotDriver
import matplotlib.pyplot as plt

def create_multi_timeframe_chart():
    """
    创建多时间框架的缠论分析图表
    包含1分钟、5分钟、15分钟、1天四个时间维度
    """
    
    code = "159647.SZ"
    begin_time = "20240101"
    end_time = None
    data_src = "custom:QmtStockAPI.CQMTData"
    
    # 定义四个时间框架
    timeframes = {
        "1分钟": KL_TYPE.K_1M,
        "5分钟": KL_TYPE.K_5M, 
        "15分钟": KL_TYPE.K_15M,
        "1天": KL_TYPE.K_DAY
    }
    
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
        "plot_macd": False,
        "plot_mean": False,
        "plot_channel": False,
        "plot_bsp": True,
        "plot_extrainfo": False,
        "plot_demark": False,
        "plot_marker": False,
        "plot_rsi": False,
        "plot_kdj": False,
    }

    # 绘图参数
    plot_para = {
        "seg": {
            # "plot_trendline": True,
        },
        "bi": {
            # "show_num": True,
            # "disp_end": True,
        },
        "figure": {
            "x_range": 200,  # 显示最近200根K线
            "w": 30,         # 图表宽度
            "h": 8,          # 每个子图高度
        },
        "marker": {
            # "markers": {  # text, position, color
            #     '2024/06/01': ('marker here', 'up', 'red'),
            #     '2024/06/08': ('marker here', 'down')
            # },
        }
    }
    
    # 创建2x2的子图布局
    fig, axes = plt.subplots(2, 2, figsize=(30, 20))
    fig.suptitle(f'{code} 多时间框架缠论分析', fontsize=16, fontweight='bold')
    
    # 为每个时间框架创建缠论分析
    timeframe_names = list(timeframes.keys())
    timeframe_types = list(timeframes.values())
    
    for i, (name, kl_type) in enumerate(timeframes.items()):
        print(f"正在处理 {name} 时间框架...")
        
        try:
            # 为每个时间框架创建独立的CChan实例
            chan = CChan(
                code=code,
                begin_time=begin_time,
                end_time=end_time,
                data_src=data_src,
                lv_list=[kl_type],  # 每个实例只包含一个时间级别
                config=config,
                autype=AUTYPE.QFQ,
            )
            
            # 调整绘图参数以适应不同时间框架
            adjusted_plot_para = plot_para.copy()
            if kl_type == KL_TYPE.K_1M:
                adjusted_plot_para["figure"]["x_range"] = 300  # 1分钟显示更多K线
            elif kl_type == KL_TYPE.K_5M:
                adjusted_plot_para["figure"]["x_range"] = 200
            elif kl_type == KL_TYPE.K_15M:
                adjusted_plot_para["figure"]["x_range"] = 150
            else:  # 日线
                adjusted_plot_para["figure"]["x_range"] = 100
            
            # 创建单独的绘图驱动器
            plot_driver = CPlotDriver(
                chan,
                plot_config=plot_config,
                plot_para=adjusted_plot_para,
            )
            
            # 获取当前子图位置
            row = i // 2
            col = i % 2
            current_ax = axes[row, col]
            
            # 将绘图内容复制到指定的子图中
            # 这里需要手动绘制，因为PlotDriver默认创建自己的图表
            plot_driver.figure.savefig(f'temp_{name}.png', dpi=100, bbox_inches='tight')
            
            # 在子图中设置标题
            current_ax.set_title(f'{name} ({kl_type.name})', fontsize=14, fontweight='bold')
            current_ax.text(0.5, 0.5, f'{name}\n正在生成图表...', 
                          horizontalalignment='center', verticalalignment='center',
                          transform=current_ax.transAxes, fontsize=12)
            
            print(f"{name} 时间框架处理完成")
            
        except Exception as e:
            print(f"处理 {name} 时间框架时出错: {str(e)}")
            row = i // 2
            col = i % 2
            current_ax = axes[row, col]
            current_ax.set_title(f'{name} (错误)', fontsize=14, fontweight='bold', color='red')
            current_ax.text(0.5, 0.5, f'{name}\n数据获取失败:\n{str(e)}', 
                          horizontalalignment='center', verticalalignment='center',
                          transform=current_ax.transAxes, fontsize=10, color='red')
    
    # 调整子图间距
    plt.tight_layout()
    plt.subplots_adjust(top=0.95)  # 为主标题留出空间
    
    # 保存图表
    plt.savefig('./multi_timeframe_chart.png', dpi=300, bbox_inches='tight')
    print("多时间框架图表已保存为 multi_timeframe_chart.png")
    
    # 显示图表
    plt.show()
    
    return fig

def create_individual_charts():
    """
    创建独立的时间框架图表
    这是一个替代方案，为每个时间框架创建单独的完整图表
    """
    
    code = "159647.SZ"
    begin_time = "20240101"
    end_time = None
    data_src = "custom:QmtStockAPI.CQMTData"
    
    # 定义四个时间框架
    timeframes = {
        "1分钟": KL_TYPE.K_1M,
        "5分钟": KL_TYPE.K_5M,
        "15分钟": KL_TYPE.K_15M,
        "1天": KL_TYPE.K_DAY
    }
    
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
        "plot_macd": False,
        "plot_mean": False,
        "plot_channel": False,
        "plot_bsp": True,
        "plot_extrainfo": False,
        "plot_demark": False,
        "plot_marker": False,
        "plot_rsi": False,
        "plot_kdj": False,
    }

    # 绘图参数
    plot_para = {
        "seg": {},
        "bi": {},
        "figure": {
            "x_range": 200,
            "w": 24,
            "h": 10,
        },
        "marker": {}
    }
    
    # 为每个时间框架创建独立图表
    for name, kl_type in timeframes.items():
        print(f"正在处理 {name} 时间框架...")
        
        try:
            # 调整绘图参数
            adjusted_plot_para = plot_para.copy()
            if kl_type == KL_TYPE.K_1M:
                adjusted_plot_para["figure"]["x_range"] = 300
            elif kl_type == KL_TYPE.K_5M:
                adjusted_plot_para["figure"]["x_range"] = 200
            elif kl_type == KL_TYPE.K_15M:
                adjusted_plot_para["figure"]["x_range"] = 150
            else:  # 日线
                adjusted_plot_para["figure"]["x_range"] = 100
            
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
            
            # 创建绘图驱动器
            plot_driver = CPlotDriver(
                chan,
                plot_config=plot_config,
                plot_para=adjusted_plot_para,
            )
            
            # 设置图表标题
            plot_driver.figure.suptitle(f'{code} - {name} 缠论分析', fontsize=16, fontweight='bold')
            
            # 保存图表
            filename = f"./chart_{name.replace('分钟', 'min').replace('天', 'day')}.png"
            plot_driver.save2img(filename)
            print(f"{name} 图表已保存为 {filename}")
            
        except Exception as e:
            print(f"处理 {name} 时间框架时出错: {str(e)}")
            continue
    
    print("所有时间框架图表处理完成")

if __name__ == "__main__":
    print("开始生成多时间框架缠论分析图表...")
    
    # 方法1：创建单独的图表文件（推荐）
    print("\n=== 创建独立时间框架图表 ===")
    create_individual_charts()
    
    # 方法2：创建多子图组合（可选）
    print("\n=== 创建多时间框架组合图表 ===")
    try:
        create_multi_timeframe_chart()
    except Exception as e:
        print(f"创建组合图表时出错: {str(e)}")
        print("请检查数据源连接和配置")