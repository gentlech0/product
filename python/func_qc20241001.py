# 【ライブラリ】
# flet------------------------
import flet as ft
# パワー計(N1913A)-------------
import pyvisa
import time
from datetime import datetime
# 無線機制御
import serial
import serial.tools.list_ports
import io

import sys
sys.path.append("sub")
# 関数ファイル
# import func_qc

#---------------------------------------------
# 機密のためすべてデタラメな値にしています。
# このままでは動きません
#---------------------------------------------

# PTT共通関数
def PC_cmd(cmd,param):
    # 共通データ
    BData = [0] * 13
    # プリアンブル
    BData[0] = 0xAB
    BData[1] = 0xCD
    BData[2] = 0xEF
    BData[3] = 0xAB
    BData[4] = 0xCD
    BData[5] = 0xEF
    BData[6] = 0xAB
    BData[7] = 0xCD
    BData[8] = 0xEF
    # 終止文字
    BData[12] = 0xAB
    # コマンド/データ----------------------
    if(cmd=='ON'): # PTT ON
        BData[9] = 0xAB
        BData[10] = 0xCD
        BData[11] = 0xEF
    elif(cmd=='OFF'): # PTT OFF
        BData[9] = 0xAB
        BData[10] = 0xCD
        BData[11] = 0xEF
    elif(cmd=='ADJSET1'):
        BData[9] = 0xAB
        BData[10] = 0xCD
        BData[11] = 0xEF
    elif(cmd=='ADJSET2'):
        BData[9] = 0xAB #
        if(param == 'null'): # アドレス指定しない場合(test)
            BData[10] = 0xCD
            BData[11] = 0xEF
        else: # アドレスを指定した場合
            BData[10] = param[0]
            BData[11] = param[1]
    elif(cmd=='ADJREAD'):
        BData[9] = 0xAB
        BData[10] = 0xCD
        BData[11] = 0xEF
    elif(cmd=='ADJWRITE'):
        BData[9] = 0xAB # Writeの決まり
        if(param == 'null'): # 値を指定しない場合(test)
            BData[10] = 0xCD
            BData[11] = 0xEF
        else: # 書き込み値を指定した場合
            BData[10] = param[1]
            BData[11] = param[0]
    # 周波数変更
    elif(cmd=='FREQ'):
        BData = [0] * 11
        # プリアンブル
        BData[0] = 0xAB
        BData[1] = 0xCD
        BData[2] = 0xEF
        BData[3] = 0xAB
        BData[4] = 0xCD
        # [136.025MHz]
        if(param == 'fL'):
            BData[5] = 0xAB
            BData[6] = 0xCD
            BData[7] = 0xEF
            BData[8] = 0xAB
            BData[9] = 0xCD
            BData[10] = 0xEF
        # [155.025MHz]
        if(param == 'fM'):
            BData[5] = 0xAB
            BData[6] = 0xCD
            BData[7] = 0xEF
            BData[8] = 0xAB
            BData[9] = 0xCD
            BData[10] = 0xEF
        # [173.975MHz]
        if(param == 'fH'):
            BData[5] = 0xAB
            BData[6] = 0xCD
            BData[7] = 0xEF
            BData[8] = 0xAB
            BData[9] = 0xCD
            BData[10] = 0xEF
    return BData





