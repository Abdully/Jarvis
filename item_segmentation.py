import csv
import time
import jieba
import timeit
import logging

def read_data(month):
    logging.info('begin to read data in {0}.'.format(month))
    bcd_list = []
    pluname_list = []
    with open('data/data_time_split/{0}.csv'.format(month)) as csv_file:
        reader = csv.reader(csv_file, delimiter='\t')
        for row in reader:
            bcd = row[8]
            pluname = row[9]
            spec = row[10]
            pkunit = row[11]
            bndname = row[15]
            bcd_exist = False
            for item in bcd_list:
                if item == bcd:
                    bcd_exist = True
            if not bcd_exist:
                bcd_list.append(bcd)
                pluname_list.append(pluname)
    logging.info('complete loading data in {0}.'.format(month))
    return (bcd_list, pluname_list)

def main():
    logging.basicConfig(filename='cf.log', level=logging.INFO)
    logging.info(time.asctime(time.localtime(time.time())))
    start_time = timeit.default_timer()

    # jieba.enable_parallel()

    _, pluname_list = read_data('2016-07-01_2016-07-31')
    for pluname in pluname_list:
        seg_pluname = jieba.cut(pluname, cut_all=False)
        print("/ ".join(seg_pluname))

    stop_time = timeit.default_timer()
    logging.info('run in {0} seconds.\n'.format(stop_time - start_time))

if __name__ == '__main__':
    main()