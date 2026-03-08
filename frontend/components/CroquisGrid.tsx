'use client';

import { Box } from '@mantine/core';
import { Habitacion } from '../types';
import HabitacionCard from './HabitacionCard';

interface CroquisGridProps {
  habitaciones: Habitacion[];
  onRoomClick: (hab: Habitacion) => void;
}

export default function CroquisGrid({ habitaciones, onRoomClick }: CroquisGridProps) {
  return (
    <Box 
      style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(12, minmax(0, 1fr))',
        gridTemplateRows: 'repeat(8, 1fr)',
        gap: '6px',
        padding: '0.5rem',
        backgroundColor: 'transparent', // Se mezcla limpiamente con el appshell
        borderRadius: '8px',
        flex: 1,
        width: '100%',
        boxSizing: 'border-box',
      }}
    >
      {habitaciones.map(hab => (
        <HabitacionCard key={hab.id} habitacion={hab} onClick={onRoomClick} />
      ))}
    </Box>
  );
}
