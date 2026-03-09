import React, { useState } from 'react';
import { Modal, Button, Select, Text, Stack, TextInput, Textarea } from '@mantine/core';
import { notifications } from '@mantine/notifications';
import { IconCheck, IconAlertCircle } from '@tabler/icons-react';
import { api } from '../app/lib/api';

const ROBOTO_FONT = 'Roboto, sans-serif';
const LABEL_SIZE = '13px';
const INPUT_SIZE = '14px';
const INPUT_HEIGHT = '34px';

interface CambioTurnoModalProps {
  opened: boolean;
  onClose: () => void;
  users: Array<{ id?: number; username: string; rol?: string }>;
  currentUser: string;
  onSuccess: (newUser: string) => void;
}

export default function CambioTurnoModal({ 
  opened, 
  onClose, 
  users, 
  currentUser,
  onSuccess 
}: CambioTurnoModalProps) {
  const [selectedUser, setSelectedUser] = useState<string | null>(null);
  const [observaciones, setObservaciones] = useState('');
  const [loading, setLoading] = useState(false);

  React.useEffect(() => {
    if (opened) {
      setSelectedUser(null);
      setObservaciones('');
    }
  }, [opened]);

  const recepcionistas = users
    .filter((u) => u.username !== currentUser && u.rol && u.rol.toLowerCase() === 'recepcionista')
    .map((u) => u.username);
  
  const dataOptions = recepcionistas.length > 0 ? recepcionistas : [];

  const handleSubmit = async () => {
    if (!selectedUser) {
      notifications.show({
        title: 'Error',
        message: 'Debe seleccionar quién recibe el turno.',
        color: 'red',
        icon: <IconAlertCircle size={18} />
      });
      return;
    }

    setLoading(true);
    try {
      await api.realizarCambioTurno({
        usuario_entrante: selectedUser,
        usuario_saliente: currentUser,
        observaciones: observaciones
      });

      notifications.show({
        title: 'Turno Cambiado',
        message: `El turno ha sido entregado a ${selectedUser}.`,
        color: 'teal',
        icon: <IconCheck size={18} />
      });
      onSuccess(selectedUser);
      onClose();
    } catch (e: any) {
      notifications.show({
        title: 'Error al cambiar turno',
        message: e.message || 'Error de red.',
        color: 'red',
        icon: <IconAlertCircle size={18} />
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <Modal
      opened={opened}
      onClose={onClose}
      title={<Text fw={700} size="lg">Cambio de Turno</Text>}
      centered
      radius="md"
      overlayProps={{ blur: 3, backgroundOpacity: 0.55 }}
    >
      <Stack gap="md">
        <Text size="sm" c="dimmed">
          Está a punto de entregar su turno. Por favor indique quién recibe la guardia y si hay alguna observación importante.
        </Text>

        <TextInput
          label={<Text size={LABEL_SIZE} fw={500} style={{ fontFamily: ROBOTO_FONT }}>Entregado por (Actual)</Text>}
          value={currentUser}
          readOnly
          disabled
          variant="filled"
          styles={{ input: { backgroundColor: '#f1f3f5', height: INPUT_HEIGHT, minHeight: INPUT_HEIGHT, fontSize: INPUT_SIZE, fontFamily: ROBOTO_FONT } }}
        />

        <Select
          label={<Text size={LABEL_SIZE} fw={500} style={{ fontFamily: ROBOTO_FONT }}>Recibido por (Entrante)</Text>}
          placeholder="Seleccione el nuevo recepcionista"
          data={dataOptions}
          value={selectedUser}
          onChange={setSelectedUser}
          required
          searchable
          nothingFoundMessage="No se encontraron usuarios"
          styles={{ input: { backgroundColor: '#ffffff', color: 'black', height: INPUT_HEIGHT, minHeight: INPUT_HEIGHT, fontSize: INPUT_SIZE, fontFamily: ROBOTO_FONT } }}
        />

        <Textarea
          label={<Text size={LABEL_SIZE} fw={500} style={{ fontFamily: ROBOTO_FONT }}>Observaciones (Opcional)</Text>}
          placeholder="Novedades, dinero en caja, incidentes..."
          value={observaciones}
          onChange={(e) => setObservaciones(e.currentTarget.value)}
          minRows={3}
          styles={{ input: { backgroundColor: '#ffffff', color: 'black', fontSize: INPUT_SIZE, fontFamily: ROBOTO_FONT } }}
        />

        <Button 
          fullWidth 
          h={INPUT_HEIGHT}
          color="teal" 
          onClick={handleSubmit} 
          loading={loading}
          mt="sm"
          styles={{ root: { fontSize: INPUT_SIZE, fontFamily: ROBOTO_FONT } }}
        >
          Confirmar Cambio de Turno
        </Button>
      </Stack>
    </Modal>
  );
}
