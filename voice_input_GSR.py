"""
マイクから音声認識
"""
import speech_recognition as sr
import threading
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
import tkinter as tk
from tkinter import font
from tkinter import scrolledtext as tk_scrolledtext
from logging import getLogger, StreamHandler, Formatter
import sys
import argparse

class VoiceRecognizer():
    """
    音声認識クラス
    """
    def __init__(self, my_frame) -> None:
        self.my_frame = my_frame
        # obtain audio from the microphone
        self.r = sr.Recognizer()
        try:
            self.mic = sr.Microphone()
        except Exception as e:
            print(f"マイクの状態を確認してください。参考({e})")
            sys.exit()
        self.do_break = False
        # ThreadPoolExecutor用準備
        self.futures = []
        self.mic_init(my_frame.v_adjust.get(), my_frame.v_threshold.get())


    def mic_init(self, is_dynamic:bool=False, threshold:int=50):
        """
        マイクの初期化
        Args:
            bool:   動的しきい値調整フラグ
            int:    しきい値
        """
        # マイクの初期設定
        self.r.energy_threshold = threshold
        logger.info(f"しきい値を設定しました：{self.r.energy_threshold:.2f}")
        self.my_frame.insert_msg(f"しきい値を設定しました：{self.r.energy_threshold:.2f}")
        # self.r.pause_threshold = 0.5
        self.r.dynamic_energy_threshold = is_dynamic     # しきい値調整する場合は動的変更しない

        # 動的調整の時だけ外部雑音に合わせてしきい値を調整
        if is_dynamic:
            with self.mic as source:
                self.r.adjust_for_ambient_noise(source, 3.0) # 外部雑音に合わせてしきい値を調整
                logger.info(f"外部雑音に合わせてしきい値を調整しました：{self.r.energy_threshold:.2f}")
                self.my_frame.insert_msg(f"外部雑音に合わせてしきい値を調整しました：{self.r.energy_threshold:.2f}")
        # listen用属性設定

    def recognize_voice_thread_pool(self, audio, i, event=None):
        """
        スレッドプールを作成して音声認識メソッドをスケジュール
        作成された Futureオブジェクトをself.futuresに追加する
        Args:
            audio:  音声データ
            int:    処理順
        """
        logger.debug("start")
        # with ThreadPoolExecutor(thread_name_prefix="Rec Thread") as pool:
        #     future = pool.submit(self.recognize_voice, audio, i)
        #     logger.debug("submit end")
        # withを使うとshutdownをwait=Trueで呼ぶので処理が終わらないと戻らない
        pool = ThreadPoolExecutor(thread_name_prefix="Rec Thread")
        future = pool.submit(self.recognize_voice, audio, i)
        logger.debug("submit end")
        pool.shutdown(False)
        self.futures.append(future)
        logger.debug("append end")
        logger.debug("end")

    def listen_voice(self, i):
        """
        音声を聞いて音声データを作成
        聞き終わったら音声認識をスレッドで呼び出す
        Args:
            int:    処理順
        """
        logger.debug("start")
        with self.mic as source:
            logger.debug("")
            # dynamic_energy_thresholdをTrueにした時の設定値を確認
            # 静かな部屋だと思ったより低く出るみたいで使わない方がいいみたい
            # 扇風機が近くにあるとダメみたい。扇風機がないと有効にしても問題ない。
            if self.r.dynamic_energy_threshold:
                self.my_frame.insert_msg(f"(しきい値：{self.r.energy_threshold:.2f})", end=" ")
                if self.r.energy_threshold < 20:
                    self.r.energy_threshold = 20
                    self.my_frame.insert_msg(f"(しきい値：{self.r.energy_threshold:.2f})", end=" ")
            self.my_frame.insert_msg(f"{i}Ω", end=" ")
            # マイク入力
            audio = self.r.listen(source)
        if not self.do_break:
            self.recognize_voice_thread_pool(audio, i)      # スレッドプールの作成
        logger.debug("end")

    def listen_voice_bg(self):
        """
        音声を聞く(background) 動かし方がよくわからない
        """
        with self.mic as source:
            # print("->")
            self.my_frame.insert_msg("->")
            ret = self.r.listen_in_background(source, self.recognize_voice)
            # print(ret)
            self.my_frame.insert_msg(ret)

    def recognize_voice(self, audio, i) -> str:
        """
        音声認識(Google Speech Recognition)
        Args:
            audio:  音声データ
            int:    処理順
        Returns:
            str:    認識した文字列
        """
        logger.debug("start")
        # print(f"{i}-->", end=" ")
        self.my_frame.insert_msg(f"{i}⎘", end=" ")
        text = ""
        # recognize speech using Google Speech Recognition
        try:
            text = self.r.recognize_google(audio, language='ja-JP')
            # print(f"\n{i}===>{text}")
            self.my_frame.insert_msg(f"\n{i}===>{text}")
        except sr.UnknownValueError:
            logger.warning("Google Speech Recognition could not understand audio")
            self.my_frame.insert_msg("❓")
        except sr.RequestError as e:
            logger.warning("Could not request results from Google Speech Recognition service; {0}".format(e))
            self.my_frame.insert_msg("❓")
        else:
            if text == "ストップ":
                self.do_break = True    # 終了フラグをオン
        logger.debug("end")
        return text

class MyFrame(tk.Frame):
    """
    画面  文字サンプル マイク：⪪Ω、認識：⌛⎘ 候補にしたけど表示されない：📍
    """
    def __init__(self, master, args:argparse.Namespace) -> None:
        """
        初期設定
        """
        super().__init__(master)
        # ウィジェット変数
        self.v_threshold = tk.IntVar(master, args.threshold)
        self.v_threshold.trace_add("write", self.mic_init)   # v_thresholdが変更された時の処理を登録
        self.v_adjust = tk.BooleanVar(master, args.dynamic)
        self.v_font = tk.IntVar(master, args.font)
        self.v_font.trace_add("write", self.change_font_size)   # v_fontが変更された時の処理を登録
        # ウィジェット作成
        self.f_top = tk.Frame(master, background="lightblue")
        self.b_start = tk.Button(self.f_top, text="開始", command=self.voice_input_th)
        self.l_threshold = tk.Label(self.f_top, text="しきい値(0〜3500)")
        self.e_threshold = tk.Entry(self.f_top, textvariable=self.v_threshold, width=4, justify=tk.RIGHT
                                    , validate="key", vcmd=(self.register(self.entry_validate), "%S"))
        self.c_adjust = tk.Checkbutton(self.f_top, variable=self.v_adjust, text="動的調整"
                                        , command=self.mic_init)
        self.l_font = tk.Label(self.f_top, text="フォントサイズ")
        self.c_font = tk.Entry(self.f_top, textvariable=self.v_font, width=3, justify=tk.RIGHT
                                    , validate="key", vcmd=(self.register(self.entry_validate), "%S"))
        # 配置
        self.c_font.pack(side=tk.RIGHT, fill=tk.Y)
        self.l_font.pack(side=tk.RIGHT, fill=tk.Y, padx=(5,0))
        self.c_adjust.pack(side=tk.RIGHT, fill=tk.Y, padx=(5,0))
        self.e_threshold.pack(side=tk.RIGHT, fill=tk.Y)
        self.l_threshold.pack(side=tk.RIGHT, fill=tk.Y, padx=(5,0))
        self.b_start.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.font4txt = font.Font(size=self.v_font.get())
        self.txt = tk_scrolledtext.ScrolledText(master, font=self.font4txt)
        self.f_top.pack(fill=tk.X)
        self.txt.pack(fill=tk.BOTH, expand=True)
        # 音声認識クラスの作成  self.txtを使うので最後に作成する
        self.vr = VoiceRecognizer(self)

    def entry_validate(self, modifyed_str:str) -> bool:
        """
        エントリーの入力検証
        intVarをtraceで使う場合、ここで空文字にならないようにすると
        エントリーの内容が空になるような変更はできなくなり操作しにくい
        ここでは挿入・削除されるテキストを対象にし空文字の対策は別途行う
        Args:
            str:    挿入・削除されるテキスト
        """
        result = modifyed_str.isdigit()     # 数字かどうか
        return result

    def change_font_size(self, var, index, mode):
        """
        画面のフォントサイズエントリーが変更された時のコールバック関数
        Args:       ウィジェット変数のコールバック関数に必要な引数
            var:    ウィジェット変数名
            index:  リストへのインデックス
            mode:   発生動作
        """
        try:
            if self.v_font.get() < 10: return       # 入力途中でも来るので1ケタの時は変更しない
        except:
            return  # 空文字の時に例外が発生するので1ケタと同じ扱いにして戻す
        self.font4txt.config(size=self.v_font.get())
            
    def mic_init(self, var=None, index=None, mode=None):
        """
        しきい値が変更された時のコールバック関数
        Args:       ウィジェット変数のコールバック関数に必要な引数
            var:    ウィジェット変数名
            index:  リストへのインデックス
            mode:   発生動作
        """
        try:
            if self.v_threshold.get() < 10: return  # 入力途中でも来るので1ケタの時は変更しない
        except:
            return  # 空文字の時に例外が発生するので1ケタと同じ扱いにして戻す
        if self.vr:
            self.vr.mic_init(self.v_adjust.get(), self.v_threshold.get())
    
    def insert_msg(self, msg:str, end:str="\n"):
        """
        ScrolledText ウィジェットへメッセージの挿入
        Args:
            str:    挿入する文字列
            str:    終端文字
        """
        msg1 = msg + end
        self.txt.insert(tk.INSERT, msg1)
        self.txt.see(tk.INSERT)
        # self.txt.update_idletasks()   # see()メソッドを実行すると必要ない

    def voice_input_th(self, event=None):
        """
        音声入力をスレッドで起動
        """
        th = threading.Thread(target = self.voice_input)
        th.start()

    def voice_input(self):
        """
        音声入力
        「ストップ」を認識したら終了
        終了時ファイル出力
        """
        self.insert_msg("話し始めてください。音声入力をはじめます。\n止める時は「ストップ」と言ってください。")
        logger.info("話し始めてください。音声入力をはじめます。\n止める時は「ストップ」と言ってください。")
        self.vr.do_break = False
        self.b_start.config(state="disable")
        self.vr.futures.clear()
        i = 1
        while True:
            self.vr.listen_voice(i)
            if self.vr.do_break: break
            i += 1
        self.insert_msg("\n「ストップ」を認識したので終了します\n")
        logger.info("「ストップ」を認識したので終了します")
        # vr.listen_voice_bg()
        logger.debug("end listen")

        # 同じファイルに追記する
        # 順番通り取得できるか
        self.insert_msg("▽結果")
        with open("音声入力.txt", "a", encoding="utf_8_sig") as f:
            f.write(f"\n◆{datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')}\n")
            for future in self.vr.futures[:-1]: # 最後の「ストップ」を除く
                s = future.result()
                logger.debug("get future result")
                if not s:continue   # 空文字は認識できなかった時なので出力しない
                # print(f"{s}")
                self.insert_msg(f"{s}")
                f.write(s + "\n")
        self.insert_msg("△", "\n\n")
        self.b_start.config(state="active")
        logger.debug("end")

class App(tk.Tk):
    def __init__(self, args:argparse.Namespace) -> None:
        super().__init__()
        self.title("音声入力")      # タイトル
        self.geometry("800x600")    # サイズ
        my_frame = MyFrame(self, args)    # MyFrameクラスのインスタンス作成

if __name__ == '__main__':
    # logger setting
    LOGLEVEL = "INFO"   # ログレベル('CRITICAL','FATAL','ERROR','WARN','WARNING','INFO','DEBUG','NOTSET')
    logger = getLogger(__name__)
    handler = StreamHandler()	# このハンドラーを使うとsys.stderrにログ出力
    handler.setLevel(LOGLEVEL)
    # ログ出形式を定義 時:分:秒.ミリ秒 L:行 M:メソッド名 T:スレッド名 コメント
    handler.setFormatter(Formatter("{asctime}.{msecs:.0f} L:{lineno:0=3} M:{funcName} T:{threadName} : {message}", "%H:%M:%S", "{"))
    logger.setLevel(LOGLEVEL)
    logger.addHandler(handler)
    logger.propagate = False

    logger.debug("start log")

    # コマンドライン引数の設定
    parser = argparse.ArgumentParser()		# インスタンス作成
    parser.add_argument("-t",'--threshold', type=int, metavar="n", default=50, help="しきい値(default:%(default)s)")	# 引数定義
    parser.add_argument("-f", '--font', type=int, metavar="n", default=20, help="フォントサイズ(default:%(default)s)")	# 引数定義
    parser.add_argument("-d", '--dynamic', type=bool, metavar="bool", default=False, help="動的しきい値調整(default:%(default)s)")	# 引数定義
            
    args = parser.parse_args()		# 引数の解析

    app = App(args)
    app.mainloop()