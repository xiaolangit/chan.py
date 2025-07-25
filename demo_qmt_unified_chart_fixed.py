from Chan import CChan
from ChanConfig import CChanConfig
from Common.CEnum import AUTYPE, DATA_SRC, KL_TYPE
from Plot.PlotDriver import CPlotDriver
from Plot.PlotMeta import CChanPlotMeta
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import numpy as np
import warnings

# 设置中文字体支持
plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

# 过滤matplotlib的布局警告
warnings.filterwarnings('ignore', category=UserWarning, module='matplotlib')

def create_unified_multi_timeframe_chart():
    """
    创建真正的4个时间框架在一张图上的缠论分析
    类似图2的效果：2x2布局，每个子图显示一个时间框架
    """
    
    code = "159647.SZ"
    begin_time = "20240101"
    end_time = None
    data_src = "custom:QmtStockAPI.CQMTData"
    
    # 定义四个时间框架
    timeframes = [
        ("1min", KL_TYPE.K_1M),
        ("5min", KL_TYPE.K_5M),
        ("15min", KL_TYPE.K_15M),
        ("1day", KL_TYPE.K_DAY)
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
        "plot_macd": False,  # 在统一视图中关闭MACD以节省空间
        "plot_mean": False,
        "plot_channel": False,
        "plot_bsp": True,
        "plot_extrainfo": False,
        "plot_demark": False,
        "plot_marker": False,
        "plot_rsi": False,
        "plot_kdj": False,
    }

    # 创建主图表 - 2x2布局
    fig = plt.figure(figsize=(24, 16))
    gs = gridspec.GridSpec(2, 2, hspace=0.3, wspace=0.25, 
                          left=0.05, right=0.95, top=0.93, bottom=0.07)
    
    # 设置主标题
    fig.suptitle(f'{code} Multi-Timeframe Chan Analysis with Buy/Sell Points\n1min | 5min | 15min | 1day', 
                fontsize=18, fontweight='bold', y=0.96)
    
    # 收集所有缠论分析数据
    chan_data = {}
    plot_metas = {}
    
    print("正在获取多时间框架数据...")
    
    # 为每个时间框架创建缠论分析实例
    for i, (name, kl_type) in enumerate(timeframes):
        print(f"处理 {name} 数据...")
        
        try:
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
            
            chan_data[name] = chan
            plot_metas[name] = CChanPlotMeta(chan[kl_type])
            print(f"✓ {name} 数据获取成功")
            
        except Exception as e:
            print(f"✗ {name} 数据获取失败: {str(e)}")
            chan_data[name] = None
            plot_metas[name] = None
    
    print("开始绘制统一图表...")
    
    # 在2x2网格中绘制每个时间框架
    for i, (name, kl_type) in enumerate(timeframes):
        row = i // 2
        col = i % 2
        
        # 创建子图
        ax = fig.add_subplot(gs[row, col])
        
        if chan_data[name] is None or plot_metas[name] is None:
            # 如果数据获取失败，显示错误信息
            ax.text(0.5, 0.5, f'{name}\nData Failed', 
                   ha='center', va='center', transform=ax.transAxes,
                   fontsize=14, color='red')
            ax.set_title(f'{name} - Error', fontsize=14, color='red')
            continue
        
        # 获取缠论分析数据
        chan = chan_data[name]
        meta = plot_metas[name]
        
        try:
            # 调整显示的K线数量
            if kl_type == KL_TYPE.K_1M:
                x_range = 300
            elif kl_type == KL_TYPE.K_5M:
                x_range = 200
            elif kl_type == KL_TYPE.K_15M:
                x_range = 150
            else:  # 日线
                x_range = 100
            
            # 计算X轴范围
            X_LEN = meta.klu_len
            if x_range and X_LEN > x_range:
                x_limits = [X_LEN - x_range, X_LEN - 1]
            else:
                x_limits = [0, X_LEN - 1]
            
            # 设置X轴
            ax.set_xlim(x_limits[0], x_limits[1]+1)
            tick_step = max(1, int((x_limits[1] - x_limits[0]) / 8))
            tick_positions = range(x_limits[0], x_limits[1], tick_step)
            ax.set_xticks(tick_positions)
            ax.set_xticklabels([meta.datetick[i] for i in tick_positions if i < len(meta.datetick)], 
                              rotation=45, fontsize=8)
            
            # 计算初始Y轴范围
            y_min = float("inf")
            y_max = float("-inf")
            for klc_meta in meta.klc_list:
                if klc_meta.klu_list[-1].idx < x_limits[0]:
                    continue
                if klc_meta.high > y_max:
                    y_max = klc_meta.high
                if klc_meta.low < y_min:
                    y_min = klc_meta.low
            
            # 先设置一个临时的Y轴范围，用于买卖点箭头计算
            y_margin = (y_max - y_min) * 0.15  # 增加边距以容纳买卖点箭头
            ax.set_ylim(y_min - y_margin, y_max + y_margin)
            
            # 绘制缠论元素（包括买卖点箭头）
            final_y_min, final_y_max = draw_chan_elements(meta, ax, plot_config, x_limits, y_min, y_max)
            
            # 根据买卖点位置最终调整Y轴范围
            if final_y_min != y_min or final_y_max != y_max:
                final_margin = (final_y_max - final_y_min) * 0.05
                ax.set_ylim(final_y_min - final_margin, final_y_max + final_margin)
            
            # 设置子图标题和样式
            ax.set_title(f'{name}', fontsize=12, fontweight='bold', pad=10)
            ax.grid(True, alpha=0.3)
            ax.tick_params(labelsize=8)
            
            # 添加最新价格信息
            klu_list = list(meta.klu_iter())
            if klu_list:
                latest_klu = klu_list[-1]
                latest_price = latest_klu.close
                ax.text(0.02, 0.98, f'Latest: {latest_price:.2f}', 
                       transform=ax.transAxes, fontsize=10,
                       verticalalignment='top',
                       bbox=dict(boxstyle='round,pad=0.3', facecolor='lightblue', alpha=0.8))
            
            print(f"✓ {name} 图表绘制完成")
            
        except Exception as e:
            print(f"✗ {name} 图表绘制失败: {str(e)}")
            ax.text(0.5, 0.5, f'{name}\nDraw Failed:\n{str(e)}', 
                   ha='center', va='center', transform=ax.transAxes,
                   fontsize=10, color='red')
            ax.set_title(f'{name} - Draw Error', fontsize=12, color='red')
    
    # 调整布局
    plt.tight_layout(rect=[0, 0.03, 1, 0.93])
    
    # 保存图表
    filename = f'./unified_multi_timeframe_with_bsp_{code.replace(".", "_")}.png'
    plt.savefig(filename, dpi=300, bbox_inches='tight', facecolor='white')
    print(f"\n✓ Unified multi-timeframe chart with buy/sell points saved as: {filename}")
    
    # 显示图表
    plt.show()
    
    return fig

def draw_chan_elements(meta, ax, plot_config, x_limits, y_min, y_max):
    """
    绘制缠论分析元素
    """
    x_begin = x_limits[0]
    
    # 绘制K线
    if plot_config.get("plot_kline", False):
        draw_klines(meta, ax, x_begin)
    
    # 绘制合并K线
    if plot_config.get("plot_kline_combine", False):
        draw_combined_klines(meta, ax, x_begin)
    
    # 绘制笔
    if plot_config.get("plot_bi", False):
        draw_bi_lines(meta, ax, x_begin)
    
    # 绘制段
    if plot_config.get("plot_seg", False):
        draw_seg_lines(meta, ax, x_begin)
    
    # 绘制中枢
    if plot_config.get("plot_zs", False):
        draw_zs_boxes(meta, ax, x_begin)
    
    # 绘制买卖点（可能会更新Y轴范围）
    if plot_config.get("plot_bsp", False):
        final_y_min, final_y_max = draw_buy_sell_points_with_range(meta, ax, x_begin, y_min, y_max)
        return final_y_min, final_y_max
    
    return y_min, y_max

def draw_klines(meta, ax, x_begin):
    """绘制K线"""
    try:
        for kl in meta.klu_iter():
            i = kl.idx
            if i < x_begin:
                continue
            
            # K线颜色
            color = 'red' if kl.close >= kl.open else 'green'
            
            # 绘制实体
            height = abs(kl.close - kl.open)
            bottom = min(kl.open, kl.close)
            ax.bar(i, height, bottom=bottom, width=0.6, color=color, alpha=0.7)
            
            # 绘制影线
            ax.plot([i, i], [kl.low, kl.high], color=color, linewidth=1)
    except Exception as e:
        print(f"绘制K线时出错: {e}")

def draw_combined_klines(meta, ax, x_begin):
    """绘制合并K线"""
    try:
        for klc in meta.klc_list:
            if klc.klu_list[-1].idx < x_begin:
                continue
            
            # 绘制合并K线的边框
            x_start = klc.klu_list[0].idx
            x_end = klc.klu_list[-1].idx
            
            # 绘制合并K线轮廓
            ax.plot([x_start, x_end, x_end, x_start, x_start], 
                   [klc.low, klc.low, klc.high, klc.high, klc.low], 
                   color='blue', linewidth=1, alpha=0.5)
    except Exception as e:
        print(f"绘制合并K线时出错: {e}")

def draw_bi_lines(meta, ax, x_begin):
    """绘制笔"""
    try:
        if hasattr(meta, 'bi_list') and meta.bi_list:
            for bi in meta.bi_list:
                if bi.end_x < x_begin:
                    continue
                
                # 绘制笔的线段
                ax.plot([bi.begin_x, bi.end_x], [bi.begin_y, bi.end_y], 
                       color='blue', linewidth=2, alpha=0.8)
                
                # 标记分型点
                ax.scatter([bi.begin_x, bi.end_x], [bi.begin_y, bi.end_y], 
                          color='blue', s=30, zorder=5)
    except Exception as e:
        print(f"绘制笔时出错: {e}")

def draw_seg_lines(meta, ax, x_begin):
    """绘制段"""
    try:
        if hasattr(meta, 'seg_list') and meta.seg_list:
            for seg in meta.seg_list:
                if seg.end_x < x_begin:
                    continue
                
                # 绘制段的线段
                ax.plot([seg.begin_x, seg.end_x], [seg.begin_y, seg.end_y], 
                       color='purple', linewidth=3, alpha=0.7)
    except Exception as e:
        print(f"绘制段时出错: {e}")

def draw_zs_boxes(meta, ax, x_begin):
    """绘制中枢"""
    try:
        if hasattr(meta, 'zs_lst') and meta.zs_lst:
            from matplotlib.patches import Rectangle
            
            for zs in meta.zs_lst:
                if zs.end < x_begin:
                    continue
                
                # 绘制中枢矩形
                width = zs.end - zs.begin
                height = zs.high - zs.low
                rect = Rectangle((zs.begin, zs.low), width, height, 
                               linewidth=1, edgecolor='orange', 
                               facecolor='yellow', alpha=0.3)
                ax.add_patch(rect)
    except Exception as e:
        print(f"绘制中枢时出错: {e}")

def draw_buy_sell_points_with_range(meta, ax, x_begin, y_min, y_max):
    """绘制买卖点 - 模仿图1的箭头和标签效果，返回更新后的Y轴范围"""
    try:
        # 使用传入的Y轴范围计算箭头长度
        y_range = y_max - y_min
        final_y_min, final_y_max = y_min, y_max
        
        # 绘制普通买卖点
        if hasattr(meta, 'bs_point_lst') and meta.bs_point_lst:
            arrow_l = 0.12  # 箭头长度比例
            arrow_h = 0.2   # 箭头头部长度比例
            arrow_w = 1.0   # 箭头宽度
            fontsize = 10   # 字体大小
            
            for bsp in meta.bs_point_lst:
                if bsp.x < x_begin:
                    continue
                
                # 根据买卖点类型设置颜色和方向
                if bsp.is_buy:
                    color = 'red'
                    arrow_dir = 1  # 向上
                    verticalalignment = 'top'
                else:
                    color = 'green'
                    arrow_dir = -1  # 向下
                    verticalalignment = 'bottom'
                
                # 计算箭头参数
                arrow_len = arrow_l * y_range
                arrow_head = arrow_len * arrow_h
                
                # 计算文本和箭头位置
                text_y = bsp.y - arrow_len * arrow_dir
                
                # 绘制买卖点标签文本
                ax.text(bsp.x, text_y, f'{bsp.desc()}',
                       fontsize=fontsize,
                       color=color,
                       verticalalignment=verticalalignment,
                       horizontalalignment='center',
                       fontweight='bold',
                       bbox=dict(boxstyle='round,pad=0.2', facecolor='white', 
                                edgecolor=color, alpha=0.8))
                
                # 绘制指向买卖点的箭头
                ax.arrow(bsp.x, text_y, 0, (arrow_len - arrow_head) * arrow_dir,
                        head_width=arrow_w, head_length=arrow_head,
                        color=color, alpha=0.8, linewidth=1.5, zorder=10)
                
                # 更新Y轴范围
                if text_y < final_y_min:
                    final_y_min = text_y - arrow_len * 0.1
                if text_y > final_y_max:
                    final_y_max = text_y + arrow_len * 0.1
        
        # 绘制段买卖点
        if hasattr(meta, 'seg_bsp_lst') and meta.seg_bsp_lst:
            arrow_l_seg = 0.15  # 段买卖点箭头稍长一些
            fontsize_seg = 12   # 段买卖点字体稍大一些
            arrow_w_seg = 1.3   # 段买卖点箭头稍粗一些
            
            for seg_bsp in meta.seg_bsp_lst:
                if seg_bsp.x < x_begin:
                    continue
                
                # 根据买卖点类型设置颜色和方向
                if seg_bsp.is_buy:
                    color = 'darkred'
                    arrow_dir = 1
                    verticalalignment = 'top'
                else:
                    color = 'darkgreen'
                    arrow_dir = -1
                    verticalalignment = 'bottom'
                
                # 计算箭头参数
                arrow_len = arrow_l_seg * y_range
                arrow_head = arrow_len * arrow_h
                
                # 计算文本和箭头位置
                text_y = seg_bsp.y - arrow_len * arrow_dir
                
                # 绘制段买卖点标签文本
                ax.text(seg_bsp.x, text_y, f'{seg_bsp.desc()}',
                       fontsize=fontsize_seg,
                       color=color,
                       verticalalignment=verticalalignment,
                       horizontalalignment='center',
                       fontweight='bold',
                       bbox=dict(boxstyle='round,pad=0.3', facecolor='yellow', 
                                edgecolor=color, alpha=0.9))
                
                # 绘制指向段买卖点的箭头
                ax.arrow(seg_bsp.x, text_y, 0, (arrow_len - arrow_head) * arrow_dir,
                        head_width=arrow_w_seg, head_length=arrow_head,
                        color=color, alpha=0.9, linewidth=2, zorder=11)
                
                # 更新Y轴范围
                if text_y < final_y_min:
                    final_y_min = text_y - arrow_len * 0.1
                if text_y > final_y_max:
                    final_y_max = text_y + arrow_len * 0.1
        
        return final_y_min, final_y_max
        
    except Exception as e:
        print(f"绘制买卖点时出错: {e}")
        return y_min, y_max

if __name__ == "__main__":
    print("=== 创建统一多时间框架缠论分析图表（含买卖点标识）===")
    print("正在生成4个时间框架在一张图上的效果...")
    print("时间框架: 1分钟、5分钟、15分钟、1天")
    print("布局: 2x2 子图布局")
    print("特性: 包含完整的买卖点箭头和标签（b1, s2s等）")
    print()
    
    try:
        fig = create_unified_multi_timeframe_chart()
        print("\n✓ 统一图表创建成功！")
        print("请查看生成的图片文件。")
        
    except Exception as e:
        print(f"\n✗ 图表创建失败: {str(e)}")
        print("请检查数据源连接和依赖库安装。")
        
        # 提供备用方案
        print("\n备用方案：")
        print("如果统一图表创建失败，可以使用以下命令生成独立图表：")
        print("python demo_qmt_advanced_multi.py")