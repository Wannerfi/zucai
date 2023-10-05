from spider.MatchStatus import *
import os

class LearningData:
    def __init__(self, path: str = './spider/competition/situation'):
        self.all_match_data = []

        files = os.listdir(path)
        for p in files:
            full_path = os.path.join(path, p)
            data = MatchStatus.get_data(full_path)
            self.all_match_data.append(data)

    # 将数据分成 k 组
    def cross_validation_data(self, k: int = 10):
        ret = [[] for i in range(k)]

        count = len(self.all_match_data)
        for i in range(count):
            index = i % k
            ret[index].append(self.all_match_data[i])

        return ret

    @staticmethod
    def to_train_data(match_status: MatchStatus, label_func=None):
        data = LearningData.__list_insert([], match_status.input_oupei_avg)
        data = LearningData.__list_insert(data, match_status.input_discrete)
        data = [float(i) for i in data]

        if label_func is None:
            label = match_status.result
        else:
            label = label_func(match_status)
        return data, [label]

    @staticmethod
    def __list_insert(target: list, data):
        if type(data) is list:
            for i in data:
                target.append(i)
        else:
            target.append(data)
        return target
