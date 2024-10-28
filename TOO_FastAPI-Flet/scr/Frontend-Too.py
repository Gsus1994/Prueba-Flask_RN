import os
import re
import time
import folium
import requests
import tempfile
import threading
import webbrowser
from flet import *
from datetime import datetime


global token
token = None
global username_global
username_global = None
direccion = "http://localhost:8000"


def main(page: Page):
    Ruta_img="C:\\Users\\Usuario\\Desktop\\Visual_Too\\resources\\"
    image_path = Ruta_img+"240509_Too_Logo_Gris_Oscuro.png"
    icon_path = Ruta_img+"240509_Too_Logo_App.ico"

    page.title = "Visualizador de Coordenadas -Too-"
    page.window_resizable = False
    page.window_height = 550
    page.window_width = 575
    page.padding = 3
    page.window_icon = icon_path

    def show_main_screen(e):
        global token, username_global
        auth_data = {
            "username": username.value,
            "password": password.value
        }
        response = requests.post(f'{direccion}/token', data=auth_data)
        if response.status_code == 200:
            token = response.json().get("access_token")
            username_global = username.value
            page.controls.clear()
            page.add(main_container)
            page.update()
        else:
            page.snack_bar = SnackBar(Text("Credenciales incorrectas"), open=True)
            page.update()

    def redirect_to_login():
        global token, username_global
        token = None
        username_global = None
        page.controls.clear()
        page.add(login_container)
        page.snack_bar = SnackBar(Text("Sesión expirada. Por favor, inicie sesión nuevamente."), open=True)
        page.update()

    def to_uppercase(e):
        e.control.value = e.control.value.upper()
        e.control.update()
    
    login_image = Image(src=image_path, width=200, height=200)
    username = TextField(
        label="Usuario", 
        width=275, 
        on_change=to_uppercase, 
        bgcolor=colors.WHITE, 
        border_radius=15, 
        border_color=colors.BLUE,
        icon=icons.PERSON
    )
    password = TextField(
        label="Contraseña", 
        width=275, 
        password=True, 
        can_reveal_password=True, 
        bgcolor=colors.WHITE, 
        border_radius=15, 
        border_color=colors.BLUE,
        icon=icons.LOCK
    )
    login_button = ElevatedButton(
        text="Iniciar Sesión", 
        bgcolor=colors.GREEN_300, 
        on_click=show_main_screen,
        icon=icons.LOGIN
    )

    login_container = Container(
        border_radius=border_radius.all(15),
        content=Column(
            alignment="center",
            horizontal_alignment="center",
            spacing=20,
            controls=[
                login_image,
                username,
                password,
                login_button,
            ]
        ),
        expand=True,
        alignment=alignment.center,
        gradient=LinearGradient(
            begin=Alignment(-1, -1),
            end=Alignment(1, 1),
            colors=[colors.GREY_800, colors.GREY_200]
        ),
        animate_opacity=300,
        opacity=1.0
    )

    def submit_data(e):
        try:
            dni_value = dni.value

            dni_pattern = re.compile(r"^\d{8}[A-Z]$")
            if not dni_pattern.match(dni_value):
                raise ValueError(f"DNI es incorrecto: {dni_value}")

            response = requests.get(f'{direccion}/single/rooms?dni={dni_value}', headers={"Authorization": f"Bearer {token}"})

            if response.status_code == 401:
                redirect_to_login()
                return

            if response.status_code != 200:
                raise ValueError(f"No se encontraron salas para el DNI proporcionado")
            
            rooms = response.json()

            sorted_rooms = sorted(rooms, key=lambda x: datetime.fromisoformat(x["fechaCreacionSala"]))

            if dni_value == sorted_rooms[0]['dniUser1']:
                name = sorted_rooms[0]['nombreUser1'] + " " + sorted_rooms[0]['apellidosUser1']
                user_color = "Azul"
                user_pri="Rojo"
                accomplice_color = "Verde"
                aco_pri="Naranja"
            else:
                name = sorted_rooms[0]['nombreUser2'] + " " + sorted_rooms[0]['apellidosUser2']
                user_color = "Verde"
                user_pri="Naranja"
                accomplice_color = "Azul"
                aco_pri="Rojo"
            
            backend_info.value = f"Nombre: {name}\nDNI: {dni_value}\nColor itinerario: {user_color}\nColor Primera Coordenada: {user_pri}\n\nAcompañante:\nColor itinerario: {accomplice_color}\nColor Primera Coordenada: {aco_pri}"
            backend_info.update()

            room_options = [dropdown.Option(
                text=f"{room['nombreUser1']} {room['apellidosUser1']} y {room['nombreUser2']} {room['apellidosUser2']} - {datetime.fromisoformat(room['fechaCreacionSala']).strftime('%d/%m/%Y - %H:%M:%S')}",
                key=room["_id"]) for room in sorted_rooms]
            dropdown_rooms.options = room_options
            dropdown_rooms.data = {room["_id"]: room for room in sorted_rooms}
            dropdown_rooms.update()

        except ValueError as ve:
            page.snack_bar = SnackBar(Text(str(ve)), open=True)
            page.update()

    def show_map(e):
        try:
            selected_room_id = dropdown_rooms.value
            if not selected_room_id:
                raise ValueError("Por favor, para poder mostrar el itinerario, solicite primero la lista de acuerdos.")

            selected_room = dropdown_rooms.data[selected_room_id]

            if dni.value == selected_room["dniUser1"]:
                user1_coordinates = selected_room["user1Coordinates"]
                user2_coordinates = selected_room["user2Coordinates"]
                user_color = 'blue'
                accomplice_color = 'green'
                user_first_coord_color = 'red'
                accomplice_first_coord_color = 'orange'
            else:
                user1_coordinates = selected_room["user2Coordinates"]
                user2_coordinates = selected_room["user1Coordinates"]
                user_color = 'green'
                accomplice_color = 'blue'
                user_first_coord_color = 'orange'
                accomplice_first_coord_color = 'red'

            itinerario_html = generate_map(user1_coordinates, user2_coordinates, backend_info.value, user_color, accomplice_color, user_first_coord_color, accomplice_first_coord_color)

            visit_info = {
                "usuario": username_global,
                "hora": datetime.now().isoformat()
            }
            response = requests.post(f'{direccion}/single/rooms/{selected_room_id}/visit', json=visit_info, headers={"Authorization": f"Bearer {token}"})

            if response.status_code == 401:
                redirect_to_login()
                return

            with tempfile.NamedTemporaryFile(delete=False, suffix=".html") as tmp_file:
                tmp_file.write(itinerario_html.encode('utf-8'))
                temp_file_path = tmp_file.name

            def open_and_remove_file(path):
                webbrowser.open(f"file://{path}")
                time.sleep(25)
                os.remove(path)

            threading.Thread(target=lambda: open_and_remove_file(temp_file_path)).start()
        except ValueError as ve:
            page.snack_bar = SnackBar(Text(str(ve)), open=True)
            page.update()

    def generate_map(user1_coordinates, user2_coordinates, backend_info, user_color, accomplice_color, user_first_coord_color, accomplice_first_coord_color):
        def convert_coordinates(coords):
            return [(coord["latitude"], coord["longitude"]) for coord in coords]

        coordenadas_Mapa1 = convert_coordinates(user1_coordinates)
        coordenadas_Mapa2 = convert_coordinates(user2_coordinates)

        todas_coordenadas = coordenadas_Mapa1 + coordenadas_Mapa2

        suma_latitud = sum(lat for lat, lon in todas_coordenadas)
        suma_longitud = sum(lon for lat, lon in todas_coordenadas)
        num_coordenadas = len(todas_coordenadas)

        try:
            latitud_promedio = suma_latitud / num_coordenadas
            longitud_promedio = suma_longitud / num_coordenadas
        except Exception:
            page.snack_bar = SnackBar(Text(f"No existen coordenadas en este acuerdo."), open=True)
            page.update()

        ubicacion_promediada = (latitud_promedio, longitud_promedio)

        latitudes = [lat for lat, lon in todas_coordenadas]
        longitudes = [lon for lat, lon in todas_coordenadas]

        norte = max(latitudes) + 0.000002
        sur = min(latitudes) - 0.000002
        este = max(longitudes) + 0.000002
        oeste = min(longitudes) - 0.000002

        mapa = folium.Map(location=ubicacion_promediada, zoom_start=14)

        for i, (lat, lon) in enumerate(coordenadas_Mapa1):
            color = user_first_coord_color if i == 0 else user_color
            folium.Marker(location=(lat, lon), icon=folium.Icon(color=color)).add_to(mapa)

        for i, (lat, lon) in enumerate(coordenadas_Mapa2):
            color = accomplice_first_coord_color if i == 0 else accomplice_color
            folium.Marker(location=(lat, lon), icon=folium.Icon(color=color)).add_to(mapa)

        folium.PolyLine(coordenadas_Mapa1, color=user_color, weight=2.5, opacity=1).add_to(mapa)
        folium.PolyLine(coordenadas_Mapa2, color=accomplice_color, weight=2.5, opacity=1).add_to(mapa)

        mapa.fit_bounds([[sur, oeste], [norte, este]])

        legend_html = f'''
        <div style="position: fixed; 
                    bottom: 60px; left: 60px; width: 250px; height: 200px; 
                    background-color: white; z-index:9999; font-size:14px;
                    border:2px solid grey; border-radius:10px;">
        &nbsp; <b>Información del Usuario</b><br>
        &nbsp; {backend_info.replace("\n","<br>&nbsp;")} 
        </div>
        '''
        mapa.get_root().html.add_child(folium.Element(legend_html))

        return mapa.get_root().render()

    def save_html(e):
        try:
            selected_room_id = dropdown_rooms.value
            if not selected_room_id:
                raise ValueError("Por favor, para poder exportar el itinerario, solicite primero la lista de acuerdos.")
            
            selected_room = dropdown_rooms.data[selected_room_id]

            if dni.value == selected_room["dniUser1"]:
                user1_coordinates = selected_room["user1Coordinates"]
                user2_coordinates = selected_room["user2Coordinates"]
                name = selected_room["nombreUser1"] + " " + selected_room["apellidosUser1"]
                user_color = 'blue'
                accomplice_color = 'green'
                user_first_coord_color = 'red'
                accomplice_first_coord_color = 'orange'
            else:
                user1_coordinates = selected_room["user2Coordinates"]
                user2_coordinates = selected_room["user1Coordinates"]
                name = selected_room["nombreUser2"] + " " + selected_room["apellidosUser2"]
                user_color = 'green'
                accomplice_color = 'blue'
                user_first_coord_color = 'orange'
                accomplice_first_coord_color = 'red'

            itinerario_html = generate_map(user1_coordinates, user2_coordinates, backend_info.value, user_color, accomplice_color, user_first_coord_color, accomplice_first_coord_color)

            desktop_path = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop')
            itinerarios_dir = os.path.join(desktop_path, 'Itinerarios-Too')
            os.makedirs(itinerarios_dir, exist_ok=True)
            
            file_path = os.path.join(itinerarios_dir, f"{name}.html")

            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(itinerario_html)

            page.snack_bar = SnackBar(Text(f"Itinerario guardado exitosamente: {file_path}"), open=True)
            page.update()

        except ValueError as ve:
            page.snack_bar = SnackBar(Text(str(ve)), open=True)
            page.update()
        except Exception as ex:
            page.snack_bar = SnackBar(Text(f"Error al guardar el itinerario: {str(ex)}"), open=True)
            page.update()

    dni = TextField(
        label="Introducir DNI", 
        width=250, 
        on_change=to_uppercase, 
        bgcolor=colors.WHITE, 
        border_radius=15, 
        border_color=colors.BLUE,
        icon=icons.BADGE
    )
    submit_button = ElevatedButton(
        text="Solicitar lista de acuerdos", 
        bgcolor=colors.LIGHT_GREEN_ACCENT_100, 
        on_click=submit_data,
        icon=icons.SEARCH
    )
    open_map_button = ElevatedButton(
        text="Mostrar Itinerario", 
        bgcolor=colors.LIGHT_GREEN_ACCENT_100, 
        on_click=show_map,
        icon=icons.MAP
    )
    backend_info = TextField(
        label="Información acerca de los usuarios", 
        width=300, 
        height=420, 
        multiline=True, 
        bgcolor=colors.LIGHT_BLUE_ACCENT_100, 
        border_radius=15
    )
    dropdown_rooms = Dropdown(
        label="Lista de acuerdos realizados", 
        width=500, 
        bgcolor=colors.LIGHT_BLUE_ACCENT_100,
        options=[], 
        data={}, 
        border_radius=15
    )
    save_button = ElevatedButton(
        text="Guardar itinerario en escritorio", 
        bgcolor=colors.LIGHT_GREEN_ACCENT_100, 
        on_click=save_html,
        icon=icons.SAVE
    )
   
    image = Image(src=image_path, width=200, height=300)
    
    main_container = Container(
        padding=padding.all(10), 
        border_radius=border_radius.all(15),
        content=Column(
            spacing=20,
            controls=[
                dni,
                submit_button,
                dropdown_rooms,
                Row(
                    spacing=20,
                    controls=[
                        open_map_button,
                        save_button                                
                    ]
                ),
                Row(
                    spacing=20,
                    controls=[
                        backend_info,
                        Container(
                            content=image,
                            alignment=alignment.top_center,
                            padding=padding.only(top=-200)
                        ) 
                    ]
                )                        
            ]
        ),
        expand=True,
        gradient=LinearGradient(
            begin=Alignment(-1, -1),
            end=Alignment(1, 1),
            colors=[colors.LIGHT_BLUE_ACCENT_100, colors.LIGHT_GREEN_ACCENT_100]
        )
    )
    page.add(login_container)

if __name__ == "__main__":
    app(target=main)
