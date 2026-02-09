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

    def make_handle_pick_files(
        self,
        selected_files_text: ft.Text,
        information_area: ft.Container,
        dropdown_area:ft.Container,
        query_area:ft.Container
    ):
        async def handle_pick_files(e: ft.ControlEvent):
            result = await ft.FilePicker().pick_files(
                allow_multiple=False,
                allowed_extensions=["xlsx", "xls", "xlsm"],
            )
            f = result[0]

            selected_files_text.value = f.name or "selected"
            selected_files_text.update()
            def _list_sheets(p: str) -> list[str]:
                with pd.ExcelFile(p, engine="openpyxl") as xls:
                    return xls.sheet_names

            try:
                sheets: list[str] = await asyncio.to_thread(_list_sheets, f.path)
            except Exception as ex:
                information_area.content = ft.Text(f"シート名の取得に失敗: {ex}", color=ft.Colors.RED)
                information_area.update()
                return
            sheet_dd = ft.Dropdown(
                label="Select Query",
                options=[ft.dropdown.Option(name) for name in sheets],
                value=(sheets[0] if sheets else None),
                expand=True,
            )
            dropdown_area.content = sheet_dd
            dropdown_area.update()

            async def load_selected_sheet(_e: ft.ControlEvent):
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
                        sheet_dd.value,
                        dtype=str,
                        header=None,
                        engine="openpyxl",
                    )

                    # 4) 以降は従来の処理
                    self.queryDataFrame.get_query_information()
                    self.queryDataFrame.get_input_output_info()
                    self.queryDataFrame.get_search_units()
                    self.queryDataFrame.get_query_elem()

                    table = self._df_to_datatable(self.queryDataFrame.query_elem, max_rows=50, max_cols=20)
                    horizontal_scroller = ft.Row(scroll="always", controls=[table])
                    scroller = ft.ListView(expand=True, controls=[horizontal_scroller])

                    handle_create_flux = self.make_handle_create_flux(query_area)

                    information_area.content = ft.Container(
                        expand=True,
                        content=ft.Column(
                            expand=True,
                            controls=[
                                scroller,
                                ft.Button(
                                    content="Create Flux",
                                    icon=ft.Icons.ARROW_RIGHT,
                                    on_click=handle_create_flux,
                                ),
                            ],
                        ),
                    )
                    information_area.update()

                except Exception as ex:
                    information_area.content = ft.Text(f"読み込み失敗: {ex}", color=ft.Colors.RED)
                    information_area.update()

            # 初期画面：シート選択→読み込みボタン
            information_area.content = ft.Container(
                expand=True,
                content=ft.Column(
                    expand=True,
                    controls=[
                        ft.Text("シート名の一覧", style=ft.TextThemeStyle.TITLE_MEDIUM),
                        sheet_dd,
                        ft.Row(
                            controls=[
                                ft.Button(
                                    content="このシートを読み込む",
                                    icon=ft.Icons.DOWNLOAD,
                                    on_click=load_selected_sheet,
                                )
                            ]
                        )
                    ],
                ),
            )
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
                self.templateParameter.exec_func(self.queryDataFrame, self._selected_rows)
                ret = self.makeFluxFile.exec_func(self.queryDataFrame.query_num, self.templateParameter)
                flux_text = ret

                async def handle_copy(_e: ft.ControlEvent):
                    try:
                        await ft.Clipboard().set(flux_text)
                        _e.page.page.show_dialog(ft.SnackBar(ft.Text("Copied.")))
                        e.page.update()
                    except Exception as ex:
                        _e.page.page.show_dialog(ft.SnackBar(ft.Text(f"NG: {ex}")))
                        e.page.update()

                async def handle_save_file(e: ft.ControlEvent):
                    print(self.templateParameter.output_filename)
                    path = await ft.FilePicker().save_file(
                        file_name=self.templateParameter.output_filename,
                        allowed_extensions=["flux", "txt"],
                    )
                    if not path:
                        e.page.snack_bar = ft.SnackBar(content=ft.Text("保存をキャンセルしました"))
                        e.page.snack_bar.open = True
                        e.page.update()
                        return
                    if not str(path).lower().endswith(".flux"):
                        path = f"{path}.flux"
                    try:
                        def _write_text(p: str, text: str):
                            with open(p, "w", encoding="utf-8", newline="\n") as f:
                                f.write(text)

                        await asyncio.to_thread(_write_text, path, flux_text)

                        e.page.snack_bar = ft.SnackBar(content=ft.Text(f"保存しました: {path}"))
                        e.page.snack_bar.open = True
                        e.page.update()

                    except Exception as ex:
                        e.page.snack_bar = ft.SnackBar(
                            content=ft.Text(f"保存に失敗しました: {ex}"),
                            bgcolor=ft.Colors.RED,
                        )
                        e.page.snack_bar.open = True
                        e.page.update()

                md = ft.Markdown(
                    value=f"```go\n{flux_text}\n```",
                    code_theme=ft.MarkdownCodeTheme.GITHUB,
                    extension_set=ft.MarkdownExtensionSet.GITHUB_WEB,
                )

                query_area.content = ft.Container(
                    expand=True,
                    border_radius=8,
                    bgcolor=ft.Colors.SURFACE,
                    padding=8,
                    content=ft.Column(
                        expand=True,
                        controls=[
                            ft.ListView(
                                expand=True,
                                scroll="always",
                                controls=[
                                    ft.Row(scroll="always", controls=[md])
                                ],
                            ),
                            ft.Row(
                                controls=[
                                    ft.Button(
                                        content="Copy",
                                        icon=ft.Icons.COPY,
                                        on_click=handle_copy,
                                    ),
                                    ft.Button(
                                        content="Save File",
                                        icon=ft.Icons.SAVE,
                                        on_click=handle_save_file,
                                    ),
                                ],
                            ),
                        ],
                    )
                )
                query_area.update()

                if on_done:
                    on_done(flux_text)

            except Exception as ex:
                query_area.content = ft.Text(f"生成失敗: {ex}", color=ft.Colors.RED)
                query_area.update()

        return handle_create_flux

    # TODO : 表示項目を絞る
    # 子クエリ、CSVヘッダ、集計キー、INPUT_入力データ物理名くらいでいいかも
    def _df_to_datatable(self, data, *, max_rows: int = 50, max_cols: int = 20) -> ft.DataTable:
        if hasattr(data, "iloc"):  # pandas DataFrame と判定
            sub = data.iloc[:max_rows, :max_cols]

            raw_default = getattr(self.queryDataFrame, "child_query_target", []) or []
            default_checked: set[int] = {i for i in raw_default if isinstance(i, int) and 0 <= i < len(sub)}

            columns: list[ft.DataColumn] = [ft.DataColumn(ft.Text("子クエリ"))]
            columns += [ft.DataColumn(ft.Text(str(c))) for c in sub.columns]

            rows: list[ft.DataRow] = []
            for i, (_, row) in enumerate(sub.iterrows()):
                is_selected = (i in default_checked) or (i in self._selected_rows)
                if is_selected:
                    self._selected_rows.add(i)

                # 先頭セル
                checkbox = ft.Checkbox(
                    value=is_selected,
                    on_change=lambda e, i=i: (
                        self._selected_rows.add(i) if e.control.value else self._selected_rows.discard(i)
                    ),
                )
                data_cells = [ft.DataCell(ft.Text("" if pd.isna(v) else str(v))) for v in row]
                rows.append(ft.DataRow(cells=[ft.DataCell(checkbox), *data_cells],))

            return ft.DataTable(
                columns=columns,
                rows=rows,
                show_checkbox_column=False,
                # heading_row_height=40,
                # data_row_max_height=36,
                # divider_thickness=1,
            )

        return ft.DataTable(columns=[], rows=[], show_checkbox_column=True)