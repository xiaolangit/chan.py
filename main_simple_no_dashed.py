from Chan import CChan
from ChanConfig import CChanConfig
from Common.CEnum import AUTYPE, DATA_SRC, KL_TYPE
from Plot.AnimatePlotDriver import CAnimateDriver
from Plot.PlotDriver import CPlotDriver
import Plot.PlotDriver as PlotDriverModule


# 猴子补丁：修改原始的绘图函数，跳过虚线部分
def plot_seg_no_dashed_patch(original_func):
    """装饰器：修改线段绘制函数，跳过虚线"""
    def wrapper(*args, **kwargs):
        # 获取meta参数
        meta = args[0] if args else None
        ax = args[1] if len(args) > 1 else None
        
        if meta and ax:
            # 复制原函数的参数
            color = kwargs.get('color', args[2] if len(args) > 2 else 'purple')
            width = kwargs.get('width', args[3] if len(args) > 3 else 1)
            disp_end = kwargs.get('disp_end', args[4] if len(args) > 4 else False)
            end_fontsize = kwargs.get('end_fontsize', args[5] if len(args) > 5 else 25)
            end_color = kwargs.get('end_color', args[6] if len(args) > 6 else "blue")
            plot_trendline = kwargs.get('plot_trendline', args[7] if len(args) > 7 else False)
            
            x_begin = ax.get_xlim()[0]
            
            # 只绘制确定的线段
            for seg_idx, seg_meta in enumerate(meta.seg_list):
                if seg_meta.end_x < x_begin:
                    continue
                if seg_meta.is_sure:  # 只绘制确定的线段，跳过不确定的
                    ax.plot([seg_meta.begin_x, seg_meta.end_x], [seg_meta.begin_y, seg_meta.end_y], color=color, linewidth=width)
                    if disp_end:
                        PlotDriverModule.bi_text(seg_idx, ax, seg_meta, end_fontsize, end_color)
                    if plot_trendline:
                        if seg_meta.tl.get('support'):
                            tl_meta = seg_meta.format_tl(seg_meta.tl['support'])
                            ax.plot([tl_meta[0], tl_meta[2]], [tl_meta[1], tl_meta[3]], color='purple', linewidth=0.5)
                        if seg_meta.tl.get('resistance'):
                            tl_meta = seg_meta.format_tl(seg_meta.tl['resistance'])
                            ax.plot([tl_meta[0], tl_meta[2]], [tl_meta[1], tl_meta[3]], color='purple', linewidth=0.5)
        return None
    return wrapper


def plot_segseg_no_dashed_patch(original_func):
    """装饰器：修改段的段绘制函数，跳过虚线"""
    def wrapper(*args, **kwargs):
        meta = args[0] if args else None
        ax = args[1] if len(args) > 1 else None
        
        if meta and ax:
            color = kwargs.get('color', args[2] if len(args) > 2 else 'orange')
            width = kwargs.get('width', args[3] if len(args) > 3 else 2)
            disp_end = kwargs.get('disp_end', args[4] if len(args) > 4 else False)
            end_fontsize = kwargs.get('end_fontsize', args[5] if len(args) > 5 else 25)
            end_color = kwargs.get('end_color', args[6] if len(args) > 6 else "blue")
            
            x_begin = ax.get_xlim()[0]
            
            # 只绘制确定的段
            for seg_idx, seg_meta in enumerate(meta.segseg_list):
                if seg_meta.end_x < x_begin:
                    continue
                if seg_meta.is_sure:  # 只绘制确定的段，跳过不确定的
                    ax.plot([seg_meta.begin_x, seg_meta.end_x], [seg_meta.begin_y, seg_meta.end_y], color=color, linewidth=width)
                    if disp_end:
                        PlotDriverModule.bi_text(seg_idx, ax, seg_meta, end_fontsize, end_color)
        return None
    return wrapper


def plot_bi_element_no_dashed_patch(original_func):
    """装饰器：修改笔绘制函数，跳过虚线"""
    def wrapper(bi, ax, color):
        # 只绘制确定的笔
        if bi.is_sure:
            ax.plot([bi.begin_x, bi.end_x], [bi.begin_y, bi.end_y], color=color)
        return None
    return wrapper


# 应用猴子补丁
PlotDriverModule.plot_seg = plot_seg_no_dashed_patch(PlotDriverModule.plot_seg)
PlotDriverModule.plot_segseg = plot_segseg_no_dashed_patch(PlotDriverModule.plot_segseg)
PlotDriverModule.plot_bi_element = plot_bi_element_no_dashed_patch(PlotDriverModule.plot_bi_element)


if __name__ == "__main__":
    code = "sz.000001"
    begin_time = "2018-01-01"
    end_time = None
    data_src = DATA_SRC.BAO_STOCK
    lv_list = [KL_TYPE.K_DAY]

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

    plot_config = {
        "plot_kline": True,
        "plot_kline_combine": True,
        "plot_bi": True,        # 只显示确定的笔
        "plot_seg": True,       # 只显示确定的线段
        "plot_eigen": False,
        "plot_zs": True,        # 只显示确定的中枢
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

    plot_para = {
        "seg": {
            # "plot_trendline": True,
        },
        "bi": {
            # "show_num": True,
            # "disp_end": True,
        },
        "figure": {
            "x_range": 200,
        },
        "marker": {
            # "markers": {  # text, position, color
            #     '2023/06/01': ('marker here', 'up', 'red'),
            #     '2023/06/08': ('marker here', 'down')
            # },
        }
    }
    
    chan = CChan(
        code=code,
        begin_time=begin_time,
        end_time=end_time,
        data_src=data_src,
        lv_list=lv_list,
        config=config,
        autype=AUTYPE.QFQ,
    )

    if not config.trigger_step:
        plot_driver = CPlotDriver(
            chan,
            plot_config=plot_config,
            plot_para=plot_para,
        )
        plot_driver.figure.show()
        plot_driver.save2img("./test_no_dashed.png")
        print("图表已生成并保存为 test_no_dashed.png")
        print("已跳过所有虚线部分（不确定的笔、线段等）")
    else:
        CAnimateDriver(
            chan,
            plot_config=plot_config,
            plot_para=plot_para,
        )