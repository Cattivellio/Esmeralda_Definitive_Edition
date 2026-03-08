export interface Habitacion {
  id: number;
  numero: string;
  tipo: string;
  precio_parcial: number;
  precio_hospedaje: number;
  descripcion: string;
  amenities: string;
  observaciones: string;
  razon_bloqueo: string;
  estado_actual: string;
  pos_x: number | null;
  pos_y: number | null;
  hora_salida: string | null;
  capacidad: number;
  abreviatura_tipo: string;
}

export interface Novedad {
  id: number;
  fecha: string;
  texto: string;
  tipo: 'novedad' | 'averia';
  estado: 'pendiente' | 'arreglada';
  usuario: string;
}
