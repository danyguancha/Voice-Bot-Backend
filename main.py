from fastapi import FastAPI
from config.db import Base, engine
from routes import chatRoutes
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles


app = FastAPI()

# Crear las tablas en la base de datos
Base.metadata.create_all(bind=engine)


app.mount("/static", StaticFiles(directory="static"), name="static")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # O puedes poner una lista de dominios específicos
    allow_credentials=True,
    allow_methods=["*"],  # Permitir todos los métodos HTTP
    allow_headers=["*"],  # Permitir todos los encabezados
)


app.include_router(chatRoutes.router, prefix="/api", tags=["chat"])

@app.get("/")
async def root():
    return {"message": "Hello World"}
