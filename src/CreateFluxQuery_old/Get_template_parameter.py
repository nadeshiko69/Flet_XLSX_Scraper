
from Get_query_dataframe import GetQueryDataframe
from CreateFluxQuery.Parameter import TAB, MANUAL_CREATE
from datetime import date, timedelta
import CreateFluxQuery.Parameter as p
import pandas as pd
import string
import re
import openpyxl

class TemplateParameter:
    def __init__(self):
        # メンバ変数
        self.query_info:str      = "Query info not found"
        self.query_elem:str      = "Query element not found"
        self.output_filename:str = "Filename not found"
        # base
        self.bucket:str          = ""
        self.start_utc:str       = ""
        self.stop_utc:str        = ""
        self.measurement:str     = ""
        self.tag_filter:str      = ""
        self.field_filter:str    = ""
        self.jst_range_clip:str  = "|> filter(fn: (r) => date.hour(t: r._time) >= $start_time and date.hour(t:r._time <=$stop_time) )"
        # child query
        self.child_query:str     = ""
        self.child_query_name:str= ""
        # pivoted
        self.pivoted_rowkey:str  = ""
        # result
        self.result_group:str    = ""
        self.result_sort:str     = f"/* SORT: {MANUAL_CREATE} */"
        self.result_rename:dict   = {}
        self.result_keep:str     = f"/* KEEP: {MANUAL_CREATE} */"
        self.yield_name:str      = f"/* YIELD: {MANUAL_CREATE} */"

        # 内部処理用
        self.child_query_list:list = []
        self.result_group_list:list
        self.result_sort_list:list
        self.result_keep_list:list
        
        self.regular_query_value = {
                    "NAME":str,
                    "EVERY":str,
                    "FUNC":str,
                    "UNIT":str,
                    "FIELD":str,
                    "KEEP":str
                }

##### BASE作成
    def get_direct_parameter(self, query_dataframe:GetQueryDataframe): # Dataframeの値を直接参照していいパラメータたち
        self.query_info         = str(query_dataframe.query_info)[1:-1].replace(", ", "\n").replace("'", "")
        self.query_elem         = query_dataframe.query_elem.to_string(index=False)
        self.output_filename    = query_dataframe.query_info["Fluxクエリーファイル名"]
        self.measurement        = query_dataframe.query_info["メジャメント"]
        self.bucket             = query_dataframe.query_info["バケット"]
        if re.match(r"^shelty_db/", self.bucket): self.bucket = self.bucket.replace("shelty_db/", "")

    def get_tag_filter(self, query_dataframe:GetQueryDataframe):
        # タグたちのうち、集計タグに記載のあるものを除外して出力
        tags = self.find_matched_element(query_dataframe.query_elem, "INPUT_入力データ物理名", r"^t_.*", True) # タグたち
        agg_tags = re.split(r"[,/、・]", query_dataframe.query_info["集計タグ"]) # TODO: 区切り文字のレパートリーがほかに見つかったら追加
        for at in agg_tags:
            tags = tags.drop(tags[tags["INPUT_項目名"] == at].index) # 値が一致したものはDrop
        if not tags.empty:
            for tag in tags:
                # TODO: タグの検索条件の記載がわかったら加筆
                # |> filter(fn: (r) => r["t_host"] =~ /^w/)
                self.tag_filter = f"{self.tag_filter}|> filter(fn: (r) => r.{tag["INPUT_入力データ物理名"]} == \"{MANUAL_CREATE}\")\n"
        else: self.tag_filter = f""

        self.read_search_units(query_dataframe)
        self.tag_filter = self.tag_filter[:-1]

    def read_search_units(self, query_dataframe:GetQueryDataframe): # 検索条件から必要なフィルタを抽出
        for _, unit in query_dataframe.search_units.iterrows():
            if "チャネル分類が" in unit["処理"]: # チャネル分類シートが確認でき次第更新
                df_channel_category = query_dataframe.get_query_dataframe("チャネル分類")

            if "オンラインの番号がついているレコードのみを対象" in unit["処理"]: # TODO: 他の設計の情報もらい次第改良
                self.tag_filter = f"{self.tag_filter}{TAB(1)}|> filter(fn: (r) => r.t_channel =~ /オンライン/) // 検索条件{unit["項番"]} : {unit["処理"]}\n"

    def get_field_filter(self, query_dataframe:GetQueryDataframe):
        # TODO: 値の範囲の制限とかあれば追加
        fields = self.find_matched_element(query_dataframe.query_elem, "INPUT_入力データ物理名", r"^f_.*", True).drop_duplicates(subset=["INPUT_入力データ物理名"]) # フィールドたち(重複カット)
        if not fields.empty:
            for _, field in fields.iterrows(): 
                self.field_filter = f"{self.field_filter}{TAB(1)}|> filter(fn: (r) => r._field == \"{field["INPUT_入力データ物理名"]}\")\n"
        self.field_filter = self.field_filter[:-1]

    def get_jst_range_clip(self,query_dataframe:GetQueryDataframe):
        if query_dataframe.query_info["元情報取得対象時間"] == "24時間": self.jst_range_clip = f"{TAB(1)}// 元情報取得対象時間 = 24時間のため範囲指定フィルタなし{MANUAL_CREATE}"
        elif  "～" in query_dataframe.query_info["元情報取得対象時間"]:
            start_time = query_dataframe.query_info["元情報取得対象時間"].split("～")[0]
            stop_time  = query_dataframe.query_info["元情報取得対象時間"].split("～")[1] # TODO: あとで別の設計から表記を見る
            tmp = string.Template(self.jst_range_clip)
            self.jst_range_clip = tmp.safe_substitute({ "start_time": start_time, "stop_time": stop_time })
        else: self.jst_range_clip = f"// JST変換後の範囲指定フィルタなし {MANUAL_CREATE}"

    def get_time_parameter(self, query_dataframe:GetQueryDataframe): # Dataframeの値から取得する時間/期間を決定するパラメータを抽出
        # target_date   = query_dataframe.query_info["元情報取得対象日"]
        # target_timing = query_dataframe.query_info["集計タイミング"]
        target_time   = query_dataframe.query_info["元情報取得対象時間"]
        # target_unit   = query_dataframe.query_info["集計時間単位"]
        
        match target_time:
            case "24時間": # TODO: 前日一日分(一昨日15時～昨日15時、JST変換で0時～0時)を取得すると想定,あとで確認
                today = date.today().strftime('%Y-%m-%d')
                yesterday = (date.today() - timedelta(days=1)).strftime('%Y-%m-%d')
                time = "15:00:00"
            case _:
                today = MANUAL_CREATE
                yesterday = MANUAL_CREATE
                time = MANUAL_CREATE
        self.start_utc = f"{yesterday}T{time}Z"
        self.stop_utc  = f"{today}T{time}Z"


##### PIVOTED作成
    # 1時間単位で表示...とかを抽出して子クエリ作成
    def make_regular_query(self, intvl:str, tags:pd.DataFrame):
        temp_content = (                
                        f"$NAME = base // baseを$UNIT単位に$FUNC, Columnの表記を$COLUMNに変更:（{MANUAL_CREATE}） \n"
                        f"{TAB(1)}|> aggregateWindow(every: $EVERY, fn: $FUNC, createEmpty: true)\n"
                        f"{TAB(1)}|> map(fn: (r) => ({{\n"
                        f"{TAB(2)}r with\n"
                        f"{TAB(3)}_time: date.truncate(t: r._time, unit: $UNIT),\n"
                        f"{TAB(3)}_field: strings.joinStr(\n"
                        f"{TAB(4)}arr: $FIELD\n"
                        f"{TAB(4)}sep: \"\"\n"
                        f"{TAB(3)})\n"
                        f"{TAB(2)}}}))\n"
                        f"{TAB(1)}|> fill(column: \"_value\", value: 【欠損補完値】) // {MANUAL_CREATE} 欠損補完値は手動入力\n"
                        f"{TAB(1)}|> keep(columns: $KEEP)\n\n"
                    )
        p.IMPORT_DATE = p.COMMENT_IN(p.IMPORT_DATE)
        match intvl:
            case "10分単位":
                self.regular_query_value = {"NAME":"per10min", 
                                            "EVERY":"10m", 
                                            "FUNC":"sum", # TODO:平均とかの可能性もありそう、なにから情報取得するか検討、手動対応でもいいかも
                                            "UNIT":"1d", 
                                            "COLUMN": "HH:MM",
                                            "FIELD":f"[strings.padLeft(v: string(v: date.hour(t: r._time)),   length: 2, pad: \"0\"), \":\",strings.padLeft(v: string(v: date.minute(t: r._time)), length: 2, pad: \"0\")]",
                                            "KEEP": self.list_to_str_for_flux(["_time","_value","_field"] + tags)
                                            }
                p.IMPORT_STRINGS = p.COMMENT_IN(p.IMPORT_STRINGS)
            case "1時間単位":
                self.regular_query_value = {"NAME":"hourly", 
                                            "EVERY":"1h", 
                                            "FUNC":"sum", # TODO:平均とかの可能性もありそう、なにから情報取得するか検討、手動対応でもいいかも
                                            "UNIT":"1d", 
                                            "COLUMN":"HH:00",
                                            "FIELD":f"[strings.padLeft(v: string(v: date.hour(t: r._time)), length: 2, pad: \"0\"), \":00\"],",
                                            "KEEP": self.list_to_str_for_flux(["_time","_value","_field"] + tags)
                                            }
                p.IMPORT_STRINGS = p.COMMENT_IN(p.IMPORT_STRINGS)
            case "1日単位":
                self.regular_query_value = {"NAME":"daily", 
                                            "EVERY":"1d", 
                                            "FUNC":"sum", # TODO:平均とかの可能性もありそう、なにから情報取得するか検討、手動対応でもいいかも
                                            "UNIT":"1mo", 
                                            "COLUMN":"YYYY/MM/DD",                                   
                                            "FIELD": f"[string(v: date.year(t: r._time)), \"/\",strings.padLeft(v: string(v: date.month(t: r._time)), length: 2, pad: \"0\"), \"/\",strings.padLeft(v: string(v: date.day(t: r._time)),   length: 2, pad: \"0\")],",
                                            "KEEP": self.list_to_str_for_flux(["_time","_value","_field"] + tags)
                                            }
                p.IMPORT_STRINGS = p.COMMENT_IN(p.IMPORT_STRINGS)
            case _:
                self.child_query = f"// {MANUAL_CREATE} : 時間単位を指定するクエリの自動作成なし\n"
                return
        self.child_query_list.append(self.regular_query_value["NAME"])
        tmp = string.Template(temp_content)
        self.child_query = tmp.safe_substitute(self.regular_query_value)

    def make_child_query(self, query_dataframe:GetQueryDataframe, targets:pd.DataFrame, tags:pd.DataFrame): # 子クエリ作成
        query = ""
        # field_names = targets["OUTPUT_CSV項目"]
        temp_content = (
                f"$CHILD_NAME = $NAME\n"
                f"{TAB(1)}|> group(columns: [$GROUP_COL])\n"
                f"{TAB(1)}|> $FUNC\n"
                f"{TAB(1)}|> fill(column: \"_value\", value: 【欠損補完値】) // {MANUAL_CREATE} 欠損補完値は手動入力\n"
                f"{TAB(1)}|> map(fn: (r) => ({{ r with _field: \"$FIELD_NAME\" }}))\n"
                f"{TAB(1)}|> keep(columns: $KEEP_COL)\n\n"
            )
        tmp = string.Template(temp_content)
        for _, target in targets.iterrows():
            # print(target)
            field_name = target["OUTPUT_CSV項目"]
            match query_dataframe.query_info["元情報取得対象時間"]:
                case "1か月間":     unit = "monthly"
                case "24時間":      unit = "daily"
                case "1時間":       unit = "hourly"
                case _:          unit = f"{MANUAL_CREATE}"
            child_name, func = self.factory_child_query(field_name, unit)
            child_name = f"{child_name}_{target.loc["CSVヘッダ"]}" # 名前の重複を避けるためCSVヘッダを付与
            group_col = f"\"{"\", \"".join(tags)}\", \"_time\""
            keep_col = self.list_to_str_for_flux(["_time","_value","_field"] + tags)
            self.child_query_list.append(child_name)
            query = f"{query}{tmp.safe_substitute({"NAME":self.regular_query_value["NAME"],"CHILD_NAME": child_name,"GROUP_COL": group_col,"FUNC": func,"FIELD_NAME": field_name,"KEEP_COL": keep_col})}"
        return query

    def factory_child_query(self, field_name:str, unit:str):
            if   any(x in field_name for x in ["最大", "max", "MAX"]):                  child_name, func = f"{unit}_max", "max()"
            elif any(x in field_name for x in ["最小", "min", "MIN"]):                  child_name, func = f"{unit}_min", "min()"
            elif any(x in field_name for x in ["合計", "sum", "SUM"]):                  child_name, func = f"{unit}_sum", "sum(column: \"_value\")"
            elif any(x in field_name for x in ["平均", "avg", "AVG", "ave", "AVE"]):    child_name, func = f"{unit}_avg", "mean()"
            elif any(x in field_name for x in ["90パーセンタイル"]):                     child_name, func = f"{unit}_p90", "quantile(q: 0.9, column: column, method: \"exact_mean\")"
            else:                                                                       child_name, func = MANUAL_CREATE, MANUAL_CREATE            
            return child_name, func

    def get_child_query(self, query_dataframe:GetQueryDataframe): # 日内MAX、SUMなど作成の必要があるか判定
        # 時間単位でデータを区切る子クエリの作成
        intvl = query_dataframe.query_info["集計時間単位"]
        tags = self.find_matched_element(query_dataframe.query_elem, "INPUT_入力データ物理名", r"^t_.*").iloc[:,0].to_list()
        self.make_regular_query(intvl, tags)
        # その他子クエリの作成
        max = self.find_matched_element(query_dataframe.query_elem, "OUTPUT_CSV項目", r"^.*(最大|max|MAX).*$" , True)#.iloc[0,:].to_list() # r"^.*MAX.*$"
        min = self.find_matched_element(query_dataframe.query_elem, "OUTPUT_CSV項目", r"^.*(最小|min|MIN).*$" , True)
        sum = self.find_matched_element(query_dataframe.query_elem, "OUTPUT_CSV項目", r"^.*(合計|sum|SUM).*$" , True)
        avg = self.find_matched_element(query_dataframe.query_elem, "OUTPUT_CSV項目", r"^.*(平均|avg|AVG|ave|AVE).*$" , True)
        p90 = self.find_matched_element(query_dataframe.query_elem, "OUTPUT_CSV項目", r"^.*90パーセンタイル.*$" , True)
        if not max.empty: self.child_query = f"{self.child_query}{self.make_child_query(query_dataframe, max, tags)}"
        if not min.empty: self.child_query = f"{self.child_query}{self.make_child_query(query_dataframe, min, tags)}"
        if not sum.empty: self.child_query = f"{self.child_query}{self.make_child_query(query_dataframe, sum, tags)}"
        if not avg.empty: self.child_query = f"{self.child_query}{self.make_child_query(query_dataframe, avg, tags)}"
        if not p90.empty: self.child_query = f"{self.child_query}{self.make_child_query(query_dataframe, p90, tags)}"

        self.child_query_name = str(self.child_query_list).replace("'", "")

    def get_group_key(self, query_dataframe:GetQueryDataframe):
        self.result_group_list = self.find_matched_element(query_dataframe.query_elem, "INPUT_入力データ物理名", r"^t_.*").iloc[:,0].to_list()
        rowkey = ["_time"] + self.result_group_list
        self.pivoted_rowkey = self.list_to_str_for_flux(rowkey)

##### RESULT作成    
    def get_result_parameter(self, query_dataframe:GetQueryDataframe): # 最後の成型に必要なパラメータ（GROUP, SORT, KEEP, YIELD）を抽出
        self.result_sort_list = ["_time"]
        self.yield_name  = f"\"{query_dataframe.query_info["Fluxクエリーファイル名"].replace(".flux", "")}\""

        # 出力用にタグ名をReplace
        replace_targets = self.result_sort_list + self.result_group_list        
        for target in replace_targets:
            if target == "_time": target = "time" # 設計の名称に合わせる
            row_num = query_dataframe.query_elem.index[query_dataframe.query_elem["INPUT_入力データ物理名"] == target].to_list()[0]
            col_num = query_dataframe.query_elem.columns.get_loc("OUTPUT_CSV項目")
            replace  = query_dataframe.query_elem.iloc[row_num, col_num]
            if target == "time": target = "_time"
            # replace_targets = [replace if x == target else x for x in replace_targets]
            self.result_rename[target] = replace
        # self.result_keep_list = list(dict.fromkeys( replace_targets + query_dataframe.query_elem["OUTPUT_CSV項目"].to_list() ))
        self.result_keep_list = query_dataframe.query_elem["OUTPUT_CSV項目"].to_list()

        self.result_group   = self.list_to_str_for_flux(self.result_group_list)
        self.result_sort    = self.list_to_str_for_flux(self.result_sort_list)
        self.result_keep    = self.list_to_str_for_flux(self.result_keep_list)
        self.result_rename  = self.list_to_str_for_flux(self.result_rename)
        

##### Utility
    # DFの列を正規表現で探索
    def find_matched_element(self, df:pd.DataFrame, col_name:str, reg:str, all_elem:bool=False) -> pd.DataFrame:
        mask = df[col_name].astype(str).str.match(reg, na=False)
        if all_elem:    return df[mask]
        else:           return df.loc[mask, [col_name]]

    def list_to_str_for_flux(self, target:list):
        return str(target).replace("'", "\"")


##### 外部実行用
    def exec_func(self, query_dataframe:GetQueryDataframe):
        print(f"{TAB(1)}Get Template Parameter")
        self.get_group_key(query_dataframe)             # RESULT_GROUP, PIVOTED_ROWKEY
        self.get_direct_parameter(query_dataframe)      # QUERY_INFO, QUERY_ELEM, OUTPUT_FILENAME, MEASUREMENT, BUCKET
        self.get_time_parameter(query_dataframe)        # START_UTC, STOP_UTC
        self.get_tag_filter(query_dataframe)            # TAG_FILTER
        self.get_field_filter(query_dataframe)          # FIELD_FILTER
        self.get_jst_range_clip(query_dataframe)        # JST_RANGE_CLIP
        self.get_child_query(query_dataframe)           # CHILD_QUERY, child_query_list
        self.get_result_parameter(query_dataframe)      # RESULT_GROUP, RESULT_SORT, RESULT_KEEP, YIELD_NAME