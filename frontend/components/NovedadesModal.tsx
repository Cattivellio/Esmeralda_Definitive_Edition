import { Modal, Group, Text, Button, ActionIcon, Stack, TextInput, SegmentedControl, Badge, Select, Title, Paper } from '@mantine/core';
import { IconBell, IconTool, IconCheck, IconPlus, IconAlertCircle, IconTrash } from '@tabler/icons-react';
import { useState, useEffect } from 'react';
import { notifications } from '@mantine/notifications';
import { Novedad } from '../types';
import DataTable from './DataTable';

interface NovedadesModalProps {
  opened: boolean;
  onClose: () => void;
  activeUser: string;
}

const ROBOTO_FONT = 'Roboto, sans-serif';
const POPPINS_FONT = 'Poppins, sans-serif';

export default function NovedadesModal({ opened, onClose, activeUser }: NovedadesModalProps) {
  const [novedades, setNovedades] = useState<Novedad[]>([]);
  const [texto, setTexto] = useState('');
  const [tipo, setTipo] = useState<string>('novedad');
  const [loading, setLoading] = useState(false);
  const [loadingList, setLoadingList] = useState(false);
  const [isFullScreen, setIsFullScreen] = useState(false);

  const loadNovedades = async () => {
    setLoadingList(true);
    try {
      const res = await fetch('http://192.168.0.123:8000/api/novedades/');
      if (res.ok) {
        const data = await res.json();
        setNovedades(data);
      }
    } catch (err) {
      console.error("Error loading novedades:", err);
    } finally {
      setLoadingList(false);
    }
  };

  useEffect(() => {
    if (opened) {
      loadNovedades();
    }
  }, [opened]);

  const handleAdd = async () => {
    if (!texto.trim()) return;
    setLoading(true);
    try {
      const res = await fetch('http://192.168.0.123:8000/api/novedades/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          texto,
          tipo,
          usuario: activeUser,
          estado: 'pendiente'
        })
      });

      if (res.ok) {
        setTexto('');
        loadNovedades();
        notifications.show({
          title: 'Registro Exitoso',
          message: `${tipo === 'novedad' ? 'Novedad' : 'Avería'} registrada correctamente`,
          color: 'teal'
        });
      }
    } catch (err) {
      notifications.show({ title: 'Error', message: 'No se pudo guardar la información', color: 'red' });
    } finally {
      setLoading(false);
    }
  };

  const handleResolve = async (id: number) => {
    try {
      const res = await fetch(`http://192.168.0.123:8000/api/novedades/${id}/resolver`, {
        method: 'PUT'
      });
      if (res.ok) {
        loadNovedades();
        notifications.show({
          title: 'Avería Resuelta',
          message: 'El estado se ha actualizado a arreglada',
          color: 'blue'
        });
      }
    } catch (err) {
      notifications.show({ title: 'Error', message: 'No se pudo actualizar el estado', color: 'red' });
    }
  };

  // Filtering is now handled by DataTable component

  const formatDate = (dateStr: string) => {
    const d = new Date(dateStr);
    return d.toLocaleString('es-VE', { 
      day: '2-digit', month: '2-digit', year: '2-digit',
      hour: '2-digit', minute: '2-digit', hour12: false 
    });
  };

  const columns = [
    { key: 'fecha', label: 'Fecha', render: (val: string) => <Text size="xs">{formatDate(val)}</Text> },
    { 
      key: 'tipo', 
      label: 'Tipo', 
      render: (val: string) => (
        <Badge color={val === 'averia' ? 'red' : 'blue'} variant="light">
          {val.toUpperCase()}
        </Badge>
      ) 
    },
    { key: 'usuario', label: 'Usuario', render: (val: string) => <Text size="xs">{val}</Text> },
    { key: 'texto', label: 'Descripción', render: (val: string) => <Text size="sm" maw={300} lineClamp={2}>{val}</Text> },
    { key: 'fecha_resolucion', label: 'Arreglada el', render: (val: string) => <Text size="xs">{val ? formatDate(val) : '-'}</Text> },
    { 
      key: 'estado', 
      label: 'Acción', 
      render: (val: string, row: any) => {
        if (row.tipo === 'averia') {
          return row.estado === 'pendiente' ? (
            <Button 
              size="compact-xs" 
              variant="light" 
              color="orange"
              leftSection={<IconTool size={14} />}
              onClick={() => handleResolve(row.id)}
            >
              Pendiente
            </Button>
          ) : (
            <Badge variant="filled" color="teal" leftSection={<IconCheck size={14} />}>
              Arreglada
            </Badge>
          );
        }
        return <Text size="xs" c="dimmed">-</Text>;
      }
    }
  ];

  return (
    <Modal
      opened={opened}
      onClose={onClose}
      title={
        <Group gap="xs">
          <IconBell size={24} color="#36ea7e" />
          <Title order={3} c="white" style={{ fontFamily: POPPINS_FONT }}>Novedades y Averías</Title>
        </Group>
      }
      fullScreen={isFullScreen}
      size="95%"
      radius="md"
      styles={{
        content: { backgroundColor: '#141414', color: '#e4e4e7', border: '1px solid #2a2a2a' },
        header: { backgroundColor: '#1e1e1e', borderBottom: '1px solid #2a2a2a' },
        close: { color: 'white' }
      }}
    >
      <Stack gap="md">
        <Paper p="md" bg="#1a1a1a" radius="md" style={{ border: '1px solid #2a2a2a' }}>
          <Stack gap="sm">
            <Text size="sm" fw={600} c="dimmed" tt="uppercase" style={{ letterSpacing: '1px' }}>Nuevo Registro</Text>
            <Group align="flex-end" grow>
              <Select
                label="Tipo"
                data={[
                  { value: 'novedad', label: 'Novedad' },
                  { value: 'averia', label: 'Avería' }
                ]}
                value={tipo}
                onChange={(v) => setTipo(v || 'novedad')}
                styles={{
                  input: { backgroundColor: '#ffffff', color: '#111', fontWeight: 600, border: '1px solid #ccc', fontSize: '14px', fontFamily: ROBOTO_FONT, height: '34px', minHeight: '34px' },
                  label: { color: '#ffffff', marginBottom: '4px', fontSize: '13px' }
                }}
              />
              <TextInput
                label="Descripción"
                placeholder="Escriba aquí la novedad o avería..."
                value={texto}
                onChange={(e) => setTexto(e.currentTarget.value)}
                styles={{
                  input: { backgroundColor: '#ffffff', color: '#111', fontWeight: 600, border: '1px solid #ccc', fontSize: '14px', fontFamily: ROBOTO_FONT, height: '34px', minHeight: '34px' },
                  label: { color: '#ffffff', marginBottom: '4px', fontSize: '13px' }
                }}
              />
              <Button 
                onClick={handleAdd} 
                loading={loading}
                style={{ 
                  background: 'linear-gradient(135deg, #36ea7e 0%, #11998e 100%)',
                  height: '36px'
                }}
              >
                Agregar
              </Button>
            </Group>
          </Stack>
        </Paper>

        <DataTable 
          columns={columns} 
          data={novedades} 
          loading={loadingList} 
          pageSize={10} 
          maxHeight={400} 
          searchPlaceholder="Filtrar por descripción, usuario..."
          filterOptions={[
            { value: 'novedad', label: 'Novedades' },
            { value: 'averia', label: 'Averías' }
          ]}
          filterKey="tipo"
          onFullScreenToggle={setIsFullScreen}
          isFullScreen={isFullScreen}
        />
      </Stack>
    </Modal>
  );
}
