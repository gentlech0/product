import ads
#S21=ads.get_dataset_list()
S21=ads.get
#print(type(S21))
print(len(S21(1)[0]))
print(S21(1)[0][352])

import pandas as pd

df = pd.DataFrame(S21(1)[0])

print(df)

df.to_csv("himg_fH.csv")