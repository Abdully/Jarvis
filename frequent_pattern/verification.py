import collections
import psycopg2
import psycopg2.extras
from datetime import datetime, timedelta

def main():
    d = datetime(year=2016, month=1, day=1)
    begin = datetime(year=2016, month=11, day=1)
    middle = datetime(year=2016, month=12, day=1)
    end = datetime(year=2016, month=12, day=31)
    window = timedelta(days=14)
    top = 10

    reco = {}
    with open('output_data_viponly_{}_{}_{}'.format(d.date(), end.date(), window.days), 'r') as f:
        lines = f.readlines()
        for line in lines:
            # print(line)
            cnt = 0
            base_items = []
            for content in line.split():
                if content == '-1':
                    cnt += 1
                elif content == '#SUP:':
                    break
                else:
                    if cnt == 0:
                        if content not in base_items:
                            base_items.append(content)
                        if content not in reco:
                            reco[content] = {}                            
                    else:
                        # print('---')
                        # print(line)
                        # print(content)
                        # print(base_items)
                        for item in base_items:
                            if line.split()[-1] not in reco[item].keys():
                                reco[item][line.split()[-1]] = []
                            if content not in reco[item][line.split()[-1]]:
                                reco[item][line.split()[-1]] = [content]

    for item in list(reco):
        if reco[item] == {}:
            del(reco[item])

    reco2 = {}
    for item in reco.keys():
        reco2[item] = {}
        for grade in sorted(reco[item].keys(), reverse=True)[0:top]:
            reco2[item][grade] = reco[item][grade]

    # for item in reco.keys():
    #     print(reco[item])

    connection = psycopg2.connect("dbname='postgres' user='postgres' host='localhost' password='postgres123456'")
    cur = connection.cursor()
    cur.execute("""SELECT uid, pluno FROM original_transaction
                      WHERE sldat::DATE >= DATE %s AND sldat::DATE <= %s""",
                 (begin, middle))
    transactions = cur.fetchall()

    users = {}
    for transaction in transactions:
        if transaction[1] in reco.keys():
            if transaction[0] not in users.keys():
                users[transaction[0]] = {}
            for grade, content in reco[transaction[1]].items():
                users[transaction[0]][grade] = content

    users2 = {}
    for user in users.keys():
        users2[user] = {}
        for grade in sorted(users[user].keys(), reverse=True)[0:top]:
            users2[user][grade] = users[user][grade]

    cur.execute("""SELECT uid, pluno FROM original_transaction
                      WHERE sldat::DATE >= DATE %s AND sldat::DATE <= %s""",
                 (middle, end))
    verifications = cur.fetchall()
    hit = 0
    precisiontotal = 0
    recalltotal = 0
    for verification in verifications:
        if verification[0] in users2.keys():
            for samesup in users2[verification[0]].values():
                if verification[1] in samesup:
                    hit += 1
                precisiontotal += 1
            recalltotal += 1
    print('hit: {}'.format(hit))
    print('precision total: {}'.format(precisiontotal))
    print('recall total: {}'.format(recalltotal))
    print('precision: {}'.format(hit/precisiontotal))
    print('recall: {}'.format(hit/recalltotal))

if __name__ == '__main__':
    main()