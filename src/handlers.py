# handlers.py
import flet as ft
import asyncio
import pandas as pd



def make_handle_pick_files(selected_files_text: ft.Text):
    async def handle_pick_files(e: ft.ControlEvent):
        files = await ft.FilePicker().pick_files(allow_multiple=False, allowed_extensions=["xlsx", "xls", "xlsm"])
        selected_files_text.value = (
            ", ".join(f.name for f in files) if files else "Cancelled"
        )
        selected_files_text.update()
        
        
        df = await asyncio.to_thread(
            pd.read_excel,
            files[0].path,
            engine="openpyxl",
            # sheet_name=0,
            # dtype=str,
        )


    return handle_pick_files


def make_handle_save_file(save_file_path_text: ft.Text):
    async def handle_save_file(e: ft.ControlEvent):
        path = await ft.FilePicker().save_file()
        
        if not path.startswith('.flux'): path = f"{path}.flux"
        
        save_file_path_text.value = path or ""
        save_file_path_text.update()

    return handle_save_file