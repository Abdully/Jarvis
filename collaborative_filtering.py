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
    item_matrix = mat(zeros((item_len, item_len)))
    for user in user_list:
        for item_1 in user.item_rank:
            for item_2 in user.item_rank:
                if item_1 != item_2:
                    item_matrix[item_list.index(item_1), item_list.index(item_2)] += 1

    for i in range(item_len):
        sum_column = sum(item_matrix, axis=1)[i, 0]
        for j in range(item_len):
            sum_row = sum(item_matrix, axis=0)[0, j]
            times = sum_column * sum_row
            if times != 0:
                item_matrix[i, j] = item_matrix[i, j] / (sqrt(times))
    return item_matrix

def top_n(item_matrix, user_list, item_list, n=3):
    topn_list = [[0] * n] * item_matrix.shape[0]
    recommendation_list = []
    for i in range(item_matrix.shape[0]):
        topn_list[i] = heapq.nlargest(n, range(len(item_matrix.tolist()[i])), item_matrix.tolist()[i].__getitem__)
    for user in user_list:
        topn = []
        for item in user.item_rank:
            topn.append(topn_list[item_list.index(item)])
            # TODO
        recommendation_list.append({user.user_id: topn})
    return recommendation_list

def measure(test_user_list, recommendation_list):
    # TODO
    true_positives = 0
    for test_item in test_user_list:
        for reco_item in recommendation_list:
            if test_item == reco_item:
                true_positives += 1
    false_positives = len(recommendation_list) - true_positives
    false_negatives = len(test_user_list) - true_positives

    precision = true_positives / (len(recommendation_list))
    recall = true_positives / len(test_user_list)
    return(precision, recall)

class User(object):
    def __init__(self, user_id, item_rank):
        self.user_id = user_id
        self.item_rank = item_rank

def main():
    ''' item-based collaborative filtering'''

    train_user_list, train_item_list = read_data('train')
    item_matrix = cosine_similarity(train_user_list, train_item_list)
    recommendation_list = top_n(item_matrix, train_user_list, train_item_list)
    print(recommendation_list)
    
if __name__ == '__main__':
    main()
