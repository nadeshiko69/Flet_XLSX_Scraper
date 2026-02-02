# handlers.py
import flet as ft
import asyncio
import pandas as pd
from CreateFluxQuery.Get_query_dataframe import GetQueryDataframe

class Handlers:
    queryDataFrame:GetQueryDataframe
    
    def __init__(self):
        self.queryDataFrame = GetQueryDataframe()

    def make_handle_save_file(self, save_file_path_text: ft.Text):
        async def handle_save_file(e: ft.ControlEvent):
            path = await ft.FilePicker().save_file()
            
            if not path.startswith('.flux'): path = f"{path}.flux"
            
            save_file_path_text.value = path or ""
            save_file_path_text.update()

        return handle_save_file



    def make_handle_pick_files(
        self,
        selected_files_text: ft.Text,
        output_area: ft.Container,
    ):
        async def handle_pick_files(e: ft.ControlEvent):
            result = await ft.FilePicker().pick_files(
                allow_multiple=False,
                allowed_extensions=["xlsx", "xls", "xlsm"],
            )

            f = result[0]
            selected_files_text.value = f.name or "selected"
            selected_files_text.update()

            # 読み込み中
            output_area.content = ft.Row(
                alignment=ft.MainAxisAlignment.CENTER,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[ft.CupertinoActivityIndicator(radius=16, color=ft.Colors.BLUE)],
            )
            output_area.update()

            try:
                
                # df = pd.read_excel(excel_path, sheet_name, dtype=str, header=None)
                
                # 重い処理なので別スレッド
                self.queryDataFrame.query_dataframe = await asyncio.to_thread(
                # df = await asyncio.to_thread(
                    pd.read_excel,
                    f.path,
                    dtype=str,
                    header=None,   
                    engine="openpyxl",
                )
                
                self.queryDataFrame.get_query_information()
                self.queryDataFrame.get_input_output_info()
                self.queryDataFrame.get_search_units()
                self.queryDataFrame.get_query_elem()
                # DF表示
                table = self._df_to_datatable(self.queryDataFrame.query_elem, max_rows=50, max_cols=20)
                output_area.content = ft.Container(content=table, expand=True)
                output_area.update()

                # 保持
                # page.session.set("excel_df", df)

            except Exception as ex:
                output_area.content = ft.Text(f"読み込み失敗: {ex}", color=ft.Colors.RED)
                output_area.update()

        return handle_pick_files

    def _df_to_datatable(self, data, *, max_rows: int = 50, max_cols: int = 20) -> ft.DataTable:
        # --- DataFrame の場合 ---
        if hasattr(data, "iloc"):  # pandas DataFrame と判定
            sub = data.iloc[:max_rows, :max_cols]
            columns = [ft.DataColumn(ft.Text(str(c))) for c in sub.columns]
            rows = [
                ft.DataRow(
                    cells=[ft.DataCell(ft.Text("" if pd.isna(v) else str(v))) for v in row]
                )
                for _, row in sub.iterrows()
            ]
            return ft.DataTable(columns=columns, rows=rows)

        # --- list[list] の場合 ---
        if isinstance(data, list) and len(data) > 0 and isinstance(data[0], (list, tuple)):
            # 列数制限
            sub = [row[:max_cols] for row in data[:max_rows]]

            # 列名は 0,1,2,... とする
            columns = [ft.DataColumn(ft.Text(str(i))) for i in range(len(sub[0]))]

            rows = [
                ft.DataRow(cells=[ft.DataCell(ft.Text(str(cell))) for cell in row])
                for row in sub
            ]
            return ft.DataTable(columns=columns, rows=rows)

        # --- list[dict] の場合 ---
        if isinstance(data, list) and len(data) > 0 and isinstance(data[0], dict):
            cols = list(data[0].keys())[:max_cols]
            sub = data[:max_rows]

            columns = [ft.DataColumn(ft.Text(str(c))) for c in cols]
            rows = [
                ft.DataRow(
                    cells=[ft.DataCell(ft.Text(str(row.get(c, "")))) for c in cols]
                )
                for row in sub
            ]
            return ft.DataTable(columns=columns, rows=rows)

        # 不明な形式
        return ft.DataTable(columns=[], rows=[])