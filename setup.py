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
from functools import partial
import customtkinter as ctk
import re

class Page:
    def __init__(self, canvas, x, y, width, height, page):
        self.canvas = canvas
        self.pagenum = page
        tag_page = "page" + str(self.pagenum)
        self.rectangle = canvas.create_rectangle(x, y, x + width, y + height, fill='white', outline='black', tag=tag_page)
        self.canvas.tag_lower(self.rectangle)
        self.setup_pagenums()

    def setup_pagenums(self):
        bbox = self.canvas.bbox(self.rectangle)
        canvas_x, canvas_y = bbox[0], bbox[1]
        label = tk.Label(self.canvas, text=str(self.pagenum)+'ページ', bg='white', font=("Meiryo", 12))
        # キャンバス内の座標に変換してラベルを配置する
        canvas_label_x = canvas_x + 10  # キャンバス内の座標に変換する処理を削除
        canvas_label_y = canvas_y + 10  # キャンバス内の座標に変換する処理を削除
        self.canvas.create_window(canvas_label_x, canvas_label_y, anchor="nw", window=label, tag='plabel')  # ラベルを直接配置する
        
class Koma:
    def __init__(self, canvas, x, y, width, height, koma, all_koma, tags_and_messages, Labels, bgcolor):
        self.canvas = canvas
        self.koma = koma
        self.tags_and_messages = tags_and_messages
        self.Labels = Labels
        self.bgcolor = bgcolor

        self.tag_koma = "koma" + str(self.koma)
        self.all_koma = all_koma

        self.rectangle = canvas.create_rectangle(x, y, x + width, y + height, fill=self.bgcolor, outline='black', tag=self.tag_koma)
        self.schemas = {
            'セリフ': '',
            'カット': ''
        }
        
        #ここ新規作成でもできるように修正！
        try:
            self.schemas.update({key: self.tags_and_messages[self.tag_koma][key] for key in self.schemas})
        except:
            pass

        self.schema_labels = {}
        self.Labels.append(self.schema_labels)

        #self.schema_labels_koma1,2,3... = {}
        #self.Labels =[{schema_labels_koma1}, {schema_labels_koma2},...]
        
        self.setup_schemas()

        self.start_x = None
        self.start_y = None
        self.resize_point = None

        self.canvas.tag_bind(self.rectangle, "<ButtonPress-1>", self.on_press)
        self.canvas.tag_bind(self.rectangle, "<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)
        self.canvas.bind("<MouseWheel>", self.zoom_in_out_combined)

        self.canvas.tag_bind(self.rectangle, "<Double-Button-1>", self.menu1_koma)
        self.canvas.tag_bind(self.rectangle, "<Shift-Button-1>", self.menu2_koma)
        self.canvas.bind("<Button-3>", self.menu_canvas)
    
    def setup_schemas(self):
        bbox = self.canvas.bbox(self.rectangle)
        canvas_x, canvas_y = bbox[0], bbox[1]
        rect_height = bbox[3] - bbox[1]  # self.rectangleの幅を取得
        rect_width = bbox[2] - bbox[0]
        label_height = (rect_height - 10) / 2  # ラベルの高さを設定（必要に応じて変更可能）
        koma_message = {}
        for idx, (key, value) in enumerate(self.schemas.items()):
            label = tk.Message(self.canvas, text=f'{key}: {value}', bg=self.bgcolor, width=rect_width, font=("Meiryo", 12))
            self.schema_labels[key] = label
            canvas_label_x = canvas_x + 5
            canvas_label_y = canvas_y + 5 + (idx * label_height)
            label.bind("<Button-1>", partial(self.on_schema_press, tag=self.tag_koma, label=label, key=key))
            self.canvas.create_window(canvas_label_x, canvas_label_y, anchor="nw", window=label, tag=self.koma)
            koma_message[key] = value 
        self.tags_and_messages[self.tag_koma] = koma_message


    def menu1_koma(self, event):
        menu = tk.Menu(self.canvas, tearoff=0)
        menu.add_command(label="コマを削除する", command=self.delete_koma)
        menu.post(event.x_root, event.y_root)
    
    def menu2_koma(self, event):
        menu = tk.Menu(self.canvas, tearoff=0)
        menulabels = ['ライトブルー', 'ピンク', 'レモン', 'ラベンダー']
        bgcolors = ['lightblue', 'pink', 'lemon chiffon', 'lavender']
        for i,c in enumerate(bgcolors):
            menu.add_command(label=menulabels[i], command=lambda c=c: self.setupcolor_koma(c))
        menu.post(event.x_root, event.y_root)

    def menu_canvas(self, event):
        menu = tk.Menu(self.canvas, tearoff=0)
        menu.add_command(label="コマを追加する", command=lambda: self.add_koma(event))
        menu.post(event.x_root, event.y_root)
    
    def add_koma(self, event):
        # 現状はself.komasをコマの追加削除で編集していないのであまり意味がないself.pagesもしかり
        tags_koma = self.get_tags_koma()
        self.all_koma = len(tags_koma) + 1
        last_tagkoma = tags_koma[-1]
        last_komanum = ''.join(re.findall(r'\d+', last_tagkoma))
        k = int(last_komanum) + 1 #一番後ろのコマにするには?
        koma = Koma(self.canvas, event.x, event.y, 100, 100, k, self.all_koma, self.tags_and_messages, self.Labels, 'lightblue')

    def delete_koma(self):
        
        # 矩形を削除
        self.canvas.delete(self.rectangle)
        
        # ラベルを削除
        for label in self.schema_labels.values():
            label.destroy()
        
        # Labelsリストから削除
        self.Labels.remove(self.schema_labels)
        
        # 正しいタグを取得
        del_tag_koma = self.tag_koma
        
        # タグが辞書に存在する場合に削除する
        if del_tag_koma in self.tags_and_messages:
            self.tags_and_messages.pop(del_tag_koma)
        
    def setupcolor_koma(self, bgcolor):
        self.canvas.itemconfig(self.rectangle, fill=bgcolor)
        for label in self.schema_labels.values():
            label.config(bg=bgcolor)

    def on_schema_press(self, event, tag, label, key):
        dialog = LabelInputDialog(self.canvas, key, self.schemas[key])
        dialog.transient(self.canvas)  # これで親ウィンドウの手前に表示されるようになる
        dialog.grab_set()  # これでダイアログがアクティブになる
        new_value = dialog.show()
        if new_value is not None:

            self.schemas[key] = new_value
            label.config(text=f'{key}: {new_value}')
            
            bbox = self.canvas.bbox(self.rectangle)
            rect_width = (bbox[2] - bbox[0])  * 0.8
            label.config(width = rect_width)
            
            d = self.tags_and_messages[tag]
            d[key] = new_value
            self.tags_and_messages[tag] = d
         
    def on_press(self, event):
        # マウスイベントの座標をキャンバス内の座標に変換する
        canvas_x = self.canvas.canvasx(event.x)
        canvas_y = self.canvas.canvasy(event.y)
        self.start_x = canvas_x
        self.start_y = canvas_y
        self.resize_point = self.detect_resize_point(canvas_x, canvas_y)

    def on_drag(self, event):
        if self.start_x is not None and self.start_y is not None and self.resize_point is not None:
            current_x, current_y = event.x, event.y
            if self.resize_point == "tl":  # Top Left
                self.canvas.coords(self.rectangle, current_x, current_y, self.canvas.coords(self.rectangle)[2], self.canvas.coords(self.rectangle)[3])
            elif self.resize_point == "tr":  # Top Right
                self.canvas.coords(self.rectangle, self.canvas.coords(self.rectangle)[0], current_y, current_x, self.canvas.coords(self.rectangle)[3])
            elif self.resize_point == "bl":  # Bottom Left
                self.canvas.coords(self.rectangle, current_x, self.canvas.coords(self.rectangle)[1], self.canvas.coords(self.rectangle)[2], current_y)
            elif self.resize_point == "br":  # Bottom Right
                self.canvas.coords(self.rectangle, self.canvas.coords(self.rectangle)[0], self.canvas.coords(self.rectangle)[1], current_x, current_y)
            for key, label in self.schema_labels.items():
                bbox = self.canvas.bbox(self.rectangle)
                rect_height = bbox[3] - bbox[1] 
                label_height = (rect_height - 10) / 2 
                x, y = self.canvas.coords(self.rectangle)[0], self.canvas.coords(self.rectangle)[1]
                label.place(x=x + 5, y=y + 5 + list(self.schema_labels.keys()).index(key) * label_height, anchor="nw")                
                rect_width = (bbox[2] - bbox[0])  * 0.8
                label.config(width = rect_width)

        elif self.start_x is not None and self.start_y is not None:
            diff_x = event.x - self.start_x
            diff_y = event.y - self.start_y
            self.canvas.move(self.rectangle, diff_x, diff_y)
            self.start_x = event.x
            self.start_y = event.y
            # ラベルの位置を再配置
            for key, label in self.schema_labels.items():
                bbox = self.canvas.bbox(self.rectangle)
                rect_height = bbox[3] - bbox[1] 
                label_height = (rect_height - 10) / 2 
                x, y = self.canvas.coords(self.rectangle)[0], self.canvas.coords(self.rectangle)[1]
                label.place(x=x + 5, y=y + 5 + list(self.schema_labels.keys()).index(key) * label_height, anchor="nw")
            
    def on_release(self, event=None):
        self.start_x = None
        self.start_y = None
        self.resize_point = None

    def detect_resize_point(self, x, y):
        # キャンバス内の座標を使用してリサイズポイントを検出する
        bbox = self.canvas.bbox(self.rectangle)
        
        if bbox[0] <= x <= bbox[0] + 10 and bbox[1] <= y <= bbox[1] + 10:
            return "tl"  # Top Left
        elif bbox[2] - 10 <= x <= bbox[2] and bbox[1] <= y <= bbox[1] + 10:
            return "tr"  # Top Right
        elif bbox[0] <= x <= bbox[0] + 10 and bbox[3] - 10 <= y <= bbox[3]:
            return "bl"  # Bottom Left
        elif bbox[2] - 10 <= x <= bbox[2] and bbox[3] - 10 <= y <= bbox[3]:
            return "br"  # Bottom Right
        else:
            return None
    
    def get_tags_koma(self):
        ids = self.canvas.find_all()
        otags = [self.canvas.gettags(id) for id in ids]
        pktags = [tag for tag in otags if tag]
        pktags2 = [item[0] for item in pktags if item[0]] 
        tags_koma = [tag for tag in pktags2 if "koma" in tag]
        return tags_koma
    
    def zoom_in_out_labels(self, event, zoom_factor):
        diff_x = 0
        diff_y = 0
        tags_koma = self.get_tags_koma()
        for i,tag_koma in enumerate(tags_koma):
            self.canvas.move(tag_koma, diff_x, diff_y)
            new_koma_coords = self.canvas.coords(tag_koma)
            for key, label in self.Labels[i].items():

                rect_width = (new_koma_coords[2] - new_koma_coords[0]) * 0.8
                label.config(width = rect_width)

                rect_height =  new_koma_coords[3] -  new_koma_coords[1]
                label_height = (rect_height - 10) / 2 
                canvas_label_x = new_koma_coords[0] + 5
                canvas_label_y = new_koma_coords[1] + 5 + list(self.schema_labels.keys()).index(key) * label_height
                label.place(x=canvas_label_x, y=canvas_label_y, anchor="nw")
                
                current_font = label['font']
                #print(current_font)
                current_size = int(re.sub(r"\D", "", current_font))
                #print(current_size)
                if zoom_factor==1.1:
                    if current_size < 12 :
                        new_size = current_size + 1
                        label['font'] = ("Meiryo", new_size)
                    else:
                        label['font'] = ("Meiryo", 12)

                else:
                    if current_size > 6:
                        new_size = current_size - 1
                        label['font'] = ("Meiryo", new_size)
                    else:
                        label['font'] = ("Meiryo", 7)

    def zoom_in_out(self, event):

        if event.delta > 0:
            zoom_factor = 1.1
        elif event.delta < 0:
            zoom_factor = 0.9
        self.canvas.scale("all", event.x, event.y, zoom_factor, zoom_factor)

        return zoom_factor

    def zoom_in_out_combined(self, event):
        zoom_factor = self.zoom_in_out(event)
        self.zoom_in_out_labels(event, zoom_factor)

class NewCreateInputDialog(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)

        self.geometry("380x250")
        self.title("新規作成")

        self.canvas = parent.canvas
        self.fonts = ("Meiryo", 12)

        self.pages = []
        self.komas = []
        self.tags_and_messages = {}

        self.Labels = []

        self.label1 = ctk.CTkLabel(master=self, text="ページ数", font=self.fonts)
        self.label1.grid(row=0, column=0, padx=20, pady=20, sticky="ew")
        self.num_page_entry = ctk.CTkEntry(master=self, placeholder_text="2以上の整数(おすすめ20以下)", width=200)
        self.num_page_entry.grid(row=0, column=1, padx=5, pady=20, columnspan=2, sticky="w")
        
        self.label2 = ctk.CTkLabel(master=self, text="1ページあたりのコマ数", font=self.fonts)
        self.label2.grid(row=1, column=0, padx=20, pady=15, sticky="ew") 
        self.num_koma_entry = ctk.CTkEntry(master=self, placeholder_text="1以上の整数(おすすめ4~5)", width=200)
        self.num_koma_entry.grid(row=1, column=1, padx=5, pady=15, columnspan=2, sticky="w")

        self.radio_var = tk.IntVar(value=1)
        self.rbtnlab = ctk.CTkLabel(master=self, text="ページはじまり", font=self.fonts)
        self.rbtnlab.grid(row=2, column=0, padx=20, pady=15, sticky="ew")
        self.rbtn1 = ctk.CTkRadioButton(master=self, text="左", variable=self.radio_var, value=1)
        self.rbtn2 = ctk.CTkRadioButton(master= self, text="右", variable=self.radio_var, value=2)
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
        num_page = self.num_page_entry.get()
        num_koma = self.num_koma_entry.get()
        start_page = self.radio_var.get()

        try:
            num_page = int(num_page)
        except:
            pass

        try:
            num_koma = int(num_koma)
        except:
            pass

        start_page = int(start_page)
            
        try:
            if num_page < 2 or num_koma < 1:
                raise TypeError("新規ファイルは作成されませんでした。")
            self.create_file(num_page, num_koma, start_page)
            self.destroy()
        except TypeError:
            if isinstance(num_page, str):
                self.label1.configure(text="ページ数\n!半角の整数を入力")
            elif num_page < 2:
                self.label1.configure(text="ページ数\n!2以上の整数を入力")
            else:
                self.label1.configure(text="ページ数")
                
            if isinstance(num_koma, str):
                self.label2.configure(text="1ページあたりのコマ数\n!半角の整数を入力")
            elif num_koma < 1:
                self.label2.configure(text="1ページあたりのコマ数\n!1以上の整数を入力")
            else:
                self.label2.configure(text="1ページあたりのコマ数")
        
            print("新規ファイルは作成されませんでした。")

    def create_file(self, num_page, num_koma, start_page):

        self.all_koma = num_koma * num_page

        if start_page == 1:

            if num_page <= 3:
                firstrowpages = num_page
                lastrowpages = 0
            else:
                firstrowpages = 3    
                lastrowpages = (num_page + 1) % 4

            rows = (num_page + 1) // 4

            p = 0

            for col in range(firstrowpages):
                p += 1
                if col == 0:
                    page = Page(self.canvas, 700 - (300 * col), 10, 300, 420, p)
                    self.pages.append(page)
                else:
                    page = Page(self.canvas, 650 - (300 * col), 10, 300, 420, p)
                    self.pages.append(page)
            for row in range(1,rows):
                for col in range(2):
                    p += 1
                    page = Page(self.canvas, 1000 - (300 * col), 10 + (row * 470), 300, 420, p)
                    self.pages.append(page)
                for col in range(2):
                    p += 1
                    page = Page(self.canvas, 350 - (300 * col), 10 + (row * 470), 300, 420, p)
                    self.pages.append(page)
            for col in range(lastrowpages):
                p +=1
                if col <= 1:
                    page = Page(self.canvas, 1000 - (300 * col), 10 + (rows * 470), 300, 420, p)
                    self.pages.append(page)
                else:
                    page = Page(self.canvas, 950 - (300 * col), 10 + (rows * 470), 300, 420, p)
                    self.pages.append(page)

            k = -1
            
            for col in range(firstrowpages):
                    for pk in range(num_koma):
                        k += 1
                        if col == 0:
                            koma = Koma(self.canvas, 800 -(300 * col), 10 + (pk * 100), 100, 100, k, self.all_koma, self.tags_and_messages, self.Labels, 'lightblue')
                            self.komas.append(koma)
                        else:
                            koma = Koma(self.canvas, 750 -(300 * col), 10 + (pk * 100), 100, 100, k, self.all_koma, self.tags_and_messages, self.Labels, 'lightblue')
                            self.komas.append(koma)
            for row in range(1,rows):
                for col in range(2):
                    for pk in range(num_koma):
                        k += 1
                        koma = Koma(self.canvas, 1100 -(300 * col), 10 + (pk * 100) + (row * 470), 100, 100, k, self.all_koma, self.tags_and_messages, self.Labels, 'lightblue')
                        self.komas.append(koma)
                for col in range(2):
                    for pk in range(num_koma):
                        k += 1
                        koma = Koma(self.canvas, 450 -(300 * col), 10 + (pk * 100) + (row * 470), 100, 100, k, self.all_koma, self.tags_and_messages, self.Labels, 'lightblue')
                        self.komas.append(koma)
            for col in range(lastrowpages):
                for pk in range(num_koma):
                    k +=1
                    if col <= 1:
                        koma = Koma(self.canvas, 1100 -(300 * col), 10 + (pk * 100) + (rows * 470), 100, 100, k, self.all_koma, self.tags_and_messages, self.Labels, 'lightblue')
                        self.komas.append(koma)
                    else:
                        koma = Koma(self.canvas, 1050 -(300 * col), 10 + (pk * 100) + (rows * 470), 100, 100, k, self.all_koma, self.tags_and_messages, self.Labels, 'lightblue')
                        self.komas.append(koma)
                    
        else:
            lastrowpages = num_page % 4

            rows = num_page // 4

            p = 0

            for row in range(rows):
                for col in range(2):
                    p += 1
                    page = Page(self.canvas, 1000 - (300 * col), 10 + (row * 470), 300, 420, p)
                    self.pages.append(page)
                for col in range(2):
                    p += 1
                    page = Page(self.canvas, 350 - (300 * col), 10 + (row * 470), 300, 420, p)
                    self.pages.append(page)
            for col in range(lastrowpages):
                    p +=1
                    if col <= 1:
                        page = Page(self.canvas, 1000 - (300 * col), 10 + (rows * 470), 300, 420, p)
                        self.pages.append(page)
                    else:
                        page = Page(self.canvas, 950 - (300 * col), 10 + (rows * 470), 300, 420, p)
                        
            
            k = -1
            
            for row in range(rows):
                for col in range(2):
                    for pk in range(num_koma):
                        k += 1
                        koma = Koma(self.canvas, 1100 -(300 * col), 10 + (pk * 100) + (row * 470), 100, 100, k, self.all_koma, self.tags_and_messages, self.Labels, 'lightblue')
                        self.komas.append(koma)
                for col in range(2):
                    for pk in range(num_koma):
                        k += 1
                        koma = Koma(self.canvas, 450 -(300 * col), 10 + (pk * 100) + (row * 470), 100, 100, k, self.all_koma, self.tags_and_messages, self.Labels, 'lightblue')
                        self.komas.append(koma)      
            for col in range(lastrowpages):
                for pk in range(num_koma):
                    k +=1
                    if col<= 1:
                        koma = Koma(self.canvas, 1100 -(300 * col), 10 + (pk * 100) + (rows * 470), 100, 100, k, self.all_koma, self.tags_and_messages, self.Labels, 'lightblue')
                        self.komas.append(koma)
                    else:    
                        koma = Koma(self.canvas, 1050 -(300 * col), 10 + (pk * 100) + (rows * 470), 100, 100, k, self.all_koma, self.tags_and_messages, self.Labels, 'lightblue')
                        self.komas.append(koma)

    def get_new_information(self):
        return self.tags_and_messages

class LabelInputDialog(ctk.CTkToplevel):
    def __init__(self, parent, key, initial_value):
        super().__init__(parent)
        self.geometry("250x140")
        self.title("スキーマの編集")

        self.key = key

        self.lab = ctk.CTkLabel(master=self, text=f"{key}:")
        self.lab.pack(padx=10, pady=10)

        self.entry = ctk.CTkEntry(master=self, width=150)
        self.entry.pack(padx=10, pady=5)
        self.entry.insert(0, initial_value)

        self.new_value = None  # 新しい値を保持するための変数を初期化

        self.btn = ctk.CTkButton(master=self, text="OK", command=self.ok_button_click)
        self.btn.pack(padx=10, pady=10)

    def ok_button_click(self):
        self.new_value = self.entry.get()  # 新しい値を取得
        self.destroy()

    def show(self):
        self.wait_window()
        return self.new_value  # 新しい値を返す
    
    def id(self):
        self.wait_window()
        return self.new_value  # 新しい値を返す