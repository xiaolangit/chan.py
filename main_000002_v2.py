from Chan import CChan
from ChanConfig import CChanConfig
from Common.CEnum import AUTYPE, DATA_SRC, KL_TYPE
from Plot.AnimatePlotDriver import CAnimateDriver
from Plot.PlotDriver import CPlotDriver
import matplotlib.pyplot as plt

class CustomPlotDriver(CPlotDriver):
    """自定义绘图驱动，只显示确定的线段和中枢"""
    
    def draw_seg(
        self,
        meta,
        ax,
        lv,
        width=5,
        color="g",
        sub_lv_cnt=None,
        facecolor='green',
        alpha=0.1,
        disp_end=False,
        end_color='g',
        end_fontsize=15,
        plot_trendline=False,
        trendline_color='orange',
        trendline_width=1,
        show_num=False,
        num_fontsize=25,
        num_color="blue",
    ):
        """重写段绘制方法，只绘制确定的段，保持原有的完整功能"""
        x_begin = ax.get_xlim()[0]

        for seg_idx, seg_meta in enumerate(meta.seg_list):
            if seg_meta.end_x < x_begin:
                continue
            # 只绘制确定的段
            if seg_meta.is_sure:
                ax.plot([seg_meta.begin_x, seg_meta.end_x], [seg_meta.begin_y, seg_meta.end_y], color=color, linewidth=width)
            if disp_end and seg_meta.is_sure:
                # 简化的端点文本显示
                ax.text(seg_meta.end_x, seg_meta.end_y, f'{seg_meta.end_y:.2f}', 
                       fontsize=end_fontsize, color=end_color, 
                       verticalalignment='bottom', horizontalalignment='center')
            if plot_trendline:
                if seg_meta.tl.get('support'):
                    tl_meta = seg_meta.format_tl(seg_meta.tl['support'])
                    ax.plot([tl_meta[0], tl_meta[2]], [tl_meta[1], tl_meta[3]], color=trendline_color, linewidth=trendline_width)
                if seg_meta.tl.get('resistance'):
                    tl_meta = seg_meta.format_tl(seg_meta.tl['resistance'])
                    ax.plot([tl_meta[0], tl_meta[2]], [tl_meta[1], tl_meta[3]], color=trendline_color, linewidth=trendline_width)
            if show_num and seg_meta.begin_x >= x_begin:
                ax.text((seg_meta.begin_x+seg_meta.end_x)/2, (seg_meta.begin_y+seg_meta.end_y)/2, f'{seg_meta.idx}', fontsize=num_fontsize, color=num_color)
        
        if sub_lv_cnt is not None and len(self.lv_lst) > 1 and lv != self.lv_lst[-1]:
            if sub_lv_cnt >= len(meta.seg_list):
                return
            else:
                begin_idx = meta.seg_list[-sub_lv_cnt].begin_x
            y_begin, y_end = ax.get_ylim()
            x_end = int(ax.get_xlim()[1])
            ax.fill_between(range(begin_idx, x_end+1), y_begin, y_end, facecolor=facecolor, alpha=alpha)

    def draw_segseg(
        self,
        meta,
        ax,
        width=7,
        color="brown",
        disp_end=False,
        end_color='brown',
        end_fontsize=15,
        show_num=False,
        num_fontsize=30,
        num_color="blue",
    ):
        """重写段段绘制方法，只绘制确定的段段"""
        from Common.CEnum import BI_DIR
        
        x_begin = ax.get_xlim()[0]

        for seg_idx, seg_meta in enumerate(meta.segseg_list):
            if seg_meta.end_x < x_begin:
                continue
            # 只绘制确定的段段
            if seg_meta.is_sure:
                ax.plot([seg_meta.begin_x, seg_meta.end_x], [seg_meta.begin_y, seg_meta.end_y], color=color, linewidth=width)
            if disp_end and seg_meta.is_sure:
                if seg_idx == 0:
                    ax.text(
                        seg_meta.begin_x,
                        seg_meta.begin_y,
                        f'{seg_meta.begin_y:.2f}',
                        fontsize=end_fontsize,
                        color=end_color,
                        verticalalignment="top" if seg_meta.dir == BI_DIR.UP else "bottom",
                        horizontalalignment='center')
                ax.text(
                    seg_meta.end_x,
                    seg_meta.end_y,
                    f'{seg_meta.end_y:.2f}',
                    fontsize=end_fontsize,
                    color=end_color,
                    verticalalignment="top" if seg_meta.dir == BI_DIR.UP else "bottom",
                    horizontalalignment='center')
            if show_num and seg_meta.begin_x >= x_begin:
                ax.text((seg_meta.begin_x+seg_meta.end_x)/2, (seg_meta.begin_y+seg_meta.end_y)/2, f'{seg_meta.idx}', fontsize=num_fontsize, color=num_color)

    def draw_zs(
        self,
        meta,
        ax,
        color='yellow',
        linewidth=3,
        sub_linewidth=2,
        show_text=True,
        fontsize=14,
        text_color='orange',
        draw_one_bi_zs=False,
    ):
        """重写中枢绘制方法，只绘制确定的中枢"""
        from matplotlib.patches import Rectangle
        
        linewidth = max(linewidth, 2)
        x_begin = ax.get_xlim()[0]
        for zs_meta in meta.zs_lst:
            if not draw_one_bi_zs and zs_meta.is_onebi_zs:
                continue
            if zs_meta.begin+zs_meta.w < x_begin:
                continue
            # 只绘制确定的中枢
            if zs_meta.is_sure:
                ax.add_patch(Rectangle((zs_meta.begin, zs_meta.low), zs_meta.w, zs_meta.h, fill=False, color=color, linewidth=linewidth))
                for sub_zs_meta in zs_meta.sub_zs_lst:
                    if sub_zs_meta.is_sure:
                        ax.add_patch(Rectangle((sub_zs_meta.begin, sub_zs_meta.low), sub_zs_meta.w, sub_zs_meta.h, fill=False, color=color, linewidth=sub_linewidth))
                if show_text:
                    # 简化的中枢文本显示
                    ax.text(zs_meta.begin + zs_meta.w/2, zs_meta.low + zs_meta.h/2, 
                           'ZS', fontsize=fontsize, color=text_color, 
                           horizontalalignment='center', verticalalignment='center')

    def draw_segzs(self, meta, ax, color='red', linewidth=10, sub_linewidth=4):
        """重写段中枢绘制方法，只绘制确定的段中枢"""
        from matplotlib.patches import Rectangle
        
        linewidth = max(linewidth, 2)
        x_begin = ax.get_xlim()[0]
        for zs_meta in meta.segzs_lst:
            if zs_meta.begin+zs_meta.w < x_begin:
                continue
            # 只绘制确定的段中枢
            if zs_meta.is_sure:
                ax.add_patch(Rectangle((zs_meta.begin, zs_meta.low), zs_meta.w, zs_meta.h, fill=False, color=color, linewidth=linewidth))
                for sub_zs_meta in zs_meta.sub_zs_lst:
                    if sub_zs_meta.is_sure:
                        ax.add_patch(Rectangle((sub_zs_meta.begin, sub_zs_meta.low), sub_zs_meta.w, sub_zs_meta.h, fill=False, color=color, linewidth=sub_linewidth))


if __name__ == "__main__":
    code = "000002.SZ"
    begin_time = "2018-01-01"
    end_time = None
    data_src = DATA_SRC.BAO_STOCK
    # 多级别K线：月线、周线、日线（从大级别到小级别）
    lv_list = [KL_TYPE.K_MON, KL_TYPE.K_WEEK, KL_TYPE.K_DAY]

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

    # 为每个时间级别配置不同的绘图参数
    plot_config = {
        KL_TYPE.K_MON: {
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
        },
        KL_TYPE.K_WEEK: {
            "plot_kline": True,
            "plot_kline_combine": True,
            "plot_bi": True,
            "plot_seg": True,
            "plot_eigen": False,
            "plot_zs": True,
            "plot_macd": True,
            "plot_mean": False,
            "plot_channel": False,
            "plot_bsp": True,
            "plot_extrainfo": False,
            "plot_demark": False,
            "plot_marker": False,
            "plot_rsi": False,
            "plot_kdj": False,
        },
        KL_TYPE.K_DAY: {
            "plot_kline": True,
            "plot_kline_combine": True,
            "plot_bi": True,
            "plot_seg": True,
            "plot_eigen": False,
            "plot_zs": True,
            "plot_macd": True,
            "plot_mean": False,
            "plot_channel": False,
            "plot_bsp": True,
            "plot_extrainfo": False,
            "plot_demark": False,
            "plot_marker": False,
            "plot_rsi": False,
            "plot_kdj": False,
        }
    }

    plot_para = {
        "kl": {
            "width": 0.8,  # 进一步增加K线宽度，让K线更清晰
            "rugd": True,  # 红涨绿跌
        },
        "klc": {
            "width": 1.0,  # 增加合并K线的宽度
        },
        "seg": {
            # "plot_trendline": True,
            "width": 3,  # 段的线宽
            "color": "red",  # 段的颜色
        },
        "bi": {
            # "show_num": True,
            # "disp_end": True,
            "color": "black",  # 笔的颜色
        },
        "zs": {
            "linewidth": 2,  # 中枢边框宽度
            "color": "yellow",  # 中枢颜色
        },
        "figure": {
            "x_range": 200,
            "w": 28,  # 增加宽度
            "h": 24,  # 增加高度以适应三个子图
            "dpi": 120,  # 提高DPI增强清晰度
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
        # 使用自定义的PlotDriver
        plot_driver = CustomPlotDriver(
            chan,
            plot_config=plot_config,
            plot_para=plot_para,
        )
        plot_driver.figure.show()
        plot_driver.save2img("./000002_no_unsure_chart.png")
    else:
        CAnimateDriver(
            chan,
            plot_config=plot_config,
            plot_para=plot_para,
        )