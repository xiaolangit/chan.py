import pandas as pd
from io import StringIO
import requests
from datetime import datetime
from typing import Iterable

from Common.CEnum import AUTYPE, DATA_FIELD, KL_TYPE
from Common.CTime import CTime
from Common.func_util import str2float
from KLine.KLine_Unit import CKLine_Unit
from .CommonStockAPI import CCommonStockApi

class CQMTData(CCommonStockApi):
    def __init__(self, code, k_type=KL_TYPE.K_DAY, begin_date=None, end_date=None, autype=AUTYPE.QFQ):
        super(CQMTData, self).__init__(code, k_type, begin_date, end_date, autype)

    def get_kl_data(self):
        # 调用 QMT 讯投的接口获取数据
        data = self._fetch_data_from_qmt(self.code, self.__convert_type(), self.begin_date, self.end_date)
        
        for index, row in data.iterrows():
            item_dict = {
                DATA_FIELD.FIELD_TIME: self.parse_timestamp(row['time']),
                DATA_FIELD.FIELD_OPEN: float(row['open']),
                DATA_FIELD.FIELD_CLOSE: float(row['close']),
                DATA_FIELD.FIELD_LOW: float(row['low']),
                DATA_FIELD.FIELD_HIGH: float(row['high']),
                DATA_FIELD.FIELD_VOLUME: float(row['volume']),
            }
            yield CKLine_Unit(item_dict)

    def SetBasicInfo(self):
        # 设置股票基本信息
        stock_info = self._fetch_stock_info_from_qmt(self.code)
        self.stock_name = stock_info.get('name', self.code)  # 假设股票名称列名为 'name'

    def _fetch_data_from_qmt(self, code, k_type, begin_date, end_date):
        # 这里是一个示例实现，实际中你需要根据 QMT 讯投的接口进行调整
        # 假设 QMT 讯投的接口返回一个 Pandas DataFrame
        # 以下代码仅为示例，实际中需要替换为 QMT 讯投的接口调用
        #url = f"http://qmt.example.com/api/data?code={code}&k_type={k_type}&begin_date={begin_date}&end_date={end_date}"
        if end_date:
            url = f"http://111.180.147.209/chan/stock?code={code}&period={k_type}&start_time={begin_date}&end_time={end_date}"
        else:
            url = f"http://111.180.147.209/chan/stock?code={code}&period={k_type}&start_time={begin_date}"

        # 发起请求获取数据
        response = requests.get(url)
        if response.status_code != 200:
            raise Exception(f"Failed to fetch data: {response.text}")

        response_json = response.json()  # 解析外层JSON
        data_str = response_json.get('data', '[]')  # 获取内层JSON字符串
        data_io = StringIO(data_str)
        data = pd.read_json(data_io)  # 解析内层JSON字符串为DataFrame

        # 按时间戳进行排序
        df_sorted = data.sort_values(by='time')

        print(df_sorted)

        return df_sorted

    def _fetch_stock_info_from_qmt(self, code):
        # 这里是一个示例实现，实际中你需要根据 QMT 讯投的接口进行调整
        # 假设 QMT 讯投的接口返回一个包含股票信息的字典
        # 以下代码仅为示例，实际中需要替换为 QMT 讯投的接口调用
        # url = f"http://qmt.example.com/api/stock_info?code={code}"
        # 发起请求获取数据
        # response = requests.get(url)
        # return response.json()
        
        # 临时返回默认值
        return {"name": code}

    @staticmethod
    def parse_timestamp(timestamp):
        # 将毫秒级时间戳转换为CTime对象
        dt = datetime.fromtimestamp(timestamp / 1000)  # 将毫秒级时间戳转换为秒级
        return CTime(dt.year, dt.month, dt.day, dt.hour, dt.minute)

    def __convert_type(self):
        _dict = {
            KL_TYPE.K_DAY: '1d',
            KL_TYPE.K_WEEK: '1w',
            KL_TYPE.K_MON: '1M',
            KL_TYPE.K_1M: '1m',
            KL_TYPE.K_5M: '5m',
            KL_TYPE.K_15M: '15m',
            KL_TYPE.K_30M: '30m',
            KL_TYPE.K_60M: '60m',
        }
        return _dict[self.k_type]