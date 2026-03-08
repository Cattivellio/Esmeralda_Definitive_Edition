'use client';

import { Modal, Text, Button, Group, Stack, Textarea, Select } from '@mantine/core';
import { Habitacion } from '../types';
import { useState, useEffect } from 'react';
import { notifications } from '@mantine/notifications';
import { IconCheck, IconTrash, IconLockOpen } from '@tabler/icons-react';

interface DirtyRoomModalProps {
  habitacion: Habitacion | null;
  onClose: () => void;
  onSuccess: () => void;
}

export function DirtyRoomModal({ habitacion, onClose, onSuccess }: DirtyRoomModalProps) {
  const [loading, setLoading] = useState(false);
  const [camareras, setCamareras] = useState<{value: string, label: string}[]>([]);
  const [camareraId, setCamareraId] = useState<string | null>(null);

  useEffect(() => {
    if (habitacion) {
      fetch('http://192.168.0.123:8000/api/habitaciones/camareras-presentes')
        .then(res => res.json())
        .then(data => {
            setCamareras(data.map((u: any) => ({ value: u.id.toString(), label: u.nombre })));
        })
        .catch(console.error);
    } else {
        setCamareraId(null);
    }
  }, [habitacion]);

  const handleClean = async () => {
    if (!habitacion || !camareraId) return;
    setLoading(true);
    try {
      const response = await fetch(`http://192.168.0.123:8000/api/habitaciones/${habitacion.id}/limpiar`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ camarera_id: parseInt(camareraId) })
      });
      if (response.ok) {
        notifications.show({
          title: 'Éxito',
          message: `La habitación ${habitacion.numero} ha sido limpiada.`,
          color: 'green',
          icon: <IconCheck size={16} />
        });
        onSuccess();
        onClose();
      }
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Modal 
      opened={!!habitacion} 
      onClose={onClose} 
      title={`Limpieza de Habitación ${habitacion?.numero}`}
      centered
      radius="md"
      styles={{
        header: { backgroundColor: '#1a1a1a', color: 'white' },
        content: { backgroundColor: '#141414', color: 'white' },
      }}
    >
      <Stack>
        <Text size="sm">¿Desea marcar esta habitación como limpia? Seleccione la camarera que realizó la limpieza.</Text>
        
        <Select
          label="Camarera"
          placeholder="Seleccione camarera presente"
          data={camareras}
          value={camareraId}
          onChange={setCamareraId}
          required
          styles={{
            input: { backgroundColor: 'white', color: 'black' },
            label: { color: 'white' }
          }}
        />

        <Group justify="flex-end" mt="md">
          <Button variant="subtle" color="gray" onClick={onClose}>Cancelar</Button>
          <Button color="green" loading={loading} onClick={handleClean} disabled={!camareraId} leftSection={<IconCheck size={16}/>}>
            Sí, Limpiar
          </Button>
        </Group>
      </Stack>
    </Modal>
  );
}

interface BlockedRoomModalProps {
  habitacion: Habitacion | null;
  onClose: () => void;
  onSuccess: () => void;
}

export function BlockedRoomModal({ habitacion, onClose, onSuccess }: BlockedRoomModalProps) {
  const [loading, setLoading] = useState(false);

  const handleUnblock = async () => {
    if (!habitacion) return;
    setLoading(true);
    try {
      const response = await fetch(`http://192.168.0.123:8000/api/habitaciones/${habitacion.id}/desbloquear`, {
        method: 'POST',
      });
      if (response.ok) {
        notifications.show({
          title: 'Éxito',
          message: `La habitación ${habitacion.numero} ha sido desbloqueada.`,
          color: 'blue',
          icon: <IconLockOpen size={16} />
        });
        onSuccess();
        onClose();
      }
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Modal 
      opened={!!habitacion} 
      onClose={onClose} 
      title={`Habitación Bloqueada ${habitacion?.numero}`}
      centered
      radius="md"
      styles={{
        header: { backgroundColor: '#1a1a1a', color: 'white' },
        content: { backgroundColor: '#141414', color: 'white' },
      }}
    >
      <Stack>
        <Text size="sm" fw={700} c="dimmed" tt="uppercase">Razón del bloqueo:</Text>
        <Text p="md" bg="#1a1a1a" style={{ borderRadius: '8px', border: '1px solid #333' }}>
          {habitacion?.razon_bloqueo || 'No se especificó una razón.'}
        </Text>
        
        <Text size="sm" mt="md">¿Desea desbloquear esta habitación ahora?</Text>
        
        <Group justify="flex-end" mt="md">
          <Button variant="subtle" color="gray" onClick={onClose}>Cerrar</Button>
          <Button color="blue" loading={loading} onClick={handleUnblock} leftSection={<IconLockOpen size={16}/>}>
            Desbloquear
          </Button>
        </Group>
      </Stack>
    </Modal>
  );
}
