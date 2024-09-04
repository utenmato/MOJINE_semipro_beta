# Copyright (c) 2024 Hzure Utenmato
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

import customtkinter as ctk
from tkinter import filedialog
import json
import re
import setup
import repage
import export
import main
import capture

class SaveJson():
    def __init__(self, parent, tags_koma, tags_page, tags_and_messages, button):

        self.parent = parent
        self.canvas = parent.canvas
        self.filedirbar_frame = parent.filedirbar_frame
        self.tags_koma = tags_koma
        self.tags_page = tags_page
        self.tags_and_messages = tags_and_messages
        self.button = button 

        if self.button in [3, 4, 5, 6]:
            self.savefilename = filedialog.asksaveasfilename(
            title = "名前を付けてjsonファイルを保存",
            initialdir = "./", # 自分自身のディレクトリ
            filetypes = [("JSON files", "*.json")]
            )

            # ファイル名に拡張子がなければ、手動で追加する
            if not self.savefilename.endswith(".json"):
                self.savefilename += ".json"

            if self.savefilename == ".json":
                pass
            else:
                self.filedirbar_frame.set_filedir(self.savefilename)
                self.save_to_json()

        #ショートカットキーコマンド用
        else:
            self.savefilename = self.filedirbar_frame.get_filedir()
            e = self.save_to_json()
            if e != 'e':
                dialog = ShortSaveDialog(self.parent)
                dialog.transient(self.parent)  # これで親ウィンドウの手前に表示されるようになる
                dialog.grab_set()  # これでダイアログがアクティブになる

    def get_savefile(self):
        return self.savefilename

    def save_to_json(self): 
        # Pageオブジェクトの情報を格納するリスト
        page_data = []
        for i,page in enumerate(self.tags_page):
            page_info = {
                'tag': page,
                'x': self.canvas.coords(page)[0],
                'y': self.canvas.coords(page)[1],
                'width': self.canvas.coords(page)[2] - self.canvas.coords(page)[0],
                'height': self.canvas.coords(page)[3] - self.canvas.coords(page)[1],
                'page': i+1,
            }
            page_data.append(page_info)

        # komaオブジェクトの情報を格納するリスト
        koma_data = []
        for i,koma in enumerate(self.tags_koma):
            koma_info = {
                'tag': koma,
                'x': self.canvas.coords(koma)[0],
                'y': self.canvas.coords(koma)[1],
                'width': self.canvas.coords(koma)[2] - self.canvas.coords(koma)[0],
                'height': self.canvas.coords(koma)[3] - self.canvas.coords(koma)[1],
                'koma': re.sub(r"\D", "", koma),
                'all_koma': len(self.tags_koma),
                'bgcolor': self.canvas.itemcget(koma, "fill")
            }
            koma_data.append(koma_info)

        tags_and_messages_data = self.tags_and_messages

        # komaとPageの情報をまとめる
        data = {
            'pages': page_data,
            'komas': koma_data,
            'tags_and_messages': tags_and_messages_data
        }

        # JSONファイルに書き込む
        try:
            with open(self.savefilename, 'w', encoding='utf-8') as file:
                json.dump(data, file, indent=4, ensure_ascii=False)
            return 'o'
        except FileNotFoundError:
            dialog = main.MessageDialog(self.parent, self.button)
            dialog.transient(self.parent)  # これで親ウィンドウの手前に表示されるようになる
            dialog.grab_set()  # これでダイアログがアクティブになる
            return 'e'


        #SaveJsonの処理が終了した後に新しいダイアログを表示する
        #setup.NewcreateInputDialog(self.canvas)  # もしくは適切な引数を渡してください

# JSONファイルからオブジェクトの情報を読み込むメソッド
class LoadDialog():
    def __init__(self, parent):

        self.filedirbar_frame = parent.filedirbar_frame
        self.canvas = parent.canvas

        self.loadfilename = filedialog.askopenfilename(
        title = "読み込むjsonファイルを選択",
        initialdir = "./", # 自分自身のディレクトリ
        filetypes = [("JSON files", "*.json")]
        )

        self.filedirbar_frame.set_filedir(self.loadfilename)

        self.komas = []
        self.pages = []
        self.Labels = []

        self.load_from_json()

    def get_new_information(self):
        return self.tags_and_messages

    def load_from_json(self):
        try:
            with open(self.loadfilename, 'r', encoding='utf-8') as file:
                data = json.load(file)

            self.tags_and_messages = data['tags_and_messages']

            # 読み込んだ情報を元にPageオブジェクトを再作成
            for page_info in data['pages']:
                page = setup.Page(
                    self.canvas,
                    page_info['x'],
                    page_info['y'],
                    page_info['width'],
                    page_info['height'],
                    page_info['page'],
                )
                self.pages.append(page)

            # 読み込んだ情報を元にkomaオブジェクトを再作成
            for koma_info in data['komas']:
                koma = setup.Koma(
                    self.canvas,
                    koma_info['x'],
                    koma_info['y'],
                    koma_info['width'],
                    koma_info['height'],
                    int(koma_info['koma']),
                    koma_info['all_koma'],
                    self.tags_and_messages,
                    self.Labels,
                    koma_info['bgcolor'],
                )
                self.komas.append(koma)
                self.all_koma = koma_info['all_koma']
                
        except FileNotFoundError:
            # ファイルが見つからない場合のエラーハンドリング
            print("JSONファイルは開かれませんでした。")

class SaveDialog(ctk.CTkToplevel):
    def __init__(self, parent, tags_and_messages, button):

        self.button = button
        self.tags_and_messages = tags_and_messages
        self.canvas = parent.canvas
        self.fonts = ("Meiryo", 12)
        
        super().__init__(parent)

        self.geometry("320x140")
        self.title("ファイルの保存")

        if self.button == 3:
            self.label1 = ctk.CTkLabel(master=self, text="現在の内容を保存しますか？", font=self.fonts)
        elif self.button in [4, 6]:
            self.label1 = ctk.CTkLabel(master=self, text="書き出しを行うには\n現在の内容を保存してください", font=self.fonts)
        elif self.button == 5:
            self.label1 = ctk.CTkLabel(master=self, text="ページ数に修正を加えるには\n現在の内容を保存してください", font=self.fonts)
        self.label1.grid(row=0, column=0, padx=10, pady=20, columnspan=2)
        
        self.btn1 = ctk.CTkButton(master=self, text="キャンセル", command=self.button1_click, font=self.fonts)
        self.btn1.grid(row=1, column=0, padx=10, pady=10)

        self.btn2 = ctk.CTkButton(master=self, text="保存する", command=self.button2_click, font=self.fonts)
        self.btn2.grid(row=1, column=1, padx=10, pady=10)

        self.grid_columnconfigure([0, 1], weight=1)
    
    def get_new_information(self):
        return self.tags_and_messages

    def button1_click(self):
        self.destroy()
    
    def button2_click(self):
        ids = self.canvas.find_all()
        otags = [self.canvas.gettags(id) for id in ids]
        pktags = [tag for tag in otags if tag]
        pktags2 = [item[0] for item in pktags if item[0]] 

        tags_koma = [tag for tag in pktags2 if "koma" in tag]
        tags_page = [tag for tag in pktags2 if "page" in tag]
        tags_page.reverse()

        self.destroy()

        savejson = SaveJson(self.master, tags_koma, tags_page, self.tags_and_messages, self.button)
        filename = savejson.get_savefile()

        if self.button == 5:
            if filename == ".json":
                pass
            else:
                dialog = repage.RepageDialog(self.canvas, savejson, self)
                dialog.transient(self.master)  # これで親ウィンドウの手前に表示されるようになる
                dialog.grab_set()  # これでダイアログがアクティブになる

        elif self.button == 4:
            if filename == ".json":
                pass
            else:
                export.ExpotCsv(self.master, savejson)
        
        elif self.button == 6:
            if filename == ".json":
                pass
            else:
                capture.ExportCapture(self.master, savejson)
    
class SaveShort():
    def __init__(self, parent, tags_and_messages, button):

        self.button = button
        self.tags_and_messages = tags_and_messages
        self.canvas = parent.canvas

        ids = self.canvas.find_all()
        otags = [self.canvas.gettags(id) for id in ids]
        pktags = [tag for tag in otags if tag]
        pktags2 = [item[0] for item in pktags if item[0]] 

        tags_koma = [tag for tag in pktags2 if "koma" in tag]
        tags_page = [tag for tag in pktags2 if "page" in tag]
        tags_page.reverse()

        SaveJson(parent, tags_koma, tags_page, self.tags_and_messages, self.button)

class ShortSaveDialog(ctk.CTkToplevel):
    def __init__(self, parent):

        super().__init__(parent)
        self.canvas = parent.canvas
        self.fonts = ("Meiryo", 12)

        self.geometry("140x50")
        self.title("メッセージ")

        self.label1 = ctk.CTkLabel(master=self, text="保存しました", font=self.fonts)
        self.label1.grid(row=0, column=0, padx=0, pady=10)

        self.grid_columnconfigure(0, weight=1)

        self.later_destroy()

    def later_destroy(self):
        # 3秒後にウィンドウを破棄
        self.after(2000, self.destroy)

