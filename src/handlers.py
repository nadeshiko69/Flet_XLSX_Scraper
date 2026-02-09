# handlers.py
import flet as ft
import asyncio
import pandas as pd
from typing import Callable
from CreateFluxQuery.Get_query_dataframe import GetQueryDataframe
from CreateFluxQuery.Get_template_parameter import TemplateParameter
from CreateFluxQuery.Make_Flux_File import MakeFluxFile

class Handlers:
    queryDataFrame:GetQueryDataframe
    
    def __init__(self):
        self.queryDataFrame = GetQueryDataframe()
        self.templateParameter = TemplateParameter()
        self.makeFluxFile = MakeFluxFile()
        self._selected_rows: set[int] = set()

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
        information_area: ft.Container,
        query_area:ft.Container
    ):
        async def handle_pick_files(e: ft.ControlEvent):
            result = await ft.FilePicker().pick_files(
                allow_multiple=False,
                allowed_extensions=["xlsx", "xls", "xlsm"],
            )

            f = result[0]
            # print(f.path)
            selected_files_text.value = f.name or "selected"
            selected_files_text.update()
            handle_create_flux = self.make_handle_create_flux(query_area)
            # 読み込み中
            information_area.content = ft.Row(
                alignment=ft.MainAxisAlignment.CENTER,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[ft.CupertinoActivityIndicator(radius=16, color=ft.Colors.BLUE)],
            )
            information_area.update()

            try:
                self.queryDataFrame.query_num = "3-3"
                self.queryDataFrame.query_dataframe = await asyncio.to_thread(
                    pd.read_excel,
                    f.path,
                    "3-3_FWCDL_オンライン　長時間取引",
                    dtype=str,
                    header=None,   
                    engine="openpyxl",
                )
                
                self.queryDataFrame.get_query_information()
                self.queryDataFrame.get_input_output_info()
                self.queryDataFrame.get_search_units()
                self.queryDataFrame.get_query_elem()
                # table:DataTable
                table = self._df_to_datatable(self.queryDataFrame.query_elem, max_rows=50, max_cols=20)
                
                
                horizontal_scroller = ft.Row(
                    scroll="always",
                    controls=[table],
                )
                
                scroller = ft.ListView(
                    expand=True,
                    controls=[horizontal_scroller],
                )

                information_area.content = ft.Container(
                    expand=True,
                    content=ft.Column(
                        expand=True,
                        controls=[
                            scroller,
                            ft.Button(
                                content="Create Flux",
                                icon=ft.Icons.UPLOAD_FILE,
                                on_click= handle_create_flux,
                            ),
                        ],
                    ),
                )

                information_area.update()

            except Exception as ex:
                information_area.content = ft.Text(f"読み込み失敗: {ex}", color=ft.Colors.RED)
                information_area.update()

        return handle_pick_files

    def make_handle_create_flux(
        self,
        query_area: ft.Container,
        *,
        on_done: Callable[[str], None] | None = None,
    ):
        async def handle_create_flux(e: ft.ControlEvent):
            try:
                # Create Parameter
                self.templateParameter.exec_func(self.queryDataFrame)
                ret = self.makeFluxFile.exec_func(self.queryDataFrame.query_num, self.templateParameter)
                        
                flux_text = ret
                
                query_area.content = ft.Container(
                    expand=True,
                    border_radius=8,
                    bgcolor=ft.Colors.SURFACE,
                    padding=8,
                    content=ft.ListView(
                        expand=True,
                        scroll="always",
                        controls=[
                            ft.Row(
                                scroll="always",
                                controls=[
                                    ft.Markdown(
                                        value=f"```go\n{flux_text}\n```",
                                        code_theme=ft.MarkdownCodeTheme.GITHUB,
                                        extension_set=ft.MarkdownExtensionSet.GITHUB_WEB,
                                    )

                                ],
                            )
                        ],
                    ),
                )

                query_area.update()

                if on_done:
                    on_done(flux_text)

            except Exception as ex:
                query_area.content = ft.Text(f"生成失敗: {ex}", color=ft.Colors.RED)
                query_area.update()

        return handle_create_flux

    def _df_to_datatable(self, data, *, max_rows: int = 50, max_cols: int = 20) -> ft.DataTable:
        if hasattr(data, "iloc"):  # pandas DataFrame と判定
            sub = data.iloc[:max_rows, :max_cols]

            columns = [ft.DataColumn(ft.Text(str(c))) for c in sub.columns]

            # ★ child_query_target を初期選択集合として使う
            #    - None でもエラーにならないようにガード
            #    - サブセット長を超える値は無視
            raw_default = getattr(self.queryDataFrame, "child_query_target", []) or []
            default_checked: set[int] = {i for i in raw_default if isinstance(i, int) and 0 <= i < len(sub)}

            rows: list[ft.DataRow] = []
            for i, (_, row) in enumerate(sub.iterrows()):
                cells = [ft.DataCell(ft.Text("" if pd.isna(v) else str(v))) for v in row]

                # 初期状態：child_query_target or 既存の self._selected_rows のいずれかに含まれていれば ON
                is_selected = (i in default_checked) or (i in self._selected_rows)

                # 内部集合も同期（再描画時に保持）
                if is_selected:
                    self._selected_rows.add(i)

                rows.append(
                    ft.DataRow(
                        selected=is_selected,
                        # ← あなたの環境で有効なイベント名（on_select_change）を使用
                        on_select_change=lambda e, i=i: (
                            self._selected_rows.add(i) if e.data else self._selected_rows.discard(i),
                            setattr(e.control, "selected", e.data),
                            e.control.update()
                        ),
                        cells=cells,
                    )
                )

            return ft.DataTable(columns=columns, rows=rows, show_checkbox_column=True)

        return ft.DataTable(columns=[], rows=[], show_checkbox_column=True)