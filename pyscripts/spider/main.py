import os.path
from Reptile import *

def clear_unuseful_data(path: str = './competition/situation'):
    file_list = os.listdir(path)
    delete_path = []
    for f in file_list:
        if f.endswith('.json'):
            f_path = os.path.join(path, f)
            data = MatchStatus.get_data(f_path)
            if data.is_unuseful():
                delete_path.append(f_path)

    for d in delete_path:
        os.remove(d)


if __name__ == '__main__':
    re = Reptile()
    # re.test()
    # clear_unuseful_data()

    finish = 1
    while not finish == 0:
        try:
            finish = re.begin()
            clear_unuseful_data()
        except:
            error_msg = traceback.format_exc()
            print_log(error_msg)
            time.sleep(30) # 挂掉重启等一下，免得被当成爬虫

