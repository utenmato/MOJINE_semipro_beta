# Copyright 2024 Hazure Utenmato
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import tkinter as tk
import customtkinter as ctk
import setup
import save_and_load
import sys

class CanvasFrame(tk.Canvas):
    def __init__(self, master, img_width, img_height, bg):
        super().__init__(master, bg=bg, height=img_height, width=img_width, highlightthickness=0)
        self.pack(fill=tk.BOTH, expand=True)

class CanvasForm:
    def __init__(self, root, canvas):
        self.root = root
        # windowサイズの初期化

        self.bg_color = "gray10"

        self.canvas = canvas

    def move_start(self, event):
        self.canvas.scan_mark(event.x, event.y)

    def move_move(self, event):
        self.canvas.scan_dragto(event.x, event.y, gain=1)

#ファイルディレクトリの表示と呼び出し
class FiledirbarFrame(ctk.CTkFrame):
    def __init__(self, *args, header_name="FiledirbarFrame", **kwargs):
        super().__init__(*args, **kwargs)

        self.filedir = ctk.StringVar()

        self.fonts = ("Meiryo", 12)
        self.header_name = header_name
        
        self.setup_form()
  
    def setup_form(self):

        label1 = ctk.CTkLabel(master=self, height=15, width=100, font=self.fonts, text="保存先 (<ctrl＋s>で上書き保存):")
        label1.grid(row=0, column=0, padx=10, pady=10, sticky="news")

        self.directory_entry = ctk.CTkEntry(master=self, textvariable=self.filedir, state='readonly',  height=15, width=700)
        self.directory_entry.grid(row=0, column=1, padx=10, pady=20, sticky="news")

    def set_filedir(self, filedir):
        self.filedir.set(filedir)
        self.directory_entry.delete(0, ctk.END)  # 現在の内容を削除
        self.directory_entry.insert(0, self.filedir.get()) 

    def get_filedir(self):
        filedir = self.filedir.get()
        return filedir
        
class ToolbarFrame(ctk.CTkFrame):
    def __init__(self, *args, header_name="ToolbarFrame", **kwargs):

        super().__init__(*args, **kwargs)

        self.fonts = ("Meiryo", 14, "bold")

        self.header_name = header_name

        # フォームのセットアップをする
        self.setup_form()

    def setup_form(self):


        btn1 = ctk.CTkButton(master=self, text="新規作成", width=150, height=50, font=self.fonts, command=self.button1_click)
        btn1.grid(row=0, column=0, padx=15, pady=10)

        btn2 = ctk.CTkButton(master=self, text="開く", width=150, height=50, font=self.fonts, command=self.button2_click)
        btn2.grid(row=1, column=0, padx=15, pady=10)

        btn3 = ctk.CTkButton(master=self, text="名前を付けて保存", width=150, height=50, font=self.fonts, command=self.button3_click)
        btn3.grid(row=2, column=0, padx=15, pady=10)

        btn5 = ctk.CTkButton(master=self, text="ページ設定変更", width=150, height=50, font=self.fonts, command=self.button5_click)
        btn5.grid(row=3, column=0, padx=15, pady=10)

        btn4 = ctk.CTkButton(master=self, text="セリフCSV書き出し", width=150, height=50, font=self.fonts, command=self.button4_click)
        btn4.grid(row=4, column=0, padx=15, pady=10)

        btn6 = ctk.CTkButton(master=self, text="画像書き出し", width=150, height=50, font=self.fonts, command=self.button6_click)
        btn6.grid(row=5, column=0, padx=15, pady=10)

        tips = ctk.CTkLabel(master=self, font=("Meiryo",12),text="【コマ操作メニュー】\n・コマを<左ダブルクリック>で削除\n・コマを<sift＋左クリック>で色変更\n・キャンバス<右クリック>でコマ追加\n・セリフ記号：\n'='人物名の後　'/'セリフ区切り", justify='left')
        tips.grid(row=6, column=0, padx=15, pady=10)

    #新規作成
    def button1_click(self):
        button = 1
        if len(self.master.canvas.find_all()) != 0:
            dialog = MessageDialog(self.master, button)
            dialog.transient(self.master)  # これで親ウィンドウの手前に表示されるようになる
            dialog.grab_set()  # これでダイアログがアクティブになる
        else:
            self.new_information = setup.NewCreateInputDialog(self.master)
            self.new_information.transient(self.master)  # これで親ウィンドウの手前に表示されるようになる
            self.new_information.grab_set()  # これでダイアログがアクティブになる
    
    #開く
    def button2_click(self):
        button = 2
        if len(self.master.canvas.find_all()) != 0:
            dialog = MessageDialog(self.master, button)
            dialog.transient(self.master)  # これで親ウィンドウの手前に表示されるようになる
            dialog.grab_set()  # これでダイアログがアクティブになる
            
        else:
            self.new_information = save_and_load.LoadDialog(self.master)

    #名前を付けて保存        
    def button3_click(self):
        button = 3
        if len(self.master.canvas.find_all()) != 0:
            self.tags_and_messages = self.new_information.get_new_information()
            savedialog = save_and_load.SaveDialog(self.master, self.tags_and_messages, button)
            savedialog.transient(self.master)  # これで親ウィンドウの手前に表示されるようになる
            savedialog.grab_set()  # これでイアログがアクティブになる 
        else:
            dialog = MessageDialog(self.master, button)
            dialog.transient(self.master)  # これで親ウィンドウの手前に表示されるようになる
            dialog.grab_set()  # これでダイアログがアクティブになる

    #ファイルディレクトリに保存ショートカット
    def button3_short(self, event):
        button = 13
        if len(self.master.canvas.find_all()) != 0:
            self.tags_and_messages = self.new_information.get_new_information()
            save_and_load.SaveShort(self.master, self.tags_and_messages, button)
        else:
            dialog = MessageDialog(self.master, button)
            dialog.transient(self.master)  # これで親ウィンドウの手前に表示されるようになる
            dialog.grab_set()  # これでダイアログがアクティブになる

    #ページ変更
    def button5_click(self):
        button = 5
        if len(self.master.canvas.find_all()) != 0:
            self.tags_and_messages = self.new_information.get_new_information()
            dialog = save_and_load.SaveDialog(self.master, self.tags_and_messages, button)
            dialog.transient(self.master)  # これで親ウィンドウの手前に表示されるようになる
            dialog.grab_set()  # これでダイアログがアクティブになる
            self.new_information = dialog
        else:
            dialog = MessageDialog(self.master, button)
            dialog.transient(self.master)  # これで親ウィンドウの手前に表示されるようになる
            dialog.grab_set()  # これでダイアログがアクティブになる

    #台詞CSV書き出し
    def button4_click(self):
        button = 4
        if len(self.master.canvas.find_all()) != 0:
            self.tags_and_messages = self.new_information.get_new_information()
            dialog = save_and_load.SaveDialog(self.master, self.tags_and_messages, button)
            dialog.transient(self.master)  # これで親ウィンドウの手前に表示されるようになる
            dialog.grab_set()  # これでダイアログがアクティブになる
        else:
            dialog = MessageDialog(self.master, button)
            dialog.transient(self.master)  # これで親ウィンドウの手前に表示されるようになる
            dialog.grab_set()  # これでダイアログがアクティブになる

    #画像書き出し
    def button6_click(self):
        button = 6
        if len(self.master.canvas.find_all()) != 0:
            self.tags_and_messages = self.new_information.get_new_information()
            dialog = save_and_load.SaveDialog(self.master, self.tags_and_messages, button)
            dialog.transient(self.master)  # これで親ウィンドウの手前に表示されるようになる
            dialog.grab_set()  # これでダイアログがアクティブになる
        else:
            dialog = MessageDialog(self.master, button)
            dialog.transient(self.master)  # これで親ウィンドウの手前に表示されるようになる
            dialog.grab_set()  # これでダイアログがアクティブになる

class MessageDialog(ctk.CTkToplevel):
    def __init__(self, parent, button):

        self.button = button
        self.fonts = ("Meiryo", 12)

        super().__init__(parent)
        self.canvas = parent.canvas

        self.geometry("320x140")
        self.title("メッセージ")

        if self.button in [1, 2]:
            self.label1 = ctk.CTkLabel(master=self, text="ファイルは一つしか開けません\nアプリを再起動してください", font=self.fonts)
        elif self.button == 13:
            self.label1 = ctk.CTkLabel(master=self, text="保存先が指定されていないか存在していません", font=self.fonts)
        elif self.button == 21:
            self.label1 = ctk.CTkLabel(master=self, text="CSVファイルを保存しました", font=self.fonts)
        elif self.button == 22:
            self.label1 = ctk.CTkLabel(master=self, text="PNGファイルを保存しました", font=self.fonts)
        else:
            self.label1 = ctk.CTkLabel(master=self, text="編集中の内容がありません", font=self.fonts)
        self.label1.grid(row=0, column=0, padx=10, pady=20)
            
        self.btn1 = ctk.CTkButton(master=self, text="OK", command=self.button1_click, font=self.fonts)
        self.btn1.grid(row=1, column=0, padx=10, pady=10)

        self.grid_columnconfigure(0, weight=1)

    def button1_click(self):
        self.destroy()

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        # フォームのセットアップをする
        self.setup_form()
        self.protocol("WM_DELETE_WINDOW", self.on_close)
        self.bind("<Control-s>", self.toolbar_frame.button3_short)

    def on_close(self):
        result = tk.messagebox.askokcancel("終了確認", "MOJINE_semiproβ版を閉じようとしています。編集中のファイルを保存せず終了してもよろしいですか？")
        if result:
            sys.exit()

    def setup_form(self):

        # ctk のフォームデザイン設定
        ctk.set_appearance_mode("dark")  # Modes: system (default), light, dark
        ctk.set_default_color_theme("blue")  # Themes: blue (default), dark-blue, green

        # ウィンドウを画面の中央に配置する
        self.center_window()

        self.title("MOJINE_semiproβ版")
        self.minsize(300, 400)

        # 行方向のマスのレイアウトを設定する。リサイズしたときに一緒に拡大したい行をweight 1に設定。
        self.grid_rowconfigure(0, weight=0)
        # 列方向のマスのレイアウトを設定する
        self.grid_columnconfigure(1, weight=1)

        self.filedirbar_frame = FiledirbarFrame(master=self, header_name="保存先")
        self.filedirbar_frame.grid(row=0, column=1, padx=10, pady=10, sticky="ew")

        # stickyは拡大したときに広がる方向のこと。nsew で4方角で指定する。
        self.toolbar_frame = ToolbarFrame(master=self, header_name="ツールバー")
        self.toolbar_frame.grid(row=1, column=0, padx=10, pady=10, sticky="news")

        self.canvas_frame = ctk.CTkFrame(master=self, bg_color="gray10")
        self.canvas_frame.grid(row=1, column=1, padx=10, pady=10, sticky="news")

        self.canvas = CanvasFrame(self.canvas_frame, 1720, 830, bg="gray10")
        
        CanvasForm(self, self.canvas)

    def center_window(self):
        # 画面サイズを取得
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()

        # ウィンドウサイズを設定
        window_width = 1720
        window_height = 1080

        # ウィンドウサイズがスクリーンサイズを超えないように調整
        if window_width > screen_width:
            window_width = screen_width
        if window_height > screen_height:
            window_height = screen_height

        # ウィンドウを中央に配置するための位置を計算
        x = int((screen_width / 2) - (window_width / 2))
        y = int((screen_height / 2) - (window_height / 2))

        # ウィンドウサイズと位置を設定
        self.geometry(f"{window_width}x{window_height}+{x}+{y}")
        

if __name__ == "__main__":
    app = App()
    app.mainloop()