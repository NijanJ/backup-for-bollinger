import pandas as pd
import numpy as np

a = [1,2,2,3,6,3,5,2,6,8,9]
b = [6,7,8,9,10]

c=(a,b)
print(c)


def Sort_and_Remove_Duplicate(x):
    return sorted(set(x))

def Same_Size_List(y):
    Minimum_Value_List = []
    Same_Size_Array =[]
    for i in range(len(y)):
        Array_Len = np.size(y[i])
        Minimum_Value_List.append(Array_Len)
    Minimum_Value = min(Minimum_Value_List)
    print(Minimum_Value)
    for i in range(len(y)):
        Array_Resize = y[i][:Minimum_Value]
        Same_Size_Array.append(Array_Resize)
    return Same_Size_Array
 
e = []
# # print(c[0])

# Same_Size_List(c)
for i in range(len(c)):
    d = Sort_and_Remove_Duplicate(c[i])
    e.append(d)
print(e)

g=[]
for i in range(len(e)):
    f = Same_Size_List(e)
    g.append(f)

print(g[0])

# nested_list = [[[1, 2, 3, 5, 6], [6, 7, 8, 9, 10]], [[1, 2, 3, 5, 6], [6, 7, 8, 9, 10]]]

# first_list = nested_list[0]
# print(first_list)