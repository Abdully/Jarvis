import re
import pickle
import psycopg2
from pathlib import Path
from operator import itemgetter


def main():
    connection = psycopg2.connect("dbname='postgres' user='postgres' host='localhost' password='postgres123456'")
    cur = connection.cursor()
    dump_filename = 'code_name.pkl'
    code_name = {}
    if Path(dump_filename).exists():
        with open(dump_filename, 'rb') as dump_file:
            code_name = pickle.load(dump_file)
    else:
        cur.execute("""SELECT DISTINCT pluno, pluname FROM original_transaction""")
        no_name = cur.fetchall()
        for no, name in no_name:
            code_name[no] = name
        with open(dump_filename, 'wb') as dump_file:
            pickle.dump(code_name, dump_file)

    lines = []
    with open('output.txt', 'r') as f:
        for line in f:
            (line_content, support) = re.findall(r'(.+) #SUP: ([0-9]+)', line)[0]
            lines.append((line_content, int(support)))
    lines = sorted(lines, key=itemgetter(1))

    for line_content, support in lines:
        line_content = line_content.split()
        for each_no in line_content:
            if each_no != '-1':
                print(code_name[each_no], end=' ')
            else:
                print(each_no, end=' ')
        print("#SUP:", support)


if __name__ == '__main__':
    main()
