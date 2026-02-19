# Flet app


## 構成
```
FLET_XLSX_SCRAPER/
├─ src
│       handlers.py : UI操作時の処理
│       main.py     : flet runで実行される
│       utility.py  : UI初期化など
│
├─ assets
│       icon.png            : 変更すればビルド時のアイコン変更？
│       splash_android.png
│
└─ CreateFluxQuery
        Get_query_dataframe.py     : Excel → Dataframe変換
        Get_template_parameter.py  : Dataframe → Parameter変換
        main.py                    : GUI化前に使用していた、メンテしていない
        Make_Flux_File.py          : TemplateにParameterを適用
        Parameter.py               : 内部処理で使用するパラメータなど
        Template                   : 出力するFluxファイルのテンプレート
```

## 起動方法
### ビルドせずに実行する場合
※Windows環境を想定

``` bash
# 仮想環境作成
python -m venv venv
.\venv\Scripts\activate
pip install -r requirement.txt
# 実行
flet run
```
### ビルド方法(Visual Studioが必要、未実施)
``` bash
# 仮想環境作成までは同じ
python -m venv venv
.\venv\Scripts\activate
pip install -r requirement.txt

# ビルド
flet build windows
# exeファイルが作成されるので実行する
```

## GUI使い方
![image001](./readme_image/001.png)
左上「Open Excel」をクリック、読み込みたいExcel設計を選択

![image002](./readme_image/002.png)
Excelのシート名を列挙したドロップダウンが表示されるので、作成したいクエリを選択→右側の「Read」をクリック

![image003](./readme_image/003.png)
左側に、シートの「OUTPUT CSV出力項目ごとの集計処理」の表を読み込んだ結果が表示される  
（表示内容はCSVヘッダ、集計のキー、入力データ物理名、処理、に限定）

表示内容を確認して、問題なければ左下「Create Flux」をクリック
#### ※確認観点
- START_UTC、STOP_UTCが期待の値か（書き換え可能）
- 子クエリ作成対象の項目に過不足ないか（チェックボックスにより変更可能）
- 入力データ物理名に不備はないか（書き換え可能）

![image004](./readme_image/004.png)
右側に生成されたFluxクエリを表示  
左を修正して再度「Create Flux」すれば再生成可能  

問題なければ、右下の「Copy」でクリップボードにコピー、もしくは「Save File」でファイル保存（デフォルトのファイル名はExcel上の「Fluxクエリーファイル名」に準拠）

## 注意点
- 上手くクエリ生成できなかった部分は【要確認】と表示されるので、手動で修正（表示されるテキストを変更したければ、src/CreateFluxQuery/Parameter.pyの定義を変更）
- Excel上で非表示にされているセルも読み込んでしまうため注意。非表示を使わないor実行前に確認して削除