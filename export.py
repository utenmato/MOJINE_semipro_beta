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

from tkinter import filedialog
import json
import pandas as pd
import main

class ExpotCsv():
    def __init__(self, parent, savejson):

        self.savefilename = savejson.get_savefile()
        self.parent =  parent

        self.exportfilename = filedialog.asksaveasfilename(
        title = "名前を付けてcsvファイルを書き出し",
        initialdir = "./", # 自分自身のディレクトリ
        filetypes = [("CSV files", "*.csv")]
        )
        print(self.exportfilename)

        # ファイル名に拡張子がなければ、手動で追加する
        if not self.exportfilename.endswith(".csv"):
            self.exportfilename += ".csv"
        
        if self.exportfilename == ".csv":
            pass
        else:
            self.export_to_csv()

    def export_to_csv(self):
        try:
            with open(self.savefilename, 'r', encoding='utf-8') as file:
                data = json.load(file)

            self.tags_and_messages = data['tags_and_messages']

            self.page_gloup = []
            self.koma_xy = []
            self.page_koma = {}

            
            for page_info in data['pages']:
                self.page_gloup.append([page_info['x'], page_info['x'] + page_info['width'], page_info['y'], page_info['y'] + page_info['height'], page_info['tag']])

            
            for koma_info in data['komas']:
                self.koma_xy.append([koma_info['x'], koma_info['y'], koma_info['tag']])

            for page in self.page_gloup:
                list1 = []
                for koma in self.koma_xy:
                    if page[0] <= koma[0] <= page[1] and page[2] <= koma[1] <= page[3]:
                        list1.append(koma[2])
                        self.page_koma[page[4]] = list1

            for page in self.page_koma:
                for i,koma in enumerate(self.page_koma[page]):
                    komas = self.page_koma[page]
                    messages = self.tags_and_messages[koma]
                    dialogs = messages['セリフ']
                    list2 = dialogs.split('/')

                    cuts = messages['カット']
                    list3 = []

                    for l in list2:
                        if '=' in l:
                            split_l = l.split('=', maxsplit=1)
                            list3.append(split_l[1])
                        else:
                            list3.append(l)

                    dialog = "\n\n".join(list3)
                    komas[i] = dialog

            for page in self.page_koma:
                list4 = [a for a in self.page_koma[page] if a != '']
                self.page_koma[page] = list4

            for page in self.page_koma:
                komas = self.page_koma[page]
                dialogs = "\n\n".join(komas)
                self.page_koma[page] = dialogs

            export_df = pd.DataFrame.from_dict(self.page_koma, orient="index", columns=["セリフ"])

            export_df.to_csv(self.exportfilename, encoding="shift-jis")

            msdialog = main.MessageDialog(self.parent, 21)
            msdialog.transient(self.parent)  # これで親ウィンドウの手前に表示されるようになる
            msdialog.grab_set()  # これでダイアログがアクティブになる

        except FileNotFoundError:
            # ファイルが見つからない場合のエラーハンドリング
            print("csvファイルは出力されませんでした。")