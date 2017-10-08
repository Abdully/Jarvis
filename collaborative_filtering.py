import csv
import time
import heapq
import _thread
import timeit
import logging
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
    logging.info('middle of cosine similarity.')
    sum_column = sum(temp_item_matrix, axis=1)
    sum_row = sum(temp_item_matrix, axis=0)
    for i in range(item_len):
        for j in range(item_len):
            times = sum_column[i, 0] * sum_row[0, j]
            if times != 0:
                item_matrix[i, j] = temp_item_matrix[i, j] / (sqrt(times))
    logging.info('complete calculating cosine similarity.')
    # try:
    #     _thread.start_new_thread(save, ('data/cosine_similarity.csv', item_matrix))
    # except:
    #     logging.error('can not start thread to save cosine_similarity')
    return item_matrix

def save(file, data):
    savetxt(file, data, delimiter = ',')
    logging.info('complete saving cosine similarity.')

def top_n(item_matrix, user_list, item_list, n=3):
    logging.info('begin to calculate top_n.')
    topn_list = [[0] * n] * item_matrix.shape[0]
    recommendation_list = {}
    item_matrix_list = item_matrix.tolist()
    for i in range(item_matrix.shape[0]):
        topn_list[i] = heapq.nlargest(n, range(len(item_matrix_list[i])), item_matrix_list[i].__getitem__)
    logging.info('middle of top_n.')
    item_dict = {}
    for index, item in enumerate(item_list):
        item_dict[item] = index
    for user in user_list:
        topn = []
        for item in user.item_rank:
            for reco_item in topn_list[item_dict[item]]:
                topn.append((item_dict[item], reco_item))
        topn.sort(key=lambda tup: item_matrix[tup[0], tup[1]], reverse=True)
        recommendation_list[user.user_id] = topn[:n]
    logging.info('complete calculating top_n.')
    return recommendation_list

def measure(test_user_list, recommendation_list, item_list):
    logging.info('begin to test.')
    precision = []
    recall = []
    true_positives = 0
    for user in test_user_list:
        for test_item in user.item_rank:
            for reco_item in recommendation_list:
                if test_item == item_list[int(reco_item)]:
                    true_positives += 1
        precision.append(true_positives / (len(recommendation_list)))
        recall.append(true_positives / len(test_user_list))
    logging.info('complete testing.')
    return(precision, recall)

class User(object):
    def __init__(self, user_id, item_rank):
        self.user_id = user_id
        self.item_rank = item_rank

def main():
    ''' item-based collaborative filtering'''
    logging.basicConfig(filename='cf.log', level=logging.INFO)
    logging.info(time.asctime(time.localtime(time.time())))
    start_time = timeit.default_timer()

    train_user_list, train_item_list = read_data('july')
    item_matrix = cosine_similarity(train_user_list, train_item_list)
    recommendation_list = top_n(item_matrix, train_user_list, train_item_list)
    test_user_list, _ = read_data('aug')
    precision, recall = measure(test_user_list, recommendation_list, train_item_list)
    result = open("result.txt", 'w+')
    print('precision: {0}'.format(precision), file=result)
    print('recall: {0}'.format(recall), file=result)

    stop_time = timeit.default_timer()
    logging.info('run in {0} seconds.\n'.format(stop_time - start_time)) 

if __name__ == '__main__':
    main()
