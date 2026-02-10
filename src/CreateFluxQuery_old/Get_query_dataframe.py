import os
import pandas as pd
import openpyxl
import numpy as np
from CreateFluxQuery.Parameter import EXCEL_PATH, TAB

class GetQueryDataframe:
    def __init__(self):
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

        # 検索条件
        self.search_units = pd.DataFrame({
                        "項番":pd.Series(dtype="str"),
                        "処理":pd.Series(dtype="str"),
                        "説明":pd.Series(dtype="str")
                    })

        # 出力項目の集計処理
        self.query_elem = pd.DataFrame({ 
                        "項番":                  pd.Series(dtype="str"),
                        "OUTPUT_CSV項目":        pd.Series(dtype="str"),
                        "CSVヘッダ":             pd.Series(dtype="str"),
                        "INPUT_入力データ物理名": pd.Series(dtype="str"),
                        "INPUT_項目名":          pd.Series(dtype="str"),
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
        row_num = self.query_dataframe.index[self.query_dataframe[target_col] == "INPUT情報"][0]
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
        row_num = self.query_dataframe.index[self.query_dataframe[1] == "OUTPUT CSV出力項目の集計処理"].tolist()

        cnt = row_num[0]+3
        while True:
            num = self.query_dataframe.iloc[cnt][1] # B列: 項番
            value = self.query_dataframe.iloc[cnt][2] # C列: OUTPUT CSV項目
            header = self.query_dataframe.iloc[cnt][3] # D列: CSVヘッダ
            input_data = self.query_dataframe.iloc[cnt][4] # E列: INPUT入力データ物理名
            input_name = self.query_dataframe.iloc[cnt][5] # F列: INPUT項目名
            # else: # {数字}_ヘッダ名 の形式になっていなければスキップ（TODO: どういう表を作るのかわかっていないので確認する）
            #     cnt += 1
            #     continue           
            if self.query_dataframe.isna().iloc[cnt][6]: # G列: 処理
                if len(self.query_elem) == 0: # 先頭が空の場合
                    exec = "-"
                else:
                    exec = self.query_elem.iloc[-1]["処理"] #　NaNなら一つ上の内容と同値とする 
            else:
                exec = self.query_dataframe.iloc[cnt][6]

            if self.query_dataframe.isna().iloc[cnt][11]: # L列: 説明 
                if len(self.query_elem) == 0:# 先頭が空の場合
                    explain = "-"
                else:
                    explain = self.query_elem.iloc[-1]["説明"] #　NaNなら一つ上の内容と同値とする 
            else:
                explain = self.query_dataframe.iloc[cnt][11]

            self.query_elem.loc[len(self.query_elem)] = [ num, value, header, input_data, input_name, exec, explain ]   

            cnt += 1
            if self.query_dataframe.isna().iloc[cnt][1]: # 次行がNaNなら,ヘッダ対象外の項目を省いて終わり 
                self.query_sub_elem = self.query_elem[self.query_elem["CSVヘッダ"].astype(str).str.match(r"^(?!\d{2}_).*", na=False) ].copy()
                self.query_elem     = self.query_elem[self.query_elem["CSVヘッダ"].astype(str).str.match(r"^\d{2}_.*", na=False)] # {数字2桁}_*の形式のもののみ残す
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
