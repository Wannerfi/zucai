import json
import os

class OuZhi:
    # europe_odds 欧赔数据 [胜, 平, 负, 胜率, 和率, 负率, 返还率, 凯利指数(3个)]，一共十个数据，存为 str
    # avg 平均欧指，和 discrete 离散值一起作为训练的输入
    def __init__(self, company: str, europe_odds: list):
        self.company = company
        self.europe_odds = europe_odds

    def get_dict(self):
        return {'company': self.company, 'europe_odds': self.europe_odds}

class YaPan:
    def __init__(self, company: str, asia_handicap: list):
        self.company = company
        self.asia_handicap = asia_handicap

    def get_dict(self):
        return {'company': self.company, 'asia_handicap': self.asia_handicap}

class MatchStatus:
    def __init__(self, timestamp: str, home_team: str, away_team: str, ):
        self.id = hash(timestamp + home_team + away_team)
        self.timestamp = timestamp
        self.home_team = home_team
        self.away_team = away_team
        self.ouzhi = []
        self.yapan = []
        self.score = []
        self.result = 0
        self.input_oupei_avg = []
        self.input_discrete = []

    def get_file_name(self):
        return '{0}_{1}_{2}.json'.format(self.timestamp, self.home_team, self.away_team).replace(' ', '_').replace(':', '_')

    def get_save_path(self):
        return './competition/situation/{0}'.format(self.get_file_name())

    def set_score(self, score: list):
        self.score = score
        self.result: int = score[0] - score[1]

    def set_oupei_input(self, avg: list, discrete: list):
        self.input_oupei_avg = avg
        self.input_discrete = discrete

    def add_ouzhi(self, ouzhi: OuZhi):
        self.ouzhi.append(ouzhi.get_dict())

    def add_yapan(self, yapan: YaPan):
        self.yapan.append(yapan.get_dict())

    def save_data(self, path: str):
        dic = self.__dict__
        js = json.dumps(dic, ensure_ascii=False)
        dir = os.path.dirname(path)
        if not os.path.exists(dir):
            os.makedirs(dir)

        with open(path, 'w', encoding='utf-8') as f:
            f.write(js)

        return js

    def is_unuseful(self):
        return len(self.ouzhi) <= 0

    @staticmethod
    def get_data(path: str):
        with open(path, 'r', encoding='utf-8') as f:
            dic = json.loads(f.read())
            ret = MatchStatus('', '', '')
            ret.__dict__ = dic
            return ret

