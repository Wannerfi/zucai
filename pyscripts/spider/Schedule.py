import json
import os

# 断点重连数据

class Schedule:
    def __init__(self):
        self.cur_round_index = 0

    def set_union_name(self, match_list: list, match_index: int, season_url_list: list, cur_list_index: int):
        self.match_list = match_list
        self.match_index = match_index
        self.season_url_list = season_url_list
        self.cur_list_index = cur_list_index

    def set_cur_round_index(self, cur_round_index: int):
        self.cur_round_index = cur_round_index

    def save_data(self, path: str = './sche.json'):
        dic = self.__dict__
        js = json.dumps(dic, ensure_ascii=False)
        dir = os.path.dirname(path)
        if not os.path.exists(dir):
            os.makedirs(dir)

        with open(path, 'w', encoding='utf-8') as f:
            f.write(js)
        return js

    @staticmethod
    def get_data(path: str = './sche.json'):
        if not os.path.exists(path):
            return None

        with open(path, 'r', encoding='utf-8') as f:
            dic = json.loads(f.read())
            ret = Schedule()
            ret.__dict__ = dic
            return ret
