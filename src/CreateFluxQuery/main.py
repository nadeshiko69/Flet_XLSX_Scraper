##### 事前準備
'''
・excel読み込み用に必要なパッケージがあるのでインストール
　pip install openpyxl (もしくはpip install -r requirement.txt)
 
・同階層に設計のExcelが格納されていることを確認
'''
##### 実行
'''
python main.py <Excelシート名に記載のクエリ番号>

python main.py 1-1
python main.py 1-1 1-2 1-3 #複数を連続で生成する場合
'''

import argparse
import sys
import pandas as pd
from Get_query_dataframe import GetQueryDataframe
from Get_template_parameter import TemplateParameter
from Make_Flux_File import MakeFluxFile
from Parameter import EXCEL_PATH, TAB

pd.set_option('display.unicode.east_asian_width', True) # 出力時のための成型

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("query_num", nargs='*', help="xlsxのシート名に記載のクエリ番号")
    # parser.add_argument("-p", "--path", help="xlsxのパス", default="")
    args = parser.parse_args()
    
    query_num = args.query_num
    
    for num in query_num:
        print(f"{num} ##### Start Creatinge Flux File")
        # インスタンス
        query_dataframe = GetQueryDataframe()
        flux_flie = MakeFluxFile()
        template_parameter = TemplateParameter()
        
        query_dataframe.exec_func(num, EXCEL_PATH)      # Excelから必要情報を取得
        template_parameter.exec_func(query_dataframe)   # 取得した情報からTemplate用の情報を抽出
        flux_flie.exec_func(num, template_parameter)   # 取得した情報からfluxファイルを出力
        
        print(f"{TAB(1)}Complete. : output/{template_parameter.output_filename}")
    
    
    
if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"###### Failed: {e} #####", file=sys.stderr)
        sys.exit(1)
