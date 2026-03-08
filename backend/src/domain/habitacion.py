from pydantic import BaseModel, computed_field
from typing import Optional

class Habitacion(BaseModel):
    id: int
    numero: str
    tipo: str
    precio_parcial: float = 0.0
    precio_hospedaje: float = 0.0
    descripcion: Optional[str] = ""
    amenities: Optional[str] = ""
    observaciones: Optional[str] = ""
    razon_bloqueo: Optional[str] = ""
    capacidad: int = 2
    nfc_code: Optional[str] = None
    
    estado_actual: str = "Libre" # Libre, Hospedaje, Parcial, Sucia, Retoque, Bloqueada
    
    pos_x: Optional[int] = None
    pos_y: Optional[int] = None
    
    # Nuevo campo para identificar si tiene borde rojo (tiempo vencido)
    hora_salida: Optional[str] = None # Formato ISO si aplica

    @computed_field
    @property
    def abreviatura_tipo(self) -> str:
        return self.tipo[:2].upper() if self.tipo else ""
