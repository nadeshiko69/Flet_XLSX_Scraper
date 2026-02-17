import flet as ft
from handlers import Handlers

def main(page: ft.Page):
    selected_files = ft.Text()
    dropdown_area  = ft.Container(width=380, alignment=ft.Alignment.CENTER_LEFT)
    read_button_area = ft.Container(width=100, alignment=ft.Alignment.CENTER_LEFT)

    information_area =  ft.Container(
                        expand=True,
                        padding=10,
                        bgcolor=ft.Colors.SURFACE,
                        border=ft.Border.all(1, ft.Colors.GREY_400),
                        border_radius=8,
                        content=ft.Column(
                            expand=True,
                            horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
                            controls=[
                                ft.Text(
                                    value="Query Information Table",
                                    selectable=True,
                                )
                            ],
                        ),
                    )
    query_area = ft.Container(
                                expand=True,
                                padding=10,
                                bgcolor=ft.Colors.SURFACE,
                                border=ft.Border.all(1, ft.Colors.GREY_400),
                                border_radius=8,
                                content=ft.Column(
                                    expand=True,
                                    horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
                                    controls=[
                                        ft.Text(
                                            value="Output Query",
                                            selectable=True,
                                        )
                                    ],
                                ),
                            )
    
    handlers = Handlers()
    handle_pick_files = handlers.make_handle_pick_files(selected_files, information_area, dropdown_area, read_button_area, query_area)

    page.window.width = 1500
    page.window.height = 1000

    page.add(
        ft.SafeArea(
            content=ft.Column(
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
                            dropdown_area,
                            read_button_area
                        ]
                    ),
                    ft.Row(
                        expand=True,
                        vertical_alignment=ft.CrossAxisAlignment.STRETCH,
                        controls=[
                            information_area,                            
                            query_area

                        ],
                    ),
                ],
            ),
            expand=True,
        )
    )

if __name__ == "__main__":
    ft.run(main)