import csv
import heapq
from numpy import *

def read_data(month):
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
    return (user_list, item_list)

def cosine_similarity(user_list, item_list):
    item_len = len(item_list)
    temp_item_matrix = mat(zeros((item_len, item_len)))
    item_matrix = mat(zeros((item_len, item_len)))
    for user in user_list:
        for item_1 in user.item_rank:
            for item_2 in user.item_rank:
                if item_1 != item_2:
                    temp_item_matrix[item_list.index(item_1), item_list.index(item_2)] += 1

    for i in range(item_len):
        sum_column = sum(temp_item_matrix, axis=1)[i, 0]
        for j in range(item_len):
            sum_row = sum(temp_item_matrix, axis=0)[0, j]
            times = sum_column * sum_row
            if times != 0:
                item_matrix[i, j] = temp_item_matrix[i, j] / (sqrt(times))
    return item_matrix

def top_n(item_matrix, user_list, item_list, n=3):
    topn_list = [[0] * n] * item_matrix.shape[0]
    recommendation_list = {}
    for i in range(item_matrix.shape[0]):
        topn_list[i] = heapq.nlargest(n, range(len(item_matrix.tolist()[i])), item_matrix.tolist()[i].__getitem__)
    for user in user_list:
        topn = []
        for item in user.item_rank:
            for reco_item in topn_list[item_list.index(item)]:
                topn.append((item_list.index(item), reco_item))
        topn.sort(key=lambda tup: item_matrix[tup[0], tup[1]], reverse=True)
        recommendation_list[user.user_id] = topn[:n]
    return recommendation_list

def measure(test_user_list, recommendation_list, item_list):
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
    return(precision, recall)

class User(object):
    def __init__(self, user_id, item_rank):
        self.user_id = user_id
        self.item_rank = item_rank

def main():
    ''' item-based collaborative filtering'''

    train_user_list, train_item_list = read_data('july')
    item_matrix = cosine_similarity(train_user_list, train_item_list)
    recommendation_list = top_n(item_matrix, train_user_list, train_item_list)
    test_user_list, _ = read_data('aug')
    precision, recall = measure(test_user_list, recommendation_list, train_item_list)
    print('precision: {0}'.format(precision))
    print('recall: {0}'.format(recall))

if __name__ == '__main__':
    main()
