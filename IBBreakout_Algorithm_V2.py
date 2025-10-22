#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
IB突破算法 V2.0 - 自动筛选股票并标记$$$交易机会点

核心逻辑澄清：
1. 严格笔：处理完包含关系后≥4根K线组合
2. 左侧笔破坏：标准缠论定义的左侧笔破坏
3. 同级别出结构：BOS突破
4. 次级别拐头：三笔破坏左侧笔
5. BOS确认条件：突破第二次IB的端点
6. $$$标记位置：第二次IB的端点（即BOS起点）

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
    SECOND_IB = auto()  # 第二次IB（右侧笔破坏）
    

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
    price: float             # IB端点价格
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
    """IB突破分析器 V2.0"""
    
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
            'entry_point_count': len([s for s in signals if s.signal_type == SignalType.ENTRY_POINT]),
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
        
        完整逻辑：
        1. 第一次IB：左侧笔破坏（标准缠论定义）
        2. 第二次IB：右侧反向笔破坏
        3. BOS确认：突破第二次IB端点
        4. $$$标记：第二次IB端点位置
        """
        patterns = []
        
        for i in range(len(bi_list) - 5):  # 需要至少6笔分析
            pattern = self._analyze_pattern_at_position(bi_list, i)
            if pattern:
                patterns.append(pattern)
        
        return patterns
    
    def _analyze_pattern_at_position(self, bi_list: CBiList, start_idx: int) -> Optional[Dict]:
        """分析指定位置的IB模式"""
        if start_idx + 5 >= len(bi_list):
            return None
        
        # 获取分析所需的笔序列（至少6笔）
        bi_sequence = bi_list[start_idx:start_idx + 6]
        
        # 检查基本交替模式
        if not self._is_valid_alternating_pattern(bi_sequence):
            return None
        
        # 识别第一次IB（左侧笔破坏）
        first_ib = self._identify_first_ib(bi_sequence)
        if not first_ib:
            return None
        
        # 识别第二次IB（右侧笔破坏）
        second_ib = self._identify_second_ib(bi_sequence, first_ib)
        if not second_ib:
            return None
        
        # 检查BOS（突破第二次IB端点）
        bos_info = self._check_bos_confirmation(bi_sequence, second_ib)
        if not bos_info:
            return None
        
        return {
            'start_idx': start_idx,
            'bi_sequence': bi_sequence,
            'first_ib': first_ib,
            'second_ib': second_ib,
            'bos': bos_info,
            'triple_dollar_price': second_ib.price,  # $$$标记就在第二次IB端点
            'pattern_type': self._classify_pattern_type(bi_sequence)
        }
    
    def _is_valid_alternating_pattern(self, bi_sequence: List[CBi]) -> bool:
        """检查是否为有效的交替模式"""
        if len(bi_sequence) < 6:
            return False
        
        # 检查方向是否严格交替
        for i in range(len(bi_sequence) - 1):
            if bi_sequence[i].dir == bi_sequence[i + 1].dir:
                return False
        
        return True
    
    def _identify_first_ib(self, bi_sequence: List[CBi]) -> Optional[IBPoint]:
        """
        识别第一次IB（左侧笔破坏）
        
        标准缠论的左侧笔破坏定义：
        - 形成分形结构被破坏
        - 改变原有走势节奏
        """
        bi1, bi2, bi3 = bi_sequence[0], bi_sequence[1], bi_sequence[2]
        
        # 检查左侧笔破坏模式
        if bi1.is_up() and bi2.is_down() and bi3.is_up():
            # 上升被破坏：笔3未能突破笔1的高点，构成左侧破坏
            if bi3.get_end_val() < bi1.get_end_val():
                return IBPoint(
                    bi_idx=bi2.idx,
                    bi=bi2,
                    ib_type=IBType.FIRST_IB,
                    price=bi2.get_end_val(),  # 第一次IB的端点
                    time_idx=bi2.get_end_klu().idx
                )
        elif bi1.is_down() and bi2.is_up() and bi3.is_down():
            # 下降被破坏：笔3未能突破笔1的低点，构成左侧破坏
            if bi3.get_end_val() > bi1.get_end_val():
                return IBPoint(
                    bi_idx=bi2.idx,
                    bi=bi2,
                    ib_type=IBType.FIRST_IB,
                    price=bi2.get_end_val(),  # 第一次IB的端点
                    time_idx=bi2.get_end_klu().idx
                )
        
        return None
    
    def _identify_second_ib(self, bi_sequence: List[CBi], first_ib: IBPoint) -> Optional[IBPoint]:
        """
        识别第二次IB（右侧反向笔破坏）
        
        第二次IB应该与第一次IB方向相反，形成对称的破坏结构
        """
        if len(bi_sequence) < 6:
            return None
        
        bi4, bi5, bi6 = bi_sequence[3], bi_sequence[4], bi_sequence[5]
        
        # 根据第一次IB的方向确定第二次IB的模式
        if first_ib.bi.is_down():  # 第一次IB是下降笔
            # 寻找上升方向的第二次IB
            if bi4.is_up() and bi5.is_down() and bi6.is_up():
                # 检查是否构成右侧破坏
                if bi6.get_end_val() < bi4.get_end_val():
                    return IBPoint(
                        bi_idx=bi5.idx,
                        bi=bi5,
                        ib_type=IBType.SECOND_IB,
                        price=bi5.get_end_val(),  # 第二次IB的端点（$$$位置）
                        time_idx=bi5.get_end_klu().idx
                    )
        else:  # 第一次IB是上升笔
            # 寻找下降方向的第二次IB
            if bi4.is_down() and bi5.is_up() and bi6.is_down():
                # 检查是否构成右侧破坏
                if bi6.get_end_val() > bi4.get_end_val():
                    return IBPoint(
                        bi_idx=bi5.idx,
                        bi=bi5,
                        ib_type=IBType.SECOND_IB,
                        price=bi5.get_end_val(),  # 第二次IB的端点（$$$位置）
                        time_idx=bi5.get_end_klu().idx
                    )
        
        return None
    
    def _check_bos_confirmation(self, bi_sequence: List[CBi], second_ib: IBPoint) -> Optional[Dict]:
        """
        检查BOS确认（突破第二次IB端点）
        
        BOS确认条件：后续走势突破第二次IB的端点价格
        """
        second_ib_price = second_ib.price
        original_direction = bi_sequence[0].dir  # 原始趋势方向
        
        # 检查第二次IB之后的笔是否产生突破
        # 这里检查最后一笔是否突破了第二次IB的端点
        last_bi = bi_sequence[-1]
        
        if original_direction == BI_DIR.UP:
            # 原始上升趋势，检查是否向上突破第二次IB端点
            if second_ib.bi.is_down():  # 第二次IB是下降笔
                if last_bi.get_end_val() > second_ib_price:
                    return {
                        'direction': BI_DIR.UP,
                        'breakout_price': last_bi.get_end_val(),
                        'ib_price': second_ib_price,
                        'bi_idx': last_bi.idx,
                        'confirmed': True
                    }
        else:
            # 原始下降趋势，检查是否向下突破第二次IB端点
            if second_ib.bi.is_up():  # 第二次IB是上升笔
                if last_bi.get_end_val() < second_ib_price:
                    return {
                        'direction': BI_DIR.DOWN,
                        'breakout_price': last_bi.get_end_val(),
                        'ib_price': second_ib_price,
                        'bi_idx': last_bi.idx,
                        'confirmed': True
                    }
        
        return None
    
    def _classify_pattern_type(self, bi_sequence: List[CBi]) -> str:
        """分类模式类型"""
        first_direction = bi_sequence[0].dir
        if first_direction == BI_DIR.UP:
            return "BULLISH_IB_PATTERN"  # 看涨IB模式
        else:
            return "BEARISH_IB_PATTERN"  # 看跌IB模式
    
    def _generate_trading_signals(self, bi_list: CBiList, ib_patterns: List[Dict]) -> List[TradingSignal]:
        """生成交易信号"""
        signals = []
        
        for pattern in ib_patterns:
            # 生成$$$标记（第二次IB端点位置）
            triple_dollar_signal = self._create_triple_dollar_signal(pattern)
            if triple_dollar_signal:
                signals.append(triple_dollar_signal)
            
            # 生成BOS确认信号
            bos_signal = self._create_bos_signal(pattern)
            if bos_signal:
                signals.append(bos_signal)
            
            # 生成入场点信号（$$$点后的次级别拐头）
            entry_signals = self._create_entry_signals(pattern, bi_list)
            signals.extend(entry_signals)
        
        return signals
    
    def _create_triple_dollar_signal(self, pattern: Dict) -> TradingSignal:
        """
        创建$$$标记信号
        
        $$$标记位置：第二次IB的端点（即BOS起点）
        """
        second_ib = pattern['second_ib']
        bos = pattern['bos']
        
        return TradingSignal(
            signal_type=SignalType.TRIPLE_DOLLAR,
            bi_idx=second_ib.bi_idx,
            price=second_ib.price,  # $$$标记在第二次IB端点
            direction=bos['direction'],
            description=f"$$$标记 - 第二次IB端点({second_ib.price:.4f})，BOS起点",
            confidence=0.90
        )
    
    def _create_bos_signal(self, pattern: Dict) -> TradingSignal:
        """创建BOS确认信号"""
        bos = pattern['bos']
        
        return TradingSignal(
            signal_type=SignalType.BOS,
            bi_idx=bos['bi_idx'],
            price=bos['breakout_price'],
            direction=bos['direction'],
            description=f"BOS确认 - 突破第二次IB端点({bos['ib_price']:.4f})",
            confidence=0.85
        )
    
    def _create_entry_signals(self, pattern: Dict, bi_list: CBiList) -> List[TradingSignal]:
        """
        创建入场点信号
        
        入场条件：$$$点后出现次级别拐头（三笔破坏左侧笔）
        """
        signals = []
        
        triple_dollar_idx = pattern['second_ib'].bi_idx
        trend_direction = pattern['bos']['direction']
        
        # 在$$$点之后寻找次级别拐头机会
        for i in range(triple_dollar_idx + 1, len(bi_list) - 2):  # 需要至少3笔来判断
            if self._is_sub_level_reversal(bi_list, i, trend_direction):
                entry_bi = bi_list[i + 2]  # 第三笔完成时确认入场
                
                signals.append(TradingSignal(
                    signal_type=SignalType.ENTRY_POINT,
                    bi_idx=entry_bi.idx,
                    price=entry_bi.get_end_val(),
                    direction=trend_direction,
                    description=f"入场点 - 次级别拐头确认，三笔破坏左侧笔",
                    confidence=0.80
                ))
        
        return signals
    
    def _is_sub_level_reversal(self, bi_list: CBiList, start_idx: int, trend_direction: BI_DIR) -> bool:
        """
        判断是否为次级别拐头
        
        条件：三笔破坏左侧笔
        """
        if start_idx + 2 >= len(bi_list):
            return False
        
        # 获取三笔序列
        bi1 = bi_list[start_idx]
        bi2 = bi_list[start_idx + 1]
        bi3 = bi_list[start_idx + 2]
        
        # 检查方向交替
        if bi1.dir == bi2.dir or bi2.dir == bi3.dir:
            return False
        
        # 检查是否破坏了左侧笔（类似第一次IB的逻辑）
        if trend_direction == BI_DIR.UP:
            # 在上升趋势中，寻找向上的次级别拐头
            if bi1.is_down() and bi2.is_up() and bi3.is_down():
                # 检查是否构成向上的拐头信号
                return bi3.get_end_val() > bi1.get_end_val()
        else:
            # 在下降趋势中，寻找向下的次级别拐头
            if bi1.is_up() and bi2.is_down() and bi3.is_up():
                # 检查是否构成向下的拐头信号
                return bi3.get_end_val() < bi1.get_end_val()
        
        return False
    
    def _create_summary(self, bi_list: CBiList, ib_patterns: List[Dict], signals: List[TradingSignal]) -> Dict:
        """创建分析摘要"""
        return {
            'total_bis': len(bi_list),
            'ib_patterns_found': len(ib_patterns),
            'total_signals': len(signals),
            'triple_dollar_signals': len([s for s in signals if s.signal_type == SignalType.TRIPLE_DOLLAR]),
            'entry_signals': len([s for s in signals if s.signal_type == SignalType.ENTRY_POINT]),
            'bos_signals': len([s for s in signals if s.signal_type == SignalType.BOS]),
            'pattern_types': [p['pattern_type'] for p in ib_patterns],
            'confidence_distribution': self._get_confidence_distribution(signals)
        }
    
    def _get_confidence_distribution(self, signals: List[TradingSignal]) -> Dict:
        """获取置信度分布"""
        if not signals:
            return {}
        
        confidences = [s.confidence for s in signals]
        return {
            'avg_confidence': sum(confidences) / len(confidences),
            'max_confidence': max(confidences),
            'min_confidence': min(confidences),
            'high_confidence_count': len([c for c in confidences if c >= 0.8])
        }


class StockScreener:
    """股票筛选器"""
    
    def __init__(self):
        self.analyzer = IBBreakoutAnalyzer()
        self.logger = logging.getLogger(__name__)
    
    def screen_stocks(self, stock_data_dict: Dict[str, CBiList]) -> Dict[str, Dict]:
        """
        筛选出现$$$标记的股票
        
        Args:
            stock_data_dict: 股票代码 -> 笔列表的字典
            
        Returns:
            筛选结果
        """
        results = {}
        
        self.logger.info(f"开始筛选 {len(stock_data_dict)} 只股票...")
        
        for stock_code, bi_list in stock_data_dict.items():
            try:
                analysis_result = self.analyzer.analyze_stock(bi_list)
                
                if analysis_result['has_pattern']:
                    results[stock_code] = analysis_result
                    self.logger.info(
                        f"✅ {stock_code}: {analysis_result['triple_dollar_count']}个$$$标记, "
                        f"{analysis_result['entry_point_count']}个入场点"
                    )
                
            except Exception as e:
                self.logger.error(f"❌ 分析{stock_code}时出错: {e}")
        
        self.logger.info(f"筛选完成，发现 {len(results)} 只符合条件的股票")
        return results
    
    def export_signals(self, screening_results: Dict[str, Dict]) -> List[Dict]:
        """导出所有信号为列表格式"""
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
        
        # 按置信度和信号类型排序
        all_signals.sort(key=lambda x: (x['confidence'], x['signal_type']), reverse=True)
        
        return all_signals
    
    def get_triple_dollar_stocks(self, screening_results: Dict[str, Dict]) -> List[str]:
        """获取所有有$$$标记的股票代码"""
        return list(screening_results.keys())


def demo_usage():
    """演示用法"""
    print("IB突破算法 V2.0 演示")
    print("=" * 60)
    
    print("""
    📋 算法核心逻辑：
    
    1. 严格笔验证：≥4根K线组合
    2. 第一次IB：左侧笔破坏（标准缠论定义）
    3. 第二次IB：右侧反向笔破坏
    4. BOS确认：突破第二次IB端点
    5. $$$标记：第二次IB端点位置
    6. 入场点：$$$后次级别拐头（三笔破坏左侧笔）
    
    📊 使用示例：
    
    # 1. 创建筛选器
    screener = StockScreener()
    
    # 2. 准备股票数据
    stock_data = {
        "000001.SZ": bi_list_1,
        "000002.SZ": bi_list_2,
        # ... 更多股票
    }
    
    # 3. 筛选股票
    results = screener.screen_stocks(stock_data)
    
    # 4. 获取$$$标记的股票
    triple_dollar_stocks = screener.get_triple_dollar_stocks(results)
    
    # 5. 导出所有信号
    signals = screener.export_signals(results)
    
    # 6. 查看结果
    for stock in triple_dollar_stocks:
        print(f"发现机会: {stock}")
    """)


if __name__ == "__main__":
    demo_usage()