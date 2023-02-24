import pandas as pd
import numpy as np
a = {"b" : [2,3,4,5,6],
    "c" : [33,55,66,77,88]
    }
a = pd.DataFrame(a)
print(a)
a = a.drop(["b"], axis = 1)
print(a)