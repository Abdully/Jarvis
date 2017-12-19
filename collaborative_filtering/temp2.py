from collaborative_filtering import *

def read_data(month):
    logging.info('begin to read data in {0}.'.format(month))
    item_list = []
    item_category_list = []
    item_name_list = []
    brand_name_list = []
    item_unit_list = []
    with open('data/{0}.csv'.format(month)) as csv_file:
        reader = csv.reader(csv_file)
        for row in reader:
            item_id = row[0]
            # item_category = row[12][:4]
            item_name = row[1]
            brand_name = row[5]
            item_unit = row[3]
            # count = round(float(row[16]))
            item_exist = False
            item_unit_list.append(item_unit)
            for item in item_list:
                if item_id == item:
                    item_exist = True
            if not item_exist:
                item_list.append(item_id)
                # item_category_list.append(item_category)
                item_name_list.append(item_name)
                if brand_name is not '':
                    brand_name_list.append(brand_name)
    logging.info('complete loading data in {0}.'.format(month))
    return (item_list, item_category_list, item_name_list, brand_name_list, item_unit_list)

def jieba_(item_name_list, month):
    jieba.load_userdict('dict/{0}.txt'.format(month))
    new_name_list = []
    for item_name in item_name_list:
        seg_item_name = pseg.cut(item_name)
        str = ""
        for word, flag in seg_item_name:
            str += word + ' ' + flag + '  '
        new_name_list.append(str)
        print(str)
    return new_name_list

def main():
    train_month = 'pluno_20160201_20160831'
    train_item_list, item_category_list, item_name_list, brand_name_list, item_unit_list = read_data(train_month)
    customize_dict(brand_name_list, train_month)
    new_name_list = jieba_(item_name_list, train_month)

if __name__ == '__main__':
    main()