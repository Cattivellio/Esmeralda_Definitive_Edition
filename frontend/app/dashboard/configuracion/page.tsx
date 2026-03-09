'use client';

import { 
  Badge, Divider, UnstyledButton, Table, Loader, Center,
  Tabs, Stepper, Modal, FileButton, Card, Select,
  Box, Title, Text, Stack, Paper, Group, ActionIcon, 
  Switch, TextInput, NumberInput, Button, SimpleGrid, Tooltip, Textarea, Avatar
} from '@mantine/core';
import { DatePickerInput } from '@mantine/dates';
import dayjs from 'dayjs';
import { 
  IconBed, IconCash, IconSettings, IconUsers, IconTrash, 
  IconPlus, IconArrowLeft, IconDeviceFloppy, IconChevronRight, IconDatabase,
  IconNfc, IconCheck, IconX, IconSearch, IconCalendar, IconWallet, IconChartBar, IconDoorEnter, IconLockAccess, IconBell, IconCake, IconHistory, IconPhoto,
  IconDownload, IconListDetails, IconPackage, IconArrowNarrowUp, IconArrowNarrowDown, IconAlertTriangle
} from '@tabler/icons-react';
import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { DashboardTable } from '../components/DashboardTable';
import { api, BASE_URL } from '../../lib/api';
import { notifications } from '@mantine/notifications';

type ConfigSection = 'habitaciones' | 'tesoreria' | 'general' | 'personal' | 'datos' | 'inventario' | null;

export default function ConfiguracionSection() {
  const router = useRouter();
  const [activeSection, setActiveSection] = useState<ConfigSection>(null);
  const [loading, setLoading] = useState(false);

  // --- STATE ---
  const [habData, setHabData] = useState<any[]>([]);
  const [inspecciones, setInspecciones] = useState<any[]>([]);
  const [activeSubTab, setActiveSubTab] = useState<string | null>('inspecciones');
  const [isInspeccionWizardOpen, setIsInspeccionWizardOpen] = useState(false);
  const [inspeccionStep, setInspeccionStep] = useState(0);
  const [currentInspeccion, setCurrentInspeccion] = useState<any>({
    telefono: 'Bien', televisor: 'Bien', aire_acondicionado: 'Bien',
    luces: 'Bien', cama: 'Bien', ducha_agua: 'Bien', observaciones: ''
  });
  const [scannedRoom, setScannedRoom] = useState<any>(null);
  const [usuariosData, setUsuariosData] = useState<any[]>([]);
  const [logsData, setLogsData] = useState<any[]>([]);
  const [isUsuarioModalOpen, setIsUsuarioModalOpen] = useState(false);
  const [editingUsuario, setEditingUsuario] = useState<any>(null);
  const [tempPhotoUrl, setTempPhotoUrl] = useState<string | null>(null);
  const [tempNfcCode, setTempNfcCode] = useState<string | null>(null);
  
  // --- INVENTARIO STATE ---
  const [inventoryData, setInventoryData] = useState<any[]>([]);
  const [isInventoryModalOpen, setIsInventoryModalOpen] = useState(false);
  const [editingInventoryItem, setEditingInventoryItem] = useState<any>(null);
  const [isStockAdjustmentModalOpen, setIsStockAdjustmentModalOpen] = useState(false);
  const [adjustingItem, setAdjustingItem] = useState<any>(null);
  const [adjustmentType, setAdjustmentType] = useState<'ENTRADA' | 'SALIDA'>('ENTRADA');
  const [movimientosInventario, setMovimientosInventario] = useState<any[]>([]);

  const [settings, setSettings] = useState<any>({
    hotel_nombre: 'Posada Esmeralda',
    hotel_rif: 'J-12345678-9',
    hotel_ciudad: '',
    hotel_parroquia: '',
    hotel_municipio: '',
    hotel_estado: '',
    hotel_correo: '',
    hotel_telefono: '',
    hotel_instagram: '',
    hotel_whatsapp: '',
    hotel_direccion_fiscal: '',
    duracion_parcial_horas: '6',
    estadia_default: 'parcial',
    horario_checkin: '15:00',
    horario_checkout: '13:00',
    tv_display_url: '',
    tv_display_active: 'false',
    gate_control_disabled: 'false',
    cam_entrada_url: '',
    cam_salida_url: '',
    reporte_policial_active: 'false',
    reporte_policial_cantidad_exp: '0',
    reporte_policial_huespedes_resta: '0',
    reporte_policial_total_huespedes: '0',
    reserva_minimo_active: 'false',
    reserva_minimo_monto: '0',
    permitir_entrada_deuda_active: 'false'
  });

  useEffect(() => {
    if (!activeSection) return;
    
    const fetchData = async () => {
      setLoading(true);
      try {
        if (activeSection === 'habitaciones') {
          const data = await api.getHabitaciones();
          setHabData(data);
          const dataInspecciones = await api.getInspecciones();
          setInspecciones(dataInspecciones);
        } else if (activeSection === 'general') {
          const all = await api.getAllSettings();
          const sObj: any = {};
          all.forEach((s: any) => sObj[s.clave] = s.valor);
          setSettings((prev: any) => ({ ...prev, ...sObj }));
        } else if (activeSection === 'personal') {
          const users = await api.getUsuarios();
          setUsuariosData(users);
        } else if (activeSection === 'datos') {
          const logs = await api.getLogs();
          setLogsData(logs);
          const movs = await api.getMovimientosInventario();
          setMovimientosInventario(movs);
        } else if (activeSection === 'inventario') {
          const inv = await api.getInventario();
          setInventoryData(inv);
        }
      } catch (error) {
        console.error('Error fetching config data:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [activeSection]);

  const saveSetting = async (clave: string, valor: string) => {
    try {
      await api.updateConfig(clave, valor);
      notifications.show({ message: `Ajuste '${clave}' guardado`, color: 'teal', autoClose: 1000 });
    } catch (e) {
      console.error(e);
      notifications.show({ message: 'Error al guardar ajuste', color: 'red' });
    }
  };

  const fetchUsuarios = async () => {
    try {
      const users = await api.getUsuarios();
      setUsuariosData(users);
    } catch (e) {
      console.error(e);
    }
  };

  const handleSaveUsuario = async (userData: any) => {
    try {
      if (editingUsuario?.id) {
        await api.updateUsuario(editingUsuario.id, userData);
        notifications.show({ message: 'Usuario actualizado', color: 'teal' });
      } else {
        await api.createUsuario({ ...userData, password: 'password123' }); // Default password
        notifications.show({ message: 'Usuario creado', color: 'teal' });
      }
      setIsUsuarioModalOpen(false);
      fetchUsuarios();
    } catch (e) {
      console.error(e);
      notifications.show({ message: 'Error al guardar usuario', color: 'red' });
    }
  };

  const handleDeleteUsuario = async (id: number) => {
    if (!confirm('¿Está seguro de eliminar este usuario?')) return;
    try {
      await api.deleteUsuario(id);
      notifications.show({ message: 'Usuario eliminado', color: 'teal' });
      fetchUsuarios();
    } catch (e) {
      console.error(e);
      notifications.show({ message: 'Error al eliminar', color: 'red' });
    }
  };

  const seedUsuarios = async () => {
    const baseUsers = [
      { username: 'alvaro', nombre: 'Alvaro Cattivelli', rol: 'socio', horario: 'Lunes a Viernes: 08:00 - 18:00', fecha_ingreso: '2020-01-01', fecha_nacimiento: '1985-05-15' },
      { username: 'anamaria', nombre: 'Ana Maria', rol: 'socio', horario: 'Lunes a Viernes: 08:00 - 18:00', fecha_ingreso: '2020-01-01', fecha_nacimiento: '1988-08-20' },
      { username: 'asdrubal', nombre: 'Asdrubal', rol: 'mantenimiento', horario: 'Lun, Mié, Vie: 07:00 - 15:00', fecha_ingreso: '2021-03-10', fecha_nacimiento: '1975-11-30' },
      { username: 'benedicta', nombre: 'Benedicta', rol: 'camarera', horario: 'Lun a Sáb: 07:00 - 15:00', fecha_ingreso: '2022-06-15', fecha_nacimiento: '1990-02-12' },
      { username: 'boom', nombre: 'Boom', rol: 'empresa', horario: 'Comercial', fecha_ingreso: '2023-01-01', fecha_nacimiento: null },
      { username: 'carlos', nombre: 'Carlos Cattivelli', rol: 'socio', horario: 'Lunes a Viernes: 08:00 - 18:00', fecha_ingreso: '2020-01-01', fecha_nacimiento: '1982-03-10' },
      { username: 'cristina', nombre: 'Cristina', rol: 'socio', horario: 'Lunes a Viernes: 08:00 - 18:00', fecha_ingreso: '2020-01-01', fecha_nacimiento: '1986-12-05' },
      { username: 'dalia', nombre: 'Dalia', rol: 'camarera', horario: 'Lun a Vie: 15:00 - 23:00', fecha_ingreso: '2022-02-20', fecha_nacimiento: '1995-07-22' },
      { username: 'daniell', nombre: 'Daniell Cattivelli', rol: 'socio', horario: 'Lunes a Viernes: 08:00 - 18:00', fecha_ingreso: '2020-01-01', fecha_nacimiento: '1992-04-18' },
      { username: 'delivery', nombre: 'Delivery', rol: 'empresa', horario: 'Comercial' },
      { username: 'elia', nombre: 'Elia', rol: 'camarera', horario: 'Lun a Vie: 07:00 - 15:00', fecha_ingreso: '2021-09-01', fecha_nacimiento: '1988-01-15' },
      { username: 'ferrexpress', nombre: 'FERREXPRESS', rol: 'empresa', horario: 'Comercial' },
      { username: 'francis', nombre: 'Francis', rol: 'camarera', horario: 'Mar a Sáb: 15:00 - 23:00', fecha_ingreso: '2022-10-05', fecha_nacimiento: '1993-09-28' },
      { username: 'gaslara', nombre: 'Gas Lara', rol: 'empresa', horario: 'Comercial' },
      { username: 'gasoil', nombre: 'Gasoil', rol: 'empresa', horario: 'Comercial' },
      { username: 'isabel', nombre: 'Isabel Cattivelli', rol: 'socio', horario: 'Lunes a Viernes: 08:00 - 18:00', fecha_ingreso: '2020-01-01', fecha_nacimiento: '1990-11-12' },
      { username: 'jesus', nombre: 'Jesus Cattivelli', rol: 'socio', horario: 'Lunes a Viernes: 08:00 - 18:00', fecha_ingreso: '2020-01-01', fecha_nacimiento: '1987-06-30' },
      { username: 'libia', nombre: 'Libia', rol: 'recepcionista', horario: 'Turnos rotativos 12H (07-19)', fecha_ingreso: '2021-05-15', fecha_nacimiento: '1984-02-25' },
      { username: 'loendry', nombre: 'Loendry', rol: 'recepcionista', horario: 'Turnos rotativos 12H (19-07)', fecha_ingreso: '2021-11-20', fecha_nacimiento: '1996-10-08' },
      { username: 'marianella', nombre: 'Marianella', rol: 'socio', horario: 'Lunes a Viernes: 08:00 - 18:00', fecha_ingreso: '2020-01-01', fecha_nacimiento: '1989-09-12' },
      { username: 'marina', nombre: 'Marina', rol: 'camarera', horario: 'Lun a Vie: 07:00 - 15:00', fecha_ingreso: '2022-01-10', fecha_nacimiento: '1991-03-05' },
      { username: 'mayela', nombre: 'Mayela', rol: 'administrador', horario: 'Lunes a Viernes: 08:00 - 16:00', fecha_ingreso: '2020-01-01', fecha_nacimiento: '1985-11-15' },
      { username: 'norvelys', nombre: 'Norvelys', rol: 'recepcionista', horario: 'Turnos rotativos 12H (07-19)', fecha_ingreso: '2022-04-01', fecha_nacimiento: '1992-06-20' },
      { username: 'ogles', nombre: 'Ogles', rol: 'vigilante', horario: 'Rotativos 24/48', fecha_ingreso: '2021-07-15', fecha_nacimiento: '1980-01-10' },
      { username: 'otto', nombre: 'Otto', rol: 'administrador', horario: 'Lunes a Viernes: 08:00 - 16:00', fecha_ingreso: '2020-01-01', fecha_nacimiento: '1983-05-22' },
      { username: 'radames', nombre: 'Radames', rol: 'mantenimiento', horario: 'Mar, Jue, Sáb: 07:00 - 15:00', fecha_ingreso: '2021-12-01', fecha_nacimiento: '1978-09-18' },
      { username: 'rosalinda', nombre: 'Rosalinda Cattivelli', rol: 'socio', horario: 'Lunes a Viernes: 08:00 - 18:00', fecha_ingreso: '2020-01-01', fecha_nacimiento: '1980-02-14' },
      { username: 'walter', nombre: 'Walter Cattivelli', rol: 'socio', horario: 'Todo el día', fecha_ingreso: '2020-01-01', fecha_nacimiento: '1991-08-15' },
      { username: 'wendy', nombre: 'Wendy Cattivelli', rol: 'socio', horario: 'Todo el día', fecha_ingreso: '2020-01-01', fecha_nacimiento: '1993-11-30' },
      { username: 'yolainny', nombre: 'Yolainny', rol: 'recepcionista', horario: 'Turnos rotativos 12H (19-07)', fecha_ingreso: '2023-02-10', fecha_nacimiento: '1994-04-12' },
    ];

    setLoading(true);
    try {
      for (const u of baseUsers) {
        await api.createUsuario({ ...u, password: 'password123' });
      }
      notifications.show({ message: 'Usuarios base cargados con éxito', color: 'teal' });
      fetchUsuarios();
    } catch (e) {
      console.error(e);
      notifications.show({ message: 'Error cargando usuarios base', color: 'red' });
    } finally {
      setLoading(false);
    }
  };

  // --- RENDERS ---
  const updateHabitacionConfig = async (h: any) => {
    try {
      await api.updateHabitacionPrecios(h.id, {
        tipo: h.tipo,
        precio_parcial: h.precio_parcial, 
        precio_hospedaje: h.precio_hospedaje, 
        capacidad: h.capacidad || 2, 
        observaciones: h.observaciones || '',
        descripcion: h.descripcion || '',
        nfc_code: h.nfc_code || null
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

  const scanNfcForUser = async () => {
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
      notifications.show({ message: 'Acerque el tag NFC al dispositivo...', color: 'blue', loading: true, id: 'nfc-user-scan' });
      
      reader.onreading = (event: any) => {
        const serialNumber = event.serialNumber;
        setTempNfcCode(serialNumber);
        notifications.hide('nfc-user-scan');
        notifications.show({ message: `Código NFC detectado: ${serialNumber}`, color: 'green' });
      };
    } catch (error) {
      notifications.hide('nfc-user-scan');
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
          onChange={(e: React.ChangeEvent<HTMLInputElement>) => {
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
          onChange={(v: string | number) => {
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
          onChange={(v: string | number) => {
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
          onChange={(v: string | number) => {
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
          onChange={(e: React.ChangeEvent<HTMLInputElement>) => {
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
          onChange={(e: React.ChangeEvent<HTMLInputElement>) => {
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

  const renderUsuarioRow = (item: any) => (
    <Table.Tr key={item.id}>
      <Table.Td>
        <Group gap="sm">
          <Avatar 
            src={item.foto_url ? `${BASE_URL.replace('/api','')}${item.foto_url}` : null} 
            radius="xl" 
            size="md"
            styles={{ placeholder: { backgroundColor: '#2a2a2a', color: 'white' } }}
          >
            {item.nombre?.split(' ').map((n:any) => n[0]).join('')}
          </Avatar>
          <Box>
            <Text size="sm" fw={600} c="white">{item.nombre || 'Sin nombre'}</Text>
            <Text size="xs" c="dimmed">@{item.username}</Text>
          </Box>
        </Group>
      </Table.Td>
      <Table.Td>
        <Badge 
          color={
            item.rol === 'administrador' ? 'red' : 
            item.rol === 'socio' ? 'grape' : 
            item.rol === 'recepcionista' ? 'blue' : 
            item.rol === 'camarera' ? 'teal' : 
            'gray'
          }
          variant="light"
        >
          {item.rol?.toUpperCase()}
        </Badge>
      </Table.Td>
      <Table.Td>
        <Group gap={6}>
          <Box style={{ width: 8, height: 8, borderRadius: '50%', backgroundColor: item.is_present ? '#24cb7c' : '#555' }} />
          <Text size="xs" fw={500} c={item.is_present ? 'teal' : 'dimmed'}>
            {item.is_present ? 'Presente' : 'Ausente'}
          </Text>
        </Group>
      </Table.Td>
      <Table.Td>
        <Text size="xs" c="dimmed" fw={500}>{item.horario || 'No definido'}</Text>
      </Table.Td>
      <Table.Td>
        <Group gap={4}>
          <IconCake size={14} color="#f06292" />
          <Text size="xs" c="white" fw={500}>
            {item.fecha_nacimiento ? dayjs(item.fecha_nacimiento).format('DD MMM') : '-'}
          </Text>
        </Group>
      </Table.Td>
      <Table.Td>
        <Group gap={4}>
          <IconHistory size={14} color="#4db6ac" />
          <Text size="xs" c="white" fw={500}>
            {item.fecha_ingreso ? dayjs(item.fecha_ingreso).format('DD/MM/YY') : '-'}
          </Text>
        </Group>
      </Table.Td>
       <Table.Td>
        <Group gap={4}>
          {item.nfc_code ? (
            <Tooltip label={`NFC: ${item.nfc_code}`}>
              <IconNfc size={14} color="#24cb7c" />
            </Tooltip>
          ) : (
             <IconNfc size={14} color="#555" />
          )}
          <Text size="xs" c={item.nfc_code ? "teal" : "dimmed"}>
             {item.nfc_code ? "Vinculado" : "Sin Tag"}
          </Text>
        </Group>
      </Table.Td>
      <Table.Td align="right">
        <Group gap="xs" justify="flex-end">
          <ActionIcon 
            variant="light" 
            color="blue" 
            onClick={() => {
              setEditingUsuario(item);
              setTempPhotoUrl(item.foto_url);
              setTempNfcCode(item.nfc_code);
              setIsUsuarioModalOpen(true);
            }}
          >
            <IconSettings size={16} />
          </ActionIcon>
          <ActionIcon 
            variant="light" 
            color="red" 
            onClick={() => handleDeleteUsuario(item.id)}
          >
            <IconTrash size={16} />
          </ActionIcon>
        </Group>
      </Table.Td>
    </Table.Tr>
  );

  const renderUsuarioCard = (item: any) => (
    <Card key={item.id} shadow="none" bg="#1e1e1e" style={{ borderBottom: '1px solid #2a2a2a' }} p="md">
      <Group justify="space-between" mb="xs">
        <Group gap="sm">
          <Avatar 
            src={item.foto_url ? `${BASE_URL.replace('/api','')}${item.foto_url}` : null} 
            radius="xl" 
            size="md"
          >
            {item.nombre?.split(' ').map((n:any) => n[0]).join('')}
          </Avatar>
          <Box>
            <Text size="sm" fw={600} c="white">{item.nombre || 'Sin nombre'}</Text>
            <Text size="xs" c="dimmed">@{item.username}</Text>
            <Group gap="xs" mt={4}>
              {item.fecha_nacimiento && <Badge size="xs" leftSection={<IconCake size={10} />} color="pink" variant="light">{dayjs(item.fecha_nacimiento).format('DD/MM')}</Badge>}
              {item.fecha_ingreso && <Badge size="xs" leftSection={<IconHistory size={10} />} color="teal" variant="light">{dayjs().diff(dayjs(item.fecha_ingreso), 'year')} años</Badge>}
            </Group>
          </Box>
        </Group>
        <Group gap="xs">
          <ActionIcon 
            variant="light" 
            color="blue" 
            onClick={() => {
              setEditingUsuario(item);
              setTempPhotoUrl(item.foto_url);
              setTempNfcCode(item.nfc_code);
              setIsUsuarioModalOpen(true);
            }}
          >
            <IconSettings size={16} />
          </ActionIcon>
          <ActionIcon 
            variant="light" 
            color="red" 
            onClick={() => handleDeleteUsuario(item.id)}
          >
            <IconTrash size={16} />
          </ActionIcon>
        </Group>
      </Group>
      <Group justify="space-between" align="flex-start">
        <Badge 
          color={
            item.rol === 'administrador' ? 'red' : 
            item.rol === 'socio' ? 'grape' : 
            item.rol === 'recepcionista' ? 'blue' : 
            item.rol === 'camarera' ? 'teal' : 
            'gray'
          }
          variant="light"
        >
          {item.rol?.toUpperCase()}
        </Badge>
        <Stack gap={2} align="flex-end">
          <Group gap={6}>
            <Box style={{ width: 8, height: 8, borderRadius: '50%', backgroundColor: item.is_present ? '#24cb7c' : '#555' }} />
            <Text size="xs" fw={700} c={item.is_present ? 'teal' : 'white'}>
              {item.is_present ? 'PRESENTE' : 'AUSENTE'}
            </Text>
          </Group>
          <Tooltip label={item.horario || 'Sin horario detallado'}>
            <Text size="xs" c="dimmed" style={{ maxWidth: 150, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
              {item.horario || 'Sin horario'}
            </Text>
          </Tooltip>
        </Stack>
      </Group>
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
      const res = await api.createInspeccion({
        habitacion_id: scannedRoom.id,
        usuario_id: activeUser.id || 1,
        ...currentInspeccion
      });

      notifications.show({ message: 'Inspección guardada correctamente', color: 'teal' });
      setIsInspeccionWizardOpen(false);
      const dataInspecciones = await api.getInspecciones();
      setInspecciones(dataInspecciones);
    } catch (err) {
      notifications.show({ message: 'Error al guardar inspección', color: 'red' });
    }
  };

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
    { id: 'tesoreria' as const, title: 'Tesorería', desc: 'Cuentas, movimientos y métodos de pago.', icon: IconWallet, color: 'blue' },
    { id: 'general' as const, title: 'Ajustes Generales', desc: 'Información del hotel y parámetros.', icon: IconSettings, color: 'orange' },
    { id: 'personal' as const, title: 'Personal y Accesos', desc: 'Usuarios del sistema y permisos.', icon: IconUsers, color: 'grape' },
    { id: 'inventario' as const, title: 'Control de Inventario', desc: 'Suministros, amenities y mantenimiento.', icon: IconPackage, color: 'teal' },
    { id: 'datos' as const, title: 'Sistema y Backup', desc: 'Base de datos y auditoría.', icon: IconDatabase, color: 'red' },
  ];

  if (!activeSection) {
    return (
      <Box>
        <Stack gap="xl">
          <Group align="flex-start" gap="lg" mb="xl">
            <ActionIcon 
              variant="light" 
              color="teal" 
              size="xl" 
              onClick={() => router.push('/dashboard/resumen')}
              style={{ marginTop: 5 }}
            >
              <IconArrowLeft size={24} />
            </ActionIcon>
            <Box>
              <Title order={2} fw={600} c="white" style={{ fontFamily: 'Poppins, sans-serif' }}>Configuración</Title>
              <Text size="sm" c="dimmed">Selecciona el apartado que deseas configurar para continuar.</Text>
            </Box>
          </Group>

          <SimpleGrid cols={{ base: 1, sm: 2, lg: 3 }} spacing="lg">
            {configCategories.map((cat) => (
              <UnstyledButton 
                key={cat.id} 
                onClick={() => {
                  if (cat.id === 'tesoreria') {
                    router.push('/dashboard/tesoreria');
                  } else {
                    setActiveSection(cat.id);
                  }
                }}
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
                  <Text fw={600} size="lg" c="white" mb={4}>{cat.title}</Text>
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
            <Title order={2} fw={600} c="white" style={{ fontFamily: 'Poppins, sans-serif' }}>{currentCategory?.title}</Title>
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
                        <Text fw={600} c="white" size="lg">Historial de Revisiones</Text>
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
                        <Text fw={600} c="white" size="lg">Inventario de Habitaciones</Text>
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

            {activeSection === 'general' && (
              <Stack gap="xl">
                {/* 1. INFORMACIÓN DEL HOTEL */}
                <Paper p="xl" radius="md" bg="#1e1e1e" style={{ border: '1px solid #2a2a2a' }}>
                  <Stack gap="lg">
                    <Group justify="space-between">
                      <Box>
                        <Text fw={600} size="lg" c="white" tt="uppercase">Perfil del Hotel</Text>
                        <Text size="xs" c="dimmed">Datos legales y de contacto para facturación y reportes.</Text>
                      </Box>
                      <IconSettings size={30} color="#333" />
                    </Group>
                    
                    <SimpleGrid cols={{ base: 1, sm: 2, md: 3 }} spacing="lg">
                      <TextInput 
                        label="Nombre del Hotel" 
                        value={settings.hotel_nombre} 
                        onChange={(e: React.ChangeEvent<HTMLInputElement>) => setSettings((prev: any) => ({...prev, hotel_nombre: e.target.value}))}
                        onBlur={() => saveSetting('hotel_nombre', settings.hotel_nombre)}
                        styles={{ input: { backgroundColor: 'white', border: '1px solid #333', color: 'black' } }} 
                      />
                      <TextInput 
                        label="RIF" 
                        value={settings.hotel_rif} 
                        onChange={(e: React.ChangeEvent<HTMLInputElement>) => setSettings((prev: any) => ({...prev, hotel_rif: e.target.value}))}
                        onBlur={() => saveSetting('hotel_rif', settings.hotel_rif)}
                        styles={{ input: { backgroundColor: 'white', border: '1px solid #333', color: 'black' } }} 
                      />
                      <TextInput 
                        label="Correo Electrónico" 
                        value={settings.hotel_correo} 
                        onChange={(e: React.ChangeEvent<HTMLInputElement>) => setSettings((prev: any) => ({...prev, hotel_correo: e.target.value}))}
                        onBlur={() => saveSetting('hotel_correo', settings.hotel_correo)}
                        styles={{ input: { backgroundColor: 'white', border: '1px solid #333', color: 'black' } }} 
                      />
                      <TextInput 
                        label="Teléfono de Contacto" 
                        value={settings.hotel_telefono} 
                        onChange={(e: React.ChangeEvent<HTMLInputElement>) => setSettings((prev: any) => ({...prev, hotel_telefono: e.target.value}))}
                        onBlur={() => saveSetting('hotel_telefono', settings.hotel_telefono)}
                        styles={{ input: { backgroundColor: 'white', border: '1px solid #333', color: 'black' } }} 
                      />
                      <TextInput 
                        label="Instagram" 
                        value={settings.hotel_instagram} 
                        onChange={(e: React.ChangeEvent<HTMLInputElement>) => setSettings((prev: any) => ({...prev, hotel_instagram: e.target.value}))}
                        onBlur={() => saveSetting('hotel_instagram', settings.hotel_instagram)}
                        styles={{ input: { backgroundColor: 'white', border: '1px solid #333', color: 'black' } }} 
                      />
                      <TextInput 
                        label="WhatsApp Business" 
                        value={settings.hotel_whatsapp} 
                        onChange={(e: React.ChangeEvent<HTMLInputElement>) => setSettings((prev: any) => ({...prev, hotel_whatsapp: e.target.value}))}
                        onBlur={() => saveSetting('hotel_whatsapp', settings.hotel_whatsapp)}
                        styles={{ input: { backgroundColor: 'white', border: '1px solid #333', color: 'black' } }} 
                      />
                    </SimpleGrid>

                    <SimpleGrid cols={{ base: 1, sm: 4 }} spacing="lg">
                      <TextInput 
                        label="Estado" 
                        value={settings.hotel_estado} 
                        onChange={(e: React.ChangeEvent<HTMLInputElement>) => setSettings((prev: any) => ({...prev, hotel_estado: e.target.value}))}
                        onBlur={() => saveSetting('hotel_estado', settings.hotel_estado)}
                        styles={{ input: { backgroundColor: 'white', color: 'black' } }} 
                      />
                      <TextInput 
                        label="Ciudad" 
                        value={settings.hotel_ciudad} 
                        onChange={(e: React.ChangeEvent<HTMLInputElement>) => setSettings((prev: any) => ({...prev, hotel_ciudad: e.target.value}))}
                        onBlur={() => saveSetting('hotel_ciudad', settings.hotel_ciudad)}
                        styles={{ input: { backgroundColor: 'white', color: 'black' } }} 
                      />
                      <TextInput 
                        label="Municipio" 
                        value={settings.hotel_municipio} 
                        onChange={(e: React.ChangeEvent<HTMLInputElement>) => setSettings((prev: any) => ({...prev, hotel_municipio: e.target.value}))}
                        onBlur={() => saveSetting('hotel_municipio', settings.hotel_municipio)}
                        styles={{ input: { backgroundColor: 'white', color: 'black' } }} 
                      />
                      <TextInput 
                        label="Parroquia" 
                        value={settings.hotel_parroquia} 
                        onChange={(e: React.ChangeEvent<HTMLInputElement>) => setSettings((prev: any) => ({...prev, hotel_parroquia: e.target.value}))}
                        onBlur={() => saveSetting('hotel_parroquia', settings.hotel_parroquia)}
                        styles={{ input: { backgroundColor: 'white', color: 'black' } }} 
                      />
                    </SimpleGrid>

                    <TextInput 
                      label="Dirección Fiscal" 
                      value={settings.hotel_direccion_fiscal} 
                      onChange={(e: React.ChangeEvent<HTMLInputElement>) => setSettings((prev: any) => ({...prev, hotel_direccion_fiscal: e.target.value}))}
                      onBlur={() => saveSetting('hotel_direccion_fiscal', settings.hotel_direccion_fiscal)}
                      styles={{ input: { backgroundColor: 'white', color: 'black' } }} 
                    />
                  </Stack>
                </Paper>

                {/* 2. OPERACIONES Y ESTADÍA */}
                <SimpleGrid cols={{ base: 1, md: 2 }} spacing="xl">
                  <Paper p="xl" radius="md" bg="#1e1e1e" style={{ border: '1px solid #2a2a2a' }}>
                    <Stack gap="lg">
                      <Text fw={600} size="md" c="white" tt="uppercase">Operaciones y Estadías</Text>
                      
                      <SimpleGrid cols={2} spacing="md">
                        <NumberInput 
                          label="Duración Parcial (Horas)" 
                          value={parseInt(settings.duracion_parcial_horas)} 
                          onChange={(val: string | number) => {
                            const strVal = val.toString();
                            setSettings((prev: any) => ({...prev, duracion_parcial_horas: strVal}));
                            saveSetting('duracion_parcial_horas', strVal);
                          }}
                          styles={{ input: { backgroundColor: 'white', color: 'black' } }} 
                        />

                        <Select
                          label="Tipo de Estadía por Default"
                          data={[
                            { value: 'parcial', label: 'Parcial (6H)' },
                            { value: 'hospedaje', label: 'Hospedaje (Hasta mediodía)' }
                          ]}
                          value={settings.estadia_default}
                          onChange={(val: string | null) => {
                            if (val) {
                              setSettings((prev: any) => ({...prev, estadia_default: val}));
                              saveSetting('estadia_default', val);
                            }
                          }}
                          styles={{ input: { backgroundColor: 'white', color: 'black' } }} 
                        />
                      </SimpleGrid>

                      <SimpleGrid cols={2} spacing="md">
                        <TextInput 
                          label="Horario Check-In (Hospedajes)" 
                          placeholder="p.ej. 15:00"
                          value={settings.horario_checkin}
                          onChange={(e: React.ChangeEvent<HTMLInputElement>) => setSettings((prev: any) => ({...prev, horario_checkin: e.target.value}))}
                          onBlur={() => saveSetting('horario_checkin', settings.horario_checkin)}
                          styles={{ input: { backgroundColor: 'white', color: 'black' } }} 
                        />
                        <TextInput 
                          label="Horario Check-Out (Hospedajes)" 
                          placeholder="p.ej. 13:00"
                          value={settings.horario_checkout}
                          onChange={(e: React.ChangeEvent<HTMLInputElement>) => setSettings((prev: any) => ({...prev, horario_checkout: e.target.value}))}
                          onBlur={() => saveSetting('horario_checkout', settings.horario_checkout)}
                          styles={{ input: { backgroundColor: 'white', color: 'black' } }} 
                        />
                      </SimpleGrid>

                      <Divider color="#2a2a2a" />
                      
                      <Group justify="space-between">
                        <Box>
                          <Text size="sm" fw={600} c="white">Mínimo para realizar reserva</Text>
                          <Text size="xs" c="dimmed">Activa el pago mínimo obligatorio</Text>
                        </Box>
                        <Switch 
                          color="teal" 
                          checked={settings.reserva_minimo_active === 'true'} 
                          onChange={(e: React.ChangeEvent<HTMLInputElement>) => {
                            const val = e.currentTarget.checked ? 'true' : 'false';
                            setSettings((prev: any) => ({...prev, reserva_minimo_active: val}));
                            saveSetting('reserva_minimo_active', val);
                          }}
                        />
                      </Group>

                      {settings.reserva_minimo_active === 'true' && (
                        <NumberInput 
                          label="Monto Mínimo de Reserva ($)" 
                          value={parseFloat(settings.reserva_minimo_monto)} 
                          onChange={(val: string | number) => {
                            const s = val.toString();
                            setSettings((prev: any) => ({...prev, reserva_minimo_monto: s}));
                            saveSetting('reserva_minimo_monto', s);
                          }}
                          styles={{ input: { backgroundColor: 'white', color: 'black' } }} 
                        />
                      )}

                      <Group justify="space-between">
                        <Box>
                          <Text size="sm" fw={600} c="white">Permitir entrada con deuda</Text>
                          <Text size="xs" c="dimmed">Habilita asignar habitación sin pago completo</Text>
                        </Box>
                        <Switch 
                          color="orange" 
                          checked={settings.permitir_entrada_deuda_active === 'true'} 
                          onChange={(e: React.ChangeEvent<HTMLInputElement>) => {
                            const val = e.currentTarget.checked ? 'true' : 'false';
                            setSettings((prev: any) => ({...prev, permitir_entrada_deuda_active: val}));
                            saveSetting('permitir_entrada_deuda_active', val);
                          }}
                        />
                      </Group>
                    </Stack>
                  </Paper>

                  <Paper p="xl" radius="md" bg="#1e1e1e" style={{ border: '1px solid #2a2a2a' }}>
                    <Stack gap="lg">
                      <Text fw={600} size="md" c="white" tt="uppercase">NFC y Pantallas (TV)</Text>
                      
                      <Group justify="space-between">
                        <Box>
                          <Text size="sm" fw={600} c="white">Activar Pantalla Principal (TV)</Text>
                          <Text size="xs" c="dimmed">Muestra información del hotel en TVs Smart</Text>
                        </Box>
                        <Switch 
                          color="teal" 
                          checked={settings.tv_display_active === 'true'} 
                          onChange={(e: React.ChangeEvent<HTMLInputElement>) => {
                            const val = e.currentTarget.checked ? 'true' : 'false';
                            setSettings((prev: any) => ({...prev, tv_display_active: val}));
                            saveSetting('tv_display_active', val);
                          }}
                        />
                      </Group>

                      {settings.tv_display_active === 'true' && (
                        <TextInput 
                          label="URL de Pantalla TV" 
                          placeholder="http://display-hotel.local"
                          value={settings.tv_display_url}
                          onChange={(e: React.ChangeEvent<HTMLInputElement>) => setSettings((prev: any) => ({...prev, tv_display_url: e.target.value}))}
                          onBlur={() => saveSetting('tv_display_url', settings.tv_display_url)}
                          styles={{ input: { backgroundColor: 'white', color: 'black' } }} 
                        />
                      )}
                    </Stack>
                  </Paper>
                </SimpleGrid>

                {/* 3. SEGURIDAD Y CONTROL */}
                <Paper p="xl" radius="md" bg="#1e1e1e" style={{ border: '1px solid #2a2a2a' }}>
                  <Stack gap="lg">
                    <Text fw={600} size="md" c="white" tt="uppercase">Seguridad y Portones</Text>
                    
                    <Group justify="space-between" bg="#141414" p="md" style={{ borderRadius: 8 }}>
                      <Box>
                        <Text size="sm" fw={600} c="red">Modo Standalone (Desactivar Cámaras/Portón)</Text>
                        <Text size="xs" c="dimmed">Deshabilita la toma de fotos y apertura remota desde el sistema.</Text>
                      </Box>
                      <Switch 
                        color="red" 
                        checked={settings.gate_control_disabled === 'true'} 
                        onChange={(e: React.ChangeEvent<HTMLInputElement>) => {
                          const val = e.currentTarget.checked ? 'true' : 'false';
                          setSettings((prev: any) => ({...prev, gate_control_disabled: val}));
                          saveSetting('gate_control_disabled', val);
                        }}
                      />
                    </Group>

                    <SimpleGrid cols={{ base: 1, sm: 2 }} spacing="lg">
                      <TextInput 
                        label="URL Cámara Entrada (JPG/MJPEG)" 
                        value={settings.cam_entrada_url}
                        onChange={(e: React.ChangeEvent<HTMLInputElement>) => setSettings((prev: any) => ({...prev, cam_entrada_url: e.target.value}))}
                        onBlur={() => saveSetting('cam_entrada_url', settings.cam_entrada_url)}
                        styles={{ input: { backgroundColor: 'white', color: 'black' } }} 
                      />
                      <TextInput 
                        label="URL Cámara Salida (JPG/MJPEG)" 
                        value={settings.cam_salida_url}
                        onChange={(e: React.ChangeEvent<HTMLInputElement>) => setSettings((prev: any) => ({...prev, cam_salida_url: e.target.value}))}
                        onBlur={() => saveSetting('cam_salida_url', settings.cam_salida_url)}
                        styles={{ input: { backgroundColor: 'white', color: 'black' } }} 
                      />
                    </SimpleGrid>
                  </Stack>
                </Paper>

                {/* 4. REPORTES POLICIALES Y ANALÍTICAS */}
                <Paper p="xl" radius="md" bg="#1e1e1e" style={{ border: '1px solid #2a2a2a' }}>
                  <Stack gap="lg">
                    <Group justify="space-between">
                      <Group gap="xs">
                        <IconDatabase size={20} color="gray" />
                        <Text fw={600} size="md" c="white" tt="uppercase">Configuración Reporte Policial</Text>
                      </Group>
                      <Switch 
                        color="teal" 
                        checked={settings.reporte_policial_active === 'true'} 
                        onChange={(e: React.ChangeEvent<HTMLInputElement>) => {
                          const val = e.currentTarget.checked ? 'true' : 'false';
                          setSettings((prev: any) => ({...prev, reporte_policial_active: val}));
                          saveSetting('reporte_policial_active', val);
                        }}
                      />
                    </Group>
                    
                    {settings.reporte_policial_active === 'true' && (
                      <SimpleGrid cols={{ base: 1, sm: 3 }} spacing="lg">
                        <Stack gap={4}>
                          <Text size="xs" fw={700} c="dimmed">CANTIDAD EXPEDIENTES</Text>
                          <NumberInput 
                              value={parseInt(settings.reporte_policial_cantidad_exp)} 
                              onChange={(val: string | number) => {
                                const s = val.toString();
                                setSettings((prev: any) => ({...prev, reporte_policial_cantidad_exp: s}));
                                saveSetting('reporte_policial_cantidad_exp', s);
                              }}
                              styles={{ input: { backgroundColor: 'white', color: 'black', height: 45, fontSize: 18, fontWeight: 600 } }} 
                            />
                        </Stack>
                        <Stack gap={4}>
                          <Text size="xs" fw={700} c="dimmed">HUESPEDES RESTA</Text>
                          <NumberInput 
                              value={parseInt(settings.reporte_policial_huespedes_resta)} 
                              onChange={(val: string | number) => {
                                const s = val.toString();
                                setSettings((prev: any) => ({...prev, reporte_policial_huespedes_resta: s}));
                                saveSetting('reporte_policial_huespedes_resta', s);
                              }}
                              styles={{ input: { backgroundColor: 'white', color: 'black', height: 45, fontSize: 18, fontWeight: 600 } }} 
                            />
                        </Stack>
                        <Stack gap={4}>
                          <Text size="xs" fw={700} c="dimmed">TOTAL HUESPEDES</Text>
                          <NumberInput 
                              value={parseInt(settings.reporte_policial_total_huespedes)} 
                              onChange={(val: string | number) => {
                                const s = val.toString();
                                setSettings((prev: any) => ({...prev, reporte_policial_total_huespedes: s}));
                                saveSetting('reporte_policial_total_huespedes', s);
                              }}
                              styles={{ input: { backgroundColor: 'white', color: 'black', height: 45, fontSize: 18, fontWeight: 600 } }} 
                            />
                        </Stack>
                      </SimpleGrid>
                    )}
                  </Stack>
                </Paper>
              </Stack>
            )}

            {activeSection === 'personal' && (
              <Stack gap="xl">
                <Paper p="xl" radius="md" bg="#1e1e1e" style={{ border: '1px solid #2a2a2a' }}>
                  <Stack gap="lg">
                    <Group justify="space-between">
                      <Box>
                        <Text fw={600} size="lg" c="white" tt="uppercase">Personal y Usuarios</Text>
                        <Text size="xs" c="dimmed">Gestiona quién tiene acceso al sistema y sus roles.</Text>
                      </Box>
                      <Group gap="sm">
                        {usuariosData.length === 0 && (
                          <Button 
                            variant="light" 
                            color="orange" 
                            leftSection={<IconDatabase size={16} />} 
                            onClick={seedUsuarios}
                          >
                            Cargar Usuarios Base
                          </Button>
                        )}
                        <Button 
                          leftSection={<IconPlus size={18} />} 
                          color="teal" 
                          onClick={() => {
                            setEditingUsuario(null);
                            setTempPhotoUrl(null);
                            setTempNfcCode(null);
                            setIsUsuarioModalOpen(true);
                          }}
                        >
                          Nuevo Usuario
                        </Button>
                      </Group>
                    </Group>

                    <Divider color="#2a2a2a" />

                    <DashboardTable 
                      columns={[
                        { key: 'u', label: 'Personal' },
                        { key: 'r', label: 'Rol / Cargo' },
                        { key: 'p', label: 'Presencia' },
                        { key: 'h', label: 'Horario' },
                        { key: 'c', label: 'Cumpleaños', width: 120 },
                         { key: 'i', label: 'Ingreso', width: 120 },
                         { key: 'nfc', label: 'NFC', width: 90 },
                         { key: 'a', label: '', width: 100, textAlign: 'right' }
                      ]}
                      data={usuariosData}
                      renderRow={renderUsuarioRow}
                      renderCard={renderUsuarioCard}
                    />
                  </Stack>
                </Paper>
              </Stack>
            )}
                        {activeSection === 'inventario' && (
              <Stack gap="xl">
                <Paper p="xl" radius="md" bg="#1e1e1e" style={{ border: '1px solid #2a2a2a' }}>
                  <Stack gap="lg">
                    <Group justify="space-between">
                      <Box>
                        <Text fw={600} size="lg" c="white" tt="uppercase">Control de Inventario</Text>
                        <Text size="xs" c="dimmed">Seguimiento de stock de amenities, limpieza y mantenimiento.</Text>
                      </Box>
                    </Group>

                    <Tabs defaultValue="productos" color="teal" variant="pills">
                      <Tabs.List mb="md">
                        <Tabs.Tab value="productos" leftSection={<IconPackage size={16} />}>Productos</Tabs.Tab>
                        <Tabs.Tab value="historial" leftSection={<IconHistory size={16} />}>Historial</Tabs.Tab>
                      </Tabs.List>

                      <Tabs.Panel value="productos" pt="xs">
                        <Group justify="flex-end" mb="md">
                          <Button 
                            leftSection={<IconPlus size={18} />} 
                            color="teal"
                            onClick={() => {
                              setEditingInventoryItem(null);
                              setIsInventoryModalOpen(true);
                            }}
                          >
                            Nuevo Producto
                          </Button>
                        </Group>

                        <Divider color="#2a2a2a" mb="md" />

                        <DashboardTable 
                          columns={[
                            { key: 'n', label: 'Producto' },
                            { key: 'c', label: 'Categoría', width: 140 },
                            { key: 's', label: 'Stock Actual', width: 120 },
                            { key: 'sc', label: 'Estado', width: 120 },
                            { key: 'a', label: '', width: 140, textAlign: 'right' }
                          ]}
                          data={inventoryData}
                          renderRow={(item: any) => {
                            const isLowStock = item.stock_actual <= item.stock_minimo;
                            const isCritical = item.stock_actual === 0;
                            return (
                              <Table.Tr key={item.id}>
                                <Table.Td>
                                  <Box>
                                    <Text size="sm" fw={600} c="white">{item.nombre}</Text>
                                    <Text size="xs" c="dimmed">{item.descripcion || 'Sin descripción'}</Text>
                                  </Box>
                                </Table.Td>
                                <Table.Td>
                                  <Badge variant="dot" color="blue">{item.categoria}</Badge>
                                </Table.Td>
                                <Table.Td>
                                  <Text size="sm" fw={700} c={isLowStock ? 'red' : 'white'}>
                                    {item.stock_actual} {item.unidad_medida}
                                  </Text>
                                </Table.Td>
                                <Table.Td>
                                  {isLowStock ? (
                                    <Badge color="red" variant="filled" leftSection={<IconAlertTriangle size={10} />}>Stock Bajo</Badge>
                                  ) : (
                                    <Badge color="teal" variant="light">Normal</Badge>
                                  )}
                                </Table.Td>
                                <Table.Td>
                                  <Group gap="xs" justify="flex-end">
                                    <Tooltip label="Entrada/Salida">
                                      <ActionIcon variant="light" color="teal" onClick={() => {
                                        setAdjustingItem(item);
                                        setIsStockAdjustmentModalOpen(true);
                                      }}>
                                        <IconArrowNarrowUp size={16} />
                                      </ActionIcon>
                                    </Tooltip>
                                    <ActionIcon variant="light" color="blue" onClick={() => {
                                      setEditingInventoryItem(item);
                                      setIsInventoryModalOpen(true);
                                    }}>
                                      <IconSettings size={16} />
                                    </ActionIcon>
                                    <ActionIcon variant="light" color="red" onClick={async () => {
                                      if (confirm('¿Eliminar producto?')) {
                                        await api.deleteInventarioItem(item.id);
                                        const inv = await api.getInventario();
                                        setInventoryData(inv);
                                      }
                                    }}>
                                      <IconTrash size={16} />
                                    </ActionIcon>
                                  </Group>
                                </Table.Td>
                              </Table.Tr>
                            );
                          }}
                          renderCard={(item: any) => {
                            const isLowStock = item.stock_actual <= item.stock_minimo;
                            return (
                              <Card key={item.id} shadow="none" bg="#1e1e1e" style={{ borderBottom: '1px solid #2a2a2a' }} p="md">
                                <Group justify="space-between" mb={4}>
                                  <Box>
                                    <Text size="sm" fw={600} c="white">{item.nombre}</Text>
                                    <Text size="xs" c="dimmed">{item.categoria}</Text>
                                  </Box>
                                  <Badge color={isLowStock ? 'red' : 'teal'}>{item.stock_actual} {item.unidad_medida}</Badge>
                                </Group>
                                <Group justify="flex-end">
                                  <Button size="compact-xs" variant="light" color="teal" onClick={() => {
                                    setAdjustingItem(item);
                                    setIsStockAdjustmentModalOpen(true);
                                  }}>Stock</Button>
                                  <Button size="compact-xs" variant="light" color="blue" onClick={() => {
                                    setEditingInventoryItem(item);
                                    setIsInventoryModalOpen(true);
                                  }}>Editar</Button>
                                </Group>
                              </Card>
                            );
                          }}
                        />
                      </Tabs.Panel>

                      <Tabs.Panel value="historial" pt="xs">
                        <Text fw={600} size="md" c="white" mb="xs">Movimientos Recientes</Text>
                        <Text size="xs" c="dimmed" mb="xl">Kardex de entradas y salidas registradas en el almacén.</Text>

                        <DashboardTable 
                          columns={[
                            { key: 'p', label: 'Producto', width: 160 },
                            { key: 't', label: 'Tipo', width: 100 },
                            { key: 'ca', label: 'Cant.', width: 80 },
                            { key: 'm', label: 'Motivo' },
                            { key: 'u', label: 'Responsable', width: 140 },
                            { key: 'f', label: 'Fecha', width: 150 }
                          ]}
                          data={movimientosInventario}
                          renderRow={(item: any) => (
                            <Table.Tr key={item.id}>
                              <Table.Td><Text size="sm" fw={600} c="white">{item.item_nombre}</Text></Table.Td>
                              <Table.Td><Badge color={item.tipo === 'ENTRADA' ? 'teal' : 'red'} size="xs">{item.tipo}</Badge></Table.Td>
                              <Table.Td><Text fw={700} c="white" size="xs">{item.cantidad}</Text></Table.Td>
                              <Table.Td><Text size="xs" c="dimmed" truncate maw={200}>{item.motivo}</Text></Table.Td>
                              <Table.Td><Text size="xs" c="white">{item.usuario_nombre}</Text></Table.Td>
                              <Table.Td><Text size="xs" c="dimmed">{dayjs(item.fecha).format('DD/MM HH:mm')}</Text></Table.Td>
                            </Table.Tr>
                          )}
                          renderCard={(item: any) => (
                            <Card key={item.id} shadow="none" bg="#1e1e1e" style={{ borderBottom: '1px solid #2a2a2a' }} p="md">
                              <Group justify="space-between" mb={4}>
                                <Text size="sm" fw={600} c="white">{item.item_nombre}</Text>
                                <Badge color={item.tipo === 'ENTRADA' ? 'teal' : 'red'} size="xs">{item.tipo}</Badge>
                              </Group>
                              <Group justify="space-between">
                                <Text size="xs" c="white">CANT: {item.cantidad}</Text>
                                <Text size="xs" c="dimmed">{dayjs(item.fecha).format('DD/MM HH:mm')}</Text>
                              </Group>
                              <Text size="xs" c="dimmed" mt={4} fs="italic">{item.motivo}</Text>
                            </Card>
                          )}
                        />
                      </Tabs.Panel>
                    </Tabs>
                  </Stack>
                </Paper>
              </Stack>
            )}

            {activeSection === 'datos' && (
              <Stack gap="xl">
                {/* ... existing backup section ... */}
                <Paper p="xl" radius="md" bg="#1e1e1e" style={{ border: '1px solid #2a2a2a' }}>
                  <Stack gap="lg">
                    <Group justify="space-between">
                      <Box>
                        <Text fw={600} size="lg" c="white" tt="uppercase">Respaldo de Seguridad</Text>
                        <Text size="xs" c="dimmed">Descarga una copia completa de la base de datos esmeralda.db</Text>
                      </Box>
                      <Button 
                        component="a" 
                        href={api.downloadBackup()} 
                        download
                        leftSection={<IconDownload size={18} />} 
                        color="teal"
                      >
                        Descargar Backup (.db)
                      </Button>
                    </Group>

                    <Divider color="#2a2a2a" />

                    <Tabs defaultValue="audit" styles={{ tab: { color: 'gray', '&[data-active]': { color: 'white' } } }}>
                      <Tabs.List>
                        <Tabs.Tab value="audit" leftSection={<IconListDetails size={16} />}>Auditoría de Sistema</Tabs.Tab>
                        <Tabs.Tab value="inventory" leftSection={<IconPackage size={16} />}>Movimientos de Stock</Tabs.Tab>
                      </Tabs.List>

                      <Tabs.Panel value="audit" pt="xl">
                        <Box>
                          <Text fw={600} size="md" c="white" mb="xs" tt="uppercase">Historial de Actividad (Logs)</Text>
                          <Text size="xs" c="dimmed" mb="xl">Últimos movimientos realizados en el sistema.</Text>
                          
                          <DashboardTable 
                            columns={[
                              { key: 'u', label: 'Usuario', width: 160 },
                              { key: 'ac', label: 'Acción', width: 220 },
                              { key: 'd', label: 'Descripción' },
                              { key: 'f', label: 'Fecha', width: 180 }
                            ]}
                            data={logsData}
                            renderRow={(item: any) => (
                              <Table.Tr key={item.id}>
                                <Table.Td><Text size="sm" fw={600} c="white">{item.usuario}</Text></Table.Td>
                                <Table.Td><Badge variant="light" color="blue" fullWidth>{item.accion}</Badge></Table.Td>
                                <Table.Td><Text size="xs" c="dimmed">{item.descripcion}</Text></Table.Td>
                                <Table.Td><Text size="xs" c="dimmed">{dayjs(item.fecha).format('DD/MM/YY HH:mm:ss')}</Text></Table.Td>
                              </Table.Tr>
                            )}
                            renderCard={(item: any) => (
                              <Card key={item.id} shadow="none" bg="#1e1e1e" style={{ borderBottom: '1px solid #2a2a2a' }} p="md">
                                <Group justify="space-between" mb={4}>
                                  <Text size="sm" fw={600} c="white">{item.usuario}</Text>
                                  <Text size="xs" c="dimmed">{dayjs(item.fecha).format('DD/MM/YY HH:mm')}</Text>
                                </Group>
                                <Badge variant="light" color="blue" mb={4}>{item.accion}</Badge>
                                <Text size="xs" c="dimmed">{item.descripcion}</Text>
                              </Card>
                            )}
                          />
                        </Box>
                      </Tabs.Panel>

                      <Tabs.Panel value="inventory" pt="xl">
                        <Box>
                          <Text fw={600} size="md" c="white" mb="xs" tt="uppercase">Historial de Inventario</Text>
                          <Text size="xs" c="dimmed" mb="xl">Registro cronológico de entradas y salidas de almacén.</Text>
                          
                          <DashboardTable 
                            columns={[
                              { key: 'p', label: 'Producto', width: 160 },
                              { key: 't', label: 'Tipo', width: 100 },
                              { key: 'ca', label: 'Cantidad', width: 100 },
                              { key: 'm', label: 'Motivo' },
                              { key: 'u', label: 'Responsable', width: 140 },
                              { key: 'f', label: 'Fecha', width: 160 }
                            ]}
                            data={movimientosInventario}
                            renderRow={(item: any) => (
                              <Table.Tr key={item.id}>
                                <Table.Td><Text size="sm" fw={600} c="white">{item.item_nombre}</Text></Table.Td>
                                <Table.Td><Badge color={item.tipo === 'ENTRADA' ? 'teal' : 'red'}>{item.tipo}</Badge></Table.Td>
                                <Table.Td><Text fw={700} c="white">{item.cantidad}</Text></Table.Td>
                                <Table.Td><Text size="xs" c="dimmed">{item.motivo}</Text></Table.Td>
                                <Table.Td><Text size="xs" c="white">{item.usuario_nombre}</Text></Table.Td>
                                <Table.Td><Text size="xs" c="dimmed">{dayjs(item.fecha).format('DD/MM HH:mm')}</Text></Table.Td>
                              </Table.Tr>
                            )}
                            renderCard={(item: any) => (
                              <Card key={item.id} shadow="none" bg="#1e1e1e" style={{ borderBottom: '1px solid #2a2a2a' }} p="md">
                                <Group justify="space-between" mb={4}>
                                  <Text size="sm" fw={600} c="white">{item.item_nombre}</Text>
                                  <Badge color={item.tipo === 'ENTRADA' ? 'teal' : 'red'}>{item.tipo}</Badge>
                                </Group>
                                <Text size="xs" c="white">Cantidad: {item.cantidad}</Text>
                                <Text size="xs" c="dimmed">{item.motivo}</Text>
                              </Card>
                            )}
                          />
                        </Box>
                      </Tabs.Panel>
                    </Tabs>
                  </Stack>
                </Paper>
              </Stack>
            )}
          </>
        )}
      </Stack>
      {/* --- MODAL INVENTARIO --- */}
      <Modal 
        opened={isInventoryModalOpen} 
        onClose={() => setIsInventoryModalOpen(false)} 
        title={editingInventoryItem ? "Editar Producto" : "Nuevo Producto"}
        bg="#141414"
        styles={{ content: { backgroundColor: '#141414' }, header: { backgroundColor: '#141414' } }}
      >
        <form onSubmit={async (e) => {
          e.preventDefault();
          const fd = new FormData(e.currentTarget);
          const data = {
            nombre: fd.get('nombre'),
            descripcion: fd.get('descripcion'),
            categoria: fd.get('categoria'),
            stock_minimo: Number(fd.get('stock_minimo')),
            unidad_medida: fd.get('unidad_medida'),
            stock_actual: editingInventoryItem ? editingInventoryItem.stock_actual : Number(fd.get('stock_actual') || 0)
          };
          if (editingInventoryItem) {
            await api.updateInventarioItem(editingInventoryItem.id, data);
          } else {
            await api.createInventarioItem(data);
          }
          setIsInventoryModalOpen(false);
          const inv = await api.getInventario();
          setInventoryData(inv);
        }}>
          <Stack gap="md">
            <TextInput name="nombre" label="Nombre del Producto" defaultValue={editingInventoryItem?.nombre} required styles={{ input: { backgroundColor: 'white', color: 'black' } }} />
            <Textarea name="descripcion" label="Descripción" defaultValue={editingInventoryItem?.descripcion} styles={{ input: { backgroundColor: 'white', color: 'black' } }} />
            <Select 
              name="categoria" 
              label="Categoría" 
              defaultValue={editingInventoryItem?.categoria || 'Amenities'}
              data={['Amenities', 'Limpieza', 'Mantenimiento', 'Papelería', 'Bebidas/MiniBar']} 
              styles={{ input: { backgroundColor: 'white', color: 'black' } }} 
            />
            <SimpleGrid cols={2}>
              <NumberInput name="stock_minimo" label="Stock Mínimo" defaultValue={editingInventoryItem?.stock_minimo || 5} styles={{ input: { backgroundColor: 'white', color: 'black' } }} />
              <Select 
                name="unidad_medida" 
                label="Unidad" 
                placeholder="Seleccionar unidad"
                defaultValue={editingInventoryItem?.unidad_medida || 'unidades'} 
                data={[
                  { value: 'unidades', label: 'Unidades' },
                  { value: 'litros', label: 'Litros' },
                  { value: 'paquetes', label: 'Paquetes' },
                  { value: 'cajas', label: 'Cajas' },
                  { value: 'galones', label: 'Galones' },
                  { value: 'kilogramos', label: 'Kilogramos' },
                  { value: 'gramos', label: 'Gramos' },
                  { value: 'mililitros', label: 'Mililitros' },
                ]}
                searchable
                styles={{ input: { backgroundColor: 'white', color: 'black' } }} 
              />
            </SimpleGrid>
            {!editingInventoryItem && (
               <NumberInput name="stock_actual" label="Stock Inicial" defaultValue={0} styles={{ input: { backgroundColor: 'white', color: 'black' } }} />
            )}
            <Group justify="flex-end" mt="xl">
              <Button variant="subtle" color="gray" onClick={() => setIsInventoryModalOpen(false)}>Cancelar</Button>
              <Button type="submit" color="teal">Guardar</Button>
            </Group>
          </Stack>
        </form>
      </Modal>

      {/* --- MODAL AJUSTE STOCK --- */}
      <Modal 
        opened={isStockAdjustmentModalOpen} 
        onClose={() => setIsStockAdjustmentModalOpen(false)} 
        title={`Ajustar Stock: ${adjustingItem?.nombre}`}
        bg="#141414"
        styles={{ content: { backgroundColor: '#141414' }, header: { backgroundColor: '#141414' } }}
      >
        <Stack gap="md">
          <Group grow>
            <Button 
              variant={adjustmentType === 'ENTRADA' ? 'filled' : 'light'} 
              color="teal" 
              onClick={() => setAdjustmentType('ENTRADA')}
              leftSection={<IconArrowNarrowUp size={18} />}
            >
              Entrada
            </Button>
            <Button 
              variant={adjustmentType === 'SALIDA' ? 'filled' : 'light'} 
              color="red" 
              onClick={() => setAdjustmentType('SALIDA')}
              leftSection={<IconArrowNarrowDown size={18} />}
            >
              Salida
            </Button>
          </Group>
          
          <NumberInput 
            id="adjust-qty" 
            label="Cantidad" 
            placeholder="0" 
            min={1} 
            styles={{ input: { backgroundColor: 'white', color: 'black' } }} 
          />
          <TextInput 
            id="adjust-reason" 
            label="Motivo / Nota" 
            placeholder="Ej: Reposición semanal, Limpieza Hab 10..." 
            styles={{ input: { backgroundColor: 'white', color: 'black' } }} 
          />

          <Group justify="flex-end" mt="xl">
            <Button variant="subtle" color="gray" onClick={() => setIsStockAdjustmentModalOpen(false)}>Cancelar</Button>
            <Button color="teal" onClick={async () => {
              const qty = Number((document.getElementById('adjust-qty') as any).value);
              const reason = (document.getElementById('adjust-reason') as any).value;
              
              if (!qty) return;

              await api.registrarMovimiento({
                item_id: adjustingItem.id,
                usuario_id: 1, // Placeholder for current user id
                cantidad: qty,
                tipo: adjustmentType,
                motivo: reason
              });

              setIsStockAdjustmentModalOpen(false);
              const inv = await api.getInventario();
              setInventoryData(inv);
              notifications.show({ message: 'Stock actualizado con éxito', color: 'teal' });
            }}>
              Confirmar
            </Button>
          </Group>
        </Stack>      </Modal>

      <Modal 
        opened={isUsuarioModalOpen} 
        onClose={() => setIsUsuarioModalOpen(false)} 
        title={
          <Group gap="xs">
            <IconUsers size={20} color="#24cb7c" />
            <Text fw={600}>{editingUsuario ? 'Editar Usuario' : 'Nuevo Usuario'}</Text>
          </Group>
        }
        centered
        bg="#141414"
        styles={{ 
          content: { backgroundColor: '#1e1e1e', color: 'white', border: '1px solid #333' }, 
          header: { backgroundColor: '#1e1e1e', color: 'white' },
          title: { color: 'white' }
        }}
      >
        <form onSubmit={(e) => {
          e.preventDefault();
          const fd = new FormData(e.currentTarget);
          handleSaveUsuario({
            ...editingUsuario,
            username: fd.get('username'),
            nombre: fd.get('nombre'),
            rol: fd.get('rol'),
            horario: fd.get('horario'),
            foto_url: tempPhotoUrl || editingUsuario?.foto_url,
            is_present: fd.get('is_present') === 'true',
             nfc_code: tempNfcCode || editingUsuario?.nfc_code,
             fecha_nacimiento: (e.currentTarget.elements as any).fecha_nacimiento?.value ? dayjs((e.currentTarget.elements as any).fecha_nacimiento.value).toISOString() : null,
            fecha_ingreso: (e.currentTarget.elements as any).fecha_ingreso?.value ? dayjs((e.currentTarget.elements as any).fecha_ingreso.value).toISOString() : null,
          });
        }}>
          <Stack gap="md">
            <Group justify="center" mb="md">
              <Stack align="center" gap={5}>
                <Avatar 
                  src={tempPhotoUrl ? `${BASE_URL.replace('/api','')}${tempPhotoUrl}` : (editingUsuario?.foto_url ? `${BASE_URL.replace('/api','')}${editingUsuario.foto_url}` : null)} 
                  size={100} 
                  radius={100} 
                  styles={{ placeholder: { backgroundColor: '#2a2a2a' } }}
                >
                  <IconPhoto size={40} color="#555" />
                </Avatar>
                <FileButton 
                  accept="image/png,image/jpeg" 
                  onChange={async (file) => {
                    if (file) {
                      const res = await api.uploadUserPhoto(file);
                      setTempPhotoUrl(res.url);
                    }
                  }}
                >
                  {(props) => <Button {...props} variant="subtle" size="compact-xs" color="teal">Cambiar Foto</Button>}
                </FileButton>
              </Stack>
            </Group>

            <TextInput 
              name="nombre" 
              label="Nombre Completo" 
              placeholder="Ej. Walter Cattivelli" 
              defaultValue={editingUsuario?.nombre}
              required
              styles={{ input: { backgroundColor: 'white', color: 'black' } }} 
            />
            
            <SimpleGrid cols={2}>
              <TextInput 
                name="username" 
                label="Cédula o ID de Usuario" 
                placeholder="cedula o username" 
                defaultValue={editingUsuario?.username}
                required
                styles={{ input: { backgroundColor: 'white', color: 'black' } }} 
              />
              <Select 
                name="rol"
                label="Rol / Cargo"
                placeholder="Seleccionar rol"
                defaultValue={editingUsuario?.rol || 'recepcionista'}
                data={[
                  { value: 'administrador', label: 'Administrador' },
                  { value: 'socio', label: 'Socio' },
                  { value: 'recepcionista', label: 'Recepcionista' },
                  { value: 'camarera', label: 'Camarera' },
                  { value: 'mantenimiento', label: 'Mantenimiento' },
                  { value: 'vigilante', label: 'Vigilante' },
                  { value: 'empresa', label: 'Empresa / Proveedor' },
                ]}
                required
                styles={{ input: { backgroundColor: 'white', color: 'black' } }} 
              />
            </SimpleGrid>

            <SimpleGrid cols={2}>
              <DatePickerInput
                name="fecha_nacimiento"
                label="Fecha de Nacimiento"
                placeholder="Seleccionar fecha"
                defaultValue={editingUsuario?.fecha_nacimiento ? new Date(editingUsuario.fecha_nacimiento) : null}
                locale="es"
                styles={{ input: { backgroundColor: 'white', color: 'black' } }} 
              />
              <DatePickerInput
                name="fecha_ingreso"
                label="Fecha de Ingreso"
                placeholder="Seleccionar fecha"
                defaultValue={editingUsuario?.fecha_ingreso ? new Date(editingUsuario.fecha_ingreso) : null}
                locale="es"
                styles={{ input: { backgroundColor: 'white', color: 'black' } }} 
              />
            </SimpleGrid>

            <Textarea
              name="horario" 
              label="Horario Detallado (Días y Horas)" 
              placeholder="Ej. Lun a Vie: 08:00 - 16:00&#10;Sáb: 08:00 - 12:00" 
              defaultValue={editingUsuario?.horario}
              minRows={3}
              styles={{ input: { backgroundColor: 'white', color: 'black' } }} 
            />

            <Select 
              name="is_present"
              label="Estado de Presencia"
              defaultValue={editingUsuario?.is_present ? 'true' : 'false'}
              data={[
                { value: 'true', label: 'Presente en Hotel' },
                { value: 'false', label: 'Ausente' },
              ]}
              styles={{ input: { backgroundColor: 'white', color: 'black' } }} 
            />

            <Group grow align="flex-end">
                <TextInput 
                  label="Código Tarjeta NFC"
                  placeholder="Sin asignar"
                  value={tempNfcCode || editingUsuario?.nfc_code || ''}
                  readOnly
                  styles={{ input: { backgroundColor: '#f8f9fa', color: '#555' } }}
                />
                <Button 
                  variant="light" 
                  color="teal" 
                  onClick={scanNfcForUser}
                  leftSection={<IconNfc size={16} />}
                >
                  Vincular Tarjeta
                </Button>
            </Group>

            {!editingUsuario && (
              <Text size="xs" c="dimmed" fs="italic">
                Nota: La contraseña temporal por defecto será 'password123'.
              </Text>
            )}

            <Group justify="flex-end" mt="xl">
              <Button variant="subtle" color="gray" onClick={() => setIsUsuarioModalOpen(false)}>Cancelar</Button>
              <Button type="submit" color="teal">Guardar Cambios</Button>
            </Group>
          </Stack>
        </form>
      </Modal>

      <Modal 
        opened={isInspeccionWizardOpen} 
        onClose={() => setIsInspeccionWizardOpen(false)} 
        fullScreen 
        bg="#141414"
        styles={{ content: { backgroundColor: '#141414' }, header: { backgroundColor: '#141414' } }}
      >
        <Stack h="100%">
          <Group justify="space-between" p="md">
            <Text fw={600} size="xl" c="teal">HABITACIÓN {scannedRoom?.numero}</Text>
            <Badge size="lg" variant="dot" color="blue">INSPECCIÓN EN CURSO</Badge>
          </Group>

          <Center h="100%">
            {inspeccionStep < itemsAInspeccionar.length ? renderWizardStep() : (
              <Stack w={600} gap="xl">
                <Title order={1} fw={600} ta="center" c="white">Finalizar Inspección</Title>
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
