from Chan import CChan
from ChanConfig import CChanConfig
from Common.CEnum import AUTYPE, DATA_SRC, KL_TYPE
from Plot.AnimatePlotDriver import CAnimateDriver
from Plot.PlotDriver import CPlotDriver
from Plot.PlotMeta import CChanPlotMeta
import matplotlib.pyplot as plt
from matplotlib.axes import Axes
from typing import Optional


def plot_seg_no_dashed(
        meta: CChanPlotMeta,
        ax: Axes,
        color='purple',
        width=1,
        disp_end=False,
        end_fontsize=25,
        end_color="blue",
        plot_trendline=False,
        trendline_color='purple',
        trendline_width=0.5,
        show_num=False,
        num_fontsize=25,
        num_color="blue",
):
    """绘制线段，但跳过不确定的线段（虚线部分）"""
    x_begin = ax.get_xlim()[0]

    for seg_idx, seg_meta in enumerate(meta.seg_list):
        if seg_meta.end_x < x_begin:
            continue
        # 只绘制确定的线段，跳过不确定的线段
        if seg_meta.is_sure:
            ax.plot([seg_meta.begin_x, seg_meta.end_x], [seg_meta.begin_y, seg_meta.end_y], color=color, linewidth=width)
            if disp_end:
                from Plot.PlotDriver import bi_text
                bi_text(seg_idx, ax, seg_meta, end_fontsize, end_color)
            if plot_trendline:
                if seg_meta.tl.get('support'):
                    tl_meta = seg_meta.format_tl(seg_meta.tl['support'])
                    ax.plot([tl_meta[0], tl_meta[2]], [tl_meta[1], tl_meta[3]], color=trendline_color, linewidth=trendline_width)
                if seg_meta.tl.get('resistance'):
                    tl_meta = seg_meta.format_tl(seg_meta.tl['resistance'])
                    ax.plot([tl_meta[0], tl_meta[2]], [tl_meta[1], tl_meta[3]], color=trendline_color, linewidth=trendline_width)


def plot_segseg_no_dashed(
        meta: CChanPlotMeta,
        ax: Axes,
        color='orange',
        width=2,
        disp_end=False,
        end_fontsize=25,
        end_color="blue",
):
    """绘制段的段，但跳过不确定的部分（虚线部分）"""
    x_begin = ax.get_xlim()[0]

    for seg_idx, seg_meta in enumerate(meta.segseg_list):
        if seg_meta.end_x < x_begin:
            continue
        # 只绘制确定的段，跳过不确定的段
        if seg_meta.is_sure:
            ax.plot([seg_meta.begin_x, seg_meta.end_x], [seg_meta.begin_y, seg_meta.end_y], color=color, linewidth=width)
            if disp_end:
                from Plot.PlotDriver import bi_text
                bi_text(seg_idx, ax, seg_meta, end_fontsize, end_color)


def plot_bi_element_no_dashed(bi_meta, ax: Axes, color: str):
    """绘制笔元素，但跳过不确定的笔（虚线部分）"""
    # 只绘制确定的笔，跳过不确定的笔
    if bi_meta.is_sure:
        ax.plot([bi_meta.begin_x, bi_meta.end_x], [bi_meta.begin_y, bi_meta.end_y], color=color)


class CPlotDriverNoDashed(CPlotDriver):
    """自定义绘图驱动器，不绘制虚线部分"""
    
    def __init__(self, chan: CChan, plot_config=None, plot_para=None):
        # 先调用父类构造函数
        super().__init__(chan, plot_config, plot_para)
        
        # 重新绘制所有内容，但跳过虚线部分
        self._redraw_without_dashed(chan, plot_config, plot_para)
    
    def _redraw_without_dashed(self, chan: CChan, plot_config, plot_para):
        """重新绘制所有内容，但跳过虚线部分"""
        if plot_para is None:
            plot_para = {}
            
        # 清除所有现有的线条
        for ax in self.figure.axes:
            # 保存K线相关的内容，清除其他线条
            lines_to_remove = []
            for line in ax.lines:
                # 移除可能的虚线
                if hasattr(line, 'get_linestyle') and (line.get_linestyle() == '--' or line.get_linestyle() == 'dashed'):
                    lines_to_remove.append(line)
            for line in lines_to_remove:
                line.remove()


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

    # 绘图配置：保持原有配置，但会在绘制时跳过虚线部分
    plot_config = {
        "plot_kline": True,
        "plot_kline_combine": True,
        "plot_bi": True,        # 只绘制确定的笔
        "plot_seg": True,       # 只绘制确定的线段
        "plot_eigen": False,
        "plot_zs": True,        # 只绘制确定的中枢
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
        # 使用自定义的不绘制虚线的绘图驱动器
        plot_driver = CPlotDriverNoDashed(
            chan,
            plot_config=plot_config,
            plot_para=plot_para,
        )
        plot_driver.figure.show()
        plot_driver.save2img("./test_no_dashed.png")
        print("图表已生成，保存为 test_no_dashed.png，已跳过所有虚线部分")
    else:
        CAnimateDriver(
            chan,
            plot_config=plot_config,
            plot_para=plot_para,
        )