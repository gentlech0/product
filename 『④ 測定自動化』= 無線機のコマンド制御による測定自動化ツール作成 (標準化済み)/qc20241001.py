# 【ライブラリ】-------------------------------------
import flet as ft # UIであるfletの使用
import pyvisa     # 測定器制御
import time
import datetime
from datetime import datetime
import serial     
import serial.tools.list_ports # シリアル通信
import io
import sys
import time
import csv
import pprint
#----------------------------------------------------
sys.path.append("sub")
from func_qc20241001 import PC_cmd
#----------------------------------------------------
# 【入力パラメータ】
baud_ = 9600  # ボーレート
tout_ = 1     # タイムアウト
#----------------------------------------------------
# 【出力パラメータ】
# 出力パワーDA値
DA_value = [[0 for j in range(2)] for i in range(52)] 
ADJ_POW_init = 0
#----------------------------------------------------

#---------------------------------------------
# 機密のためすべてデタラメな値にしています。
# このままでは動きません
#---------------------------------------------

# 【メイン処理】
def main(page: ft.Page):

    page.title = "DA値 VS 送信Power特性アプリ"  # タイトル
    page.window_width = 600
    page.window_height = 1000
    # page.vertical_alignment = ft.MainAxisAlignment.CENTER # 縦方向アライン

    # 【フォームのテキスト】
    # COMポート番号
    txt_COM = ft.TextField(value="7",text_size=18,text_align=ft.TextAlign.RIGHT, width=60)
    # COMポート
    COM_ = "COM" + str(txt_COM.value)

    # パワー計IPアドレス
    txt_IP = ft.TextField(value="192.168.62.118",text_size=18,text_align=ft.TextAlign.RIGHT, width=180)
    IP_address = 'TCPIP::' + str(txt_IP.value)

    # パワー値アドレス
    txt_pow_adrr = ft.TextField(value="24",text_size=18,text_align=ft.TextAlign.RIGHT, width=80)
    POW_addr = str(txt_pow_adrr.value)

    # パワー値
    txt_pow_now = ft.TextField(value="0",text_size=18,text_align=ft.TextAlign.RIGHT, width=80)
    POW_now = str(txt_pow_now.value)

    # ボーレート
    txt_baud = ft.TextField(value="9600",text_size=18,text_align=ft.TextAlign.RIGHT, width=80)
    baud_ = int(txt_baud.value)
    
    # プログレスバー表示
    prog_value = 0
    prog_txt = ft.TextField(value="0",text_size=18, text_align=ft.TextAlign.RIGHT, width=100) 

    # リストビュー追加
    lv = ft.ListView(expand=1,spacing=10,padding=20,auto_scroll=True)

    # プログレスバー初期化
    pb = ft.ProgressBar(width=500)
    pb.value = 0

    def READ_PW():  # パワー計(N1913A)の値を読取
        IP_address = 'TCPIP::' + str(txt_IP.value) # IPアドレス
        rm = pyvisa.ResourceManager()              # インスタンス化
        inst = rm.open_resource(IP_address)        # IP指定して接続
        inst.write('FETC?') # 値を取得する             
        tmp_val = inst.read()  
        return tmp_val

    def PTT_ON(): # 送信開始
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
        
    def ADJ_READ(addr): # 調整値読取
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

    def ADJ_WRITE(addr, val): # 調整値書込
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

    def DECtoHEX(val): # 10進数->16進
        val_ADJ = [0] * 2
        val_ADJ[1] = val // 16
        val_ADJ[0] = val % 16

        # # 10の位
        if(val_ADJ[1]<10):
            val_ADJ[1] = val_ADJ[1] + 48 # "0"=48を足す
        else:
            val_ADJ[1] = val_ADJ[1] + 55 # "A"=65を足す

        # # 1の位
        if(val_ADJ[0]<10):
            val_ADJ[0] = val_ADJ[0] + 48 # "0"=48を足す
        else:
            val_ADJ[0] = val_ADJ[0] + 55 # "A"=65を足す

        return val_ADJ

    def HEXtoDEC(val): # 10進数->16進

        import binascii
        val_ADJ_1 = val[0:1] # 10の位
        val_ADJ_0 = val[1:2] # 1の位

        # 16進変換
        val_ADJ_0 = val_ADJ_0.encode("utf-8")
        val_ADJ_0 = binascii.hexlify(val_ADJ_0).decode("utf-8")    
        val_ADJ_0 = int(val_ADJ_0)

        # 16進変換
        val_ADJ_1 = val_ADJ_1.encode("utf-8")
        val_ADJ_1 = binascii.hexlify(val_ADJ_1).decode("utf-8")    
        val_ADJ_1 = int(val_ADJ_1)
    
        # 10の位
        if(val_ADJ_1<=39): # 9以下
            val_ADJ_1 = val_ADJ_1 - 30 # "0"=30を引く
        else:
            val_ADJ_1 = val_ADJ_1 - 41 + 10 # "A"=41を引く

        # 1の位
        if(val_ADJ_0<=39): # 9以下
            val_ADJ_0 = val_ADJ_0 - 30 # "0"=30を引く
        else:
            val_ADJ_0 = val_ADJ_0 - 41 + 10 # "A"=41を引く
    
        result = val_ADJ_0 + val_ADJ_1 * 16

        return result

    # 調整値を5刻みに変更しパワーを測定する---------------------------
    def MEASUREMENT(e):

        # パラメータ更新
        page.update() # 画面更新
        time.sleep(0.3)
        COM_ = "COM" + str(txt_COM.value)          # COMポート
        IP_address = 'TCPIP::' + str(txt_IP.value) # IPアドレス
        POW_addr = txt_pow_adrr.value              # パワー調整のアドレス
        baud_ = int(txt_baud.value)                # ボーレートボーレート

        # 行：0〜255、列：パワー値, 5ステップ
        j = 0
        for i in range(0,260,5):
            DA_value[j][0] = i
            j = j + 1    

        # アドレス読取り(文字コード変換)
        adrr_1 = DECtoHEX(int(POW_addr[0]))[0] # 10の位 (例,0x50='2')
        adrr_2 = DECtoHEX(int(POW_addr[1]))[0] # 1の位 (例,0x52='4')
        addr_pow = [adrr_1, adrr_2] # (例,['2','4'])

        # 調整値読み取り、フォームに調整値記録(16進)
        ADJ_POW_init = ADJ_READ(addr_pow) 
        txt_pow_now.value = ADJ_POW_init

        tmp = ADJ_POW_init
        time.sleep(0.3)
        page.update()
        
        # 測定開始
        for i in range(52):

            # 調整値書き込み(0-255)
            ADJ_WRITE(addr_pow, DECtoHEX(DA_value[i][0])) 
            print(HEXtoDEC(ADJ_READ(addr_pow)))
            time.sleep(0.3)

            # 送信
            PTT_ON()                
            time.sleep(0.3)

            # パワー計読取り
            DA_value[i][1] = READ_PW()
            print(DA_value[i][1]) 
            PTT_OFF()               
            time.sleep(0.3)

            # 進捗率表示
            prog_txt.value = round(i/52.0*100,2)
            pb.value = round(i/52.0,2)

            # 履歴表示
            disp_DA = DA_value[i][0]
            disp_PW = DA_value[i][1][0:5] + DA_value[i][1][-6:-4] + DA_value[i][1][-2:]
            sentence = 'DA = '+str(disp_DA)+',   PW[W] = '+str(disp_PW)
            lv.controls.append(ft.Text(sentence))
            time.sleep(0.3)
            page.update()

        # プログレスバーを100%にする
        prog_txt.value = 100
        pb.value = 1
        time.sleep(0.3)
        page.update()
        
        # 調整値戻す
        ADJ_WRITE(addr_pow, DECtoHEX(HEXtoDEC(tmp))) # 調整値書き込み

        # 現在時刻取得しファイル名とする
        dt_now = datetime.now()
        with open('output.csv', 'w', newline="") as f: # CSV出力
            writer = csv.writer(f)
            writer.writerows(DA_value)
        lv.controls.append(ft.Text("測定完了しました！"))
        print("測定完了!")
        page.update()
        return None
    
    # メインページ
    page.add(
        ft.Text("--------------【使用方法】------------------------------------------------", size=18),
        ft.Text("① 測定する周波数(fL/fM/fH)のMCHを準備する。", size=18),
        ft.Text("② 測定するMCHを選択する。", size=18),
        ft.Text("③ 「COMポート」、「パワー計のIPアドレス」を入力する。", size=18),
        ft.Text("④ RAMMAP値(f1〜f5)を「PWアドレス」に入力する。", size=18),
        ft.Text("⑤ 「ボーレート」を入力する。", size=18),
        ft.Text("⑤ 「測定開始」ボタンを押す。", size=18),
        ft.Text("⑥ CSVファイル(output.csv)が出力される。", size=18),
        ft.Text("--------------【入力パラメータ】---------------------------------------", size=18),
        ft.Row(
            [ft.Text("COM番号", size=18),txt_COM,
            ft.Text("IPアドレス", size=18),txt_IP,],
            alignment=ft.alignment.center,
        ),
        ft.Row(
            [ft.Text("PWアドレス", size=18),txt_pow_adrr,
            ft.Text("ボーレート", size=18),txt_baud,],
            alignment=ft.alignment.center,
        ),

        ft.Column([ft.Text("『進捗率』・・・",size=18),pb]),
        ft.Row([
        prog_txt,ft.Text("%", size=18),
        ft.Text("測定前PW値", size=18),txt_pow_now,],),
        ft.Row([
        ft.FilledButton(text="測定開始 (Click!!)",on_click=MEASUREMENT)],
        ),
        ft.Text("--------------【履歴】-----------------------------------------------", size=18),
    )
    page.add(lv)

ft.app(target=main)