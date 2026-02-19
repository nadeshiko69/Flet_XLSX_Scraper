import flet as ft

class Utility:
    def init_UI(self,
                information_area: ft.Container,
                query_area:ft.Container
                ):
        
        information_area.content = ft.Column(
            expand=True,
            horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
            controls=[
                ft.Text(
                    value="Query Information Table",
                    selectable=True,
                )
            ],
        )
        query_area.content = ft.Column(
            expand=True,
            horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
            controls=[
                ft.Text(
                    value="Output Query",
                    selectable=True,
                )
            ],
        )

        information_area.update()
        query_area.update()