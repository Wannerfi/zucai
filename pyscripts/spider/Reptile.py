'''
爬取网站数据并保存到本地
'''

import os
import traceback

from selenium import webdriver
from selenium.webdriver.common.by import By
import time
from MatchStatus import *
from Schedule import *
import re
import shutil
import pandas as pd

def print_log(msg: str, log_path='log.txt'):
    localtime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    with open(log_path, 'a', encoding='utf-8') as f:
        f.write(localtime + ' ' + msg + '\n')

class Reptile:
    def dump_and_delay(self, driver: webdriver.Edge, url: str):
        print_log('跳转网页{0}'.format(url))
        driver.get(url)
        time.sleep(31)  # 防止反爬虫检测

    # 先进入对应的联赛，然后爬出所有的赛季网址，再遍历所有网址拿到联赛数据
    def go_to_match(self, driver: webdriver.Edge, match_name: str, out_season_url_list: list):
        all_match = driver.find_element(By.ID, 'select_notcups')
        match = all_match.find_element(By.XPATH, '//option[contains(text(), "{0}")]'.format(match_name))
        match_value = match.get_attribute('value')

        # 跳转到对应网页
        self.dump_and_delay(driver, 'https://liansai.500.com/zuqiu-{0}/'.format(match_value))

        # 添加赛季列表
        season_title = driver.find_element(By.XPATH, '//ul[@class="ldrop_list"]')
        season_list = season_title.find_elements(By.XPATH, '//ul[@class="ldrop_list"]/li/a')
        for s in season_list[::-1]:  # 从小到大
            sub_url = s.get_attribute('href')
            out_season_url_list.append(sub_url)

    def get_season_data(self, driver: webdriver.Edge, url: str, sche: Schedule):
        self.dump_and_delay(driver, url)
        cur_round_index = 0
        while cur_round_index < sche.cur_round_index:
            rounds = driver.find_elements(By.XPATH, '//span[@class="lcol_hd_lun"]/a')
            rounds[0].click()
            cur_round_index += 1
            time.sleep(4)

        self.get_round_data(driver, url, cur_round_index) # 回来后还是 cur_round_index

        # 表格有多轮
        next_round = driver.find_elements(By.XPATH, '//span[@class="lcol_hd_lun"]')
        while not ('1' in next_round[0].text.strip()):
            # 进入下一轮
            rounds = next_round[0].find_elements(By.XPATH, './/a')
            rounds[0].click()
            time.sleep(4)
            cur_round_index += 1

            self.get_round_data(driver, url, cur_round_index)
            sche.set_cur_round_index(cur_round_index)
            sche.save_data()

            next_round = driver.find_elements(By.XPATH, '//span[@class="lcol_hd_lun"]')

    def get_round_data(self, driver: webdriver.Edge, url: str, round_index: int):
        all_match = driver.find_elements(By.XPATH, '//tbody[@class="jTrInterval"]/tr')
        i = 0
        count = len(all_match)
        while i < count:
            all_match = driver.find_elements(By.XPATH, '//tbody[@class="jTrInterval"]/tr')
            m_info = all_match[i].find_elements(By.XPATH, './/td')
            i += 1

            timestamp = m_info[0].text.strip()
            home_team = m_info[1].text.strip()
            away_team = m_info[3].text.strip()
            match_status = MatchStatus(timestamp, home_team, away_team)

            # 还没出比赛结果 或 没有平均欧指
            # 如果已经保存了，就不再保存
            if ('vs' in m_info[2].text.lower()) or (len(m_info[5].text.strip()) <= 0) or os.path.exists(match_status.get_save_path()):
                continue

            analyze_url = m_info[6].find_element(By.XPATH, './/a').get_attribute('href')
            self.dump_and_delay(driver, analyze_url)
            self.get_match_data(driver, match_status)

            # 恢复到当前轮
            self.dump_and_delay(driver, url)
            cur_round_index = 0
            while cur_round_index < round_index:
                cur_round_index += 1
                rounds = driver.find_elements(By.XPATH, '//span[@class="lcol_hd_lun"]/a')
                rounds[0].click()
                time.sleep(4)


    def get_match_data(self, driver: webdriver.Edge, match_status: MatchStatus):
        score_str = driver.find_element(By.XPATH,
                                        '//div[@class="odds_hd_center"]/p[@class="odds_hd_bf"]/strong').text.strip()
        score = score_str.split(':')
        if 'vs' in score_str.lower():
            return
        match_status.set_score([int(score[0]), int(score[1])])

        time.sleep(4)
        driver.find_element(By.XPATH, '//ul[@class="odds_nav_list"]/li[contains(@onclick, "ouzhi")]').click()
        olddownpl = driver.find_element(By.XPATH, '//tr[@xls="header"]/th/a[contains(@class, "olddownpl")]')
        olddownpl.click()  # 下载欧赔
        time.sleep(4)
        print_log('finish down ouzhi step:{0} {1} vs {2}'.format(match_status.timestamp, match_status.home_team,
                                                            match_status.away_team))
        try: # 可能 excel 解析错误
            self.process_oupei(match_status)
        except:
            error_msg = traceback.format_exc()
            print_log(error_msg)

        driver.find_element(By.XPATH, '//ul[@class="odds_nav_list"]/li[contains(@onclick, "yazhi")]').click()
        downpl = driver.find_element(By.XPATH, '//tr[@xls="header"]/th/a[contains(@class, "downpl")]')
        downpl.click()  # 下载亚盘
        time.sleep(4)
        print_log('finish down yapan step:{0} {1} vs {2}'.format(match_status.timestamp, match_status.home_team,
                                                            match_status.away_team))
        self.process_yapan(match_status)

        match_status.save_data(match_status.get_save_path())
        pass

    def match_and_move_download_file(self, save_dic_path: str, pattern: str, prefix:str = '', try_times: int = 10):
        download_path = 'C:\\Users\\90571\\Downloads'
        tf = None
        cnt = 0
        while (not tf) and cnt < try_times:
            time.sleep(2)
            print_log('等待下载完成')
            files = os.listdir(download_path)
            for f in files:
                if re.search(pattern, f):
                    tf = f
                    break
            cnt += 1

        if not tf:
            return None

        source_path = os.path.join(download_path, tf) # 这里报错就是没有下载好
        target_path = os.path.join(save_dic_path, prefix + tf)
        if not os.path.exists(save_dic_path):
            os.makedirs(save_dic_path)
        shutil.move(source_path, target_path)
        return target_path

    def process_oupei(self, match_status: MatchStatus, save_dic_path: str = '{0}/competition/europe'.format(os.getcwd())):
        xml_path = self.match_and_move_download_file(save_dic_path, '欧洲数据', match_status.timestamp.split(' ')[0])

        if not xml_path:
            print_log('process oupei error:'.format(match_status.timestamp, match_status.home_team, match_status.away_team))
            return

        df_sheet_list = pd.ExcelFile(xml_path)
        sheet_name = df_sheet_list.sheet_names[1]
        oupei_xls = pd.read_excel(xml_path, sheet_name=sheet_name, usecols="A,L:U", skiprows=lambda x:x in range(0, 3))
        avg = [format(x, '.5f') for x in oupei_xls.values[0][1:]]
        discrete = [str(x) for x in oupei_xls.values[1][1:4]]
        match_status.set_oupei_input(avg, discrete)
        for v in oupei_xls.values[2:]:
            odds = [format(x, '.5f') for x in v[1:]]
            o = OuZhi(v[0], odds)
            match_status.add_ouzhi(o)
        pass

    def process_yapan(self, match_status: MatchStatus, save_dic_path: str = '{0}/competition/asia_andicap'.format(os.getcwd())):
        xml_path = self.match_and_move_download_file(save_dic_path, '亚盘', match_status.timestamp.split(' ')[0])

        if not xml_path:
            print_log('process yapan error:'.format(match_status.timestamp, match_status.home_team, match_status.away_team))
            return

        yapan_xls = pd.read_excel(xml_path, usecols="A, F:H", skiprows=lambda x:x in range(0, 4))
        for v in yapan_xls.values:
            yapan = [x for x in v[1:]]
            y = YaPan(v[0], yapan)
            match_status.add_yapan(y)
        pass

    def begin(self, ):
        # 浏览器设置
        options = webdriver.EdgeOptions()
        # options.add_argument('headless') # 无界面
        service = webdriver.EdgeService(executable_path='msedgedriver.exe')

        # 开始启动浏览器
        print_log('begin')
        driver = webdriver.Edge(options=options, service=service)
        driver.implicitly_wait(100)  # 隐式等待
        driver.get('https://liansai.500.com/zuqiu-194/')

        five_match = ['英超', '西甲', '意甲', '德甲', '法甲']
        sche = Schedule.get_data()
        i = 0
        j = 0
        season_url_list = []
        if sche:
            five_match = sche.match_list
            i = sche.match_index
            season_url_list = sche.season_url_list
            j = sche.cur_list_index
        else:
            sche = Schedule()

        while i < len(five_match):
            if len(season_url_list) <= 0:
                self.go_to_match(driver, five_match[i], season_url_list)
                j = 2 # 2 开始是因为 2002 赛季开始才有欧赔指数

            while j < len(season_url_list):
                # 保存记录
                sche.set_union_name(five_match, i, season_url_list, j)
                sche.save_data()

                self.get_season_data(driver, season_url_list[j], sche)
                sche.set_cur_round_index(0)  # 重置轮数
                j += 1
            i += 1
            j = 0
            season_url_list = []

        print_log('end')
        return 0

    def test(self):
        # 浏览器设置
        options = webdriver.EdgeOptions()
        options.add_argument('headless') # 无界面
        service = webdriver.EdgeService(executable_path='msedgedriver.exe')

        # 开始启动浏览器
        print_log('begin')
        driver = webdriver.Edge(options=options, service=service)
        driver.implicitly_wait(2)  # 隐式等待
        driver.get('https://liansai.500.com/zuqiu-6858/')

        self.get_season_data(driver, 'https://liansai.500.com/zuqiu-6858/', Schedule())

        while True:
            pass
        pass