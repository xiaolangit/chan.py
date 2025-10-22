# 三种线段算法详细实现描述

## 1. Chan算法 (SegListChan) - 特征序列法详细实现

### 核心概念

Chan算法基于缠论的特征序列理论，通过识别分形特征来确定线段的起始和结束。

### 关键数据结构

#### CEigenFX 类 - 特征分形处理器
```python
class CEigenFX:
    def __init__(self, _dir: BI_DIR, exclude_included=True, lv=SEG_TYPE.BI):
        self.dir = _dir  # 线段方向
        self.ele: List[Optional[CEigen]] = [None, None, None]  # 三个特征元素
        self.lst: List[CBi] = []  # 所有添加的笔
        self.exclude_included = exclude_included  # 是否排除包含关系
        self.last_evidence_bi: Optional[CBi] = None  # 最后证据笔
```

#### CEigen 类 - 特征元素
```python
class CEigen(CKLine_Combiner[CBi]):
    def __init__(self, bi, _dir):
        super().__init__(bi, _dir)
        self.gap = False  # 是否存在缺口
```

### 算法实现流程

#### 1. 主更新流程 (update方法)
```python
def update(self, bi_lst: CBiList):
    # 1. 初始化：删除末尾不确定的线段
    self.do_init()
    
    # 2. 计算确定线段
    if len(self) == 0:
        self.cal_seg_sure(bi_lst, begin_idx=0)
    else:
        self.cal_seg_sure(bi_lst, begin_idx=self[-1].end_bi.idx+1)
    
    # 3. 收集剩余线段
    self.collect_left_seg(bi_lst)
```

#### 2. 核心算法：cal_seg_sure
```python
def cal_seg_sure(self, bi_lst: CBiList, begin_idx: int):
    # 创建两个特征分形处理器
    up_eigen = CEigenFX(BI_DIR.UP, lv=self.lv)    # 处理上升线段的下降笔
    down_eigen = CEigenFX(BI_DIR.DOWN, lv=self.lv) # 处理下降线段的上升笔
    
    last_seg_dir = None if len(self) == 0 else self[-1].dir
    
    for bi in bi_lst[begin_idx:]:
        fx_eigen = None
        
        # 根据笔的方向和当前线段方向，选择合适的特征处理器
        if bi.is_down() and last_seg_dir != BI_DIR.UP:
            if up_eigen.add(bi):  # 如果形成分形
                fx_eigen = up_eigen
        elif bi.is_up() and last_seg_dir != BI_DIR.DOWN:
            if down_eigen.add(bi):  # 如果形成分形
                fx_eigen = down_eigen
        
        # 第一段方向确定逻辑
        if len(self) == 0:
            if up_eigen.ele[1] is not None and bi.is_down():
                last_seg_dir = BI_DIR.DOWN
                down_eigen.clear()
            elif down_eigen.ele[1] is not None and bi.is_up():
                up_eigen.clear()
                last_seg_dir = BI_DIR.UP
        
        # 处理找到的分形
        if fx_eigen:
            self.treat_fx_eigen(fx_eigen, bi_lst)
            break
```

#### 3. 分形特征添加流程 (CEigenFX.add方法)
```python
def add(self, bi: CBi) -> bool:
    """添加笔到特征序列，返回是否形成分形"""
    assert bi.dir != self.dir  # 笔的方向必须与线段方向相反
    self.lst.append(bi)
    
    if self.ele[0] is None:         # 处理第一个元素
        return self.treat_first_ele(bi)
    elif self.ele[1] is None:       # 处理第二个元素
        return self.treat_second_ele(bi)
    elif self.ele[2] is None:       # 处理第三个元素
        return self.treat_third_ele(bi)
    else:
        raise CChanException("特征序列已满")
```

#### 4. 三元素处理详解

**第一元素处理：**
```python
def treat_first_ele(self, bi: CBi) -> bool:
    self.ele[0] = CEigen(bi, self.kl_dir)
    return False  # 第一个元素不可能形成分形
```

**第二元素处理：**
```python
def treat_second_ele(self, bi: CBi) -> bool:
    # 尝试与第一元素合并
    combine_dir = self.ele[0].try_add(bi, exclude_included=self.exclude_included)
    
    if combine_dir != KLINE_DIR.COMBINE:  # 不能合并
        self.ele[1] = CEigen(bi, self.kl_dir)
        # 检查前两元素是否可能成为分形
        if (self.is_up() and self.ele[1].high < self.ele[0].high) or \
           (self.is_down() and self.ele[1].low > self.ele[0].low):
            return self.reset()  # 重置并重新开始
    return False
```

**第三元素处理：**
```python
def treat_third_ele(self, bi: CBi) -> bool:
    self.last_evidence_bi = bi
    
    # 尝试与第二元素合并
    combine_dir = self.ele[1].try_add(bi, allow_top_equal=allow_top_equal)
    
    if combine_dir == KLINE_DIR.COMBINE:
        return False  # 合并成功，继续等待
    
    # 创建第三元素
    self.ele[2] = CEigen(bi, combine_dir)
    
    # 检查是否有实际突破
    if not self.actual_break():
        return self.reset()
    
    # 更新第二元素的分形信息
    self.ele[1].update_fx(self.ele[0], self.ele[2], 
                         exclude_included=self.exclude_included)
    
    # 检查分形类型是否匹配线段方向
    fx = self.ele[1].fx
    is_fx = (self.is_up() and fx == FX_TYPE.TOP) or \
            (self.is_down() and fx == FX_TYPE.BOTTOM)
    
    return True if is_fx else self.reset()
```

#### 5. 线段结束判断 (can_be_end方法)
```python
def can_be_end(self, bi_lst: CBiList):
    """判断线段是否可以结束"""
    if self.ele[1].gap:  # 如果存在缺口
        end_bi_idx = self.GetPeakBiIdx()
        thred_value = bi_lst[end_bi_idx].get_end_val()
        break_thred = self.ele[0].low if self.is_up() else self.ele[0].high
        
        # 寻找反向分形来确认线段结束
        return self.find_revert_fx(bi_lst, end_bi_idx+2, thred_value, break_thred)
    else:
        return True  # 无缺口直接确认
```

---

## 2. DYH算法 (SegListDYH) - 定义一详细实现

### 核心概念

DYH算法通过两种情况（situation1和situation2）来判断笔之间的突破关系，从而识别线段。

### 关键判断函数

#### Situation1 - 弱突破情况
```python
def situation1(cur_bi, next_bi, pre_bi):
    """
    情况一：当前笔相对于前笔没有创新高/低，但被后续笔完全包含
    """
    if cur_bi.is_down() and cur_bi._low() > pre_bi._low():
        # 下降笔没有创新低，且被后续笔完全包含
        if next_bi._high() < cur_bi._high() and next_bi._low() < cur_bi._low():
            return True
    elif cur_bi.is_up() and cur_bi._high() < pre_bi._high():
        # 上升笔没有创新高，且被后续笔完全包含
        if next_bi._low() > cur_bi._low() and next_bi._high() > cur_bi._high():
            return True
    return False
```

#### Situation2 - 强突破情况
```python
def situation2(cur_bi, next_bi, pre_bi):
    """
    情况二：当前笔创新高/低，且后续笔继续突破
    """
    if cur_bi.is_down() and cur_bi._low() < pre_bi._low():
        # 下降笔创新低，且后续笔继续下跌
        if next_bi._high() < cur_bi._high() and next_bi._low() < pre_bi._low():
            return True
    elif cur_bi.is_up() and cur_bi._high() > pre_bi._high():
        # 上升笔创新高，且后续笔继续上涨
        if next_bi._low() > cur_bi._low() and next_bi._high() > pre_bi._high():
            return True
    return False
```

### 算法实现流程

#### 1. 主更新流程
```python
def update(self, bi_lst: CBiList):
    # 1. 初始化处理
    self.do_init()
    
    # 2. 计算确定的笔线段
    self.cal_bi_sure(bi_lst)
    
    # 3. 尝试更新最后一个线段
    self.try_update_last_seg(bi_lst)
    
    # 4. 如果有剩余笔突破，计算不确定线段
    if self.left_bi_break(bi_lst):
        self.cal_bi_unsure(bi_lst)
    
    # 5. 收集剩余线段
    self.collect_left_seg(bi_lst)
```

#### 2. 确定线段计算 (cal_bi_sure)
```python
def cal_bi_sure(self, bi_lst):
    BI_LEN = len(bi_lst)
    next_begin_bi = bi_lst[0]
    
    for idx, bi in enumerate(bi_lst):
        # 需要至少3个笔才能判断
        if idx + 2 >= BI_LEN or idx < 2:
            continue
        
        # 方向连续性检查
        if len(self) > 0 and bi.dir != self[-1].end_bi.dir:
            continue
        
        # 检查是否突破起始笔的范围
        if bi.is_down() and bi_lst[idx-1]._high() < next_begin_bi._low():
            continue
        if bi.is_up() and bi_lst[idx-1]._low() > next_begin_bi._high():
            continue
        
        # 确定线段更新逻辑
        if (self.sure_seg_update_end and len(self) and 
            ((bi.is_down() and bi._low() < self[-1].end_bi._low()) or 
             (bi.is_up() and bi._high() > self[-1].end_bi._high()))):
            
            self[-1].end_bi = bi  # 更新线段终点
            if idx != BI_LEN-1:
                next_begin_bi = bi_lst[idx+1]
                continue
        
        # 线段识别核心逻辑
        if ((len(self) == 0 or bi.idx - self[-1].end_bi.idx >= 4) and 
            (situation1(bi, bi_lst[idx + 2], bi_lst[idx - 2]) or 
             situation2(bi, bi_lst[idx + 2], bi_lst[idx - 2]))):
            
            self.add_new_seg(bi_lst, idx-1)  # 添加新线段
            next_begin_bi = bi
```

#### 3. 不确定线段计算 (cal_bi_unsure)
```python
def cal_bi_unsure(self, bi_lst: CBiList):
    """计算不确定的线段"""
    if len(self) == 0:
        return
    
    last_seg_dir = self[-1].end_bi.dir
    end_bi = None
    peak_value = float("inf") if last_seg_dir == BI_DIR.UP else float("-inf")
    
    # 寻找最极端的笔作为线段终点
    for bi in bi_lst[self[-1].end_bi.idx+3:]:
        if bi.dir == last_seg_dir:
            continue  # 跳过同方向笔
        
        cur_value = bi._low() if last_seg_dir == BI_DIR.UP else bi._high()
        
        # 更新极值
        if ((last_seg_dir == BI_DIR.UP and cur_value < peak_value) or 
            (last_seg_dir == BI_DIR.DOWN and cur_value > peak_value)):
            end_bi = bi
            peak_value = cur_value
    
    if end_bi:
        self.add_new_seg(bi_lst, end_bi.idx, is_sure=False)
```

#### 4. 最后线段更新 (try_update_last_seg)
```python
def try_update_last_seg(self, bi_lst: CBiList):
    """尝试更新最后一个线段的终点"""
    if len(self) == 0:
        return
    
    last_bi = self[-1].end_bi
    peak_value = last_bi.get_end_val()
    new_peak_bi = None
    
    # 寻找更极端的同方向笔
    for bi in bi_lst[self[-1].end_bi.idx+1:]:
        if bi.dir != last_bi.dir:
            continue
        
        if ((bi.is_down() and bi._low() < peak_value) or 
            (bi.is_up() and bi._high() > peak_value)):
            peak_value = bi.get_end_val()
            new_peak_bi = bi
    
    if new_peak_bi:
        self[-1].end_bi = new_peak_bi
        self[-1].is_sure = False  # 标记为不确定
```

---

## 3. Def算法 (SegListDef) - 定义二详细实现

### 核心概念

Def算法是最简化的线段识别方法，仅通过比较笔的高低点来判断是否构成线段。

### 关键判断函数

```python
def is_up_seg(bi, pre_bi):
    """判断是否构成上升线段：当前笔高点超过前笔高点"""
    return bi._high() > pre_bi._high()

def is_down_seg(bi, pre_bi):
    """判断是否构成下降线段：当前笔低点低于前笔低点"""
    return bi._low() < pre_bi._low()
```

### 算法实现流程

#### 1. 主更新流程
```python
def update(self, bi_lst: CBiList):
    # 1. 初始化
    self.do_init()
    
    # 2. 计算确定线段
    self.cal_bi_sure(bi_lst)
    
    # 3. 收集剩余线段
    self.collect_left_seg(bi_lst)
```

#### 2. 核心算法 (cal_bi_sure)
```python
def cal_bi_sure(self, bi_lst):
    peak_bi = None  # 当前峰值笔
    
    if len(bi_lst) == 0:
        return
    
    for idx, bi in enumerate(bi_lst):
        if idx < 2:
            continue  # 需要至少2个笔才能比较
        
        # 峰值笔更新逻辑
        if peak_bi and ((bi.is_up() and peak_bi.is_up() and 
                        bi._high() >= peak_bi._high()) or 
                       (bi.is_down() and peak_bi.is_down() and 
                        bi._low() <= peak_bi._low())):
            peak_bi = bi  # 更新峰值笔
            continue
        
        # 确定线段更新逻辑
        if (self.sure_seg_update_end and len(self) and 
            bi.dir == self[-1].dir and 
            ((bi.is_up() and bi._high() >= self[-1].end_bi._high()) or 
             (bi.is_down() and bi._low() <= self[-1].end_bi._low()))):
            
            self.update_last_end(bi_lst, bi.idx)  # 更新线段终点
            peak_bi = None
            continue
        
        # 线段识别核心逻辑
        pre_bi = bi_lst[idx-2]  # 前两个笔
        
        if ((bi.is_up() and is_up_seg(bi, pre_bi)) or 
            (bi.is_down() and is_down_seg(bi, pre_bi))):
            
            if peak_bi is None:
                # 没有峰值笔，且方向不同于最后线段
                if len(self) == 0 or bi.dir != self[-1].dir:
                    peak_bi = bi
                    continue
            elif peak_bi.dir != bi.dir:
                # 峰值笔方向不同，且间隔足够
                if bi.idx - peak_bi.idx <= 2:
                    continue
                
                self.add_new_seg(bi_lst, peak_bi.idx)  # 添加线段
                peak_bi = bi
                continue
    
    # 处理最后的峰值笔
    if peak_bi is not None:
        self.add_new_seg(bi_lst, peak_bi.idx, is_sure=False)
```

#### 3. 线段终点更新 (update_last_end)
```python
def update_last_end(self, bi_lst, new_endbi_idx: int):
    """更新最后一个线段的终点"""
    last_endbi_idx = self[-1].end_bi.idx
    assert new_endbi_idx >= last_endbi_idx + 2
    
    # 更新终点笔
    self[-1].end_bi = bi_lst[new_endbi_idx]
    
    # 更新线段包含的笔列表
    self.lst[-1].update_bi_list(bi_lst, last_endbi_idx, new_endbi_idx)
```

---

## 算法复杂度分析

| 算法 | 时间复杂度 | 空间复杂度 | 主要计算开销 |
|------|------------|------------|--------------|
| Chan | O(n²) | O(n) | 分形特征计算、反向分形搜索 |
| DYH | O(n) | O(1) | 双情况判断、极值搜索 |
| Def | O(n) | O(1) | 简单高低点比较 |

## 关键差异总结

1. **Chan算法**：通过完整的分形特征序列理论，最符合缠论原理，但计算复杂
2. **DYH算法**：通过笔的突破关系判断，平衡了精度和性能
3. **Def算法**：通过简单的高低点比较，速度最快但可能不够精确

每种算法都有其适用场景，可根据具体需求选择使用。