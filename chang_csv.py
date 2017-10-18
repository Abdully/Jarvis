import csv

with open("data/testData_20160801_20160831_raw.csv") as f, open("data/testData_20160801_20160831.csv", 'w') as out:
    r = csv.reader(f, delimiter='\t')
    w = csv.writer(out, delimiter=',')
    for l in r:
        w.writerow(l)
