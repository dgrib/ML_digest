# from pymongo import MongoClient
#
# client = MongoClient('localhost')
# db = client['ml_digest']
# ml_collection = db.ml_collection
# simple_collection = db.simple_collection
#
# for i in ml_collection.find():
#     one_dict = dict()
#     one_dict['model'] = i['model']
#     one_dict['pk'] = i['pk']
#     for fields_key, fields_value in i['fields'].items():
#         one_dict[fields_key] = fields_value
#
#     simple_collection.insert_one(one_dict)

import numpy as np

A = [[1,2,3], [4,5,6]]
B = [[7,8], [9,10], [11,12]]
C = [[7,8], [9,10], [11,12], [13, 14]]


def matrix_mul(a, b):
    if len(a[0]) != len(b):
        return "Incorrect matrix size for multiplying"
    else:
        c = [[0 for _0 in range(len(b[0]))] for _1 in range(len(a))]
        for ic1 in range(len(c)):
            ib2 = 0
            for i1 in range(len(b[0])):
                counter = 0
                for i2 in range(len(a[0])):
                    counter += a[ic1][i2] * b[i2][ib2]
                c[ic1][i1] = counter
                ib2 += 1
        return c


print(matrix_mul(C, A))

