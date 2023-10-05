import numpy as np
from LearningData import *

class LinearRegression:
    def __init__(self, data: np.matrix, labels: np.matrix):
        self.data = data
        self.labels = labels

        num_features = self.data.shape[1] #获取列数
        self.theta = np.zeros((num_features, 1))

    def train(self, alpha, num_iterations = 500):
        '''
        :param alpha: 学习率
        :param num_iterations: 迭代次数
        :return:
        '''
        cost_history = self.gradient_descend(alpha, num_iterations)
        return self.theta, cost_history

    def gradient_descend(self, alpha, num_iterations):
        cost_history = []
        for i in range(num_iterations):
            self.gradient_step(alpha)
            cost = self.cost_function(self.data, self.labels)

            print('轮数{0}/{1}: 当前损失: {2}'.format(i, num_iterations, cost))

            cost_history.append(cost)
        return cost_history

    def gradient_step(self, alpha):
        '''
        批量梯度下降
        :param alpha: 学习率
        :return:
        '''
        num_examples = self.data.shape[0]
        prediction = LinearRegression.hypothesis(self.data, self.theta)
        delta = prediction - self.labels # [n * 1]
        sum = (np.dot(delta.T, self.data)).T
        self.theta = self.theta - alpha * (1 / num_examples) * sum

    def cost_function(self, data, labels):
        '''
        损失计算
        :param data:
        :param labels:
        :return:
        '''
        num_examples = data.shape[0]
        delta = LinearRegression.hypothesis(self.data, self.theta) - labels
        cost = np.dot(delta.T, delta)
        return cost[0, 0] / (2 * delta.shape[0])

    @staticmethod
    def hypothesis(data, theta):
        '''
        线性模型 y = theta * data，所以这里得到新预测的 y
        :param data:
        :param theta:
        :return:
        '''
        predictions = np.dot(data, theta)
        return predictions

    def get_cost(self, data, labels):
        '''
        :param data:
        :param labels:
        :return:
        '''
        return self.cost_function(data, labels)

    def predict(self):
        '''
        用训练的参数模型，与预测得到的回归结果
        :return:
        '''
        predictions = LinearRegression.hypothesis(self.data, self.theta)

def save_theta(theta, theta_f_path: str = 'linear_regression_to_result_theta.res'):
    with open(theta_f_path, 'w', encoding='utf-8') as f:
        [rows, cols] = theta.shape
        f.write('{0}'.format(rows))
        f.write('\n')
        f.write('{0}'.format(cols))
        f.write('\n')
        for i in range(rows):
            for j in range(cols):
                f.write('{0}'.format(theta[i, j]))
                f.write(' ')
            f.write('\n')

def get_theta(theta_f_path: str = 'linear_regression_to_result_theta.res'):
    with open(theta_f_path, 'r', encoding='utf-8') as f:
        ret: list = []
        lines = f.readlines()
        for i in range(len(lines)):
            if i < 2:
                continue

            row = lines[i].strip('\n')
            ret.append([float(_) for _ in row.split(' ') if _])

        return np.mat(ret)


def predict_new_data(new_data, theta):
    '''
    用训练的参数模型，与预测得到的回归结果
    :return:
    '''
    return LinearRegression.hypothesis(new_data, theta)

def train_input_to_result():
    # 获取数据
    l_data = LearningData()
    all_match_data_array = l_data.cross_validation_data()

    # 将所有数据变成训练数据
    label_fun = None #lambda match: 1 if match.result > 0 else 0
    all_learning_array = [] #[[(data, label), (data, label), ...], [], ...]
    for match_array in all_match_data_array:
        learning_array = [] #每一项为(data, label)
        for _ in match_array:
            learning_array.append(LearningData.to_train_data(_, label_fun))
        all_learning_array.append(learning_array)


    for i in range(len(all_learning_array)):
        # 划分测试集
        test_index = i

        train_data = []
        train_labels = []
        test_data = []
        test_labels = []

        for j in range(len(all_learning_array)):
            learning_array = all_learning_array[j]
            if j == test_index:
                for _ in learning_array:
                    if not _ in test_data:
                        test_data.append(_[0])
                        test_labels.append(_[1])
            else:
                for _ in learning_array:
                    if not _ in train_data:
                        train_data.append(_[0])
                        train_labels.append(_[1])

        # 在data的第0列插入偏置量
        train_data = np.mat(train_data)
        train_data = np.insert(train_data, 0, 1.0, axis=1)
        test_data = np.mat(test_data)
        test_data = np.insert(test_data, 0, 1.0, axis=1)

        # 开始训练
        num_iterations = 10000
        learning_rate = 0.00000007
        linear_regression = LinearRegression(train_data, train_labels)
        theta, cost_history = linear_regression.train(learning_rate, num_iterations)
        save_theta(theta, 'linear_regression_to_result_theta_{0}.res'.format(i))

        # 测试预测正确率
        test_input_to_result_correct_rate(test_data, test_labels, theta)

        break #跑一次看看

def test_input_to_result_correct_rate(test_data, test_labels, theta = None):
    if theta is None:
        theta = get_theta()

    right_cnt = 0
    for i in range(test_data.shape[0]):
        d = test_data[i]
        l = test_labels[i]

        _res = predict_new_data(d, theta)

        # 用四舍五入测试
        if round(_res[0, 0]) == l[0]:
            right_cnt += 1

    print('正确率: {0}'.format(right_cnt / test_data.shape[0]))


if __name__ == '__main__':
    train_input_to_result()