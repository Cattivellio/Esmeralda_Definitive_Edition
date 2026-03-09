'use client';

import { Box } from '@mantine/core';
import { Habitacion } from '../types';
import HabitacionCard from './HabitacionCard';

interface ModernGridProps {
  habitaciones: Habitacion[];
  onRoomClick: (hab: Habitacion) => void;
  bcv: number;
}

export default function ModernGrid({ habitaciones, onRoomClick, bcv }: ModernGridProps) {
  // Ordenar lógicamente las habitaciones por número para esta vista en lista/cuadrángulo
  // (Así no aparecen desordenadas por el archivo de la bd si las jalamos en el orden que vienen)
  const habitacionesOrdenadas = [...habitaciones].sort((a, b) => {
    return a.numero.localeCompare(b.numero, undefined, { numeric: true });
  });

  return (
    <Box 
      style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(100px, 1fr))', // Piezas más anchas para ajustarse
        gridAutoRows: 'minmax(120px, 1fr)', // Auto-distribuye el alto exacto requerido para rellenar toda la pantalla hacia abajo
        gap: '12px',
        padding: '0.5rem',
        width: '100%',
        height: '100%',
      }}
    >
      {habitacionesOrdenadas.map(hab => (
        <HabitacionCard key={hab.id} habitacion={hab} disablePosition={true} onClick={onRoomClick} bcv={bcv} />
      ))}
    </Box>
  );
}
