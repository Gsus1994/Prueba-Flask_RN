import base64
import logging
from bson import ObjectId
from mangum import Mangum
from Crypto.Cipher import AES
from jose import JWTError, jwt
from typing import List, Optional
from passlib.context import CryptContext
from datetime import datetime, timedelta
from Crypto.Util.Padding import pad, unpad
from fastapi.openapi.utils import get_openapi
from pydantic import BaseModel, Field, field_validator
from motor.motor_asyncio import AsyncIOMotorClient
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.models import OAuthFlows as OAuthFlowsModel
from fastapi import FastAPI, HTTPException, APIRouter, Depends, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
#-------------------------------------------------------------------Configuración del logging
logging.basicConfig(level=logging.INFO)
#-------------------------------------------------------------------Instancia FastAPI
Too = FastAPI(
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    title="Too",
    description="Interfaz para visualización de coordenadas de la app Too",
    version="2.1"
    )
"""#-------------------------------------------------------------------Configuración CORS
origins = [
    ]
Too.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    )"""
#-------------------------------------------------------------------Conexión a la base de datos
MONGO_URL = "mongodb+srv://jesusmoralescarr:nlq0xgLZMK71mg4H@consent.7xqmdhq.mongodb.net/Consent?retryWrites=true&w=majority&appName=Consent"
client = AsyncIOMotorClient(MONGO_URL)
db = client.get_database("Consent")  
collection = db.get_collection("Room")
collection2 = db.get_collection("Polis") 
#-------------------------------------------------------------------Configuración de seguridad
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")

SECRET_KEY = "11892df588b5bbe224f039a88caa004c79a83fc9775e4a44800baa138567330f" # Token
ALGORITHM = "HS256"
TokenTime=5
AES_KEY = bytes.fromhex("d632d224c8063ef9a6884b47bcf40a3d73cf351c2da32124a983704c774d4d91") # Cifrado de la base de datos

def decrypt_aes(data: Optional[str]) -> Optional[str]:
    if not data:
        return None
    try:
        data_bytes = base64.b64decode(data)
        cipher = AES.new(AES_KEY, AES.MODE_ECB)
        decrypted = unpad(cipher.decrypt(data_bytes), AES.block_size)
        decrypted_str = decrypted.decode('utf-8')
        print(f"Desencriptando {data} --> {decrypted_str}")
        return decrypted_str
    except Exception as e:
        logging.error(f"Error al desencriptar {data}: {e}")
        raise HTTPException(status_code=500, detail=f"Error al desencriptar {data}")

def encrypt_aes(data: str) -> str:
    try:
        cipher = AES.new(AES_KEY, AES.MODE_ECB)
        padded_data = pad(data.encode('utf-8'), AES.block_size)
        encrypted = cipher.encrypt(padded_data)
        encrypted_b64 = base64.b64encode(encrypted).decode('utf-8')
        logging.debug(f"Encriptado: {data} --> {encrypted_b64}")
        return encrypted_b64
    except Exception as e:
        logging.error(f"Error al encriptar {data}: {e}")
        raise HTTPException(status_code=500, detail="Error al encriptar los datos.")

def get_password_hash(password):
    return pwd_context.hash(password)

async def verify_password(plain_password, hashed_password):
    logging.debug(f"Verificando contraseña: {plain_password} contra {hashed_password}")
    return pwd_context.verify(plain_password, hashed_password)

async def authenticate_user(username: str, password: str):
    user = await collection2.find_one({"username": username})
    logging.debug(f"Usuario encontrado: {user}")
    if user and "hashed_password" in user and await verify_password(password, user["hashed_password"]):
        return user
    return False

def create_access_token(data: dict):
    to_encode = data.copy()
    to_encode.update({"exp": datetime.utcnow() + timedelta(minutes=TokenTime)})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudieron validar las credenciales",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = await collection2.find_one({"username": username})
    if user is None:
        raise credentials_exception
    return user
#-------------------------------------------------------------------Modelos
class User(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class Coordinates(BaseModel):
    latitude: float
    longitude: float
    time: Optional[datetime] = None

class Room(BaseModel):
    id: str = Field(alias="_id")
    fechaCreacionSala: datetime
    user1: str
    user2: Optional[str]
    user1Accepted: bool
    user2Accepted: bool
    user1Revoked: bool
    user2Revoked: bool
    user1Coordinates: List[Coordinates]
    user2Coordinates: List[Coordinates]
    nombreUser1: Optional[str]
    apellidosUser1: Optional[str]
    fechaNacimientoUser1: Optional[datetime]
    dniUser1: Optional[str]
    emailUser1: Optional[str]
    fechaAceptacionUser1: Optional[datetime]
    nombreUser2: Optional[str]
    apellidosUser2: Optional[str]
    fechaNacimientoUser2: Optional[datetime]
    dniUser2: Optional[str]
    emailUser2: Optional[str]
    fechaAceptacionUser2: Optional[datetime]
    roomFirma: Optional[str]
    class_name: str = Field(alias="_class", default="")
    visitas: Optional[List[dict]] = None

    @field_validator("fechaCreacionSala", "fechaNacimientoUser1", "fechaNacimientoUser2", "fechaAceptacionUser1", "fechaAceptacionUser2", mode="before")
    def parse_datetime(cls, value):
        if isinstance(value, str):
            return datetime.fromisoformat(value.replace("Z", "+00:00"))
        return value

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None,
        }

class ItinerarioResponse(BaseModel):
    itinerario: str

class MessageResponse(BaseModel):
    message: str
#-------------------------------------------------------------------Esquemas
async def UserEntity(item) -> dict:
    return {
        "username": item["username"],
        "hashed_password": item["hashed_password"]
    }

async def RoomEntity(item) -> dict:
    def iso_format(value):
        if isinstance(value, datetime):
            return value.isoformat()
        return value

    def decrypt_field(field):
        if field is None:
            return None
        try:
            return decrypt_aes(field)
        except Exception as e:
            logging.error(f"Error al desencriptar el campo: {e}")
            return None

    def safe_get(dictionary, key, default=None):
        return dictionary.get(key) if dictionary.get(key) is not None else default

    def is_valid_datetime(value):
        if isinstance(value, datetime):
            return True
        try:
            datetime.fromisoformat(value)
            return True
        except (ValueError, TypeError):
            return False

    def transform_coordinates(coordinates):
        return [{
            "latitude": coord["latitude"],
            "longitude": coord["longitude"],
            "time": iso_format(datetime.strptime(coord["time"], "%d-%m-%Y %H:%M:%S")) if "time" in coord else None
        } for coord in coordinates]

    try:
        decrypted_room = {
            "nombreUser1": decrypt_field(safe_get(item, "nombreUser1")),
            "apellidosUser1": decrypt_field(safe_get(item, "apellidosUser1")),
            "dniUser1": decrypt_field(safe_get(item, "dniUser1")),
            "nombreUser2": decrypt_field(safe_get(item, "nombreUser2")),
            "apellidosUser2": decrypt_field(safe_get(item, "apellidosUser2")),
            "dniUser2": decrypt_field(safe_get(item, "dniUser2")),
            "fechaCreacionSala": iso_format(decrypt_field(safe_get(item, "fechaCreacionSala"))),
            "user1Coordinates": transform_coordinates(safe_get(item, "user1Coordinates", [])),
            "user2Coordinates": transform_coordinates(safe_get(item, "user2Coordinates", [])),
            "emailUser1": decrypt_field(safe_get(item, "emailUser1")),
            "emailUser2": decrypt_field(safe_get(item, "emailUser2")),
            "fechaNacimientoUser1": iso_format(decrypt_field(safe_get(item, "fechaNacimientoUser1"))) if is_valid_datetime(decrypt_field(safe_get(item, "fechaNacimientoUser1"))) else None,
            "fechaNacimientoUser2": iso_format(decrypt_field(safe_get(item, "fechaNacimientoUser2"))) if is_valid_datetime(decrypt_field(safe_get(item, "fechaNacimientoUser2"))) else None,
            "fechaAceptacionUser1": iso_format(decrypt_field(safe_get(item, "fechaAceptacionUser1"))) if is_valid_datetime(decrypt_field(safe_get(item, "fechaAceptacionUser1"))) else None,
            "fechaAceptacionUser2": iso_format(decrypt_field(safe_get(item, "fechaAceptacionUser2"))) if is_valid_datetime(decrypt_field(safe_get(item, "fechaAceptacionUser2"))) else None,
            "user1": safe_get(item, "user1"),
            "user2": safe_get(item, "user2"),
            "user1Accepted": safe_get(item, "user1Accepted", False),
            "user2Accepted": safe_get(item, "user2Accepted", False),
            "user1Revoked": safe_get(item, "user1Revoked", False),
            "user2Revoked": safe_get(item, "user2Revoked", False),
            "itinerario": safe_get(item, "itinerario", None),
            "visitas": safe_get(item, "visitas", []),
            "roomFirma": decrypt_field(safe_get(item, "roomFirma")),
            "class_name": str(safe_get(item, "_class", "")),
            "_id": str(safe_get(item, "_id", ""))
        }
        return decrypted_room
    except KeyError as e:
        logging.error(f"Missing key during room transformation: {e}")
        raise HTTPException(status_code=400, detail=f"Missing key: {e}")
    except Exception as e:
        logging.error(f"Error transforming room data: {e}")
        raise HTTPException(status_code=500, detail="Error transforming room data.")

async def RoomsEntities(entity) -> list:
    return [await RoomEntity(item) for item in entity]
#-------------------------------------------------------------------Rutas de autenticación
Users = APIRouter()

@Users.post("/token", response_model=Token, tags=["Autenticación de usuarios"])
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = await authenticate_user(form_data.username, form_data.password)
    logging.debug(f"Resultado de autenticación: {user}")
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": user["username"]})
    return {"access_token": access_token, "token_type": "bearer"}
#-------------------------------------------------------------------Rutas de salas
Salas = APIRouter()

@Salas.get('/rooms', response_model=List[Room], tags=["Salas"], dependencies=[Depends(get_current_user)])
async def get_rooms_single_user(dni: str):
    encrypted_dni = encrypt_aes(dni)

    rooms_user1 = await collection.find({"dniUser1": encrypted_dni}).to_list(length=1000)
    rooms_user2 = await collection.find({"dniUser2": encrypted_dni}).to_list(length=1000)
    rooms = rooms_user1 + rooms_user2

    if not rooms:
        raise HTTPException(status_code=404, detail="Salas no encontradas")
    try:
        result = await RoomsEntities(rooms)
        return result
    except Exception as e:
        logging.error(f"Error al formatear la sala: {e}")
        raise HTTPException(status_code=500, detail="Error al formatear la sala")

@Salas.post('/rooms/{room_id}/visit', response_model=MessageResponse, tags=["Salas"], dependencies=[Depends(get_current_user)])
async def create_visit(room_id: str, current_user: User = Depends(get_current_user)):
    data = await collection.find_one({"_id": ObjectId(room_id)})
    if data is None:
        raise HTTPException(status_code=404, detail="Sala no encontrada")
    visit_info = {
        "usuario": current_user["username"],
        "hora": datetime.now()
    }
    update_data = {"$push": {"visitas": visit_info}}
    result = await collection.update_one({"_id": ObjectId(room_id)}, update_data)
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Sala no encontrada")
    return {"message": "Visita registrada."}

@Salas.put('/rooms/{room_id}/visit', response_model=MessageResponse, tags=["Salas"], dependencies=[Depends(get_current_user)])
async def update_visit(room_id: str, current_user: User = Depends(get_current_user)):
    data = await collection.find_one({"_id": ObjectId(room_id)})
    if data is None:
        raise HTTPException(status_code=404, detail="Sala no encontrada")
    visit_info = {
        "usuario": current_user["username"],
        "hora": datetime.now()
    }
    update_data = {"$push": {"visitas": visit_info}}
    result = await collection.update_one({"_id": ObjectId(room_id)}, update_data)
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Sala no encontrada")
    return {"message": "Visita actualizada."}
#-------------------------------------------------------------------Registro de Routers
Too.include_router(Salas, prefix="/single")
Too.include_router(Users, prefix="")
#-------------------------------------------------------------------Configuración del esquema OpenAPI para Swagger
def custom_openapi():
    if Too.openapi_schema:
        return Too.openapi_schema
    openapi_schema = get_openapi(
        title="Too",
        version="2.1",
        description="Interfaz para visualización de coordenadas de la app Too",
        routes=Too.routes,
    )
    openapi_schema["components"]["securitySchemes"] = {
        "OAuth2PasswordBearer": {
            "type": "oauth2",
            "flows": {
                "password": {
                    "tokenUrl": "/token"
                }
            }
        }
    }
    openapi_schema["security"] = [{"OAuth2PasswordBearer": []}]
    Too.openapi_schema = openapi_schema
    return Too.openapi_schema
Too.openapi = custom_openapi

#-------------------------------------------------------------------AWS
"""handler = Mangum(Too)"""
#-------------------------------------------------------------------Uvicorn
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("Backend-Too:Too")
