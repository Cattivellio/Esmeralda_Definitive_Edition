import { Badge, Box, Text, Tooltip, Paper, Group } from '@mantine/core';
import { Habitacion } from '../types';
import classes from './HabitacionCard.module.css';

interface HabitacionCardProps {
  habitacion: Habitacion;
  disablePosition?: boolean;
  onClick?: (hab: Habitacion) => void;
  bcv?: number;
}

// Mapa de colores exactos como en la imagen
const estadoColores: Record<string, string> = {
  Libre: 'linear-gradient(135deg, rgb(5, 117, 230) 0%, rgb(2, 27, 121) 100%)',
  Hospedaje: 'linear-gradient(135deg, rgb(189, 195, 199) 0%, rgb(36, 54, 70) 100%)',
  Parcial: 'linear-gradient(135deg, rgb(180, 20, 20) 0%, rgb(60, 0, 0) 100%)',
  Sucia: 'linear-gradient(135deg, rgb(220, 82, 45) 0%, rgb(70, 40, 20) 100%)',
  Retoque: 'linear-gradient(135deg, rgb(120, 40, 240) 0%, rgb(60, 10, 100) 100%)',
  Bloqueada: 'linear-gradient(135deg, #444 0%, #000 100%)',
  Reservada: 'linear-gradient(135deg, rgb(20, 171, 169) 0%, rgb(10, 60, 130) 100%)',
};

export default function HabitacionCard({ habitacion, disablePosition = false, onClick, bcv = 0 }: HabitacionCardProps) {
  const isVencida = habitacion.hora_salida && new Date(habitacion.hora_salida) < new Date();
  
  const tooltipLabel = (
    <Box p={4}>
      <Text fw={700} size="sm" mb={4} style={{ borderBottom: '1px solid rgba(255,255,255,0.2)', paddingBottom: 2 }}>
        {habitacion.tipo.toUpperCase()} - {habitacion.estado_actual}
      </Text>
      
      <Group gap="xs" wrap="nowrap" mb={2}>
        <Box style={{ width: 10, height: 10, borderRadius: '50%', background: estadoColores.Parcial }} />
        <Text size="xs" fw={600}>${habitacion.precio_parcial.toFixed(2)}</Text>
        <Text size="xs" c="dimmed">({(habitacion.precio_parcial * bcv).toLocaleString('es-VE')} Bs)</Text>
      </Group>

      <Group gap="xs" wrap="nowrap">
        <Box style={{ width: 10, height: 10, borderRadius: '50%', background: estadoColores.Hospedaje }} />
        <Text size="xs" fw={600}>${habitacion.precio_hospedaje.toFixed(2)}</Text>
        <Text size="xs" c="dimmed">({(habitacion.precio_hospedaje * bcv).toLocaleString('es-VE')} Bs)</Text>
      </Group>
    </Box>
  );

  return (
    <Tooltip 
      label={tooltipLabel} 
      position="top" 
      withArrow
      multiline
      transitionProps={{ transition: 'pop', duration: 200 }}
    >
      <Paper
        radius="12px"
        p="xs"
        className={`${classes.card} ${isVencida ? classes.vencida : ''}`}
        style={{ 
          background: estadoColores[habitacion.estado_actual] || '#444', 
          color: 'white',
          gridColumn: disablePosition ? 'auto' : (habitacion.pos_x || 'auto'),
          gridRow: disablePosition ? 'auto' : (habitacion.pos_y || 'auto'),
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          cursor: 'pointer',
          width: '100%',
          height: '100%',
          boxSizing: 'border-box',
        }}
        onClick={() => onClick && onClick(habitacion)}
      >
        <Text fw={500} lh={1} style={{ fontSize: 'clamp(1rem, 1.8vw, 3rem)' }}>
          {habitacion.numero}
        </Text>
        <Text fw={400} lh={1} opacity={0.8} style={{ fontSize: 'clamp(0.6rem, 1vw, 1.2rem)', marginTop: '4px' }}>
          {habitacion.abreviatura_tipo}
        </Text>
      </Paper>
    </Tooltip>
  );
}
