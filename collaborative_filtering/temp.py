from collaborative_filtering import *

def main():
    
    n_begin = 20
    n_end = 21
    n_step = 5
    gaussian_sigma_list = [2, 5, 10, 20, 50, 100]
    train_month = 'trainData_07'
    test_month = 'testData_08_07'

    logging.basicConfig(filename='cf.log', level=logging.INFO)
    logging.info(time.asctime(time.localtime(time.time())))
    start_time = timeit.default_timer()

    precision_list = []
    recall_list = []
    train_user_list, train_item_list, item_category_list, item_name_list, brand_name_list, item_unit_list = read_data(train_month)
    
    customize_dict(brand_name_list, train_month)

    new_name_list = jieba_(item_name_list, train_month)
    for gaussian_sigma in gaussian_sigma_list:
        sig = 0
        item_matrix = cosine_similarity(train_user_list, train_item_list, item_category_list, new_name_list, gaussian_sigma)
        test_user_list, _, _, _, _, _ = read_data(test_month)
        for n in range(n_begin, n_end, n_step):
            recommendation_list = top_n(item_matrix, train_user_list, train_item_list, n)
            output(recommendation_list, train_item_list)
            precision, recall = measure(test_user_list, recommendation_list, train_item_list)
            print(recall)
            print('----')
            if recall > 0.047:
                sig = 1
                print(gaussian_sigma)
                precision_list.append(precision)
                recall_list.append(recall)
        result = open("result/result.txt", 'w')
        print('precision = {0}'.format(precision_list), file=result)
        print('recall = {0}'.format(recall_list), file=result)
        if sig == 1:
            break

    stop_time = timeit.default_timer()
    logging.info('run in {0} seconds.\n'.format(stop_time - start_time))

    # draw(n_begin, n_end, n_step)

    notify()

if __name__ == '__main__':
    main()