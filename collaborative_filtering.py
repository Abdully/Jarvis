import csv
import time
import heapq
import _thread
import timeit
import logging
from pylab import *
from numpy import *
# TODO:
# 1. 根据训练集中的物品数量确定测试集推荐数量

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
    sum_column = sum(temp_item_matrix, axis=1)
    sum_row = sum(temp_item_matrix, axis=0)
    for i in range(item_len):
        for j in range(item_len):
            times = sum_column[i, 0] * sum_row[0, j]
            if times != 0:
                item_matrix[i, j] = temp_item_matrix[i, j] / (sqrt(times))
    logging.info('complete calculating cosine similarity.')
    return item_matrix

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

def measure(test_user_list, recommendation_list, item_list, ignore_test_threshold):
    logging.info('begin to test.')
    true_positives = 0
    precision_denominator = 0
    recall_denominator = 0
    for user in test_user_list:
        if (recommendation_list.__contains__(user.user_id)) and (len(user.item_rank) >= ignore_test_threshold):
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

def draw(precision_list, recall_list):
    x = [i for i in range(3, 21)]
    precision_10 = [0.01024428684003152, 0.01182033096926714, 0.011583924349881796, 0.011426319936958234, 0.01165146909827761, 0.012263593380614658, 0.012214342001576044, 0.012174940898345154, 0.01246507629486353, 0.012509850275807723, 0.012002182214948172, 0.012833502195204323, 0.012687155240346729, 0.013371749408983452, 0.013071895424836602, 0.013265038087733123, 0.013126788602712455, 0.013002364066193853]
    recall_10 = [0.0017624728850325379, 0.0027114967462039045, 0.003321583514099783, 0.003931670281995662, 0.0046773318872017355, 0.005626355748373102, 0.006304229934924078, 0.006982104121475054, 0.007863340563991324, 0.008609002169197397, 0.008947939262472886, 0.010303687635574838, 0.010913774403470716, 0.012269522776572669, 0.01274403470715835, 0.013693058568329718, 0.014303145336225596, 0.014913232104121476]
    precision_15 = [0.00966183574879227, 0.010265700483091788, 0.009178743961352657, 0.00966183574879227, 0.009316770186335404, 0.010567632850241546, 0.011272141706924315, 0.011352657004830917, 0.011418533157663592, 0.011876006441223833, 0.011519881085098476, 0.012077294685990338, 0.012399355877616747, 0.012983091787439614, 0.012929809605001421, 0.013150831991411701, 0.013348588863463006, 0.013164251207729469]
    recall_15 = [0.001230138390568939, 0.001742696053305997, 0.00194771911840082, 0.002460276781137878, 0.002767811378780113, 0.0035879036391594054, 0.004305484366991286, 0.004818042029728345, 0.005330599692465402, 0.006048180420297283, 0.006355715017939518, 0.007175807278318811, 0.007893388006150692, 0.008815991799077397, 0.009328549461814455, 0.010046130189646335, 0.010763710917478216, 0.011173757047667862]
    precision_10_new = [0.010638297872340425, 0.012115839243498818, 0.011347517730496455, 0.011623325453112687, 0.01165146909827761, 0.012115839243498818, 0.012083004990806409, 0.012174940898345154, 0.01246507629486353, 0.012509850275807723, 0.012002182214948172, 0.012664640324214792, 0.012687155240346729, 0.013297872340425532, 0.013071895424836602, 0.013199369582348306, 0.013126788602712455, 0.013002364066193853]
    recall_10_new = [0.0019221186018366912, 0.0029187726916779385, 0.003417099736598562, 0.004200185092902399, 0.004912080871360433, 0.005837545383355877, 0.006549441161813911, 0.007332526518117747, 0.00825799103011319, 0.009041076386417029, 0.009397024275646046, 0.010678436676870505, 0.011461522033174344, 0.012814124012244608, 0.013383640635011034, 0.014309105147006479, 0.015021000925464512, 0.015661707126076743]
    plot(x, precision_10, label="precision_10")
    plot(x, recall_10, label= "recall_10")
    plot(x, precision_15, label="precision_15")
    plot(x, recall_15, label="recall_15")
    plot(x, precision_10_new, label="precision_new")
    plot(x, recall_10_new, label="recall_new")
    plot(x, precision_list, label="precision_10_new2")
    plot(x, recall_list, label="recall_10_new2")
    legend(loc='lower right')
    savefig("result.png")

class User(object):
    def __init__(self, user_id, item_rank):
        self.user_id = user_id
        self.item_rank = item_rank

def main():
    # ''' item-based collaborative filtering'''
    logging.basicConfig(filename='cf.log', level=logging.INFO)
    logging.info(time.asctime(time.localtime(time.time())))
    start_time = timeit.default_timer()

    precision_list = []
    recall_list = []
    train_user_list, train_item_list = read_data('trainData_20160501_20160731')
    item_matrix = cosine_similarity(train_user_list, train_item_list)
    test_user_list, _ = read_data('testData_20160801_20160831')
    for n in range(3, 21):
        recommendation_list = top_n(item_matrix, train_user_list, train_item_list, n)
        precision, recall = measure(test_user_list, recommendation_list, train_item_list, 10)
        precision_list.append(precision)
        recall_list.append(recall)
    result = open("result.txt", 'w+')
    print('precision: {0}'.format(precision_list), file=result)
    print('recall: {0}'.format(recall_list), file=result)
    draw(precision_list, recall_list)

    stop_time = timeit.default_timer()
    logging.info('run in {0} seconds.\n'.format(stop_time - start_time))

if __name__ == '__main__':
    main()
