# Too


## 1. Introducción

Nombre del Proyecto: Visualizador

Descripción: El proyecto "Visualizador" es una aplicación diseñada para el seguimiento de los usuarios de Too y la visualización de sus itinerarios durante el transcurso de los acuerdos firmados. El FRONTEND está desarrollado usando Flet y el BACKEND está construido sobre FastAPI y puede desplegarse usando tanto Docker, como una función lambda de AWS.

-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
## 2. Requisitos 
### [BACKEND]

### Requisitos de Software:
	Docker
	Python 3.12 o superior

### Dependencias del Proyecto (Listadas en el archivo requirements.txt:):
	annotated-types==0.7.0
	anyio==4.4.0
	certifi==2024.6.2
	click==8.1.7
	colorama==0.4.6
	dnspython==2.6.1
	ecdsa==0.19.0
	email_validator==2.2.0
	astapi==0.111.0
	fastapi-cli==0.0.4
	h11==0.14.0
	httpcore==1.0.5
	httptools==0.6.1
	httpx==0.27.0
	idna==3.7
	Jinja2==3.1.4
	markdown-it-py==3.0.0
	MarkupSafe==2.1.5
	mdurl==0.1.2
	motor==3.5.0
	orjson==3.10.5
	passlib==1.7.4
	pyasn1==0.6.0
	pycryptodome==3.20.0
	pydantic==2.8.0
	pydantic_core==2.20.0
	Pygments==2.18.0
	pymongo==4.8.0
	python-dateutil==2.9.0.post0
	python-dotenv==1.0.1
	python-jose==3.3.0
	python-multipart==0.0.9
	PyYAML==6.0.1
	rich==13.7.1
	rsa==4.9
	shellingham==1.5.4
	six==1.16.0
	sniffio==1.3.1
	starlette==0.37.2
	typer==0.12.3
	typing_extensions==4.12.2
	ujson==5.10.0
	uvicorn==0.30.1
	watchfiles==0.22.0
	websockets==12.0

-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
## 3.1. Instrucciones de Instalación y despliegue (LOCAL):
### [BACKEND]	
 	CAMBIAR
  		-host, port, data-base direction, CORS
	
	1. Clonar el Repositorio
		git clone <URL_del_repositorio>
		cd <nombre_del_directorio>
	
	2. Construcción de la Imagen Docker
		docker build -t visualizador .

	3. Ejecución del Contenedor
		docker run -p 8000:8000 visualizador

### 3.2. Instrucciones para despliegue en AWS:
### [BACKEND]	
	 CAMBIAR
  		-host, port, data-base direction, CORS
	
	1. Construir y Probar la Imagen Localmente
		docker build -t visualizador-lambda .
		docker run -p 9000:8080 visualizador-lambda
	
	2. Crear un Repositorio ECR (Elastic Container Registry)
		aws ecr create-repository --repository-name visualizador-lambda
	
	3. Iniciar Sesión en ECR
		aws ecr get-login-password --region <your-region> | docker login --username AWS --password-stdin <your-account-id>.dkr.ecr.<your-region>.amazonaws.com

	4. Etiquetar y Subir la Imagen al Repositorio ECR
		docker tag visualizador-lambda:latest <your-account-id>.dkr.ecr.<your-region>.amazonaws.com/visualizador-lambda:latest
		docker push <your-account-id>.dkr.ecr.<your-region>.amazonaws.com/visualizador-lambda:latest
	
	5. Crear la Función Lambda en AWS a partir de un contenedor(tutoriales disponibles en línea). 


## Crear ejecutable (modificar ruta de imágenes):
### [FRONTEND]
  pyinstaller --onefile --noconsole --name "Visual-Too" --icon="ruta donde está el icono para la app.ico" --add-data "ruta donde está la imagen que se muestra dentro de la app.png;." Frontend-Too.py
  
  Distribuir usando drive. (Investigar como crear instalador(.exe))

-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
## 4. Instrucciones de Uso:

Una vez que el contenedor esté en funcionamiento, la aplicación estará disponible en http://localhost:8000 ó en la URL generada para la función Lambda de AWS. Puedes interactuar con la API para visializar y generar el itinerario de una sala (dos personas) de la aplicación Too.

-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
## 5. Detalles Técnicos

### Estructura del Proyecto:
 	resources: Directorio con imágenes para usar en la interfaz.
	src/Fronted.py: Contiene la lógica de la interfaz gráfica.
 	src/Backend.py: Contiene la lógica para la gestión de la interfaz y la conexión con la base de datos.
	Visualizador.txt: Contiene los comandos para construir y arrancar el contenedor Docker y crear el ejecutable de la interfaz gráfica.
	dockerfile: Define el entorno de Docker para la aplicación.
	requirements.txt: Lista de dependencias de Python necesarias para el proyecto.

-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
## 6. Licencia

Este proyecto está licenciado bajo la licencia MIT. Para más detalles, consulta el archivo LICENSE en el repositorio.



-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
## Estructura del directorio:

Too-main/
├── .gitignore
├── LICENSE
├── README.md
├── Visual_Too/
│   ├── Visualizador.txt
│   ├── dockerfile
│   ├── requeriments.txt
│   ├── resources/
│   │   ├── 240509_ReAction_Logo Blanco.png
│   │   ├── 240509_Too_Logo App.png
│   │   ├── 240509_Too_Logo Color_Blanco.png
│   │   ├── 240509_Too_Logo Gris_Claro.png
│   │   ├── 240509_Too_Logo_App.ico
│   │   ├── 240509_Too_Logo_Gris_Oscuro.png
│   ├── scr/
│   │   ├── Backend-Too.py
│   │   ├── Frontend-Too.py

