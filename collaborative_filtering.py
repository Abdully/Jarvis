import os
import re
import csv
import time
import heapq
import jieba
import _thread
import timeit
import logging
import Levenshtein
from pylab import *
from numpy import *
from scipy import signal
import jieba.posseg as pseg

''' raw data info

db_name   说明    index     proj_name             example

uid     订单编号     0                           160203104111518000
sldat   购买时间     1                           2016/2/3 10:41
pno     收银员编号   2                           15
cno     收银机编号   3                           8331
cmrid   性别年龄     4                           女[45 以上]
vipno   会员编号     5      user_id              2900000161443
id      商品单内编号  6                           3
pluno   商品编号     7      item_id              14721041
bcd     条码         8                          6903252713411
pluname 商品名称     9      item_name            康师傅面霸煮面上汤排骨面五入100g*5
spec    包装规格     10                          1*6
pkunit  商品单位     11     item_unit            包
dptno   商品类型编号  12     item_category        14721
dptname 商品类型名称  13                          连包装
bndno   品牌编号     14                          14177
bndname 品牌名称     15     brand_name           康师傅方便面
qty     购买数量     16     count                1
amt     金额        17                           17.5
disamt  是否打折     18                          0  
ismmx   是否促销     19                          0
mtype   促销类型     2019                        0
mdocno  促销单号     21
isdel   是否更正     2219                        0
'''

def read_data(month):
    logging.info('begin to read data in {0}.'.format(month))
    user_list = []
    item_list = []
    item_category_list = []
    item_name_list = []
    brand_name_list = []
    item_unit_list = []
    with open('data/{0}.csv'.format(month)) as csv_file:
        reader = csv.reader(csv_file)
        for row in reader:
            user_id = row[5]
            item_id = row[7]
            item_category = row[12][:4]
            item_name = row[9]
            brand_name = row[15]
            item_unit = row[11]
            count = round(float(row[16]))
            user_exist = False
            item_exist = False
            item_unit_list.append(item_unit)
            for item in item_list:
                if item_id == item:
                    item_exist = True
            if not item_exist:
                item_list.append(item_id)
                item_category_list.append(item_category)
                item_name_list.append(item_name)
                if brand_name is not '':
                    brand_name_list.append(brand_name)
            for user in user_list:
                if user_id == user.user_id:
                    user_exist = True
                    user.item_rank[item_id] = count + user.item_rank.get(item_id, 0)
            if not user_exist:
                user = User(user_id, {item_id: count})
                user_list.append(user)
    logging.info('complete loading data in {0}.'.format(month))
    return (user_list, item_list, item_category_list, item_name_list, brand_name_list, item_unit_list)

def unite_unit(item_unit_list):
    new_item_unit_list = list(set(item_unit_list))
    print(new_item_unit_list)

def customize_dict(brand_name_list, month):
    new_brand_name_list = list(set(brand_name_list))
    with open('dict/{0}.txt'.format(month), 'w') as txt_file:
        for brand_name in new_brand_name_list:
            txt_file.write(brand_name + '\n')

def gaussian(x, sigma):
    return (math.exp(-pow(x, 2) / sigma))

def jieba_(item_name_list, month):
    jieba.load_userdict('dict/{0}.txt'.format(month))
    new_name_list = []
    for item_name in item_name_list:
        meaning_list = ['ns', 'n', 'vn', 'v', 'nr', 'nz', 'i', 'nz', 'a', 'nt']
        seg_item_name = pseg.cut(item_name)
        str = ""
        for word, flag in seg_item_name:
            if flag in meaning_list:
                str += word
        new_name_list.append(str)
    return new_name_list

def visualization(user_list, item_list):
    item_len = len(item_list)
    user_len = len(user_list)
    user_dict = {}
    item_dict = {}
    item_cnt = {}
    for user in user_list:
        user_dict[len(user.item_rank)] = 1 + user_dict.get(len(user.item_rank), 0)
        for item in user.item_rank:
            item_dict[item] = user.item_rank[item] + item_dict.get(item, 0)
    for item in item_dict:
        item_cnt[item_dict[item]] = 1 + item_cnt.get(item_dict[item], 0)
    axis('equal')
    pie(list(user_dict.values()), labels=list(user_dict.keys()), autopct='%d%%')
    savefig("visualization_user.png", dpi=400)
    clf()
    axis('equal')
    pie(list(item_cnt.values()), labels=list(item_cnt.keys()), autopct='%d%%')
    savefig("visualization_item.png", dpi=400)

def cosine_similarity(user_list, item_list, item_category_list, new_name_list, gaussian_sigma):
    logging.info('begin to calculate cosine similarity.')
    item_len = len(item_list)
    temp_item_matrix = mat(zeros((item_len, item_len)))
    item_matrix = mat(zeros((item_len, item_len)))
    item_dict = {}
    for index, item in enumerate(item_list):
        item_dict[item] = index
    for user in user_list:
        for item_1 in user.item_rank:
            for item_2 in user.item_rank:
                if item_1 != item_2:
                    temp_item_matrix[item_dict[item_1], item_dict[item_2]] += 1
                    if item_category_list[item_dict[item_1]] == item_category_list[item_dict[item_2]]:
                        dis = Levenshtein.distance(new_name_list[item_dict[item_1]], new_name_list[item_dict[item_2]])
                        if (new_name_list[item_dict[item_1]] != '') and (new_name_list[item_dict[item_2]] != ''):
                            temp_item_matrix[item_dict[item_1], item_dict[item_2]] += gaussian(dis, gaussian_sigma) * temp_item_matrix[item_dict[item_1], item_dict[item_2]]
                        # if dis != 0:
                        #     temp_item_matrix[item_dict[item_1], item_dict[item_2]] += 10/dis
    sum_column = sum(temp_item_matrix, axis=1)
    sum_row = sum(temp_item_matrix, axis=0)
    for i in range(item_len):
        for j in range(item_len):
            times = sum_column[i, 0] * sum_row[0, j]
            if times != 0:
                item_matrix[i, j] = temp_item_matrix[i, j] / (sqrt(times))
    logging.info('complete calculating cosine similarity.')
    return item_matrix

def output(recommendation_list, item_list):
    with open('result/recommendation_list.csv', 'w') as csv_file:
        for key, values in recommendation_list.items():
            items = []
            for value in values:
                items.append(item_list[value])
            csv_file.write('%s, %s\n' %(key, items))

def top_n(item_matrix, user_list, item_list, n=3):
    logging.info('begin to calculate top_{0}.'.format(n))
    topn_list = [[0] * n] * item_matrix.shape[0]
    recommendation_list = {}
    item_matrix_list = item_matrix.tolist()
    for i in range(item_matrix.shape[0]):
        topn_list[i] = heapq.nlargest(n, range(len(item_matrix_list[i])), item_matrix_list[i].__getitem__)
    logging.info('middle of top_{0}.'.format(n))
    item_dict = {}
    for index, item in enumerate(item_list):
        item_dict[item] = index
    for user in user_list:
        top = []
        for item in user.item_rank:
            for reco_item in topn_list[item_dict[item]]:
                top.append((item_dict[item], reco_item))
        top.sort(key=lambda tup: item_matrix[tup[0], tup[1]], reverse=True)
        top_reco = []
        for item in top:
            top_reco.append(item[1])
        top_reco_deduplication = list(set(top_reco))
        top_reco_deduplication.sort(key=top_reco.index)
        recommendation_list[user.user_id] = top_reco_deduplication[:n]
    logging.info('complete calculating top_{0}.'.format(n))
    return recommendation_list

def measure(test_user_list, recommendation_list, item_list, ignore_item_threshold=0):
    logging.info('begin to test.')
    true_positives = 0
    precision_denominator = 0
    recall_denominator = 0
    for user in test_user_list:
        if (recommendation_list.__contains__(user.user_id)) and (len(user.item_rank) >= ignore_item_threshold):
            item_len = 0
            for test_item in user.item_rank:
                if (test_item in item_list):
                    item_len += 1
                    for reco_item in recommendation_list[user.user_id]:
                        if test_item == item_list[int(reco_item)]:
                            true_positives += 1
            precision_denominator += len(recommendation_list[user.user_id])
            recall_denominator += item_len
    precision = true_positives / precision_denominator
    recall = true_positives / recall_denominator
    logging.info('complete testing.')
    return (precision, recall)

def draw(n_begin, n_end, n_step):
    x = [i for i in range(n_begin, n_end, n_step)]
    result_files = os.listdir("result")
    for file in result_files:
        if os.path.splitext(file)[1] == '.txt':
            f = open("result/{0}".format(file))
            data = f.readlines()
            tail = int((n_end - n_begin - 1) / n_step) + 2
            plot(x, re.split('[ |\]||,|\[||\n]+', data[0])[2:tail], label=("precision:" + os.path.splitext(file)[0]))
            plot(x, re.split('[ |\]||,|\[||\n]+', data[1])[2:tail], label=("recall:" + os.path.splitext(file)[0]))
    legend(loc='lower right')
    savefig("result.png", dpi=400)

def notify():
    # os.system('ssh -p 8000 Yang@10.60.41.125')
    os.system('python3 /Users/Yang/Developer/Jarvis/notify.py')

class User(object):
    def __init__(self, user_id, item_rank):
        self.user_id = user_id
        self.item_rank = item_rank

def main():
    # ''' item-based collaborative filtering'''

    n_begin = 20
    n_end = 101
    n_step = 5
    gaussian_sigma = 10
    train_month = 'trainData_07'
    test_month = 'testData_08_07'

    logging.basicConfig(filename='cf.log', level=logging.INFO)
    logging.info(time.asctime(time.localtime(time.time())))
    start_time = timeit.default_timer()

    precision_list = []
    recall_list = []
    train_user_list, train_item_list, item_category_list, item_name_list, brand_name_list, item_unit_list = read_data(train_month)
    
    customize_dict(brand_name_list, train_month)

    new_name_list = jieba_(item_name_list, train_month)
    item_matrix = cosine_similarity(train_user_list, train_item_list, item_category_list, new_name_list, gaussian_sigma)
    test_user_list, _, _, _, _, _ = read_data(test_month)
    for n in range(n_begin, n_end, n_step):
        recommendation_list = top_n(item_matrix, train_user_list, train_item_list, n)
        output(recommendation_list, train_item_list)
        precision, recall = measure(test_user_list, recommendation_list, train_item_list)
        precision_list.append(precision)
        recall_list.append(recall)
    result = open("result/result.txt", 'w')
    print('precision = {0}'.format(precision_list), file=result)
    print('recall = {0}'.format(recall_list), file=result)

    stop_time = timeit.default_timer()
    logging.info('run in {0} seconds.\n'.format(stop_time - start_time))

    # draw(n_begin, n_end, n_step)

    notify()

if __name__ == '__main__':
    main()
