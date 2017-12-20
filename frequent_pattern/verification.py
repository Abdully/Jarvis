import psycopg2
import psycopg2.extras
import collections
import operator
from datetime import datetime, timedelta

def main():
    d = datetime(year=2016, month=1, day=1)
    begin = datetime(year=2016, month=11, day=1)
    bmiddle = datetime(year=2016, month=11, day=30)
    emiddle = datetime(year=2016, month=12, day=1)
    end = datetime(year=2016, month=12, day=31)
    window = timedelta(days=14)
    top_begin = 5
    top_end = 16

    precision = []
    recall = []

    for top in range(top_begin, top_end, 1):
        reco = {}
        with open('output_data_viponly_{}_{}_{}'.format(d.date(), end.date(), window.days), 'r') as f:
            lines = f.readlines()
            for line in lines:
                # print(line)
                cnt = 0
                base_item = []
                for content in line.split():
                    if content == '-1':
                        cnt += 1
                    elif content == '#SUP:':
                        break
                    elif len(line.split()) > 5:
                        if cnt == 0:
                            if content not in base_item:
                                base_item.append(content)
                            if content not in reco:
                                reco[content] = {}
                        elif cnt == 1:
                            for item in base_item:
                                if content not in reco[item].keys():
                                    reco[item][content] = line.split()[-1]
                                elif line.split()[-1] > reco[item][content]:
                                    reco[item][content] = line.split()[-1]

        # for item in reco.keys():
        #     print(item)
        #     print(reco[item])
        #     print('-------')

        connection = psycopg2.connect("dbname='postgres' user='postgres' host='localhost' password='postgres123456'")
        cur = connection.cursor()
        cur.execute("""SELECT DISTINCT uid, vipno, pluno FROM original_transaction
                            WHERE sldat::DATE >= DATE %s AND sldat::DATE <= %s AND vipno NOTNULL;""",
                            (begin, bmiddle))
        transactions = cur.fetchall()

        users = {}
        for transaction in transactions:
            if transaction[2] in reco.keys():
                if transaction[1] not in users.keys():
                    users[transaction[1]] = {}
                if transaction[2] not in users[transaction[1]].keys():
                    users[transaction[1]][transaction[2]] = 1
                else:
                    users[transaction[1]][transaction[2]] += 1

        # for user in users.keys():
        #     print(user)
        #     print(users[user])
        #     print('-----')

        user_items = {}
        user_reco = {}
        for user in users.keys():
            user_items[user] = {}
            user_reco[user] = []
            for item in users[user].keys():
                for reco_item in reco[item]:
                    key = int(users[user][item]) * int(reco[item][reco_item])
                    if reco_item not in user_items[user].keys():
                        user_items[user][reco_item] = key
                    else:
                        user_items[user][reco_item] += key
            user_reco[user] = sorted(user_items[user].items(), reverse=True, key=operator.itemgetter(1))[:top]
        
        # for user in user_reco:
        #     print(user_reco[user])

        cur.execute("""SELECT DISTINCT uid, vipno, pluno FROM original_transaction
                            WHERE sldat::DATE >= DATE %s AND sldat::DATE <= %s AND vipno NOTNULL;""",
                            (emiddle, end))   
        transactions = cur.fetchall()
        
        hit = 0
        pre = 0
        rec = 0
        for transaction in transactions:
            if transaction[1] in user_reco.keys():
                rec += 1
                for tuple in user_reco[transaction[1]]:
                    pre += 1
                    if transaction[2] == tuple[0]:
                        hit += 1
        print('top: {}'.format(top))
        print('hit: {}'.format(hit))
        print('precision: {}'.format(hit/pre))
        print('recall: {}'.format(hit/rec))
        print('--------')

        precision.append(hit/pre)
        recall.append(hit/rec)

    print(precision)
    print(recall)

if __name__ == '__main__':
    main()