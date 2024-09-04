## MOJINE_semipro_beta バージョン1.0.0-beta.1　ビルド手順

### 必要なツール
- Python 3.12
- Nuitka
- その他の依存ライブラリ（[requirements.txt](requirements.txt)参照）

### 環境設定
1. リポジトリをクローンします。
   ```bash
   git clone https://github.com/utenmato/MOJINE_semipro_beta.git
   cd yourrepository
   ```
2. 必要なパッケージをインストールします。
   ```bash
   pip install customtkinter==5.2.2 Nuitka==2.4.8 numpy==2.0.1 pandas==2.2.2 pillow==10.4.0
   ```

### ビルド手順
1. リポジトリに保存されているビルド用のバッチファイルを実行します。
   ```bash
   .\build.bat
   ```
### 注意点
- 環境によっては、依存関係のインストールやビルド手順が異なる場合があります。
