from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

# Configuración de SQLite
SQLALCHEMY_DATABASE_URL = "sqlite:///./catalogo_productos.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Modelo de la Base de Datos
class ProductoModel(Base):
    __tablename__ = "productos"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, index=True)
    descripcion = Column(String, nullable=True)
    precio = Column(Float)
    stock = Column(Integer)
    categoria = Column(String, index=True)

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="API Catálogo de Productos",
    description="Backend RESTful para gestión de inventario y catálogo de productos con FastAPI y SQLite.",
    version="1.0.0"
)

def obtener_base_datos():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Modelos Pydantic (Validación)
class ProductoCrear(BaseModel):
    nombre: str
    descripcion: Optional[str] = None
    precio: float
    stock: int
    categoria: str

    class Config:
        from_attributes = True

class ProductoRespuesta(ProductoCrear):
    id: int


# ENDPOINTS

@app.post("/productos", response_model=ProductoRespuesta, status_code=201, tags=["Productos"])
def crear_producto(producto: ProductoCrear, db: Session = Depends(obtener_base_datos)):
    """Registra un nuevo producto en el catálogo."""
    db_producto = ProductoModel(**producto.model_dump())
    db.add(db_producto)
    db.commit()
    db.refresh(db_producto)
    return db_producto

@app.get("/productos", response_model=List[ProductoRespuesta], tags=["Productos"])
def listar_productos(db: Session = Depends(obtener_base_datos)):
    """Obtiene la lista completa de productos disponibles."""
    return db.query(ProductoModel).all()

@app.get("/productos/{producto_id}", response_model=ProductoRespuesta, tags=["Productos"])
def obtener_producto(producto_id: int, db: Session = Depends(obtener_base_datos)):
    """Busca y devuelve un producto específico por su ID."""
    producto = db.query(ProductoModel).filter(ProductoModel.id == producto_id).first()
    if not producto:
        raise HTTPException(status_code=404, detail="El producto no fue encontrado.")
    return producto

@app.delete("/productos/{producto_id}", status_code=204, tags=["Productos"])
def eliminar_producto(producto_id: int, db: Session = Depends(obtener_base_datos)):
    """Elimina un producto del catálogo por su ID."""
    producto = db.query(ProductoModel).filter(ProductoModel.id == producto_id).first()
    if not producto:
        raise HTTPException(status_code=404, detail="El producto no fue encontrado.")
    
    db.delete(producto)
    db.commit()
    return
