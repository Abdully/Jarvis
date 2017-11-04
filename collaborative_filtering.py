import os
import re
import csv
import time
import heapq
import _thread
import timeit
import logging
from pylab import *
from numpy import *

def read_data(month):
    logging.info('begin to read data in {0}.'.format(month))
    user_list = []
    item_list = []
    with open('data/{0}.csv'.format(month)) as csv_file:
        reader = csv.reader(csv_file)
        for row in reader:
            user_id = row[0]
            item_id = row[1]
            count = int(row[2])
            user_exist = False
            item_exist = False
            for item in item_list:
                if item_id == item:
                    item_exist = True
            if not item_exist:
                item_list.append(item_id)
            for user in user_list:
                if user_id == user.user_id:
                    user_exist = True
                    user.item_rank[item_id] = count + user.item_rank.get(item_id, 0)
            if not user_exist:
                user = User(user_id, {item_id: count})
                user_list.append(user)
    logging.info('complete loading data in {0}.'.format(month))
    return (user_list, item_list)

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

def cosine_similarity(user_list, item_list):
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

    n_begin = 10
    n_end = 11
    n_step = 5

    logging.basicConfig(filename='cf.log', level=logging.INFO)
    logging.info(time.asctime(time.localtime(time.time())))
    start_time = timeit.default_timer()

    precision_list = []
    recall_list = []
    train_user_list, train_item_list = read_data('05/trainData_05_07')
    item_matrix = cosine_similarity(train_user_list, train_item_list)
    test_user_list, _ = read_data('05/testData_08_05')
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
