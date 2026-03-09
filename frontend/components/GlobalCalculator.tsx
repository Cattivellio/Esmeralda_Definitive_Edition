'use client';
import { useState, useEffect } from 'react';
import CalculadoraModal from './CalculadoraModal';
import { api } from '../app/lib/api';

export default function GlobalCalculator() {
  const [opened, setOpened] = useState(false);
  const [tasa, setTasa] = useState(0);
  const [roomPrices, setRoomPrices] = useState<{ tipo: string, parcial: number, hospedaje: number }[]>([]);

  useEffect(() => {
    const loadData = async () => {
      try {
        const config = await api.getConfig('bcv');
        setTasa(parseFloat(config.valor) || 0);

        const habitaciones = await api.getHabitaciones();
        // Extract unique types and their first-encountered prices
        const typesMap: Record<string, { tipo: string, parcial: number, hospedaje: number }> = {};
        habitaciones.forEach(h => {
          if (!typesMap[h.tipo]) {
            typesMap[h.tipo] = {
              tipo: h.tipo,
              parcial: h.precio_parcial || 0,
              hospedaje: h.precio_hospedaje || 0
            };
          }
        });
        setRoomPrices(Object.values(typesMap));
      } catch (err) {
        console.error("Error loading calculator data:", err);
      }
    };
    
    loadData();

    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.altKey && e.key.toLowerCase() === 'c') {
        e.preventDefault();
        setOpened(prev => !prev);
      }
    };

    const handleToggleEvent = () => setOpened(prev => !prev);

    window.addEventListener('keydown', handleKeyDown);
    window.addEventListener('toggle-calculator', handleToggleEvent);
    return () => {
      window.removeEventListener('keydown', handleKeyDown);
      window.removeEventListener('toggle-calculator', handleToggleEvent);
    };
  }, []);

  return (
    <CalculadoraModal 
      opened={opened} 
      onClose={() => setOpened(false)} 
      tasa={tasa} 
      roomPrices={roomPrices}
    />
  );
}
