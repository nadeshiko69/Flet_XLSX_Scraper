# handlers.py
import flet as ft
import asyncio
import pandas as pd




# def make_handle_pick_files(*, page: ft.Page, selected_files_text: ft.Text, output_area: ft.Container):
#     async def handle_pick_files(e: ft.ControlEvent):
#         files = await ft.FilePicker().pick_files(allow_multiple=False, allowed_extensions=["xlsx", "xls", "xlsm"])
#         selected_files_text.value = (
#             ", ".join(f.name for f in files) if files else "Cancelled"
#         )
#         selected_files_text.update()
        
#         output_area = page.add(
#             ft.CupertinoActivityIndicator(
#                 animating=True,
#                 color=ft.Colors.RED,
#                 radius=50,
#             )            
#         )
        
#         df = await asyncio.to_thread(
#             pd.read_excel,
#             files[0].path,
#             engine="openpyxl",
#             # sheet_name=0,
#             # dtype=str,
#         )
        
#         print("a")
#         # output_area = page.clean()
#         output_area = await page.add(str(df))


    # return handle_pick_files


def make_handle_save_file(save_file_path_text: ft.Text):
    async def handle_save_file(e: ft.ControlEvent):
        path = await ft.FilePicker().save_file()
        
        if not path.startswith('.flux'): path = f"{path}.flux"
        
        save_file_path_text.value = path or ""
        save_file_path_text.update()

    return handle_save_file









# handlers.py
import asyncio
import pandas as pd
import flet as ft


def make_handle_pick_files(
    *,
    page: ft.Page,
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
            # 重い処理なので別スレッド
            df = await asyncio.to_thread(
                pd.read_excel,
                f.path,
                engine="openpyxl",
            )

            # DF表示
            table = _df_to_datatable(df, max_rows=50, max_cols=20)
            output_area.content = ft.Container(content=table, expand=True)
            output_area.update()

            # 保持
            # page.session.set("excel_df", df)

        except Exception as ex:
            output_area.content = ft.Text(f"読み込み失敗: {ex}", color=ft.Colors.RED)
            output_area.update()

    return handle_pick_files

def _df_to_datatable(df: pd.DataFrame, *, max_rows: int = 50, max_cols: int = 20) -> ft.DataTable:
    sub = df.iloc[:max_rows, :max_cols]
    columns = [ft.DataColumn(ft.Text(str(c))) for c in sub.columns]
    rows = [
        ft.DataRow(
            cells=[ft.DataCell(ft.Text("" if pd.isna(v) else str(v))) for v in row]
        )
        for _, row in sub.iterrows()
    ]
    return ft.DataTable(columns=columns, rows=rows)