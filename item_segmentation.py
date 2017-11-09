import csv
import time
import jieba
import timeit
import thulac
import logging
import Levenshtein
import jieba.analyse
import jieba.posseg as pseg

def read_data(month):
    logging.info('begin to read data in {0}.'.format(month))
    item_list = []
    pluname_list = []
    item_dptno = {}
    with open('data/{0}.csv'.format(month)) as csv_file:
        reader = csv.reader(csv_file)
        for row in reader:
            item_id = row[7]
            bcd = row[8]
            pluname = row[9]
            spec = row[10]
            pkunit = row[11]
            dptno = row[12][0:4]
            dptname = row[13]
            bndname = row[15]
            item_exist = False
            for item in item_list:
                if item == item_id:
                    item_exist = True
            if not item_exist:
                item_dptno[item_id] = dptno
                item_list.append(item_id)
                pluname_list.append(pluname)
    logging.info('complete loading data in {0}.'.format(month))
    return (item_list, pluname_list, item_dptno)

def levenshtein_distabce(item1, item2):
    return Levenshtein.distance(item1, item2)

def jieba_(pluname_list):
    for pluname in pluname_list:
        # seg_pluname = jieba.analyse.textrank(pluname, topK=20, withWeight=False, allowPOS=('ns', 'n', 'vn', 'v', 'nr', 'nz', 'i', 'nz', 'a', 'nt'))
        # print(seg_pluname)
        # print("/ ".join(seg_pluname))
        list = ['ns', 'n', 'vn', 'v', 'nr', 'nz', 'i', 'nz', 'a', 'nt']
        seg_pluname = pseg.cut(pluname)
        str = ""
        for word, flag in seg_pluname:
            if flag in list:
                str += word
                # print("".join(word), end='')
        print(str)

def thulac_(pluname_list):
    thu = thulac.thulac(seg_only=True)
    for pluname in pluname_list:
        print(thu.cut(pluname, text=True))


def main():
    logging.basicConfig(filename='cf.log', level=logging.INFO)
    logging.info(time.asctime(time.localtime(time.time())))
    start_time = timeit.default_timer()

    item_list, pluname_list, item_dptno = read_data('train_test_set/trainData_07T')
    
    # jieba.enable_parallel()
    jieba_(pluname_list)
    print(levenshtein_distabce("1", "21"))
    
    # thulac_(pluname_list)

    stop_time = timeit.default_timer()
    logging.info('run in {0} seconds.\n'.format(stop_time - start_time))

if __name__ == '__main__':
    main()