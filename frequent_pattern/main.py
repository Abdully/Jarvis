import pickle
import psycopg2
import psycopg2.extras
from pathlib import Path
from datetime import datetime, timedelta
from operator import itemgetter
from itertools import groupby
from collections import defaultdict


def writeout(file, sequence):
    for transaction in sequence:
        transaction = [str(i) for i in transaction]
        file.writelines([' '.join(transaction), ' -1 '])
    file.writelines(['-2', '\n'])


def main():
    connection = psycopg2.connect("dbname='postgres' user='postgres' host='localhost' password='postgres123456'")
    cur = connection.cursor()
    d = datetime(year=2016, month=1, day=1)
    end = datetime(year=2016, month=6, day=30)
    window = timedelta(days=90)

    with open('window_transaction_data_viponly_{}_{}_{}.txt'.format(d.date(), end.date(), window.days), 'w') as f:
        dump_filename = 'dump_viponly_{}_{}.pkl'.format(d.date(), end.date())
        groups = defaultdict(list)
        if Path(dump_filename).exists():
            with open(dump_filename, 'rb') as dump_file:
                groups = pickle.load(dump_file)
        else:
            cur.execute("""SELECT DISTINCT uid, pluno, vipno FROM original_transaction
                             WHERE uid IN
                               (SELECT DISTINCT uid FROM original_transaction
                                  WHERE sldat::DATE >= DATE %s AND sldat::DATE <= DATE %s
                                    AND vipno IS NOT NULL)
                                AND pluno <> '30380001' AND pluno <> '30380002' AND pluno <> '30380003'""",
                        (d, end))
            transactions = cur.fetchall()
            grouped = groupby(transactions, key=itemgetter(2))
            for _, g in grouped:
                group = list(g)
                for i in group:
                    groups[i[2]].append((i[0], i[1]))
            with open(dump_filename, 'wb') as dump_file:
                pickle.dump(groups, dump_file)

        user_transactions = defaultdict(dict)
        for k, v in groups.items():
            user_transaction = groups[k]
            transaction_grouped = groupby(user_transaction, key=itemgetter(0))
            user_transaction_group = defaultdict(list)
            for _, g in transaction_grouped:
                group = list(g)
                for i in group:
                    user_transaction_group[i[0]].append(i[1])
            user_transactions[k].update(user_transaction_group)

        while d + window <= end:
            cur.execute("""SELECT DISTINCT vipno, uid FROM original_transaction
                             WHERE sldat::DATE >= DATE %s AND sldat::DATE < DATE %s
                               AND vipno IS NOT NULL
                               AND pluno <> '30380001' AND pluno <> '30380002' AND pluno <> '30380003'""",
                        (d, d + window))
            vip_transaction_ids = cur.fetchall()
            vip_transaction_id_grouped = groupby(vip_transaction_ids, key=itemgetter(0))
            for vip, g in vip_transaction_id_grouped:
                transaction_ids = list(g)
                window_transactions = [sorted(set(user_transactions[vip][id[1]])) for id in transaction_ids]
                print(d, vip)
                writeout(f, window_transactions)
            d += timedelta(days=1)


if __name__ == '__main__':
    main()
