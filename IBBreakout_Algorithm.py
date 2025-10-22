#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
IB突破算法 - 自动筛选股票并标记$$$交易机会点

算法逻辑：
1. 严格笔处理完包含关系后不少于4根K线组合
2. 识别IB（Internal Bar）破坏模式
3. 标记$$$点（同级别结构打止损的位置）
4. 标记次级别拐头入场点

作者：基于缠论理论的创新算法
"""

from typing import List, Optional, Dict, Tuple
from dataclasses import dataclass
from enum import Enum, auto
import logging

from Bi.Bi import CBi
from Bi.BiList import CBiList
from Bi.BiConfig import CBiConfig
from Common.CEnum import BI_DIR, FX_TYPE
from KLine.KLine import CKLine


class IBType(Enum):
    """IB类型枚举"""
    FIRST_IB = auto()   # 第一次IB（左侧笔破坏）
    SECOND_IB = auto()  # 第二次IB（右侧反向笔破坏）
    

class SignalType(Enum):
    """信号类型枚举"""
    TRIPLE_DOLLAR = auto()  # $$$标记点
    ENTRY_POINT = auto()    # 入场点
    BOS = auto()           # Break of Structure


@dataclass
class IBPoint:
    """IB点数据结构"""
    bi_idx: int              # 笔索引
    bi: CBi                  # 笔对象
    ib_type: IBType          # IB类型
    price: float             # IB价格
    time_idx: int            # 时间索引
    is_broken: bool = False  # 是否被突破
    

@dataclass
class TradingSignal:
    """交易信号数据结构"""
    signal_type: SignalType  # 信号类型
    bi_idx: int              # 笔索引
    price: float             # 信号价格
    direction: BI_DIR        # 方向
    description: str         # 描述
    confidence: float        # 置信度
    

class IBBreakoutAnalyzer:
    """IB突破分析器"""
    
    def __init__(self):
        """初始化分析器"""
        # 配置严格笔模式
        self.bi_config = CBiConfig(
            is_strict=True,           # 严格模式
            bi_fx_check="strict",     # 严格分形检查
            bi_allow_sub_peak=False   # 不允许次高低点
        )
        
        self.logger = logging.getLogger(__name__)
        
    def analyze_stock(self, bi_list: CBiList) -> Dict:
        """
        分析单只股票的IB突破模式
        
        Args:
            bi_list: 笔列表
            
        Returns:
            分析结果字典
        """
        if len(bi_list) < 6:  # 至少需要6笔来分析完整模式
            return {
                'has_pattern': False,
                'reason': '笔数量不足，需要至少6笔'
            }
        
        # 验证所有笔都符合严格标准（≥4根K线组合）
        if not self._validate_strict_bis(bi_list):
            return {
                'has_pattern': False,
                'reason': '存在不符合严格标准的笔（<4根K线组合）'
            }
        
        # 识别IB模式
        ib_patterns = self._identify_ib_patterns(bi_list)
        
        # 生成交易信号
        signals = self._generate_trading_signals(bi_list, ib_patterns)
        
        # 筛选出有$$$标记的模式
        triple_dollar_signals = [s for s in signals if s.signal_type == SignalType.TRIPLE_DOLLAR]
        
        return {
            'has_pattern': len(triple_dollar_signals) > 0,
            'ib_patterns': ib_patterns,
            'signals': signals,
            'triple_dollar_count': len(triple_dollar_signals),
            'analysis_summary': self._create_summary(bi_list, ib_patterns, signals)
        }
    
    def _validate_strict_bis(self, bi_list: CBiList) -> bool:
        """验证所有笔都符合严格标准"""
        for bi in bi_list:
            span = bi.end_klc.idx - bi.begin_klc.idx
            if span < 4:  # 严格笔要求≥4根K线组合
                self.logger.warning(f"笔{bi.idx}跨度不足: {span} < 4")
                return False
        return True
    
    def _identify_ib_patterns(self, bi_list: CBiList) -> List[Dict]:
        """
        识别IB突破模式
        
        逻辑：
        1. 第一次IB：左侧笔破坏标记
        2. 第二次IB：右侧反向笔破坏
        3. BOS：按原方向突破
        """
        patterns = []
        
        for i in range(len(bi_list) - 5):  # 需要至少6笔分析
            pattern = self._analyze_pattern_at_position(bi_list, i)
            if pattern:
                patterns.append(pattern)
        
        return patterns
    
    def _analyze_pattern_at_position(self, bi_list: CBiList, start_idx: int) -> Optional[Dict]:
        """分析指定位置的模式"""
        if start_idx + 5 >= len(bi_list):
            return None
        
        # 获取分析所需的笔序列
        bi_sequence = bi_list[start_idx:start_idx + 6]
        
        # 检查基本模式：上-下-上-下-上-下 或 下-上-下-上-下-上
        if not self._is_valid_alternating_pattern(bi_sequence):
            return None
        
        # 分析IB模式
        first_ib = self._identify_first_ib(bi_sequence)
        if not first_ib:
            return None
        
        second_ib = self._identify_second_ib(bi_sequence, first_ib)
        if not second_ib:
            return None
        
        # 检查BOS（突破结构）
        bos_info = self._identify_bos(bi_sequence, first_ib, second_ib)
        if not bos_info:
            return None
        
        return {
            'start_idx': start_idx,
            'bi_sequence': bi_sequence,
            'first_ib': first_ib,
            'second_ib': second_ib,
            'bos': bos_info,
            'pattern_type': self._classify_pattern_type(bi_sequence)
        }
    
    def _is_valid_alternating_pattern(self, bi_sequence: List[CBi]) -> bool:
        """检查是否为有效的交替模式"""
        if len(bi_sequence) < 6:
            return False
        
        # 检查方向是否交替
        for i in range(len(bi_sequence) - 1):
            if bi_sequence[i].dir == bi_sequence[i + 1].dir:
                return False
        
        return True
    
    def _identify_first_ib(self, bi_sequence: List[CBi]) -> Optional[IBPoint]:
        """识别第一次IB（左侧笔破坏）"""
        # 分析前三笔，寻找第一次内部破坏
        # 模式：笔1 -> 笔2 -> 笔3，其中笔2创造内部结构，笔3破坏
        
        bi1, bi2, bi3 = bi_sequence[0], bi_sequence[1], bi_sequence[2]
        
        # 检查是否形成IB模式
        if bi1.is_up() and bi2.is_down() and bi3.is_up():
            # 上升-下降-上升模式
            if (bi3.get_end_val() < bi1.get_end_val() and 
                bi3.get_end_val() > bi2.get_end_val()):
                return IBPoint(
                    bi_idx=bi2.idx,
                    bi=bi2,
                    ib_type=IBType.FIRST_IB,
                    price=bi2.get_end_val(),
                    time_idx=bi2.get_end_klu().idx
                )
        elif bi1.is_down() and bi2.is_up() and bi3.is_down():
            # 下降-上升-下降模式
            if (bi3.get_end_val() > bi1.get_end_val() and 
                bi3.get_end_val() < bi2.get_end_val()):
                return IBPoint(
                    bi_idx=bi2.idx,
                    bi=bi2,
                    ib_type=IBType.FIRST_IB,
                    price=bi2.get_end_val(),
                    time_idx=bi2.get_end_klu().idx
                )
        
        return None
    
    def _identify_second_ib(self, bi_sequence: List[CBi], first_ib: IBPoint) -> Optional[IBPoint]:
        """识别第二次IB（右侧反向笔破坏）"""
        # 分析第4、5、6笔，寻找第二次内部破坏
        if len(bi_sequence) < 6:
            return None
        
        bi4, bi5, bi6 = bi_sequence[3], bi_sequence[4], bi_sequence[5]
        
        # 第二次IB应该与第一次IB方向相反
        if first_ib.bi.is_up():
            # 第一次是上升IB，寻找下降IB
            if bi4.is_down() and bi5.is_up() and bi6.is_down():
                if (bi6.get_end_val() > bi4.get_end_val() and 
                    bi6.get_end_val() < bi5.get_end_val()):
                    return IBPoint(
                        bi_idx=bi5.idx,
                        bi=bi5,
                        ib_type=IBType.SECOND_IB,
                        price=bi5.get_end_val(),
                        time_idx=bi5.get_end_klu().idx
                    )
        else:
            # 第一次是下降IB，寻找上升IB
            if bi4.is_up() and bi5.is_down() and bi6.is_up():
                if (bi6.get_end_val() < bi4.get_end_val() and 
                    bi6.get_end_val() > bi5.get_end_val()):
                    return IBPoint(
                        bi_idx=bi5.idx,
                        bi=bi5,
                        ib_type=IBType.SECOND_IB,
                        price=bi5.get_end_val(),
                        time_idx=bi5.get_end_klu().idx
                    )
        
        return None
    
    def _identify_bos(self, bi_sequence: List[CBi], first_ib: IBPoint, second_ib: IBPoint) -> Optional[Dict]:
        """识别BOS（突破结构）"""
        # BOS应该是按照原方向突破第一次IB后的结构
        
        # 确定原始趋势方向（第一笔的方向）
        original_direction = bi_sequence[0].dir
        
        # 检查最后的突破是否符合BOS条件
        last_bi = bi_sequence[-1]
        
        if original_direction == BI_DIR.UP:
            # 原始上升趋势，检查是否向上突破
            if (last_bi.is_up() and 
                last_bi.get_end_val() > first_ib.price):
                return {
                    'direction': BI_DIR.UP,
                    'breakout_price': last_bi.get_end_val(),
                    'reference_price': first_ib.price,
                    'bi_idx': last_bi.idx
                }
        else:
            # 原始下降趋势，检查是否向下突破
            if (last_bi.is_down() and 
                last_bi.get_end_val() < first_ib.price):
                return {
                    'direction': BI_DIR.DOWN,
                    'breakout_price': last_bi.get_end_val(),
                    'reference_price': first_ib.price,
                    'bi_idx': last_bi.idx
                }
        
        return None
    
    def _classify_pattern_type(self, bi_sequence: List[CBi]) -> str:
        """分类模式类型"""
        first_direction = bi_sequence[0].dir
        if first_direction == BI_DIR.UP:
            return "BULLISH_IB_PATTERN"
        else:
            return "BEARISH_IB_PATTERN"
    
    def _generate_trading_signals(self, bi_list: CBiList, ib_patterns: List[Dict]) -> List[TradingSignal]:
        """生成交易信号"""
        signals = []
        
        for pattern in ib_patterns:
            # 生成$$$标记（第二次IB被突破的位置）
            triple_dollar_signal = self._create_triple_dollar_signal(pattern)
            if triple_dollar_signal:
                signals.append(triple_dollar_signal)
            
            # 生成入场点信号
            entry_signals = self._create_entry_signals(pattern, bi_list)
            signals.extend(entry_signals)
            
            # 生成BOS信号
            bos_signal = self._create_bos_signal(pattern)
            if bos_signal:
                signals.append(bos_signal)
        
        return signals
    
    def _create_triple_dollar_signal(self, pattern: Dict) -> Optional[TradingSignal]:
        """创建$$$标记信号"""
        second_ib = pattern['second_ib']
        bos = pattern['bos']
        
        # $$$标记在第二次IB被突破的位置
        if bos:
            return TradingSignal(
                signal_type=SignalType.TRIPLE_DOLLAR,
                bi_idx=second_ib.bi_idx,
                price=second_ib.price,
                direction=bos['direction'],
                description=f"$$$标记 - 第二次IB({second_ib.price:.4f})被突破，形成BOS",
                confidence=0.85
            )
        
        return None
    
    def _create_entry_signals(self, pattern: Dict, bi_list: CBiList) -> List[TradingSignal]:
        """创建入场点信号"""
        signals = []
        
        # 寻找$$$点之后的次级别拐头机会
        triple_dollar_idx = pattern['second_ib'].bi_idx
        bos_direction = pattern['bos']['direction']
        
        # 在$$$点之后寻找入场机会
        for i in range(triple_dollar_idx + 1, len(bi_list)):
            bi = bi_list[i]
            
            # 检查是否为次级别拐头入场点
            if self._is_entry_point(bi, bos_direction, pattern):
                signals.append(TradingSignal(
                    signal_type=SignalType.ENTRY_POINT,
                    bi_idx=bi.idx,
                    price=bi.get_end_val(),
                    direction=bos_direction,
                    description=f"入场点 - 次级别拐头，跟随{bos_direction.name}方向",
                    confidence=0.75
                ))
        
        return signals
    
    def _is_entry_point(self, bi: CBi, trend_direction: BI_DIR, pattern: Dict) -> bool:
        """判断是否为入场点"""
        # 简化的入场点判断逻辑
        # 实际应用中可以根据具体策略优化
        
        second_ib_price = pattern['second_ib'].price
        
        if trend_direction == BI_DIR.UP:
            # 上升趋势中，寻找下降笔结束后的入场点
            return (bi.is_down() and 
                    bi.get_end_val() > second_ib_price and
                    bi.get_end_val() < pattern['bos']['breakout_price'])
        else:
            # 下降趋势中，寻找上升笔结束后的入场点
            return (bi.is_up() and 
                    bi.get_end_val() < second_ib_price and
                    bi.get_end_val() > pattern['bos']['breakout_price'])
    
    def _create_bos_signal(self, pattern: Dict) -> Optional[TradingSignal]:
        """创建BOS信号"""
        bos = pattern['bos']
        if bos:
            return TradingSignal(
                signal_type=SignalType.BOS,
                bi_idx=bos['bi_idx'],
                price=bos['breakout_price'],
                direction=bos['direction'],
                description=f"BOS - 突破结构，方向：{bos['direction'].name}",
                confidence=0.80
            )
        return None
    
    def _create_summary(self, bi_list: CBiList, ib_patterns: List[Dict], signals: List[TradingSignal]) -> Dict:
        """创建分析摘要"""
        return {
            'total_bis': len(bi_list),
            'ib_patterns_found': len(ib_patterns),
            'total_signals': len(signals),
            'triple_dollar_signals': len([s for s in signals if s.signal_type == SignalType.TRIPLE_DOLLAR]),
            'entry_signals': len([s for s in signals if s.signal_type == SignalType.ENTRY_POINT]),
            'bos_signals': len([s for s in signals if s.signal_type == SignalType.BOS]),
            'pattern_types': [p['pattern_type'] for p in ib_patterns]
        }


class StockScreener:
    """股票筛选器"""
    
    def __init__(self):
        self.analyzer = IBBreakoutAnalyzer()
        self.logger = logging.getLogger(__name__)
    
    def screen_stocks(self, stock_data_dict: Dict[str, CBiList]) -> Dict[str, Dict]:
        """
        筛选股票
        
        Args:
            stock_data_dict: 股票代码 -> 笔列表的字典
            
        Returns:
            筛选结果
        """
        results = {}
        
        for stock_code, bi_list in stock_data_dict.items():
            try:
                analysis_result = self.analyzer.analyze_stock(bi_list)
                
                if analysis_result['has_pattern']:
                    results[stock_code] = analysis_result
                    self.logger.info(f"发现机会: {stock_code} - {analysis_result['triple_dollar_count']}个$$$标记")
                
            except Exception as e:
                self.logger.error(f"分析股票{stock_code}时出错: {e}")
        
        return results
    
    def export_signals(self, screening_results: Dict[str, Dict]) -> List[Dict]:
        """导出信号列表"""
        all_signals = []
        
        for stock_code, result in screening_results.items():
            for signal in result.get('signals', []):
                all_signals.append({
                    'stock_code': stock_code,
                    'signal_type': signal.signal_type.name,
                    'bi_idx': signal.bi_idx,
                    'price': signal.price,
                    'direction': signal.direction.name,
                    'description': signal.description,
                    'confidence': signal.confidence
                })
        
        # 按置信度排序
        all_signals.sort(key=lambda x: x['confidence'], reverse=True)
        
        return all_signals


def demo_usage():
    """演示用法"""
    print("IB突破算法演示")
    print("=" * 50)
    
    # 创建筛选器
    screener = StockScreener()
    
    # 示例：筛选股票数据
    # stock_data = {
    #     "000001.SZ": bi_list_1,
    #     "000002.SZ": bi_list_2,
    #     # 更多股票...
    # }
    
    # results = screener.screen_stocks(stock_data)
    # signals = screener.export_signals(results)
    
    print("""
    使用方法：
    
    1. 准备股票的笔数据（CBiList）
    2. 创建StockScreener实例
    3. 调用screen_stocks()筛选
    4. 获取$$$标记和入场点信号
    
    示例代码：
    screener = StockScreener()
    results = screener.screen_stocks(stock_data_dict)
    signals = screener.export_signals(results)
    
    # 查看$$$标记
    for signal in signals:
        if signal['signal_type'] == 'TRIPLE_DOLLAR':
            print(f"发现$$$标记: {signal}")
    """)


if __name__ == "__main__":
    demo_usage()