import re

##### PARAMETER
# 必要に応じて編集
# EXCEL_PATH = "設計Sample.xlsx"
EXCEL_PATH = "クエリー設計_20260129.xlsx"
MANUAL_CREATE = "【要確認】"         # 手動対応が必要な箇所にコメントで残す文字列
MISSING_VALUE = "【NONE】"          # Excelを読み込んだ際の空のセルを埋める文字列
TAB_SPACE = "    "                  # 出力ファイルのTab

# 固定
IMPORT_MATH = "// import \"math\""
IMPORT_STRINGS = "// import \"strings\""
IMPORT_REGEXP = "// import \"regexp\""
IMPORT_DATE = "// import \"date\""

# 複数タブ打つとき用
def TAB(n: int):
    return TAB_SPACE * n

def COMMENT_IN(imp:str):
    return re.sub(r'^\s*//\s*', '', imp)