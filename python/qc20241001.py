# 【ライブラリ】-------------------------------------
import flet as ft # UIであるfletの使用
import pyvisa # 測定器制御
import time
from datetime import datetime
import serial # シリアル通信
import serial.tools.list_ports
import io
import sys
import time
#----------------------------------------------------
sys.path.append("sub")
from func_qc20241001 import PC_cmd
#----------------------------------------------------
# 【入力パラメータ】
baud_ = 9600  # ボーレート
tout_ = 1     # タイムアウト
#----------------------------------------------------
# 【出力パラメータ】
# 初期パワー調整値
ADJ_POW_init = [0]*3
# 周波数セット
f_now = [0]*3
# 一時値
tmp_val = 0

#---------------------------------------------
# 機密のためすべてデタラメな値にしています。
# このままでは動きません
#---------------------------------------------

# パワー格納
PW_fl = [0]*25
PW_fm = [0]*25
PW_fh = [0]*25
#----------------------------------------------------
# 【メイン処理】
def main(page: ft.Page):

    page.title = "DA値 VS 送信Power特性アプリ"  # タイトル
    page.vertical_alignment = ft.MainAxisAlignment.CENTER # 縦方向アライン

    # 【フォームのテキスト】
    # COMポート番号
    txt_COM = ft.TextField(value="8", text_align=ft.TextAlign.RIGHT, width=60) # COMポート
    COM_ = "COM" + str(txt_COM.value)

    # パワー計IPアドレス
    txt_IP = ft.TextField(value="192.168.62.117", text_align=ft.TextAlign.RIGHT, width=150)
    IP_address = 'TCPIP::' + str(txt_IP.value)
    
    txt_num = ft.TextField(value="0", text_align=ft.TextAlign.RIGHT, width=100) # 一時的に使用する

    # パワー計(N1913A)で読み取り
    def READ_PW():
        IP_address = 'TCPIP::' + str(txt_IP.value) # IPアドレス
        rm = pyvisa.ResourceManager()              # インスタンス化
        inst = rm.open_resource(IP_address)        # IP指定して接続
        inst.write('FETC?') # 値を取得する             
        tmp_val = inst.read()  
        return tmp_val

    # COMポート接続
    # def COM_connect(e):
    #     ser = serial.Serial(COM_, baud_, timeout=tout_)
    #     print("接続OK")
    #     return None
    
    # COMポート切断
    # def COM_disconnect(e):
    #     ser = serial.Serial(COM_, baud_, timeout=tout_)
    #     print("切断OK")
    #     ser.close()
    #     return None

    def PTT_ON(): # 送信
        ser = serial.Serial(COM_, baud_, timeout=tout_)
        BData = PC_cmd('ON','null')
        BData = bytearray(BData) # バイナリデータ変換
        ser.write(BData)         # 書き込み
        ser.close()
        return None

    def PTT_OFF(): # 送信停止
        ser = serial.Serial(COM_, baud_, timeout=tout_)
        BData = PC_cmd('OFF','null')
        BData = bytearray(BData) # バイナリデータ変換
        ser.write(BData)         # 書き込み
        ser.close()
        return None
        
    def ADJ_READ(addr): # 調整値読取り
        ser = serial.Serial(COM_, baud_, timeout=tout_)
        BData = PC_cmd('ADJSET1','null')      # 上位ビット指定
        BData = bytearray(BData)              # バイナリデータ変換
        ser.write(BData)                      # 書き込み
        
        BData = PC_cmd('ADJSET2',addr)        # 下位ビット指定
        # BData = PC_cmd('ADJSET2','null')    # 下位ビット指定
        BData = bytearray(BData)              # バイナリデータ変換
        ser.write(BData)                      # 書き込み
        
        BData = PC_cmd('ADJREAD','null')      # 調整値指定
        BData = bytearray(BData)              # バイナリデータ変換
        ser.write(BData)                      # 書き込み
        
        line = ser.readline()                 # 返り値取得
        line = chr(line[10]) + chr(line[11])  # 結合して表示
        ser.close()
        return line

    def ADJ_WRITE(addr, val): # 調整値書き込み
        ser = serial.Serial(COM_, baud_, timeout=tout_)
        BData = PC_cmd('ADJSET1','null')      # 上位ビット指定
        BData = bytearray(BData)              # バイナリデータ変換
        ser.write(BData)                      # 書き込み
        
        BData = PC_cmd('ADJSET2',addr)        # 下位ビット指定
        # BData = PC_cmd('ADJSET2','null')    # 下位ビット指定
        BData = bytearray(BData)              # バイナリデータ変換
        ser.write(BData)                      # 書き込み

        BData = PC_cmd('ADJWRITE',val)        # アドレスを指定した場合
        # BData = PC_cmd('ADJWRITE','null')   # アドレス未指定
        BData = bytearray(BData)              # バイナリデータ変換
        ser.write(BData)                      # 調整値書き込み
        ser.close()
        return None

    def ADJ_FREQ(freq): # 周波数変更
        ser = serial.Serial(COM_, baud_, timeout=tout_)
        BData = PC_cmd('FREQ',freq)
        BData = bytearray(BData) # バイナリデータ変換
        ser.write(BData)         # 書き込み
        ser.close()
        return None

    def DECtoHEX(val): # 10進数->16進
        val_ADJ = [0] * 2
        val_ADJ[1] = val // 16
        val_ADJ[0] = val % 16

        # # 10の位
        if(val_ADJ[1]<10):
            val_ADJ[1] = val_ADJ[1] + 48 # "0"=48を足す
        else:
            val_ADJ[1] = val_ADJ[1] + 55 # "A"=65を足す足す

        # # 1の位
        if(val_ADJ[0]<10):
            val_ADJ[0] = val_ADJ[0] + 48 # "0"=48を足す
        else:
            val_ADJ[0] = val_ADJ[0] + 55 # "A"=65を足す

        return val_ADJ


    # 調整値を5刻みに変更しパワーを測定する
    def MEASUREMENT(e):

        page.update()

        # パワー(f1,f3,f5)のアドレス("24","26","28")
        addr_pow = [[0xAB, 0xAB],[0xAB, 0xCD],[0xAB, 0xEF]]

        # パワー(f1-f5)の調整値5ステップ
        val_pow = []
        for i in range(0,256,5):
            val_pow.append(i)

        # 測定前の調整値初期値取得--------------------------------------------
        # for i in range(3):
        #     ADJ_POW_init[i] = ADJ_READ(addr_pow[i])

        # # グローバル変数の調整値に出力
        # print(ADJ_POW_init)
        #---------------------------------------------------------------

        # 3. 調整値書き込み----------------------------------------------
        k = 0
        for j in ['fL','fM','fH']:
            ADJ_FREQ(j)          # 周波数変更
            k = k + 1
            for i in val_pow:
                print(i)
                ADJ_WRITE(addr_pow[k-1], DECtoHEX(i)) # 調整値書き込み
                time.sleep(0.3)
                print(ADJ_READ(addr_pow[k-1]))
                time.sleep(0.3)
                PTT_ON()                # 送信
                time.sleep(2)
                print(READ_PW()) # パワー値読取り
                PTT_OFF()               # 送信停止
                time.sleep(1)

        print("測定完了!")
        page.update()
        return None
    
    # メインページ
    page.add(
        ft.Text("【入力パラメータ】", size=24),
        ft.Row(
            [ft.Text("COM番号", size=24),txt_COM,
            ft.Text("IPアドレス", size=24),txt_IP,],
            alignment=ft.alignment.center,
        ),

        ft.Row([
            # [ft.FilledButton(text="パワー値取得",on_click=READ_PW),
            # ft.FilledButton(text="COM接続",on_click=COM_connect),
            # ft.FilledButton(text="COM切断",on_click=COM_disconnect),
            # ft.FilledButton(text="送信開始",on_click=PTT_ON),
            # ft.FilledButton(text="送信停止",on_click=PTT_OFF),
            # ft.FilledButton(text="調整読取",on_click=ADJ_READ),
            # ft.FilledButton(text="調整書込",on_click=ADJ_WRITE),
            ft.FilledButton(text="測定開始",on_click=MEASUREMENT)],
        ),
    )

ft.app(target=main)