# app.py
import flet as ft
from handlers import Handlers

def main(page: ft.Page):
    selected_files = ft.Text()
    save_file_path = ft.Text()
    output_area = ft.Container(
        expand=True,
        margin=20,
        padding=20
    )
    handlers = Handlers()

    # 非同期ハンドラ
    handle_pick_files = handlers.make_handle_pick_files(
        selected_files,
        output_area,
    )

    handle_save_file = handlers.make_handle_save_file(save_file_path)
    
    # 画面サイズ
    page.window.width = 500
    page.window.height = 500

    # UI
    page.add(
        ft.SafeArea(
            ft.Column(
                expand=True,
                controls=[
                ft.Row(
                    controls=[
                        ft.Button(
                            content="Open Excel",
                            icon=ft.Icons.UPLOAD_FILE,
                            on_click=handle_pick_files,
                        ),
                        selected_files,
                    ]
                ),
                ft.Row(
                    controls=[
                        ft.Button(
                            content="Save Flux",
                            icon=ft.Icons.SAVE,
                            on_click=handle_save_file,
                            disabled=page.web
                        ),
                        save_file_path,
                    ]
                ),
                output_area,
            ])
        )
    )


if __name__ == "__main__":
    ft.run(main)