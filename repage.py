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

import tkinter as tk
import customtkinter as ctk
import json
import setup
import main

class RepageDialog(ctk.CTkToplevel):
    def __init__(self, canvas, savejson, save_dialog):
        self.save_dialog = save_dialog  # SaveDialog のインスタンスを保持
        self.repagefilename = savejson.get_savefile()

        self.canvas = canvas
        
        self.komas = []
        self.pages = []
        self.Labels = []
        
        try:
            with open(self.repagefilename, 'r', encoding='utf-8') as file:
                self.data = json.load(file)
        except FileNotFoundError:
            dialog = main.MessageDialog(self.parent, 13)
            dialog.transient(self.parent)  # これで親ウィンドウの手前に表示されるようになる
            dialog.grab_set()  # これでダイアログがアクティブになる

        self.pages_info = self.data['pages']
        self.last_info = self.pages_info[-1]
        self.lastpage = self.last_info['page']

        first_info = self.pages_info[0]
        second_info = self.pages_info[1]
        firstpage_x = first_info['x']
        secondpage_x = second_info['x']
        width = first_info['width']

        if (firstpage_x - secondpage_x) - width > 10:
            self.radio_var = tk.IntVar(value=1)
            self.laststartpage = 1
        else:
            self.radio_var = tk.IntVar(value=2)
            self.laststartpage = 2

        if self.laststartpage == 1:
            col1_x = firstpage_x + width
            col2_x = firstpage_x
            col3_x = secondpage_x
            col4_x = secondpage_x - width
        elif self.laststartpage == 2:
            col1_x = firstpage_x
            col2_x = secondpage_x
            col3_x = secondpage_x - (50 * (width/300)) - width
            col4_x = col3_x - width

        self.col_x = [col1_x, col2_x, col3_x, col4_x]
        self.row1_y = first_info['y']
        self.interval = 50 * (width / 300)
        self.width = width
        self.height = first_info['height']

        super().__init__()

        self.geometry("400x250")
        self.title("ページ変更")
        self.fonts = ("Meiryo", 12)

        self.label0 = ctk.CTkLabel(master=self, text="現在のページ数は" + str(self.lastpage)+ "ページです。" + "\nページはじまりの変更に対しコマの位置は連動しません。", font=self.fonts)
        self.label0.grid(row=0, column=0, padx=20, pady=15, columnspan=2, sticky="ew")

        self.label1 = ctk.CTkLabel(master=self, text="ページ数", font=self.fonts)
        self.label1.grid(row=1, column=0, padx=20, pady=15, sticky="ew")
        self.num_page_entry = ctk.CTkEntry(master=self, placeholder_text="2以上の整数(おすすめ20以下)", width=200)
        self.num_page_entry.grid(row=1, column=1, padx=5, pady=15, columnspan=2, sticky="w")

        self.rbtnlab = ctk.CTkLabel(master=self, text="ページはじまり", font=self.fonts)
        self.rbtnlab.grid(row=2, column=0, padx=20, pady=15, sticky="ew")
        self.rbtn1 = ctk.CTkRadioButton(master=self, text="左", variable=self.radio_var, value=1)
        self.rbtn2 = ctk.CTkRadioButton(master=self, text="右", variable=self.radio_var, value=2)
        self.rbtn1.grid(row=2, column=1, padx=5, pady=15, columnspan=2, sticky="w")
        self.rbtn2.grid(row=2, column=1, padx=5, pady=15, columnspan=2, sticky="e")

        self.button1 = ctk.CTkButton(master=self, text="キャンセル", command=self.button1_click, font=self.fonts)
        self.button1.grid(row=3, column=0, padx=20, pady=15, sticky="e")

        self.button2 = ctk.CTkButton(master=self, text="ファイル作成", command=self.button2_click, font=self.fonts)
        self.button2.grid(row=3, column=1, padx=20, pady=15, sticky="e")

        self.grid_columnconfigure([0, 1], weight=1)

    def button1_click(self):
        self.destroy()
    
    def button2_click(self):

        try: 
            self.new_num_page = int(self.num_page_entry.get())
        except:
            self.new_num_page = self.num_page_entry.get()
        
        self.new_start_page = int(self.radio_var.get())

        try:
            if self.new_num_page < 2:
                raise TypeError("ページ設定は変更されませんでした。")
            self.repage()
            self.destroy()
        except TypeError:
            if isinstance(self.new_num_page, str):
                self.label1.configure(text="ページ数\n!半角の整数を入力")
            else:
                self.label1.configure(text="ページ数\n!2以上の整数を入力")

    def repage(self):
        
        self.canvas.delete("all")
        for widget in self.canvas.winfo_children():
            widget.destroy()

        self.tags_and_messages = self.data['tags_and_messages']

        if self.new_start_page == 1:
           
            if self.new_num_page <= 3:
                firstrowpages = self.new_num_page
                lastrowpages = 0
            else:
                firstrowpages = 3    
                lastrowpages = (self.new_num_page + 1) % 4

            rows = (self.new_num_page + 1) // 4
            
            p = 0
            for col in range(firstrowpages):
                p += 1
                page = setup.Page(self.canvas, self.col_x[col+1], self.row1_y, self.width, self.height, p)
                self.pages.append(page)
            for row in range(1,rows):
                for col in self.col_x:
                    p += 1
                    page = setup.Page(self.canvas, col, self.row1_y + (row * (self.height + self.interval)), self.width, self.height, p)
                    self.pages.append(page)
            for col in range(lastrowpages):
                p +=1
                page = setup.Page(self.canvas, self.col_x[col], self.row1_y + (rows * (self.height + self.interval)), self.width, self.height, p)
                self.pages.append(page)
        
        else:
            lastrowpages = self.new_num_page % 4

            rows = self.new_num_page // 4

            p = 0

            for row in range(rows):
                for col in self.col_x:
                    p += 1
                    page = setup.Page(self.canvas, col, self.row1_y + (row * (self.height + self.interval)), self.width, self.height, p)
                    self.pages.append(page)
            for col in range(lastrowpages):
                p +=1
                page = setup.Page(self.canvas, self.col_x[col], self.row1_y + (rows * (self.height + self.interval)), self.width, self.height, p)
                self.pages.append(page)

        # 読み込んだ情報を元にkomaオブジェクトを再作成
        for koma_info in self.data['komas']:
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

        # SaveDialog の tags_and_messages を更新
        self.save_dialog.tags_and_messages = self.tags_and_messages

