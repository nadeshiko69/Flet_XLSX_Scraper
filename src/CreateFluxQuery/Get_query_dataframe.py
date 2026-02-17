import os
import pandas as pd
import openpyxl
import numpy as np
from CreateFluxQuery.Parameter import EXCEL_PATH, TAB

class GetQueryDataframe:
    def __init__(self):
        self.query_num:str
        self.query_dataframe:pd.DataFrame
        # クエリ情報
        self.query_info = {
                        "取得内容":str,
                        "Fluxクエリーファイル名":str,
                        "元情報":str,
                        "帳票ファイル作成単位":str,
                        "元情報取得対象日":str,
                        "集計タイミング":str,
                        "バケット":str,
                        "集計タグ":str,                 # G列
                        "元情報取得対象時間":str,        # G列
                        "集計時間単位":str,             # G列
                        "メジャメント":str              # G列
                    }

        self.input_info:list = [] # INPUT情報
        self.output_info:list = [] # CSV出力項目
        
        self.child_query_target:list = []

        # 検索条件
        self.search_units = pd.DataFrame({
                        "項番":pd.Series(dtype="str"),
                        "処理":pd.Series(dtype="str"),
                        "説明":pd.Series(dtype="str")
                    })

        # 出力項目の集計処理
        self.query_elem = pd.DataFrame({ 
                        "項番":                  pd.Series(dtype="str"),
                        "OUTPUT CSV項目":        pd.Series(dtype="str"),
                        "CSVヘッダ":             pd.Series(dtype="str"),
                        "集計のキー":              pd.Series(dtype="str"), # 3-XX以降のみ存在
                        "入力データ物理名": pd.Series(dtype="str"),
                        "項目名":          pd.Series(dtype="str"),
                        "処理":                  pd.Series(dtype="str"),
                        "説明":                  pd.Series(dtype="str")
                        })
        # query_elemのcolumnkeyに該当しないもの（subtitle的なやつ）
        self.query_sub_elem = pd.DataFrame({ 
                        "項番":                  pd.Series(dtype="str"),
                        "OUTPUT_CSV項目":        pd.Series(dtype="str"),
                        "CSVヘッダ":             pd.Series(dtype="str"),
                        "INPUT_入力データ物理名": pd.Series(dtype="str"),
                        "INPUT_項目名":          pd.Series(dtype="str"),
                        "処理":                  pd.Series(dtype="str"),
                        "説明":                  pd.Series(dtype="str")
                        })

    # Excelから必要な情報を抽出してDetaFrameを返す
    def get_query_dataframe(self, query_num:str, excel_path: str=""):
        self.query_num=query_num
        if excel_path == "":
            excel_path = EXCEL_PATH
        if not os.path.isfile(excel_path):
            raise FileNotFoundError(f"ファイルが見つかりません: {excel_path}")
        try:
            wb = openpyxl.load_workbook(excel_path, read_only=True)
            sheet_name = [name for name in wb.sheetnames if query_num in name][0] # クエリ番号と部分一致するシート名を検索
            df = pd.read_excel(excel_path, sheet_name, dtype=str, header=None)
            return df
        except Exception as e:
            print(f"Excelファイルの読み込み中にエラーが発生しました: {e}")
            return None

    # クエリの情報を取得
    def get_query_information(self):
        target_col = 1 # B列
        value_col = 3 # D列
        for key in self.query_info:
            if key == "集計タグ":
                target_col = 6 # G列
                value_col = 9 # J列
            row_num = self.query_dataframe.index[self.query_dataframe[target_col] == key].tolist()
            value = self.query_dataframe.iloc[row_num][value_col].iloc[0] # D列orJ列から探索
            self.query_info[key] = value

    def get_input_output_info(self):
        target_col = 1 # B列
        value_col = 3 # D列
        
        
        s = self.query_dataframe[target_col]  # Series
        mask = s.astype("string").str.contains("INPUT情報", regex=False, na=False)

        # row_num = self.query_dataframe.index["INPUT情報" in self.query_dataframe[target_col]][0]
        
        if mask.any():
            row_num = int(np.flatnonzero(mask.to_numpy())[0])  # 例: 0,1,2,...
        else:
            row_num = None

        # input_info作成
        self.input_info.append(self.query_dataframe.iloc[row_num][value_col])
        row_num += 1
        while self.query_dataframe.iloc[row_num][target_col] is np.nan:
            self.input_info.append(self.query_dataframe.iloc[row_num][value_col])
            row_num += 1

        # output_info作成
        self.output_info.append((
            self.query_dataframe.iloc[row_num][value_col],
            # self.query_dataframe.iloc[row_num][value_col+1]
        ))
        row_num += 1
        while self.query_dataframe.iloc[row_num][target_col] is np.nan:
            self.output_info.append((
                self.query_dataframe.iloc[row_num][value_col],
                # self.query_dataframe.iloc[row_num][value_col+1] # 右隣列にr, c, vのいずれかを記載しておく
            ))
            row_num += 1

    # 検索条件を取得
    def get_search_units(self):
        row_num = self.query_dataframe.index[self.query_dataframe[1] == "検索条件"].tolist()
        cnt = row_num[0]+2
        while True:
            num = self.query_dataframe.iloc[cnt][1] # B列
            value = self.query_dataframe.iloc[cnt][2] # C列
            explain = self.query_dataframe.iloc[cnt][3] # D列

            self.search_units.loc[len(self.search_units)] = [ num, value, explain ]   

            cnt += 1
            if self.query_dataframe.isna().iloc[cnt][1]: # 次行がNaNなら終わり
                break 

    # クエリの出力項目を取得
    def get_query_elem(self):
        row_num = self.query_dataframe.index[self.query_dataframe[1] == "OUTPUT CSV出力項目毎の集計処理"].tolist()[0] # query_elemを取得し始める行番号
        end_num = self.query_dataframe.index[self.query_dataframe[1] == "OUTPUTイメージ"].tolist()[0]-2 # query_elemを取得し終わる行番号

        # 列名を2行分チェック
        row_title_1 = self.query_dataframe.iloc[row_num+1]
        row_title_2 = self.query_dataframe.iloc[row_num+2]
              
        init_num = row_num+3
        cnt = init_num
        while True:
            tmp_list = [] # query_elemの各列の値をquery_dataframeの何列目から取得するか
            for row_name in self.query_elem:
                if row_name in row_title_1.values:
                    col_idx = int(row_title_1[row_title_1 == row_name].index[0])
                elif row_name in row_title_2.values:
                    col_idx = int(row_title_2[row_title_2 == row_name].index[0])
                else:
                    col_idx = None
                    pass
                tmp_list.append((row_name, col_idx))
            tmp_dict = dict(tmp_list)
            num = self.query_dataframe.iloc[cnt][tmp_dict.get('項番')]
            value = self.query_dataframe.iloc[cnt][tmp_dict.get('OUTPUT CSV項目')]
            header = self.query_dataframe.iloc[cnt][tmp_dict.get('CSVヘッダ')]
            input_data = self.query_dataframe.iloc[cnt][tmp_dict.get('入力データ物理名')]
            input_name = self.query_dataframe.iloc[cnt][tmp_dict.get('項目名')]
            exec = self.query_dataframe.iloc[cnt][tmp_dict.get('処理')]
            explain = self.query_dataframe.iloc[cnt][tmp_dict.get('説明')]
            
            if input_data.startswith("f_"):
                self.child_query_target.append(cnt - init_num) # GUI上でチェックをつけておく行数を記憶
            
            row = pd.Series({
                "項番": num,
                "OUTPUT CSV項目": value,
                "CSVヘッダ": header,
                "入力データ物理名": input_data,
                "項目名": input_name,
                "処理": exec,
                "説明": explain,
            })
            self.query_elem.loc[len(self.query_elem)] = row
            cnt += 1
            if cnt > end_num:
                # 1-1の33行目みたいなやつを弾きたければここで条件分岐
                break


    def exec_func(self, query_num:str, excel_path:str):
        print(f"{TAB(1)}Get Query Information")
        
        self.query_dataframe = self.get_query_dataframe(query_num, excel_path)
        self.get_query_information()
        self.get_input_output_info()
        self.get_search_units()
        self.get_query_elem()
        
        # print(self.input_info, self.output_info)

if __name__ == "__main__":
    from Make_Flux_File import MakeFluxFile
    get_query_information = GetQueryDataframe()
    make_flux_flie = MakeFluxFile() 
    # Excelから必要情報を取得
    get_query_information.exec_func("1-1", EXCEL_PATH)
    # 取得した情報からfluxファイルを出力
    make_flux_flie.exec_func("1-1", get_query_information)
