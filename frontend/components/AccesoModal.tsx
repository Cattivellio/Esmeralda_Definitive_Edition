'use client';

import { useState, useEffect } from 'react';
import { Modal, Select, MultiSelect, Button, Group, Stack, Text, LoadingOverlay, Box, Tooltip, Avatar } from '@mantine/core';
import { IconDoorEnter, IconDoorExit, IconCheck, IconAlertCircle, IconUsers } from '@tabler/icons-react';
import { notifications } from '@mantine/notifications';

const ROBOTO_FONT = 'Roboto, sans-serif';
const LABEL_SIZE = '13px';
const INPUT_SIZE = '14px';
const INPUT_HEIGHT = '34px';

interface AccesoModalProps {
  opened: boolean;
  onClose: () => void;
  tipo: 'entrada' | 'salida';
}

interface Persona {
  nombre: string;
  cedula: string;
  cargo: string;
  estado: string; // "presente" o "ausente"
}

export default function AccesoModal({ opened, onClose, tipo }: AccesoModalProps) {
  const [cargosResumen, setCargosResumen] = useState<any[]>([]);
  const [selectedCargo, setSelectedCargo] = useState<string | null>(null);
  const [personas, setPersonas] = useState<Persona[]>([]);
  const [selectedPersonas, setSelectedPersonas] = useState<string[]>([]);
  const [loading, setLoading] = useState(false);
  const [submitting, setSubmitting] = useState(false);

  // Cargar resumen de cargos al abrir
  useEffect(() => {
    if (opened) {
      loadCargosResumen();
      setSelectedCargo(null);
      setPersonas([]);
      setSelectedPersonas([]);
    }
  }, [opened]);

  // Cargar personas cuando cambia el cargo
  useEffect(() => {
    if (selectedCargo) {
      loadPersonas(selectedCargo);
    }
  }, [selectedCargo]);

  const loadCargosResumen = async () => {
    setLoading(true);
    try {
      const res = await fetch('http://192.168.0.123:8000/api/acceso/cargos-resumen');
      if (res.ok) {
        const data = await res.json();
        setCargosResumen(data);
      }
    } catch (err) {
      console.error("Error loading cargos-resumen:", err);
    } finally {
      setLoading(false);
    }
  };

  const loadPersonas = async (cargo: string) => {
    setLoading(true);
    try {
      const res = await fetch(`http://192.168.0.123:8000/api/acceso/personas/${cargo}`);
      if (res.ok) {
        const data = await res.json();
        setPersonas(prev => {
          const map = new Map(prev.map(p => [p.cedula, p]));
          data.forEach((p: Persona) => map.set(p.cedula, p));
          return Array.from(map.values());
        });
      }
    } catch (err) {
      console.error("Error loading personas:", err);
    } finally {
      setLoading(false);
    }
  };

  const handleRegistrar = async () => {
    if (selectedPersonas.length === 0) return;

    // Obtener objetos persona completos que vamos a registrar
    const personasToRegister = personas.filter(p => selectedPersonas.includes(p.cedula));

    if (personasToRegister.length === 0) return;

    setSubmitting(true);
    try {
      const res = await fetch('http://192.168.0.123:8000/api/acceso/registrar', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          personas: personasToRegister,
          tipo: tipo
        })
      });

      if (res.ok) {
        const data = await res.json();
        const num = data.modificados;
        notifications.show({
          title: tipo === 'entrada' ? 'ENTRADA Registrada' : 'SALIDA Registrada',
          message: `Se registraron exitosamente a ${num} persona(s).`,
          color: tipo === 'entrada' ? 'rgb(40, 190, 100)' : 'rgb(242, 5, 5)',
          icon: <IconCheck size={18} />
        });
        onClose();
      } else {
        const error = await res.json();
        notifications.show({
          title: 'Error',
          message: error.detail || 'Ocurrió un problema en la operación.',
          color: 'red',
          icon: <IconAlertCircle size={18} />
        });
      }
    } catch (err) {
      notifications.show({ title: 'Error de red', message: 'No se pudo conectar con el servidor', color: 'red' });
    } finally {
      setSubmitting(false);
    }
  };

  // Preparar opciones de cargo mapeando el resumen
  const cargosOptions = cargosResumen.map(c => {
    // Si la operación es Entrada, requiero que haya Ausentes (>0)
    // Si la operación es Salida, requiero que haya Presentes (>0)
    const countAvailable = tipo === 'entrada' ? c.ausentes : c.presentes;
    const isDisabled = countAvailable === 0;

    return {
      value: c.cargo,
      label: c.cargo,
      disabled: isDisabled,
      countAvailable
    };
  });

  // Filtrar personas a mostrar en el Multiselect (las del cargo actual + las ya seleccionadas previamente)
  const personasOptions = personas
    .filter(p => {
      const isValidState = tipo === 'entrada' ? p.estado === 'ausente' : p.estado === 'presente';
      const isCurrentCargo = p.cargo === selectedCargo;
      const isSelected = selectedPersonas.includes(p.cedula);
      return isValidState && (isCurrentCargo || isSelected);
    })
    .map(p => ({
      value: p.cedula,
      label: p.cargo !== selectedCargo ? `${p.nombre} (${p.cargo})` : p.nombre,
      description: p.cedula
    }));

  return (
    <Modal
      opened={opened}
      onClose={onClose}
      title={
        <Group gap="xs">
          {tipo === 'entrada' ? <IconDoorEnter color="rgb(40, 190, 100)" /> : <IconDoorExit color="rgb(242, 5, 5)" />}
          <Text fw={700} size="lg">Control de Portones: {tipo === 'entrada' ? 'ENTRADA' : 'SALIDA'}</Text>
        </Group>
      }
      size="md"
      centered
      radius="md"
      styles={{
        header: { backgroundColor: '#1e1e1e', borderBottom: '1px solid #2a2a2a' },
        content: { backgroundColor: '#141414', color: 'white' },
        title: { color: 'white' },
        close: { color: 'white' }
      }}
    >
      <Box pos="relative">
        <LoadingOverlay visible={loading || submitting} overlayProps={{ blur: 2 }} zIndex={100} />
        <Stack gap="md">
          <Select
            label={<Text size={LABEL_SIZE} c="white" fw={500} style={{ fontFamily: ROBOTO_FONT }}>Filtrar por Cargo</Text>}
            placeholder="Seleccione un cargo"
            data={cargosOptions.map(c => ({ value: c.value, label: c.label, disabled: c.disabled }))}
            value={selectedCargo}
            onChange={setSelectedCargo}
            searchable
            styles={{ input: { backgroundColor: '#ffffff', color: 'black', height: INPUT_HEIGHT, minHeight: INPUT_HEIGHT, fontSize: INPUT_SIZE, fontFamily: ROBOTO_FONT } }}
            renderOption={({ option, checked }) => {
              const opt = cargosOptions.find(o => o.value === option.value);
              const isDisabled = opt?.disabled;
              const content = (
                <Group justify="space-between" w="100%" wrap="nowrap" style={{ opacity: isDisabled ? 0.5 : 1 }}>
                  <Text size="sm">{option.label}</Text>
                  <Text size="xs" c={isDisabled ? "dimmed" : "teal"}>{opt?.countAvailable} disponibles</Text>
                </Group>
              );

              if (isDisabled) {
                return (
                  <Tooltip label={`No hay personas con el cargo de ${option.label} ${tipo === 'entrada' ? 'fuera' : 'dentro'} del hotel`} position="right">
                    {content}
                  </Tooltip>
                );
              }
              return content;
            }}
          />

          <MultiSelect
            label={<Text size={LABEL_SIZE} c="white" fw={500} style={{ fontFamily: ROBOTO_FONT }}>Personas</Text>}
            placeholder={selectedCargo ? "Seleccione o busque personas" : "Primero seleccione un cargo"}
            data={personasOptions}
            value={selectedPersonas}
            onChange={setSelectedPersonas}
            searchable
            clearable
            disabled={!selectedCargo}
            leftSection={<IconUsers size={16} />}
            hidePickedOptions
            maxDropdownHeight={200}
            styles={{ input: { backgroundColor: '#ffffff', color: 'black', minHeight: INPUT_HEIGHT, fontSize: INPUT_SIZE, fontFamily: ROBOTO_FONT } }}
          />

          <Button 
            fullWidth 
            h={INPUT_HEIGHT}
            radius="md"
            mt="md"
            style={{ 
              backgroundColor: tipo === 'entrada' ? 'rgb(40, 190, 100)' : 'rgb(242, 5, 5)',
              fontSize: INPUT_SIZE, 
              fontFamily: ROBOTO_FONT,
              textTransform: 'uppercase'
            }}
            disabled={selectedPersonas.length === 0}
            onClick={handleRegistrar}
            leftSection={tipo === 'entrada' ? <IconDoorEnter size={20} /> : <IconDoorExit size={20} />}
          >
            Confirmar {tipo === 'entrada' ? 'Entrada' : 'Salida'} ({selectedPersonas.length})
          </Button>
        </Stack>
      </Box>
    </Modal>
  );
}
