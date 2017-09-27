import csv

class Data(object):
    """shopping data.

    Args:
        user_id: user id.
        item_id: item id.
        count: count of user purchases.
        qty: total number of item.
        amt: total sum up.
    """

    def __init__(self, month):
        self.user_id = []
        self.item_id = []
        self.count = []
        self.qty = []
        self.amt = []
        with open('data/{0}.csv'.format(month)) as csv_file:
            reader = csv.reader(csv_file)
            for row in reader:
                self.user_id.append(row[0])
                self.item_id.append(row[1])
                self.count.append(row[2])
                self.qty.append(row[3])
                self.amt.append(row[4])

    def euclidean_distance(self):
        pass

    def cosine_similarity(self, parameter_list):
        pass

    def k_neighborhoods(self):
        pass

    def test(self):
        pass

def main():
    """item-based collaborative filtering
    """

    training_data = Data('july')


if __name__ == '__main__':
    main()
