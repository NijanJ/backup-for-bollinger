import pandas as pd
import numpy as np
technologies = ({
     'Courses':["Spark","Java","Hadoop","Python","pandas"],
     'Fee' :[20000,np.nan,26000,np.nan,24000],
     'Duration':['30days',np.nan,'35days','40days',np.nan],
     'Discount':[1000,np.nan,2500,2100,np.nan]
               })
df = pd.DataFrame(technologies)

value = df["Discount"][0:3].count()
c = [1, 4, 3, 2,np.nan, 7, np.nan, 8, np.nan,6]
c = sorted(list(set(c)))
print(c)