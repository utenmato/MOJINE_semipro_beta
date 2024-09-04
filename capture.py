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
from PIL import Image, ImageDraw, ImageFont
import os
import main
import json

class ExportCapture():
    def __init__(self, parent, savejson):

        self.savefilename = savejson.get_savefile()
        self.parent = parent
        self.canvas = parent.canvas

        self.pages_data = []
        self.komas_data = []

        try:
            with open(self.savefilename, 'r', encoding='utf-8') as file:
                data = json.load(file)
        except FileNotFoundError:
            dialog = main.MessageDialog(self.parent, 13)
            dialog.transient(self.parent)  # これで親ウィンドウの手前に表示されるようになる
            dialog.grab_set()  # これでダイアログがアクティブになる
        
        for page_info in data['pages']:
            self.pages_data.append([page_info['x'], page_info['y'], page_info['x'] + page_info['width'] , page_info['y'] + page_info['height'] , page_info['width'] , page_info['height'], page_info['page']])
        
        for koma_info in data['komas']:
            self.komas_data.append([koma_info['x'], koma_info['y'], koma_info['x'] + koma_info['width'] , koma_info['y'] + koma_info['height'], koma_info['width'], koma_info['height'], koma_info['bgcolor'], koma_info['tag']],)
        
        self.tags_and_messages = data['tags_and_messages']
        
        self.image_from_json()

    def image_from_json(self):
        try:
            # 画像保存先のフォルダを選択
            self.folder_path = filedialog.askdirectory(title="画像保存先のフォルダを選択")
            
            # キャンセルボタンが押された場合、FileNotFoundErrorを発生させる
            if not self.folder_path:
                raise FileNotFoundError("PNG画像は出力されませんでした。")
            else:
                self.save_pages_as_images()
                
        except FileNotFoundError:
            print("PNG画像は出力されませんでした。")

    def save_pages_as_images(self):
        target_height = 1000  # 目標の高さを1000ピクセルに設定

        # 日本語フォントを読み込む
        try:
            font_path = "C:\\Windows\\Fonts\\msgothic.ttc"  # フォントの正しいパスを指定
            font = ImageFont.truetype(font_path, int(16))  # フォントサイズもスケーリング
        except IOError:
            font = ImageFont.load_default()  # 指定したフォントが見つからない場合、デフォルトのフォントを使用

        for page in self.pages_data:
            # ページの境界ボックスを取得
            page_x1 = page[0]
            page_y1 = page[1]
            page_x2 = page[2]
            page_y2 = page[3]
            page_width = page[4]
            page_height = page[5]
            page_num = page[6]

            # スケーリングファクターを計算（高さを850pxに固定）
            scale_factor = target_height / page_height
            scaled_width = int(page_width * scale_factor)
            scaled_height = int(page_height * scale_factor)

            # PillowのImageオブジェクトを作成（スケーリング後のサイズで）
            image = Image.new("RGB", (scaled_width, scaled_height), "white")
            draw = ImageDraw.Draw(image)

            # ページ境界の描画（スケーリング後のサイズで）
            draw.rectangle([0, 0, scaled_width, scaled_height], outline='black', width=1)

            for koma in self.komas_data:
                koma_x1 = koma[0]
                koma_y1 = koma[1]
                koma_x2 = koma[2]
                koma_y2 = koma[3]
                koma_width = koma[4]
                koma_bgcolor = koma[6]
                tag_koma = koma[7]

                rgb_tuple_16bit = self.canvas.winfo_rgb(koma_bgcolor)
                # 16ビット（0-65535）から8ビット（0-255）に変換
                rgb_tuple_8bit = tuple([int(x / 256) for x in rgb_tuple_16bit])

                # Pillowで使えるように、'#RRGGBB'形式の文字列に変換する場合
                hex_color = '#{:02x}{:02x}{:02x}'.format(*rgb_tuple_8bit)

                # Komaがページ内に存在するか確認
                if (page_x1 <= koma_x1 <= page_x2) and (page_y1 <= koma_y1 <= page_y2):
                    # ページ内でのKomaの相対位置を計算し、スケーリング
                    relative_x1 = int((koma_x1 - page_x1) * scale_factor)
                    relative_y1 = int((koma_y1 - page_y1) * scale_factor)
                    relative_x2 = int((koma_x2 - page_x1) * scale_factor)
                    relative_y2 = int((koma_y2 - page_y1) * scale_factor)

                    # Komaの描画
                    draw.rectangle([relative_x1, relative_y1, relative_x2, relative_y2], fill=hex_color, outline='black', width=1)

                    # Koma内のテキスト（例としてセリフ）を描画
                    text1 = f"セリフ: {self.tags_and_messages[tag_koma]['セリフ']}"
                    text2 = f"カット: {self.tags_and_messages[tag_koma]['カット']}"
                    text1_x = relative_x1 + 5
                    text1_y = relative_y1 + 5
                    text2_x = relative_x1 + 5
                    text2_y = (relative_y1 + relative_y2) / 2
                    koma_width = koma_width * scale_factor - 10
                    self.draw_text_with_wrap(draw, text1, position=(text1_x, text1_y), font=font, max_width=koma_width)
                    self.draw_text_with_wrap(draw, text2, position=(text2_x, text2_y), font=font, max_width=koma_width)

            # 画像の保存
            filename = f"{page_num}ページ.png"
            full_path = os.path.join(self.folder_path, filename)
            image.save(full_path, dpi=(600, 600))

        dialog = main.MessageDialog(self.parent, 22)
        dialog.transient(self.parent)  # これで親ウィンドウの手前に表示されるようになる
        dialog.grab_set()  # これでダイアログがアクティブになる

    def draw_text_with_wrap(self, draw, text, position, font, max_width, fill='black'):
        lines = []
        line = ''
        
        # 日本語を考慮して、単語ではなく文字単位で分割する
        for char in text:
            # 新しい行を試しに作成してみる
            test_line = f'{line}{char}'
            
            # テキストの幅を取得
            width = font.getbbox(test_line)[2]
            
            # 指定された幅内に収まる場合、そのまま行に追加
            if width <= max_width:
                line = test_line
            else:
                # 収まらない場合、現在の行を確定し、新しい行を作成
                lines.append(line)
                line = char
        
        # 最後の行を追加
        lines.append(line)
        
        x, y = position
        for line in lines:
            draw.text((x, y), line, font=font, fill=fill)
            # 行ごとに高さを加算
            y += font.getbbox(line)[3] - font.getbbox(line)[1]
