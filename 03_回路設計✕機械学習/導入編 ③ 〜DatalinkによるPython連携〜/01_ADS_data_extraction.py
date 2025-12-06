#############################################
##########  ADS EDA -> output.csv  ##########
#############################################

# ADS EDA にコマンドを記載。シミュレーション実行すると
# data/python/ADS2Pyth_oneway.d にデータが保存される。
# そのデータを csv として出力するためのファイル。

import ads
import pandas as pd

# EDAデータ取得
S21=ads.get

# S21データ抽出
df = pd.DataFrame(S21(1)[0])

# csv出力(任意のファイル名をつける)
df.to_csv("output.csv")

# シングルスイープの場合
# (例) C001.csv, L001.csv

# マルチスイープの場合
# (例) gain, fpeak, img, himg