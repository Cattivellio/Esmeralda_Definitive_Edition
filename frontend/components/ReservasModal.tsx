'use client';

import { Modal, Button, Group, Badge, Text, ActionIcon, Tooltip, Box } from '@mantine/core';
import { IconCheck, IconX, IconCalendar } from '@tabler/icons-react';
import DataTable from './DataTable';
import { useState, useEffect } from 'react';
import { notifications } from '@mantine/notifications';
import { api } from '../app/lib/api';
import dayjs from 'dayjs';

interface ReservasModalProps {
  opened: boolean;
  onClose: () => void;
  onSuccess?: () => void;
}

export default function ReservasModal({ opened, onClose, onSuccess }: ReservasModalProps) {
  const [data, setData] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);

  const fetchReservas = async () => {
    setLoading(true);
    try {
      const respData = await api.getReservasProximas();
      setData(respData);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (opened) fetchReservas();
  }, [opened]);

  const handleCancelar = async (id: string) => {
    if (!confirm('¿Está seguro de cancelar esta reserva?')) return;
    try {
      await api.cancelarReserva(id);
      notifications.show({ title: 'Éxito', message: 'Reserva cancelada', color: 'red' });
      fetchReservas();
      if (onSuccess) onSuccess();
    } catch (err) {
      console.error(err);
    }
  };

  const handleActivar = async (id: string) => {
    try {
      await api.activarReserva(id);
      notifications.show({ title: 'Éxito', message: 'Reserva activada correctamente', color: 'green' });
      fetchReservas();
      if (onSuccess) onSuccess();
    } catch (err: any) {
      notifications.show({ title: 'Error', message: err.message || 'No se pudo activar', color: 'red' });
    }
  };

  const [isFullScreen, setIsFullScreen] = useState(false);

  const columns = [
    { key: 'habitacion_numero', label: 'Hab.', render: (val: string) => <Badge variant="outline" color="gray">H-{val}</Badge> },
    { key: 'cliente_nombre', label: 'Cliente', render: (val: string) => <Text fw={700} size="sm">{val}</Text> },
    { key: 'fecha_entrada', label: 'Entrada', render: (val: string) => dayjs(val).format('DD-MM-YYYY HH:mm') },
    { key: 'fecha_salida', label: 'Salida', render: (val: string) => dayjs(val).format('DD-MM-YYYY HH:mm') },
    { key: 'tipo_estadia', label: 'Tipo', render: (val: string) => (
      <Badge color={val === 'hospedaje' ? 'blue' : 'orange'} variant="filled" tt="uppercase">{val}</Badge>
    )},
    { 
      key: 'pago', 
      label: 'Pago', 
      render: (_: any, row: any) => {
        const fullPaid = row.monto_pagado >= (row.monto_total - 0.01);
        return (
          <Group gap={4} wrap="nowrap">
            <Badge color={fullPaid ? 'green' : 'red'} variant="light">
              ${row.monto_pagado.toFixed(2)} / ${row.monto_total.toFixed(2)}
            </Badge>
            <Text size="xs" c="dimmed">({row.metodo_pago})</Text>
          </Group>
        );
      } 
    },
    { key: 'usuario_creacion', label: 'Registró', render: (val: string, row: any) => (
      <Box>
        <Text size="xs" fw={500}>{val}</Text>
        <Text size="10px" c="dimmed">{dayjs(row.fecha_creacion).format('DD/MM HH:mm')}</Text>
      </Box>
    )},
    { 
      key: 'acciones', 
      label: 'Acciones', 
      render: (_: any, row: any) => (
        <Group gap="xs" wrap="nowrap">
          <Tooltip label="Activar Reserva">
            <ActionIcon color="green" variant="light" onClick={() => handleActivar(row.id)}>
              <IconCheck size={18} />
            </ActionIcon>
          </Tooltip>
          <Tooltip label="Cancelar Reserva">
            <ActionIcon color="red" variant="light" onClick={() => handleCancelar(row.id)}>
              <IconX size={18} />
            </ActionIcon>
          </Tooltip>
        </Group>
      )
    }
  ];

  return (
    <Modal
      opened={opened}
      onClose={onClose}
      title={<Group gap="xs"><IconCalendar color="#36ea7e" /><Text fw={700} size="lg">Reservas Próximas</Text></Group>}
      size="xl"
      centered
      fullScreen={isFullScreen}
      styles={{
        content: { backgroundColor: '#141414', border: '1px solid #2a2a2a', color: 'white' },
        header: { backgroundColor: '#1a1a1a', borderBottom: '1px solid #2a2a2a' },
        title: { color: 'white' },
        close: { color: 'white' }
      }}
    >
      <Box mt="md">
        <DataTable 
          columns={columns}
          data={data}
          loading={loading}
          maxHeight="60vh"
          searchPlaceholder="Buscar por nombre, habitación..."
          onFullScreenToggle={setIsFullScreen}
          isFullScreen={isFullScreen}
          filterKey="tipo_estadia"
          filterOptions={[
            { value: 'hospedaje', label: 'Hospedajes' },
            { value: 'parcial', label: 'Parciales' }
          ]}
        />
      </Box>
    </Modal>
  );
}
