'use client';

import { 
  Box, Title, Text, Stack, Paper, Group, ActionIcon, 
  Switch, TextInput, NumberInput, Button, SimpleGrid,
  Badge, Divider, UnstyledButton, Table, Loader, Center,
  Tabs, Stepper, Modal, FileButton, Card
} from '@mantine/core';
import { 
  IconBed, IconCash, IconSettings, IconUsers, IconTrash, 
  IconPlus, IconArrowLeft, IconDeviceFloppy, IconChevronRight, IconDatabase,
  IconNfc, IconCheck, IconX
} from '@tabler/icons-react';
import { useState, useEffect } from 'react';
import { DashboardTable } from '../components/DashboardTable';
import { api } from '../../lib/api';
import { notifications } from '@mantine/notifications';

type ConfigSection = 'habitaciones' | 'pagos' | 'general' | 'personal' | 'datos' | null;

export default function ConfiguracionSection() {
  const [activeSection, setActiveSection] = useState<ConfigSection>(null);
  const [loading, setLoading] = useState(false);

  // --- STATE ---
  const [habData, setHabData] = useState<any[]>([]);
  const [payData, setPayData] = useState<any[]>([]);
  const [inspecciones, setInspecciones] = useState<any[]>([]);
  const [activeSubTab, setActiveSubTab] = useState<string | null>('inspecciones');
  const [isInspeccionWizardOpen, setIsInspeccionWizardOpen] = useState(false);
  const [inspeccionStep, setInspeccionStep] = useState(0);
  const [currentInspeccion, setCurrentInspeccion] = useState<any>({
    telefono: 'Bien', televisor: 'Bien', aire_acondicionado: 'Bien',
    luces: 'Bien', cama: 'Bien', ducha_agua: 'Bien', observaciones: ''
  });
  const [scannedRoom, setScannedRoom] = useState<any>(null);
  const [settings, setSettings] = useState({
    bcv: '0',
    hotel_name: 'Posada Esmeralda',
    hotel_rif: 'J-12345678-9'
  });

  useEffect(() => {
    if (!activeSection) return;
    
    const fetchData = async () => {
      setLoading(true);
      try {
        if (activeSection === 'habitaciones') {
          const data = await api.getHabitaciones();
          setHabData(data);
          const resI = await fetch('http://192.168.0.123:8000/api/configuracion/inspecciones');
          if (resI.ok) setInspecciones(await resI.json());
        } else if (activeSection === 'pagos') {
          const data = await api.getMetodosPago();
          setPayData(data);
        } else if (activeSection === 'general') {
          const bcv = await api.getConfig('bcv');
          setSettings(prev => ({ ...prev, bcv: bcv.valor }));
        }
      } catch (error) {
        console.error('Error fetching config data:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [activeSection]);

  // --- RENDERS ---
  const updateHabitacionConfig = async (h: any) => {
    try {
      await fetch(`http://192.168.0.123:8000/api/configuracion/habitaciones/${h.id}/precios`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          tipo: h.tipo,
          precio_parcial: h.precio_parcial, 
          precio_hospedaje: h.precio_hospedaje, 
          capacidad: h.capacidad || 2, 
          observaciones: h.observaciones || '',
          descripcion: h.descripcion || '',
          nfc_code: h.nfc_code || null
        })
      });
      notifications.show({ message: 'Habitación actualizada', color: 'teal', icon: <IconDeviceFloppy size={16} /> });
    } catch (err) {
      console.error(err);
      notifications.show({ message: 'Error al actualizar', color: 'red' });
    }
  };

  const scanNfc = async (index: number) => {
    if (!('NDEFReader' in window)) {
      notifications.show({
        title: 'No compatible',
        message: 'Tu dispositivo o navegador no soporta lectura NFC.',
        color: 'red'
      });
      return;
    }

    try {
      // @ts-ignore
      const reader = new NDEFReader();
      await reader.scan();
      notifications.show({ message: 'Acerque el tag NFC al dispositivo...', color: 'blue', loading: true, id: 'nfc-scan' });
      
      reader.onreading = (event: any) => {
        const serialNumber = event.serialNumber;
        const next = [...habData];
        next[index].nfc_code = serialNumber;
        setHabData(next);
        notifications.hide('nfc-scan');
        notifications.show({ message: `Código NFC detectado: ${serialNumber}`, color: 'green' });
      };
    } catch (error) {
      notifications.hide('nfc-scan');
      notifications.show({ message: 'Error al iniciar escaneo NFC', color: 'red' });
    }
  };

  const renderHabRow = (item: any, index: number) => (
    <Table.Tr key={item.id}>
      <Table.Td style={{ textAlign: 'center' }}><Text fw={900} c="white" size="lg">{item.numero}</Text></Table.Td>
      <Table.Td>
        <TextInput 
          size="xs"
          value={item.tipo} 
          onChange={(e) => {
            const next = [...habData];
            next[index].tipo = e.target.value;
            setHabData(next);
          }} 
          style={{ width: 80 }}
          styles={{ input: { backgroundColor: '#2a2a2a', color: 'white', border: '1px solid #333', fontWeight: 700 } }}
        />
      </Table.Td>
      <Table.Td>
        <NumberInput 
          size="xs"
          value={item.precio_parcial} 
          onChange={(v) => {
            const next = [...habData];
            next[index].precio_parcial = Number(v);
            setHabData(next);
          }} 
          decimalScale={2} 
          hideControls 
          suffix=" $"
          styles={{ input: { backgroundColor: '#2a2a2a', color: 'white', border: '1px solid #333' } }}
        />
      </Table.Td>
      <Table.Td>
        <NumberInput 
          size="xs"
          value={item.precio_hospedaje} 
          onChange={(v) => {
            const next = [...habData];
            next[index].precio_hospedaje = Number(v);
            setHabData(next);
          }} 
          decimalScale={2} 
          hideControls
          suffix=" $"
          styles={{ input: { backgroundColor: '#2a2a2a', color: 'white', border: '1px solid #333' } }}
        />
      </Table.Td>
      <Table.Td>
        <NumberInput 
          size="xs"
          value={item.capacidad || 2} 
          onChange={(v) => {
            const next = [...habData];
            next[index].capacidad = Number(v);
            setHabData(next);
          }} 
          min={1}
          max={10}
          style={{ width: 50 }}
          styles={{ input: { backgroundColor: '#2a2a2a', color: 'white', border: '1px solid #333' } }}
        />
      </Table.Td>
      <Table.Td>
        <Badge variant="light" color={item.estado_actual === 'Libre' ? 'teal' : 'orange'}>
          {item.estado_actual}
        </Badge>
      </Table.Td>
      <Table.Td>
        <TextInput 
          size="xs"
          value={item.observaciones || ''} 
          onChange={(e) => {
            const next = [...habData];
            next[index].observaciones = e.target.value;
            setHabData(next);
          }} 
          style={{ width: 120 }}
          styles={{ input: { backgroundColor: '#2a2a2a', color: 'white', border: '1px solid #333' } }}
        />
      </Table.Td>
      <Table.Td>
        <TextInput 
          size="xs"
          value={item.descripcion || ''} 
          onChange={(e) => {
            const next = [...habData];
            next[index].descripcion = e.target.value;
            setHabData(next);
          }} 
          style={{ width: 150 }}
          styles={{ input: { backgroundColor: '#2a2a2a', color: 'white', border: '1px solid #333' } }}
        />
      </Table.Td>
      <Table.Td style={{ textAlign: 'center' }}>
        <Group gap={4} justify="center">
          {item.nfc_code ? <IconCheck size={18} color="#24cb7c" stroke={3} /> : <IconX size={18} color="#ff3333" stroke={1.5} />}
          <ActionIcon 
            variant="subtle" 
            size="sm" 
            color="blue" 
            onClick={() => scanNfc(index)}
            title="Asignar NFC"
          >
            <IconNfc size={16} />
          </ActionIcon>
        </Group>
      </Table.Td>
      <Table.Td style={{ textAlign: 'right' }}>
        <ActionIcon variant="light" color="teal" onClick={() => updateHabitacionConfig(item)}>
          <IconDeviceFloppy size={18} />
        </ActionIcon>
      </Table.Td>
    </Table.Tr>
  );

  const renderInspeccionRow = (item: any) => (
    <Table.Tr key={item.id}>
      <Table.Td style={{ textAlign: 'center' }}><Text fw={700} c="white">{item.habitacion_numero}</Text></Table.Td>
      <Table.Td><Text size="xs">{new Date(item.fecha).toLocaleString()}</Text></Table.Td>
      <Table.Td><Text size="xs" fw={500}>{item.inspector_nombre}</Text></Table.Td>
      <Table.Td style={{ textAlign: 'center' }}>{item.telefono === 'Bien' ? <IconCheck size={14} color="teal" /> : <IconX size={14} color="red" />}</Table.Td>
      <Table.Td style={{ textAlign: 'center' }}>{item.televisor === 'Bien' ? <IconCheck size={14} color="teal" /> : <IconX size={14} color="red" />}</Table.Td>
      <Table.Td style={{ textAlign: 'center' }}>{item.aire_acondicionado === 'Bien' ? <IconCheck size={14} color="teal" /> : <IconX size={14} color="red" />}</Table.Td>
      <Table.Td style={{ textAlign: 'center' }}>{item.luces === 'Bien' ? <IconCheck size={14} color="teal" /> : <IconX size={14} color="red" />}</Table.Td>
      <Table.Td style={{ textAlign: 'center' }}>{item.cama === 'Bien' ? <IconCheck size={14} color="teal" /> : <IconX size={14} color="red" />}</Table.Td>
      <Table.Td style={{ textAlign: 'center' }}>{item.ducha_agua === 'Bien' ? <IconCheck size={14} color="teal" /> : <IconX size={14} color="red" />}</Table.Td>
      <Table.Td><Text size="xs" truncate maw={100}>{item.observaciones}</Text></Table.Td>
    </Table.Tr>
  );

  const renderInspeccionCard = (item: any) => (
    <Card shadow="none" radius={0} bg="#1e1e1e" style={{ borderBottom: '1px solid #2a2a2a', marginBottom: 4 }} p="md">
      <Group justify="space-between" mb="xs">
        <Text fw={900} size="lg" c="teal">HAB {item.habitacion_numero}</Text>
        <Text size="xs" c="dimmed">{new Date(item.fecha).toLocaleString()}</Text>
      </Group>
      <Text size="sm" fw={700} c="white" mb="md">{item.inspector_nombre}</Text>
      
      <SimpleGrid cols={2} spacing="xs">
        <Group gap={4}><Text size="xs" c="dimmed">Tel:</Text>{item.telefono === 'Bien' ? <IconCheck size={14} color="teal" /> : <IconX size={14} color="red" />}</Group>
        <Group gap={4}><Text size="xs" c="dimmed">TV:</Text>{item.televisor === 'Bien' ? <IconCheck size={14} color="teal" /> : <IconX size={14} color="red" />}</Group>
        <Group gap={4}><Text size="xs" c="dimmed">AC:</Text>{item.aire_acondicionado === 'Bien' ? <IconCheck size={14} color="teal" /> : <IconX size={14} color="red" />}</Group>
        <Group gap={4}><Text size="xs" c="dimmed">Luz:</Text>{item.luces === 'Bien' ? <IconCheck size={14} color="teal" /> : <IconX size={14} color="red" />}</Group>
        <Group gap={4}><Text size="xs" c="dimmed">Cama:</Text>{item.cama === 'Bien' ? <IconCheck size={14} color="teal" /> : <IconX size={14} color="red" />}</Group>
        <Group gap={4}><Text size="xs" c="dimmed">Ducha:</Text>{item.ducha_agua === 'Bien' ? <IconCheck size={14} color="teal" /> : <IconX size={14} color="red" />}</Group>
      </SimpleGrid>

      {item.observaciones && (
        <Box mt="md" p="xs" bg="#141414" style={{ borderRadius: 4, borderLeft: '3px solid #24cb7c' }}>
          <Text size="xs" c="dimmed" fs="italic">{item.observaciones}</Text>
        </Box>
      )}
    </Card>
  );

  const renderHabCard = (item: any, index: number) => (
    <Card shadow="none" radius={0} bg="#1e1e1e" style={{ borderBottom: '1px solid #2a2a2a', marginBottom: 4 }} p="md">
      <Group justify="space-between" mb="md">
        <Group gap="xs">
          <Text fw={900} size="xl" c="white">#{item.numero}</Text>
          <Badge color={item.estado_actual === 'Libre' ? 'teal' : 'orange'}>{item.estado_actual}</Badge>
        </Group>
        <ActionIcon variant="light" color="teal" size="lg" onClick={() => updateHabitacionConfig(item)}>
          <IconDeviceFloppy size={20} />
        </ActionIcon>
      </Group>

      <Stack gap="xs">
        <Group grow>
          <TextInput label="Tipo" size="xs" value={item.tipo} onChange={(e) => {
            const next = [...habData];
            next[index].tipo = e.target.value;
            setHabData(next);
          }} styles={{ input: { backgroundColor: '#2a2a2a', color: 'white' } }} />
          <NumberInput label="Capacidad" size="xs" value={item.capacidad} onChange={(v) => {
            const next = [...habData];
            next[index].capacidad = v;
            setHabData(next);
          }} styles={{ input: { backgroundColor: '#2a2a2a', color: 'white' } }} />
        </Group>

        <Group grow>
          <NumberInput label="Parcial" size="xs" value={item.precio_parcial} onChange={(v) => {
            const next = [...habData];
            next[index].precio_parcial = v;
            setHabData(next);
          }} suffix=" $" styles={{ input: { backgroundColor: '#2a2a2a', color: 'white' } }} />
          <NumberInput label="Hospedaje" size="xs" value={item.precio_hospedaje} onChange={(v) => {
            const next = [...habData];
            next[index].precio_hospedaje = v;
            setHabData(next);
          }} suffix=" $" styles={{ input: { backgroundColor: '#2a2a2a', color: 'white' } }} />
        </Group>

        <TextInput label="Observaciones" size="xs" value={item.observaciones || ''} onChange={(e) => {
            const next = [...habData];
            next[index].observaciones = e.target.value;
            setHabData(next);
          }} styles={{ input: { backgroundColor: '#2a2a2a', color: 'white' } }} />

        <Group justify="space-between" mt="xs">
          <Text size="xs" c="dimmed">NFC: {item.nfc_code ? <Text span c="teal" fw={700}>Vinculado</Text> : <Text span c="red">Sin asignar</Text>}</Text>
          <Button variant="light" size="compact-xs" leftSection={<IconNfc size={14} />} onClick={() => scanNfc(index)}>Re-escanear</Button>
        </Group>
      </Stack>
    </Card>
  );

  const startInspeccion = async () => {
    if (!('NDEFReader' in window)) {
      notifications.show({ title: 'No compatible', message: 'NFC no disponible en este dispositivo.', color: 'red' });
      return;
    }

    try {
      // @ts-ignore
      const reader = new NDEFReader();
      await reader.scan();
      notifications.show({ message: 'Escaneando habitación...', color: 'blue', loading: true, id: 'nfc-inspeccion' });
      
      reader.onreading = (event: any) => {
        const serial = event.serialNumber;
        const room = habData.find(h => h.nfc_code === serial);
        notifications.hide('nfc-inspeccion');

        if (room) {
          setScannedRoom(room);
          setInspeccionStep(0);
          setIsInspeccionWizardOpen(true);
          setCurrentInspeccion({
            telefono: 'Bien', televisor: 'Bien', aire_acondicionado: 'Bien',
            luces: 'Bien', cama: 'Bien', ducha_agua: 'Bien', observaciones: ''
          });
        } else {
          notifications.show({ message: 'Habitación no registrada con este tag NFC', color: 'red' });
        }
      };
    } catch (e) {
      notifications.hide('nfc-inspeccion');
    }
  };

  const submitInspeccion = async () => {
    try {
      const activeUser = JSON.parse(localStorage.getItem('activeUser') || '{}');
      const res = await fetch('http://192.168.0.123:8000/api/configuracion/inspecciones', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          habitacion_id: scannedRoom.id,
          usuario_id: activeUser.id || 1,
          ...currentInspeccion
        })
      });
      if (res.ok) {
        notifications.show({ message: 'Inspección guardada correctamente', color: 'teal' });
        setIsInspeccionWizardOpen(false);
        const resI = await fetch('http://192.168.0.123:8000/api/configuracion/inspecciones');
        if (resI.ok) setInspecciones(await resI.json());
      }
    } catch (err) {
      notifications.show({ message: 'Error al guardar inspección', color: 'red' });
    }
  };

  const renderPayCard = (item: any) => (
    <Card shadow="none" radius={0} bg="#1e1e1e" style={{ borderBottom: '1px solid #2a2a2a', marginBottom: 4 }} p="md">
      <Group justify="space-between">
        <Group gap="xs">
          <Box style={{ width: 12, height: 12, borderRadius: '50%', backgroundColor: item.color }} />
          <Text fw={700} c="white">{item.nombre}</Text>
        </Group>
        <Badge color="gray">{item.moneda}</Badge>
      </Group>
      <Group justify="space-between" mt="md">
        <Text size="xs" c="dimmed">Tasa Aplicada:</Text>
        <Text fw={800} c="teal" size="lg">{item.moneda === 'USD' ? '1.00' : settings.bcv}</Text>
      </Group>
    </Card>
  );

  const renderPayRow = (item: any) => (
    <Table.Tr key={item.id}>
      <Table.Td><Text size="sm" fw={600} c="white">{item.nombre}</Text></Table.Td>
      <Table.Td style={{ textAlign: 'center' }}>
        <Badge color="gray">{item.moneda}</Badge>
      </Table.Td>
      <Table.Td style={{ textAlign: 'right' }}>
        <Text fw={700} c="teal">{item.moneda === 'USD' ? '1.00' : settings.bcv}</Text>
      </Table.Td>
      <Table.Td style={{ textAlign: 'center' }}>
        <Box style={{ width: 16, height: 16, borderRadius: '50%', backgroundColor: item.color, margin: '0 auto' }} />
      </Table.Td>
      <Table.Td style={{ textAlign: 'right' }}>
        <ActionIcon variant="subtle" color="gray"><IconSettings size={16} /></ActionIcon>
      </Table.Td>
    </Table.Tr>
  );

  const itemsAInspeccionar = [
    { key: 'telefono', label: 'Teléfono de la Habitación' },
    { key: 'televisor', label: 'Televisor / Control Remoto' },
    { key: 'aire_acondicionado', label: 'Aire Acondicionado' },
    { key: 'luces', label: 'Iluminación y Bombillos' },
    { key: 'cama', label: 'Camas y Tendidos' },
    { key: 'ducha_agua', label: 'Ducha y Grifería' },
  ];

  const renderWizardStep = () => {
    const item = itemsAInspeccionar[inspeccionStep];
    if (!item) return null;

    return (
      <Stack align="center" gap={40} py={60}>
        <Title order={1} ta="center" size={42} c="white">{item.label}</Title>
        <Group gap="xl">
          <Button 
            size="xl" 
            h={100} 
            w={200} 
            color="teal" 
            variant={currentInspeccion[item.key] === 'Bien' ? 'filled' : 'light'}
            onClick={() => setCurrentInspeccion({...currentInspeccion, [item.key]: 'Bien'})}
            leftSection={<IconCheck size={32} />}
          >
            BIEN
          </Button>
          <Button 
            size="xl" 
            h={100} 
            w={200} 
            color="red" 
            variant={currentInspeccion[item.key] === 'Mal' ? 'filled' : 'light'}
            onClick={() => setCurrentInspeccion({...currentInspeccion, [item.key]: 'Mal'})}
            leftSection={<IconX size={32} />}
          >
            MAL
          </Button>
        </Group>
        <Button 
          size="lg" 
          w={300} 
          variant="gradient" 
          gradient={{ from: 'teal', to: 'blue' }}
          onClick={() => setInspeccionStep(inspeccionStep + 1)}
          rightSection={<IconChevronRight size={20} />}
          mt={50}
        >
          SIGUIENTE
        </Button>
      </Stack>
    );
  };

  const configCategories = [
    { id: 'habitaciones' as const, title: 'Habitaciones', desc: 'Gestionar inventario, tipos y estados.', icon: IconBed, color: 'teal' },
    { id: 'pagos' as const, title: 'Métodos de Pago', desc: 'Monedas, tasas y colores de ID.', icon: IconCash, color: 'blue' },
    { id: 'general' as const, title: 'Ajustes Generales', desc: 'Información del hotel y parámetros.', icon: IconSettings, color: 'orange' },
    { id: 'personal' as const, title: 'Personal y Accesos', desc: 'Usuarios del sistema y permisos.', icon: IconUsers, color: 'grape' },
    { id: 'datos' as const, title: 'Sistema y Backup', desc: 'Base de datos y mantenimiento.', icon: IconDatabase, color: 'red' },
  ];

  if (!activeSection) {
    return (
      <Box>
        <Stack gap="xl">
          <Box>
            <Title order={2} c="white" style={{ fontFamily: 'Poppins, sans-serif' }}>Configuración</Title>
            <Text size="sm" c="dimmed">Selecciona el apartado que deseas configurar para continuar.</Text>
          </Box>

          <SimpleGrid cols={{ base: 1, sm: 2, lg: 3 }} spacing="lg">
            {configCategories.map((cat) => (
              <UnstyledButton 
                key={cat.id} 
                onClick={() => setActiveSection(cat.id)}
                style={{ height: '100%' }}
              >
                <Paper 
                  p="xl" 
                  radius="md" 
                  bg="#1e1e1e" 
                  style={{ 
                    border: '1px solid #2a2a2a', 
                    transition: 'all 0.2s ease',
                    height: '100%'
                  }}
                  styles={{
                    root: {
                      '&:hover': {
                        borderColor: `var(--mantine-color-${cat.color}-6)`,
                        transform: 'translateY(-4px)',
                        backgroundColor: 'rgba(255,255,255,0.02)'
                      }
                    }
                  }}
                  className="config-card"
                >
                  <Group justify="space-between" mb="lg">
                    <Box 
                      p="md" 
                      style={{ 
                        borderRadius: 12, 
                        backgroundColor: `rgba(var(--mantine-color-${cat.color}-6-rgb), 0.1)`,
                        color: `var(--mantine-color-${cat.color}-6)`
                      }}
                    >
                      <cat.icon size={32} />
                    </Box>
                    <IconChevronRight size={20} color="#555" />
                  </Group>
                  <Text fw={700} size="lg" c="white" mb={4}>{cat.title}</Text>
                  <Text size="sm" c="dimmed" style={{ lineHeight: 1.5 }}>{cat.desc}</Text>
                </Paper>
              </UnstyledButton>
            ))}
          </SimpleGrid>
        </Stack>

        <style jsx global>{`
          .config-card:hover {
            border-color: #24cb7c !important;
            transform: translateY(-5px);
            background-color: rgba(255,255,255,0.02) !important;
          }
        `}</style>
      </Box>
    );
  }

  const currentCategory = configCategories.find(c => c.id === activeSection);

  return (
    <Box>
      <Stack gap="xl">
        <Group align="flex-start" gap="lg" mb="xl">
          <ActionIcon 
            variant="light" 
            color="teal" 
            size="xl" 
            onClick={() => setActiveSection(null)}
            style={{ marginTop: 5 }}
          >
            <IconArrowLeft size={24} />
          </ActionIcon>
          <Box>
            <Title order={2} c="white" style={{ fontFamily: 'Poppins, sans-serif' }}>{currentCategory?.title}</Title>
            <Text size="sm" c="dimmed">{currentCategory?.desc}</Text>
          </Box>
        </Group>

        <Divider color="#2a2a2a" />

        {loading ? (
          <Center h={400}>
            <Stack align="center">
              <Loader color="teal" size="lg" type="bars" />
              <Text c="dimmed" size="sm">Cargando datos...</Text>
            </Stack>
          </Center>
        ) : (
          <>
            {activeSection === 'habitaciones' && (
              <Stack gap="md">
                <Tabs value={activeSubTab} onChange={setActiveSubTab} variant="pills" color="teal">
                  <Tabs.List mb="md">
                    <Tabs.Tab value="inspecciones">Inspecciones</Tabs.Tab>
                    <Tabs.Tab value="inventario">Inventario</Tabs.Tab>
                  </Tabs.List>

                  <Tabs.Panel value="inspecciones">
                    <Stack gap="md">
                      <Group justify="space-between">
                        <Text fw={700} c="white" size="lg">Historial de Revisiones</Text>
                        <Button 
                          leftSection={<IconNfc size={18} />} 
                          color="teal" 
                          variant="light"
                          onClick={() => startInspeccion()}
                        >
                          Nueva Inspección (Escanear NFC)
                        </Button>
                      </Group>
                      <DashboardTable 
                        columns={[
                          { key: 'h', label: 'Hab', width: 60, textAlign: 'center' },
                          { key: 'f', label: 'Fecha' },
                          { key: 'i', label: 'Inspector' },
                          { key: 'tel', label: 'Tel', textAlign: 'center' },
                          { key: 'tv', label: 'TV', textAlign: 'center' },
                          { key: 'ac', label: 'AC', textAlign: 'center' },
                          { key: 'lu', label: 'Luz', textAlign: 'center' },
                          { key: 'ca', label: 'Cama', textAlign: 'center' },
                          { key: 'du', label: 'Ducha', textAlign: 'center' },
                          { key: 'o', label: 'Obs' }
                        ]}
                        data={inspecciones}
                        renderRow={renderInspeccionRow}
                        renderCard={renderInspeccionCard}
                      />
                    </Stack>
                  </Tabs.Panel>

                  <Tabs.Panel value="inventario">
                    <Stack gap="md">
                      <Group justify="space-between">
                        <Text fw={700} c="white" size="lg">Inventario de Habitaciones</Text>
                      </Group>
                      <DashboardTable 
                        columns={[
                          { key: 'n', label: 'N°', width: 60, textAlign: 'center' },
                          { key: 't', label: 'Tipo' },
                          { key: 'p1', label: 'Parcial' },
                          { key: 'p2', label: 'Hospedaje' },
                          { key: 'c', label: 'Cap.', textAlign: 'center' },
                          { key: 'e', label: 'Estado', textAlign: 'center' },
                          { key: 'o', label: 'Observaciones' },
                          { key: 'd', label: 'Descripción' },
                          { key: 'nfc', label: 'NFC', textAlign: 'center' },
                          { key: 'a', label: '', width: 60, textAlign: 'right' }
                        ]}
                        data={habData}
                        renderRow={(item, index) => renderHabRow(item, index)}
                        renderCard={(item, index) => renderHabCard(item, index)}
                      />
                    </Stack>
                  </Tabs.Panel>
                </Tabs>
              </Stack>
            )}

            {activeSection === 'pagos' && (
              <Stack gap="md">
                <Group justify="space-between">
                  <Text fw={700} c="white" size="lg">Métodos de Pago y Monedas</Text>
                  <Button leftSection={<IconPlus size={16} />} color="teal">Agregar Método</Button>
                </Group>
                <DashboardTable 
                  columns={[
                    { key: 'n', label: 'Nombre' },
                    { key: 's', label: 'Moneda', textAlign: 'center' },
                    { key: 't', label: 'Tasa/Valor', textAlign: 'right' },
                    { key: 'c', label: 'Color ID', textAlign: 'center' },
                    { key: 'a', label: '', width: 80, textAlign: 'right' }
                  ]}
                  data={payData}
                  renderRow={renderPayRow}
                  renderCard={renderPayCard}
                />
              </Stack>
            )}

            {activeSection === 'general' && (
              <SimpleGrid cols={{ base: 1, md: 2 }} spacing="xl">
                <Paper p="xl" radius="md" bg="#1e1e1e" style={{ border: '1px solid #2a2a2a' }}>
                  <Stack gap="md">
                    <Text fw={700} c="white">Información del Hotel</Text>
                    <TextInput label="Nombre Comercial" defaultValue={settings.hotel_name} styles={{ input: { backgroundColor: '#2a2a2a', border: '1px solid #333', color: 'white' } }} />
                    <TextInput label="RIF / Identificación" defaultValue={settings.hotel_rif} styles={{ input: { backgroundColor: '#2a2a2a', border: '1px solid #333', color: 'white' } }} />
                    <Button fullWidth color="teal" leftSection={<IconDeviceFloppy size={16} />} mt="md">Guardar Cambios</Button>
                  </Stack>
                </Paper>
                <Paper p="xl" radius="md" bg="#1e1e1e" style={{ border: '1px solid #2a2a2a' }}>
                  <Stack gap="md">
                    <Text fw={700} c="white">Parámetros Críticos</Text>
                    <Group justify="space-between">
                      <Box>
                        <Text size="sm" fw={600} c="white">Modo Nocturno</Text>
                        <Text size="xs" c="dimmed">Activar tema oscuro automático</Text>
                      </Box>
                      <Switch color="teal" defaultChecked />
                    </Group>
                    <Divider color="#2a2a2a" />
                    <NumberInput label="Tasa BCV (Bs/$)" value={parseFloat(settings.bcv)} decimalScale={2} styles={{ input: { backgroundColor: '#2a2a2a', border: '1px solid #333', color: 'white' } }} />
                  </Stack>
                </Paper>
              </SimpleGrid>
            )}

            {(activeSection === 'personal' || activeSection === 'datos') && (
              <Paper p="xl" radius="md" bg="#1e1e1e" style={{ border: '1px solid #2a2a2a', height: 400, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                <Stack align="center" gap="xs">
                  <IconSettings size={40} color="#555" />
                  <Text c="dimmed">Módulo en proceso de implementación...</Text>
                </Stack>
              </Paper>
            )}
          </>
        )}
      </Stack>

      <Modal 
        opened={isInspeccionWizardOpen} 
        onClose={() => setIsInspeccionWizardOpen(false)} 
        fullScreen 
        bg="#141414"
        styles={{ content: { backgroundColor: '#141414' }, header: { backgroundColor: '#141414' } }}
      >
        <Stack h="100%">
          <Group justify="space-between" p="md">
            <Text fw={900} size="xl" c="teal">HABITACIÓN {scannedRoom?.numero}</Text>
            <Badge size="lg" variant="dot" color="blue">INSPECCIÓN EN CURSO</Badge>
          </Group>

          <Center h="100%">
            {inspeccionStep < itemsAInspeccionar.length ? renderWizardStep() : (
              <Stack w={600} gap="xl">
                <Title order={1} ta="center" c="white">Finalizar Inspección</Title>
                <TextInput 
                  label="Observaciones adicionales" 
                  placeholder="Escriba aquí si algo necesita reparación..."
                  size="lg"
                  value={currentInspeccion.observaciones}
                  onChange={(e) => setCurrentInspeccion({...currentInspeccion, observaciones: e.target.value})}
                  styles={{ input: { backgroundColor: '#2a2a2a', border: '1px solid #333', color: 'white' } }}
                />
                
                <Box>
                  <Text size="sm" fw={500} c="dimmed" mb="xs">Evidencia Fotográfica (Opcional)</Text>
                  <FileButton onChange={() => {}} accept="image/png,image/jpeg">
                    {(props) => <Button {...props} variant="light" color="blue" fullWidth>Adjuntar Foto</Button>}
                  </FileButton>
                </Box>

                <Button 
                  size="xl" 
                  fullWidth 
                  color="teal" 
                  onClick={submitInspeccion}
                  leftSection={<IconDeviceFloppy size={24} />}
                >
                  GUARDAR INSPECCIÓN
                </Button>
              </Stack>
            )}
          </Center>
        </Stack>
      </Modal>
    </Box>
  );
}
