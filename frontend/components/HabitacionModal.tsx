'use client';
 
import { 
  Modal, Grid, Box, Text, Group, TextInput, Select, 
  NumberInput, Button, ActionIcon, Badge, Tabs, Textarea,
  Divider, Stack, Paper, ThemeIcon, ScrollArea, Title, Accordion, Popover,
  Autocomplete
} from '@mantine/core';
import { DateTimePicker, DatePickerInput, DatePicker } from '@mantine/dates';
import dayjs from 'dayjs';
import { useMediaQuery } from '@mantine/hooks';
import { 
  IconSearch, IconUser, IconCalendar, IconPlus, IconTrash, 
  IconLock, IconClock, IconCheck, IconX, IconCash, IconHistory,
  IconBed, IconUsers, IconEye, IconMaximize, IconMinimize, IconArrowsExchange
} from '@tabler/icons-react';
import { notifications } from '@mantine/notifications';
import { Habitacion } from '../types';
import { useState, useEffect, useRef } from 'react';
import DataTableModal from './DataTableModal';
import { api } from '../app/lib/api';

interface HabitacionModalProps {
  habitacion: Habitacion | null;
  initialData?: any;
  opened: boolean;
  onClose: () => void;
  onSuccess?: () => void;
  bcv?: number;
  currentUser?: any;
}

const ACCENT_GRADIENT = 'linear-gradient(135deg, #36ea7e 0%, #11998e 100%)';
const ROBOTO_FONT = 'Roboto, sans-serif';
const LABEL_SIZE = '13px';
const INPUT_SIZE = '14px';
const INPUT_HEIGHT = '34px';

export default function HabitacionModal({ habitacion, initialData, opened, onClose, onSuccess, bcv = 45.62, currentUser }: HabitacionModalProps) {
  const isMobile = useMediaQuery('(max-width: 767px)');
  
  // Estado para manejar a los huéspedes (P1, P2, etc.)
  const [activePersona, setActivePersona] = useState<string>('P1');
  const [huespedes, setHuespedes] = useState<Record<string, any>>({
    'P1': { cedula: '', nombre: '', fecha_nacimiento: null, nacionalidad: 'Venezolano', estado_civil: 'Soltero', profesion: 'Comerciante', telefono: '', observaciones: '', tipo_cedula: 'V-', codigo_telefono: '+58', reputacion: 'positivo', visitas: 0, estado: 'ausente' },
  });
  const huespedesRef = useRef<Record<string, any>>(huespedes);

  const [esReserva, setEsReserva] = useState(false);

  const ESTADOS_VENEZUELA = [
    'Amazonas', 'Anzoátegui', 'Apure', 'Aragua', 'Barinas', 'Bolívar', 'Carabobo', 'Cojedes', 
    'Delta Amacuro', 'Falcón', 'Guárico', 'Lara', 'Mérida', 'Miranda', 'Monagas', 
    'Nueva Esparta', 'Portuguesa', 'Sucre', 'Táchira', 'Trujillo', 'Vargas', 'Yaracuy', 
    'Zulia', 'Distrito Capital', 'Extranjero'
  ];

  const updateHuesped = (field: string, value: any) => {
    if (field === 'cedula' || field === 'tipo_cedula') setErrorSearch(false);
    setHuespedes(prev => {
      const next = {
        ...prev,
        [activePersona]: { ...prev[activePersona], [field]: value }
      };
      huespedesRef.current = next;
      return next;
    });
  };
  
  // Estado de Gestión y Estancia
  const [costoDolar, setCostoDolar] = useState<number>(0);
  const [tipoEstadia, setTipoEstadia] = useState<string | null>('hospedaje');
  const [procedencia, setProcedencia] = useState('Lara');
  const [destino, setDestino] = useState('Lara');
  const [dias, setDias] = useState<number>(1);
  const [voucher, setVoucher] = useState('');
  const [appliedVoucher, setAppliedVoucher] = useState<any>(null);
  const [observacionesTransaccion, setObservacionesTransaccion] = useState('');
  
  const [dobText, setDobText] = useState<string>('');
  const [dobPopoverOpened, setDobPopoverOpened] = useState(false);

  useEffect(() => {
    const d = huespedes[activePersona]?.fecha_nacimiento;
    if (d) {
      const formatted = dayjs(d).isValid() ? dayjs(d).format('DD-MM-YYYY') : '';
      if (formatted !== dobText && formatted !== '') {
        setDobText(formatted);
      }
    } else {
      if (dobText !== '') setDobText('');
    }
  }, [activePersona, huespedes[activePersona]?.fecha_nacimiento]);

  const onDobTextChange = (val: string) => {
    // Basic mask: DD-MM-YYYY
    let raw = val.replace(/\D/g, '').slice(0, 8);
    let out = raw;
    if (raw.length > 2) out = raw.slice(0, 2) + '-' + raw.slice(2);
    if (raw.length > 4) out = out.slice(0, 5) + '-' + out.slice(5);
    setDobText(out);

    if (raw.length === 8) {
      const day = parseInt(raw.slice(0, 2));
      const month = parseInt(raw.slice(2, 4)) - 1;
      const year = parseInt(raw.slice(4, 8));
      const d = new Date(year, month, day);
      if (!isNaN(d.getTime())) {
        updateHuesped('fecha_nacimiento', d);
      }
    } else if (raw.length === 0) {
       updateHuesped('fecha_nacimiento', null);
    }
  };
  
  // Datos de Configuración
  const [horasParcialConfig, setHorasParcialConfig] = useState<number>(6);
  const [metodosPagoDisponibles, setMetodosPagoDisponibles] = useState<any[]>([]);
  
  // Refs para control de foco
  const inputNombreRef = useRef<HTMLInputElement>(null);
  const [errorSearch, setErrorSearch] = useState(false);
  const [showWarningModal, setShowWarningModal] = useState(false);
  const [showReputacionModal, setShowReputacionModal] = useState(false);
  const [isFullScreen, setIsFullScreen] = useState(false);

  // Cambio de Habitacion
  const [showCambiarHabitacionModal, setShowCambiarHabitacionModal] = useState(false);
  const [habitacionesLibres, setHabitacionesLibres] = useState<{value: string, label: string}[]>([]);
  const [nuevaHabitacionId, setNuevaHabitacionId] = useState<string | null>(null);
  const [cambioMotivo, setCambioMotivo] = useState('');
  const [loadingCambio, setLoadingCambio] = useState(false);

  // Historial de visitas
  const [showHistorialModal, setShowHistorialModal] = useState(false);
  const [historialData, setHistorialData] = useState<any[]>([]);
  const [loadingHistorial, setLoadingHistorial] = useState(false);
  
  // Bloqueo
  const [showBloquearModal, setShowBloquearModal] = useState(false);
  const [bloquearMotivo, setBloquearMotivo] = useState('');
  const [loadingBloqueo, setLoadingBloqueo] = useState(false);

  // Historial de Habitación
  const [showRoomHistoryModal, setShowRoomHistoryModal] = useState(false);
  const [roomHistoryData, setRoomHistoryData] = useState<any[]>([]);
  const [loadingRoomHistory, setLoadingRoomHistory] = useState(false);

  // Historial de Acceso (Entradas/Salidas)
  const [showAccessHistoryModal, setShowAccessHistoryModal] = useState(false);
  const [accessHistoryData, setAccessHistoryData] = useState<any[]>([]);
  const [loadingAccessHistory, setLoadingAccessHistory] = useState(false);

  const [showRetoqueModal, setShowRetoqueModal] = useState(false);
  const [camareraId, setCamareraId] = useState<string | null>(null);
  const [camareras, setCamareras] = useState<{value: string, label: string}[]>([]);
  const [loadingRetoque, setLoadingRetoque] = useState(false);

  const [fechaEntrada, setFechaEntrada] = useState<Date>(new Date());
  const [fechaSalidaCalculada, setFechaSalidaCalculada] = useState<Date | null>(null);

  const [pagos, setPagos] = useState([{ id: Date.now(), metodo: 'Efectivo Dolar', monto: 0, referencia: '' }]);
  const [extras, setExtras] = useState<{id: number, descripcion: string, monto: any}[]>([]);
  const [loading, setLoading] = useState(false);

  const calculateAge = (dob: any) => {
    if (!dob) return null;
    const birthDate = dob instanceof Date ? dob : new Date(dob);
    if (isNaN(birthDate.getTime())) return null;
    
    const today = new Date();
    let age = today.getFullYear() - birthDate.getFullYear();
    const m = today.getMonth() - birthDate.getMonth();
    if (m < 0 || (m === 0 && today.getDate() < birthDate.getDate())) {
      age--;
    }
    return age;
  };

  const handleValidateVoucher = async () => {
    if (!voucher.trim()) return;
    try {
      const data = await api.getVoucher(voucher.trim().toUpperCase());
      setAppliedVoucher(data);
      setVoucher(data.codigo);
      notifications.show({
        title: 'Cupón Aplicado',
        message: `Descuento: ${data.tipo === 'porcentaje' ? `${data.valor}%` : `$${data.valor}`}`,
        color: 'green'
      });
    } catch (err: any) {
      notifications.show({
        title: 'Error',
        message: err.message || 'Cupón no válido o inactivo.',
        color: 'red'
      });
      setAppliedVoucher(null);
      console.error("Error validando cupón:", err);
    }
  };

  const handleRemoveVoucher = () => {
    setAppliedVoucher(null);
    setVoucher('');
    notifications.show({
      title: 'Cupón Removido',
      message: 'Se ha eliminado el descuento del total.',
      color: 'blue'
    });
  };

  const handleBloquear = async () => {
    if (!bloquearMotivo.trim() || !habitacion) {
        notifications.show({ title: 'Atención', message: 'Debe ingresar un motivo para bloquear la habitación', color: 'yellow' });
        return;
    }
    setLoadingBloqueo(true);
    try {
      await api.bloquearHabitacion(habitacion.id, { 
        motivo: bloquearMotivo,
        nueva_habitacion_id: nuevaHabitacionId ? parseInt(nuevaHabitacionId) : null
      });
      notifications.show({ title: 'Éxito', message: '¡Habitación bloqueada con éxito!', color: 'gray', icon: <IconLock /> });
      if (onSuccess) onSuccess();
      onClose();
      setShowBloquearModal(false);
    } catch (err: any) {
      notifications.show({ title: 'Error', message: err.message || 'Ocurrió un problema.', color: 'red', icon: <IconX /> });
    } finally {
      setLoadingBloqueo(false);
    }
  };

  const handleFetchHistorial = async () => {
    const cedulaActual = huespedes[activePersona].cedula;
    const tipo = huespedes[activePersona].tipo_cedula;
    if (!cedulaActual) {
      notifications.show({ title: 'Atención', message: 'Debe ingresar una cédula para ver el historial', color: 'yellow' });
      return;
    }
    
    setShowHistorialModal(true);
    setLoadingHistorial(true);
    try {
      const data = await api.getClienteHistorial(`${tipo}${cedulaActual}`);
      setHistorialData(data);
    } catch (err) {
      console.error("Error buscando historial:", err);
    } finally {
      setLoadingHistorial(false);
    }
  };

  const handleFetchRoomHistory = async () => {
    if (!habitacion) return;
    
    setShowRoomHistoryModal(true);
    setLoadingRoomHistory(true);
    try {
      const data = await api.getHabitacionHistorial(habitacion.id);
      setRoomHistoryData(data);
    } catch (err) {
      console.error("Error buscando historial de habitación:", err);
    } finally {
      setLoadingRoomHistory(false);
    }
  };

  const handleFetchAccessHistory = async () => {
    const cedulaActual = huespedes[activePersona].cedula;
    const tipo = huespedes[activePersona].tipo_cedula;
    if (!cedulaActual) {
      notifications.show({ title: 'Atención', message: 'Debe ingresar una cédula para ver el historial de acceso', color: 'yellow' });
      return;
    }
    
    setShowAccessHistoryModal(true);
    setLoadingAccessHistory(true);
    try {
      const data = await api.getAccesoHistorialCliente(`${tipo}${cedulaActual}`);
      setAccessHistoryData(data);
    } catch (err) {
      console.error("Error buscando historial de acceso:", err);
    } finally {
      setLoadingAccessHistory(false);
    }
  };

  // Generar columnas de forma dinámica según los métodos de pago presentes en los datos
  const paymentMethodsFull = metodosPagoDisponibles;
  const paymentMethodsKeys = Array.from(new Set(historialData.flatMap(h => Object.keys(h.pagos || {}))));
  
  const historialColumns = [
    { key: 'fecha_entrada', label: 'Entrada', render: (val: string) => new Date(val).toLocaleString('es-VE', { day: '2-digit', month: '2-digit', year: 'numeric', hour: '2-digit', minute: '2-digit', hour12: false }) },
    { key: 'fecha_salida', label: 'Salida', render: (val: string) => val ? new Date(val).toLocaleString('es-VE', { day: '2-digit', month: '2-digit', year: 'numeric', hour: '2-digit', minute: '2-digit', hour12: false }) : <Badge variant="dot" color="green">Activa</Badge> },
    { key: 'habitacion', label: 'Hab.', render: (val: string) => <Badge variant="outline" color="gray">H-{val}</Badge> },
    { key: 'tipo_estadia', label: 'Tipo', render: (val: string) => {
      const isHospedaje = val.toLowerCase() === 'hospedaje';
      return (
        <Badge 
          variant="filled" 
          fw={700}
          styles={{ 
            root: { 
              textTransform: 'uppercase',
              background: isHospedaje 
                ? 'linear-gradient(135deg, rgb(189, 195, 199) 0%, rgb(36, 54, 70) 100%)'
                : 'linear-gradient(135deg, rgb(180, 20, 20) 0%, rgb(60, 0, 0) 100%)',
              border: 'none'
            } 
          }}
        >
          {val}
        </Badge>
      );
    }},
    ...paymentMethodsKeys.map(method => ({
      key: `pagos.${method}`,
      label: method,
      render: (val: any) => {
        if (!val) return <Text c="dimmed" size="xs">-</Text>;
        const color = metodosPagoDisponibles.find(m => m.nombre === method)?.color || 'transparent';
        return (
          <Badge 
            variant="filled" 
            styles={{ root: { backgroundColor: color, color: '#000', fontWeight: 700 } }}
          >
            ${Number(val).toFixed(2)}
          </Badge>
        );
      }
    })),
    { key: 'procedencia', label: 'Procedencia' },
    { key: 'destino', label: 'Destino' },
  ];

  const roomPaymentMethods = Array.from(new Set(roomHistoryData.flatMap(h => Object.keys(h.pagos || {}))));
  const roomHistoryColumns = [
    { key: 'fecha_entrada', label: 'Entrada', render: (val: string) => new Date(val).toLocaleString('es-VE', { day: '2-digit', month: '2-digit', year: 'numeric', hour: '2-digit', minute: '2-digit', hour12: false }) },
    { key: 'fecha_salida', label: 'Salida', render: (val: string) => val ? new Date(val).toLocaleString('es-VE', { day: '2-digit', month: '2-digit', year: 'numeric', hour: '2-digit', minute: '2-digit', hour12: false }) : <Badge variant="dot" color="green">Activa</Badge> },
    { key: 'cliente', label: 'Cliente', render: (val: string) => <Text fw={500} size="sm">{val}</Text> },
    { key: 'tipo_estadia', label: 'Tipo', render: (val: string) => {
      const isHospedaje = val?.toLowerCase() === 'hospedaje';
      return (
        <Badge 
          variant="filled" 
          fw={700}
          styles={{ 
            root: { 
              textTransform: 'uppercase',
              background: isHospedaje 
                ? 'linear-gradient(135deg, rgb(189, 195, 199) 0%, rgb(36, 54, 70) 100%)'
                : 'linear-gradient(135deg, rgb(180, 20, 20) 0%, rgb(60, 0, 0) 100%)',
              border: 'none'
            } 
          }}
        >
          {val}
        </Badge>
      );
    }},
    ...Array.from(new Set(roomHistoryData.flatMap(h => Object.keys(h.pagos || {})))).map(method => ({
      key: `pagos.${method}`,
      label: method,
      render: (val: any) => {
        if (!val) return <Text c="dimmed" size="xs">-</Text>;
        const color = metodosPagoDisponibles.find(m => m.nombre === method)?.color || 'transparent';
        return (
          <Badge 
            variant="filled" 
            styles={{ root: { backgroundColor: color, color: '#000', fontWeight: 700 } }}
          >
            ${Number(val).toFixed(2)}
          </Badge>
        );
      }
    })),
    { key: 'observaciones', label: 'Observaciones', render: (val: string) => <Text size="xs" truncate="end" maw={200}>{val || '-'}</Text> },
  ];

  const accessHistoryColumns = [
    { key: 'timestamp', label: 'Fecha/Hora', render: (val: string) => new Date(val).toLocaleString('es-VE', { day: '2-digit', month: '2-digit', year: 'numeric', hour: '2-digit', minute: '2-digit', hour12: false }) },
    { key: 'tipo', label: 'Operación', render: (val: string) => (
      <Badge color={val === 'entrada' ? 'teal' : 'orange'} variant="filled" style={{ textTransform: 'uppercase' }}>
        {val}
      </Badge>
    )},
    { key: 'nombre', label: 'Persona' },
    { key: 'cedula', label: 'Cédula' },
  ];

  // Fetch habitaciones libres cuando se abre el modal de cambio o bloqueo
  useEffect(() => {
    if (showCambiarHabitacionModal || (showBloquearModal && (habitacion?.estado_actual !== 'Libre' && habitacion?.estado_actual !== 'Bloqueada'))) {
      api.getHabitaciones()
        .then(data => {
          const libres = data.filter((h: any) => h.estado_actual === 'Libre' && h.id !== habitacion?.id);
          setHabitacionesLibres(libres.map((h: any) => ({ value: h.id.toString(), label: `Hab. ${h.numero} (${h.tipo})` })));
        })
        .catch(console.error);
    }
  }, [showCambiarHabitacionModal, showBloquearModal, habitacion?.id]);

  const handleCambioHabitacion = async () => {
    if (!nuevaHabitacionId || !cambioMotivo.trim() || !habitacion) return;
    setLoadingCambio(true);
    try {
      await api.cambiarHabitacion(habitacion.id, {
        nueva_habitacion_id: parseInt(nuevaHabitacionId),
        motivo: cambioMotivo
      });
      notifications.show({ title: 'Éxito', message: '¡Cambio realizado con éxito!', color: 'green', icon: <IconCheck /> });
      if (onSuccess) onSuccess();
      else window.location.reload();
      onClose();
      setShowCambiarHabitacionModal(false);
    } catch (err: any) {
      notifications.show({ title: 'Error', message: err.message || 'Ocurrió un problema.', color: 'red', icon: <IconX /> });
    } finally {
      setLoadingCambio(false);
    }
  };

  // Fetch Configuración
  useEffect(() => {
    if (opened) {
      // Cargar horas parcial
      api.getConfig('horas_parcial')
        .then(data => setHorasParcialConfig(parseInt(data.valor) || 6))
        .catch(console.error);

      // Cargar métodos de pago
      api.getMetodosPago()
        .then(data => {
          const activos = data.filter((m: any) => m.activo);
          setMetodosPagoDisponibles(activos);
          // Si no hay pagos, inicializar con el primero disponible
          if (pagos.length === 1 && pagos[0].monto === 0 && activos.length > 0) {
            setPagos([{ id: Date.now(), metodo: activos[0].nombre, monto: 0, referencia: '' }]);
          }
        })
        .catch(console.error);

      // Cargar camareras presentes
      api.getCamarerasPresentes()
        .then(data => {
            setCamareras(data.map((u: any) => ({ value: u.id.toString(), label: u.nombre })));
        })
        .catch(console.error);
    }
  }, [opened]);

  // Estado de Pagos

  const addPago = () => {
    const defaultMetodo = metodosPagoDisponibles.length > 0 ? metodosPagoDisponibles[0].nombre : 'Efectivo Dolar';
    setPagos([...pagos, { id: Date.now(), metodo: defaultMetodo, monto: 0, referencia: '' }]);
  };

  const removePago = (idToRemove: number) => {
    if (pagos.length > 1) {
      setPagos(pagos.filter(p => p.id !== idToRemove));
    }
  };

  const updatePago = (id: number, field: string, value: any) => {
    setPagos(pagos.map(p => p.id === id ? { ...p, [field]: value } : p));
  };

  // Estado de Extras
  const addExtra = () => setExtras([...extras, { id: Date.now(), descripcion: 'Lencería', monto: 0 }]);
  const removeExtra = (idToRemove: number) => setExtras(extras.filter(e => e.id !== idToRemove));
  const updateExtra = (id: number, field: string, value: any) => {
    setExtras(extras.map(e => e.id === id ? { ...e, [field]: value } : e));
  };

  // Lógica Matemática
  const TASA = bcv;
  const totalExtras = extras.reduce((sum, e) => sum + (Number(e.monto) || 0), 0);
  
  let montoDescuento = 0;
  if (appliedVoucher) {
    if (appliedVoucher.tipo === 'porcentaje') {
      // Aplicado solo al costo de la habitación
      montoDescuento = costoDolar * (appliedVoucher.valor / 100);
    } else {
      // Aplicado solo hasta el tope del costo de la habitación
      montoDescuento = Math.min(costoDolar, appliedVoucher.valor);
    }
  }

  const subtotalConDescuento = Math.max(0, costoDolar - montoDescuento);
  const costoTotalDolares = subtotalConDescuento + totalExtras;

  const totalPagadoDolares = pagos.reduce((sum, p) => {
    const metodoData = metodosPagoDisponibles.find(m => m.nombre === p.metodo);
    const esDivisa = metodoData ? metodoData.moneda === 'USD' : ['Efectivo Dolar', 'Zelle'].includes(p.metodo);
    const monto = Number(p.monto) || 0;
    return sum + (esDivisa ? monto : monto / TASA);
  }, 0);
  const restanteDolares = Math.max(0, costoTotalDolares - totalPagadoDolares);

  // Lógica de Envío

  const resetForm = () => {
    setActivePersona('P1');
    const cap = habitacion?.capacidad || 2;
    const defaultHuespedes: Record<string, any> = {};
    for (let i = 1; i <= cap; i++) {
        defaultHuespedes[`P${i}`] = { 
          cedula: '', nombre: '', fecha_nacimiento: null, nacionalidad: 'Venezolano', 
          profesion: 'Comerciante', telefono: '', observaciones: '', tipo_cedula: 'V-', 
          codigo_telefono: '+58', reputacion: 'positivo', visitas: 0, estado: 'ausente',
          estado_civil: 'Soltero'
        };
    }
    setHuespedes(defaultHuespedes);
    huespedesRef.current = defaultHuespedes;
    setTipoEstadia('hospedaje');
    setDias(1);
    const defaultMetodo = metodosPagoDisponibles.length > 0 ? metodosPagoDisponibles[0].nombre : 'Efectivo Dolar';
    setPagos([{ id: Date.now(), metodo: defaultMetodo, monto: 0, referencia: '' }]);
    setExtras([]);
    setVoucher('');
    setAppliedVoucher(null);
    setObservacionesTransaccion('');
    setProcedencia('Lara');
    setDestino('Lara');
    setFechaEntrada(new Date());
    setErrorSearch(false);
  };

  const cargarEstancia = (data: any) => {
    const cap = habitacion?.capacidad || 2;
    const defaultHuespedes: Record<string, any> = {};
    for (let i = 1; i <= cap; i++) {
        defaultHuespedes[`P${i}`] = { 
          cedula: '', nombre: '', fecha_nacimiento: null, nacionalidad: 'Venezolano', 
          profesion: 'Comerciante', telefono: '', observaciones: '', tipo_cedula: 'V-', 
          codigo_telefono: '+58', estado_civil: 'Soltero'
        };
    }
    
    setHuespedes(prev => {
      const updated: Record<string, any> = { ...defaultHuespedes }; // Resetear todos antes del map
      if(data.huespedes) {
        data.huespedes.forEach((h: any, index: number) => {
          const key = `P${index + 1}`;
          let birthDate = null;
          if (h.fecha_nacimiento) {
            const dtPart = typeof h.fecha_nacimiento === 'string' ? h.fecha_nacimiento.split('T')[0] : '';
            const parts = dtPart.split('-');
            if (parts.length === 3) {
              birthDate = new Date(Number(parts[0]), Number(parts[1]) - 1, Number(parts[2]));
            } else {
              birthDate = new Date(h.fecha_nacimiento);
            }
            if (isNaN(birthDate.getTime())) birthDate = null;
          }

          updated[key] = {
            cedula: h.cedula || '',
            nombre: h.nombre || '',
            fecha_nacimiento: birthDate,
            nacionalidad: h.nacionalidad || 'Venezolano',
            profesion: h.profesion || 'Comerciante',
            telefono: h.telefono || '',
            observaciones: h.observaciones || '',
            tipo_cedula: h.tipo_cedula || 'V-',
            codigo_telefono: h.codigo_telefono || '+58',
            reputacion: h.reputacion || 'positivo',
            visitas: h.visitas || 0,
            estado: h.estado || 'ausente',
            estado_civil: h.estado_civil || 'Soltero'
          };
        });
      }
      huespedesRef.current = updated;
      return updated;
    });
    
    setActivePersona('P1');
    setTipoEstadia(data.tipo_estadia);
    setProcedencia(data.procedencia || 'Lara');
    setDestino(data.destino || 'Lara');
    setObservacionesTransaccion(data.observaciones || '');
    setVoucher(data.voucher_codigo || '');
    if (data.voucher_codigo) {
      // Intentar cargar detalles del voucher si existe
      api.getVoucher(data.voucher_codigo)
        .then(vData => {
           if (vData.codigo) setAppliedVoucher(vData);
        })
        .catch(e => console.error("Error cargando voucher previo:", e));
    } else {
      setAppliedVoucher(null);
    }
    setFechaEntrada(new Date(data.fecha_entrada));
    if (data.fecha_salida_planificada) {
      setFechaSalidaCalculada(new Date(data.fecha_salida_planificada));
    }

    if (data.pagos) setPagos(data.pagos.map((p: any) => ({ ...p, id: Math.random() })));
    if (data.extras) setExtras(data.extras.map((e: any) => ({ ...e, id: Math.random() })));
    setErrorSearch(false);
  };

  useEffect(() => {
    if (opened && habitacion) {
      if (habitacion.estado_actual !== 'Libre' && initialData) {
        cargarEstancia(initialData);
      } else {
        resetForm();
      }
    }
  }, [opened, habitacion?.id, initialData]);

  const handleUpdateStay = async () => {
    if (!habitacion || habitacion.estado_actual === 'Libre') return;
    
    try {
      const huespedesActivos = Object.values(huespedesRef.current)
        .filter(h => h.cedula && h.cedula.trim() !== '')
        .map(h => {
          let birthStr = null;
          if (h.fecha_nacimiento) {
            const d = new Date(h.fecha_nacimiento);
            if (!isNaN(d.getTime())) {
              if (d.getUTCHours() === 0 && d.getUTCMinutes() === 0) {
                 birthStr = d.toISOString().split('T')[0];
              } else {
                 const yyyy = d.getFullYear();
                 const mm = String(d.getMonth() + 1).padStart(2, '0');
                 const dd = String(d.getDate()).padStart(2, '0');
                 birthStr = `${yyyy}-${mm}-${dd}`;
              }
            }
          }
          const cleanField = (val: string, prefix: string) => {
            if (!val) return "";
            let v = val.trim();
            while (prefix && v.startsWith(prefix)) {
              v = v.slice(prefix.length);
            }
            return v;
          };

          return {
            ...h,
            cedula: `${h.tipo_cedula}${cleanField(h.cedula, h.tipo_cedula)}`,
            telefono: `${h.codigo_telefono}${cleanField(h.telefono, h.codigo_telefono)}`,
            fecha_nacimiento: birthStr
          };
        });

      const payload = {
        huespedes: huespedesActivos,
        tipo_estadia: (tipoEstadia || 'hospedaje').toLowerCase(),
        fecha_entrada: fechaEntrada instanceof Date && !isNaN(fechaEntrada.getTime()) ? fechaEntrada.toISOString() : new Date().toISOString(),
        fecha_salida_planificada: fechaSalidaCalculada instanceof Date && !isNaN(fechaSalidaCalculada.getTime()) ? fechaSalidaCalculada.toISOString() : new Date().toISOString(),
        pagos: pagos.map(p => ({ metodo: p.metodo, monto: Number(p.monto) || 0, referencia: p.referencia || '' })),
        extras: extras.map(e => ({ descripcion: e.descripcion, monto: Number(e.monto) || 0 })),
        procedencia: procedencia || 'Lara',
        destino: destino || 'Lara',
        observaciones_transaccion: observacionesTransaccion || '',
        codigo_descuento: voucher || null
      };

      await api.updateEstancia(habitacion.id, payload);
      // No alertamos en el guardado automático para no molestar al cerrar
    } catch (err) {
      console.error("Error al actualizar estancia:", err);
    }
  };

  const handleClose = async () => {
    if (habitacion && habitacion.estado_actual !== 'Libre') {
      await handleUpdateStay();
    }
    onClose();
  };

  const handleSearchClient = async () => {
    const cedulaActual = huespedes[activePersona].cedula;
    const tipo = huespedes[activePersona].tipo_cedula;
    if (!cedulaActual) return;

    try {
      const data = await api.getCliente(`${tipo}${cedulaActual}`);
        
      // Convertir la fecha de string a objeto Date si existe sin problemas de timezone
      let birthDate = null;
      if (data.fecha_nacimiento) {
        const dtPart = typeof data.fecha_nacimiento === 'string' ? data.fecha_nacimiento.split('T')[0] : '';
        const parts = dtPart.split('-');
        if (parts.length === 3) {
          birthDate = new Date(Number(parts[0]), Number(parts[1]) - 1, Number(parts[2]));
        } else {
          birthDate = new Date(data.fecha_nacimiento);
        }
        if (isNaN(birthDate.getTime())) birthDate = null;
      }

      setHuespedes(prev => {
        const next = {
          ...prev,
          [activePersona]: { 
            ...prev[activePersona], 
            cedula: data.cedula,
            tipo_cedula: data.tipo_cedula,
            nombre: data.nombre,
            fecha_nacimiento: birthDate,
            nacionalidad: data.nacionalidad,
            telefono: data.telefono || '',
            codigo_telefono: data.codigo_telefono || '+58',
            profesion: data.profesion || 'Comerciante',
            observaciones: data.observaciones || '',
            reputacion: data.reputacion || 'positivo',
            visitas: data.visitas || 0,
            estado: data.estado || 'ausente',
            estado_civil: data.estado_civil || 'Soltero'
          }
        };
        huespedesRef.current = next;

        // Si el cliente tiene dirección, la usamos como procedencia por defecto
        if (data.direccion) setProcedencia(data.direccion);
        
        if (data.reputacion === 'negativo') {
          setShowReputacionModal(true);
        }
        
        return next;
      });

      // Buscar datos pasados (pago, procedencia, destino)
      try {
        const dataExtra = await api.getClienteDatosPasados(`${tipo}${cedulaActual}`);
        
        // 1. Método de Pago (si es el primer pago con monto 0)
        if (dataExtra.metodo) {
          setPagos(prevPagos => {
            if (prevPagos.length === 1 && Number(prevPagos[0].monto) === 0) {
              return [{ ...prevPagos[0], metodo: dataExtra.metodo }];
            }
            return prevPagos;
          });
        }

        // 2. Procedencia y Destino
        if (dataExtra.procedencia) setProcedencia(dataExtra.procedencia);
        if (dataExtra.destino) setDestino(dataExtra.destino);
      } catch (err) {
        console.error("Error al obtener datos pasados:", err);
      }
    } catch (err: any) {
      console.error("Error buscando cliente:", err);
      setErrorSearch(true);
      inputNombreRef.current?.focus();
    }
  };

  const executeIngresar = async () => {
    setLoading(true);
    try {
      const huespedesActivos = Object.values(huespedesRef.current)
        .filter(h => h.cedula && h.cedula.trim() !== '')
        .map(h => {
          let birthStr = null;
          if (h.fecha_nacimiento) {
            const d = new Date(h.fecha_nacimiento);
            if (!isNaN(d.getTime())) {
              if (d.getUTCHours() === 0 && d.getUTCMinutes() === 0) {
                 birthStr = d.toISOString().split('T')[0];
              } else {
                 const yyyy = d.getFullYear();
                 const mm = String(d.getMonth() + 1).padStart(2, '0');
                 const dd = String(d.getDate()).padStart(2, '0');
                 birthStr = `${yyyy}-${mm}-${dd}`;
              }
            }
          }
          const cleanField = (val: string, prefix: string) => {
            if (!val) return "";
            let v = val.trim();
            while (prefix && v.startsWith(prefix)) {
              v = v.slice(prefix.length);
            }
            return v;
          };

          return {
            ...h,
            cedula: `${h.tipo_cedula}${cleanField(h.cedula, h.tipo_cedula)}`,
            telefono: `${h.codigo_telefono}${cleanField(h.telefono, h.codigo_telefono)}`,
            fecha_nacimiento: birthStr
          };
        });
      
      const payload = {
        huespedes: huespedesActivos,
        tipo_estadia: (tipoEstadia || 'hospedaje').toLowerCase(),
        fecha_entrada: fechaEntrada instanceof Date && !isNaN(fechaEntrada.getTime()) ? fechaEntrada.toISOString() : new Date().toISOString(),
        fecha_salida_planificada: fechaSalidaCalculada instanceof Date && !isNaN(fechaSalidaCalculada.getTime()) ? fechaSalidaCalculada.toISOString() : new Date().toISOString(),
        pagos: pagos.map(p => ({ metodo: p.metodo, monto: Number(p.monto) || 0, referencia: p.referencia || '' })),
        extras: extras.map(e => ({ descripcion: e.descripcion, monto: Number(e.monto) || 0 })),
        procedencia: procedencia || 'Lara',
        destino: destino || 'Lara',
        observaciones_transaccion: observacionesTransaccion || '',
        codigo_descuento: voucher || null,
        usuario_id: currentUser?.id
      };

      await api.ingresarCliente(habitacion!.id, payload);
      notifications.show({
        title: 'Éxito',
        message: '¡Ingreso registrado con éxito!',
        color: 'green',
        icon: <IconCheck />
      });
      if (onSuccess) {
        onSuccess();
      } else {
        window.location.reload(); 
      }
      onClose();
    } catch (err: any) {
      console.error("Error de red/ejecución:", err);
      notifications.show({
        title: 'Error',
        message: err.message || 'Ocurrió un problema en el servidor',
        color: 'red',
        icon: <IconX />
      });
    } finally {
      setLoading(false);
      setShowWarningModal(false);
    }
  };

  const handleIngresar = () => {
    if (!habitacion || !tipoEstadia) {
      notifications.show({
        title: 'Atención',
        message: 'Por favor complete los datos básicos de la habitación.',
        color: 'yellow'
      });
      return;
    }

    const p1 = huespedes['P1'];
    
    // Validaciones de datos del cliente obligatorios (Teléfono es opcional)
    if (!p1.cedula || !p1.nombre || !p1.fecha_nacimiento || !p1.nacionalidad || !p1.profesion || !procedencia || !destino) {
      notifications.show({
        title: 'Datos Incompletos',
        message: 'Todos los campos del cliente principal (P1) (excepto teléfono y observaciones), incluyendo procedencia y destino, deben ser llenados.',
        color: 'yellow'
      });
      return;
    }

    if (!p1.tipo_cedula || !p1.codigo_telefono) {
      notifications.show({
        title: 'Datos Incompletos',
        message: 'Debe seleccionar el tipo de documento y el código de teléfono.',
        color: 'yellow'
      });
      return;
    }

    // Validación de edad
    const age = calculateAge(p1.fecha_nacimiento);
    if (age === null || age < 18 || age > 100) {
      notifications.show({
        title: 'Edad Incoherente',
        message: `El cliente debe ser mayor de 18 años y menor de 100 (Edad calculada: ${age ?? '?'}).`,
        color: 'red'
      });
      return;
    }

    // Validación de teléfono (solo si se ingresó algo)
    if (p1.telefono && p1.telefono.trim() !== '') {
      const phoneNumbersOnly = p1.telefono.replace(/\D/g, '');
      if (phoneNumbersOnly.length < 7 || phoneNumbersOnly.length > 15) {
        notifications.show({
          title: 'Teléfono Incoherente',
          message: 'Por favor verifique el número de teléfono (debe tener entre 7 y 15 dígitos).',
          color: 'red'
        });
        return;
      }
    }

    if (restanteDolares > 0.01) {
      setShowWarningModal(true);
    } else {
      executeIngresar();
    }
  };

  const handleLiberar = async () => {
    if (!habitacion) return;

    // Validación de presencia para egreso
    if (huespedes['P1'].estado === 'ausente') {
      notifications.show({
        title: 'Egreso Denegado',
        message: 'El cliente principal (P1) no se encuentra PRESENTE en el hotel. No puede realizar el egreso si el cliente no está presente.',
        color: 'red',
        icon: <IconX />
      });
      return;
    }

    setLoading(true);
    try {
      await api.liberarHabitacion(habitacion.id);
      notifications.show({
        title: 'Éxito',
        message: '¡Habitación liberada correctamente!',
        color: 'green',
        icon: <IconCheck />
      });
      if (onSuccess) onSuccess();
      else window.location.reload();
      onClose();
    } catch (err: any) {
      notifications.show({
        title: 'Error',
        message: err.message || 'Ocurrió un problema',
        color: 'red',
        icon: <IconX />
      });
    } finally {
      setLoading(false);
    }
  };

  const handlePasarAHospedaje = async () => {
    if (!habitacion) return;
    setLoading(true);
    try {
      await api.pasarAHospedaje(habitacion.id);
      notifications.show({
        title: 'Éxito',
        message: '¡Convertido a hospedaje correctamente!',
        color: 'grape',
        icon: <IconCheck />
      });
      if (onSuccess) onSuccess();
      else window.location.reload();
      onClose();
    } catch (err: any) {
      notifications.show({
        title: 'Error',
        message: err.message || 'Ocurrió un problema',
        color: 'red',
        icon: <IconX />
      });
    } finally {
      setLoading(false);
    }
  };

  const handleRetoque = async () => {
    if (!camareraId || !habitacion) return;
    setLoadingRetoque(true);
    try {
      await api.setRetoque(habitacion.id, parseInt(camareraId));
      notifications.show({ title: 'Éxito', message: 'La habitación ahora está en RETOQUE', color: 'grape', icon: <IconClock /> });
      if (onSuccess) onSuccess();
      onClose();
      setShowRetoqueModal(false);
    } catch (err: any) {
      notifications.show({
        title: 'Error',
        message: err.message || 'Error al poner en retoque.',
        color: 'red'
      });
    } finally {
      setLoadingRetoque(false);
    }
  };

  const handleFinalizarRetoque = async () => {
    if (!habitacion) return;
    setLoading(true);
    try {
      await api.finalizarRetoque(habitacion.id);
      notifications.show({ title: 'Éxito', message: 'Retoque finalizado correctamente', color: 'green', icon: <IconCheck /> });
      if (onSuccess) onSuccess();
      onClose();
    } catch (err: any) {
      notifications.show({
        title: 'Error',
        message: err.message || 'Error al finalizar retoque.',
        color: 'red'
      });
    } finally {
      setLoading(false);
    }
  };


  useEffect(() => {
    // Si la fecha de entrada es mayor a "ahora + 10 min", es una reserva
    const ahora = dayjs();
    const diff = dayjs(fechaEntrada).diff(ahora, 'minute');
    setEsReserva(diff > 10);
  }, [fechaEntrada]);

  // Sincronizar Costo con Días de Hospedaje
  useEffect(() => {
    if (tipoEstadia?.toLowerCase() === 'hospedaje' && habitacion) {
      setCostoDolar((habitacion.precio_hospedaje || 40) * dias);
    } else if (tipoEstadia?.toLowerCase() === 'parcial' && habitacion) {
      setCostoDolar(habitacion.precio_parcial || 20);
    }
  }, [tipoEstadia, dias, habitacion]);

  useEffect(() => {
    if (!tipoEstadia) return;

    const d = new Date(fechaEntrada);

    if (tipoEstadia.toLowerCase() === 'parcial') {
      d.setHours(d.getHours() + horasParcialConfig);
    } else {
      if (d.getHours() >= 9) {
        d.setDate(d.getDate() + 1);
      }
      d.setHours(13, 0, 0, 0);

      if (dias > 1) {
        d.setDate(d.getDate() + (dias - 1));
      }
    }
    
    setFechaSalidaCalculada(d);
  }, [tipoEstadia, dias, fechaEntrada]);

  if (!habitacion) return null;

  const currentHuesped = huespedes[activePersona];

  // Renderizados modulares para reciclarlos en Desktop y Mobile
  const renderColumnaCliente = () => (
    <Paper bg="#1e1e1e" p="sm" radius="md" style={{ border: '1px solid #2a2a2a', height: '720px', display: 'flex', flexDirection: 'column' }}>
      <Stack gap={5} style={{ flex: 1 }}>
        <Group justify="flex-end" align="center" mb={2}>
          <Group gap={4} style={{ flexWrap: 'nowrap' }}>
            {Array.from({ length: habitacion?.capacidad || 1 }, (_, i) => `P${i + 1}`).map((p) => (
              <Button 
                key={p} size="xs" variant={activePersona === p ? 'filled' : 'light'} 
                style={{ 
                  background: activePersona === p ? ACCENT_GRADIENT : undefined, 
                  color: activePersona === p ? 'white' : 'gray',
                  border: 'none'
                }}
                onClick={() => setActivePersona(p)} px="xs"
              >
                {p}
              </Button>
            ))}
          </Group>
        </Group>

        <Divider color="#2a2a2a" my={2} />

        <Group wrap="nowrap" align="center" gap={8}>
          <Text size="13px" c="white" fw={500} w="30%" tt="uppercase" style={{ fontFamily: ROBOTO_FONT }}>Cédula</Text>
          <Group 
            gap={0} 
            flex={1} 
            style={{ 
              transition: 'all 0.3s ease',
              borderRadius: '6px',
              border: errorSearch ? '1.5px solid #ff6b6b' : '1px solid transparent',
              animation: errorSearch ? 'shake 0.8s cubic-bezier(.36,.07,.19,.97) both' : 'none',
              overflow: 'hidden',
              backgroundColor: errorSearch ? '#fff5f5' : '#ffffff'
            }}
          >
            <Select 
              value={currentHuesped.tipo_cedula}
              onChange={(v) => updateHuesped('tipo_cedula', v)}
              allowDeselect={false}
              data={['V-', 'E-', 'J-', 'G-', 'P-']} 
              w={75}
              styles={{ 
                input: { 
                  backgroundColor: 'transparent', color: 'black', height: '34px', minHeight: '34px', borderTopRightRadius: 0, borderBottomRightRadius: 0,
                  border: 'none', fontSize: '13px', fontFamily: ROBOTO_FONT
                } 
              }}
            />
            <TextInput 
              value={currentHuesped.cedula}
              onChange={(e) => updateHuesped('cedula', e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleSearchClient()}
              placeholder="12345678" 
              rightSection={<ActionIcon color="gray.7" variant="subtle" onClick={handleSearchClient} size="sm"><IconSearch size={16} /></ActionIcon>} 
              styles={{ 
                input: { 
                  backgroundColor: 'transparent', color: 'black', height: '34px', minHeight: '34px', borderTopLeftRadius: 0, borderBottomLeftRadius: 0,
                  border: 'none',
                  borderLeft: '1px solid rgba(0,0,0,0.05)',
                  fontSize: '14px', fontFamily: ROBOTO_FONT
                } 
              }} 
              flex={1} 
            />
          </Group>
        </Group>

        <Group wrap="nowrap" align="center" gap={8}>
          <Text size="13px" c="white" fw={500} w="30%" tt="uppercase" style={{ fontFamily: ROBOTO_FONT }}>Nombre</Text>
          <TextInput 
            ref={inputNombreRef}
            value={currentHuesped.nombre}
            onChange={(e) => updateHuesped('nombre', e.target.value)}
            placeholder="Nombre Apellido..." 
            styles={{ input: { backgroundColor: '#ffffff', color: 'black', height: '34px', minHeight: '34px', fontSize: '14px', fontFamily: ROBOTO_FONT } }} flex={1} 
          />
        </Group>

        <Group wrap="nowrap" align="center" gap={8}>
          <Text size="13px" c="white" fw={500} w="30%" tt="uppercase" style={{ fontFamily: ROBOTO_FONT }}>Nacimiento</Text>
          <Box flex={1} pos="relative">
            <TextInput 
              value={dobText}
              onChange={(e) => onDobTextChange(e.target.value)}
              placeholder="DD-MM-YYYY" 
              styles={{ input: { backgroundColor: '#ffffff', color: 'black', height: '34px', minHeight: '34px', fontSize: '14px', fontFamily: ROBOTO_FONT, paddingRight: '45px' } }} 
              w="100%"
            />
            <Popover opened={dobPopoverOpened} onChange={setDobPopoverOpened} position="bottom" withArrow shadow="none">
              <Popover.Target>
                <Badge 
                  variant="light" 
                  color={currentHuesped.fecha_nacimiento ? "gray.9" : "gray.5"}
                  size="sm" 
                  style={{ 
                    position: 'absolute', 
                    right: '8px', 
                    top: '50%', 
                    transform: 'translateY(-50%)',
                    cursor: 'pointer',
                    userSelect: 'none'
                  }}
                  onClick={() => setDobPopoverOpened(o => !o)}
                >
                  {currentHuesped.fecha_nacimiento ? `${calculateAge(currentHuesped.fecha_nacimiento)} años` : '???'}
                </Badge>
              </Popover.Target>
              <Popover.Dropdown p={0}>
                <DatePicker 
                  value={currentHuesped.fecha_nacimiento}
                  onChange={(v) => {
                    updateHuesped('fecha_nacimiento', v);
                    setDobPopoverOpened(false);
                  }}
                />
              </Popover.Dropdown>
            </Popover>
          </Box>
        </Group>

        <Group wrap="nowrap" align="center" gap={8}>
          <Text size="13px" c="white" fw={500} w="30%" tt="uppercase" style={{ fontFamily: ROBOTO_FONT }}>Nacion.</Text>
          <Select 
            value={currentHuesped.nacionalidad}
            onChange={(v) => updateHuesped('nacionalidad', v)}
            allowDeselect={false}
            data={['Venezolano', 'Extranjero']} 
            styles={{ input: { backgroundColor: '#ffffff', color: 'black', height: '34px', minHeight: '34px', fontSize: '14px', fontFamily: ROBOTO_FONT } }} flex={1} 
          />
        </Group>

        <Group wrap="nowrap" align="center" gap={8}>
          <Text size="13px" c="white" fw={500} w="30%" tt="uppercase" style={{ fontFamily: ROBOTO_FONT }}>Profesión</Text>
          <Select 
            value={currentHuesped.profesion}
            onChange={(v) => updateHuesped('profesion', v)}
            allowDeselect={false}
            data={['Comerciante', 'Empleado', 'Estudiante']} 
            styles={{ input: { backgroundColor: '#ffffff', color: 'black', height: '34px', minHeight: '34px', fontSize: '14px', fontFamily: ROBOTO_FONT } }} flex={1} 
          />
        </Group>

        <Group wrap="nowrap" align="center" gap={8}>
          <Text size="13px" c="white" fw={500} w="30%" tt="uppercase" style={{ fontFamily: ROBOTO_FONT }}>E. Civil</Text>
          <Select 
            value={currentHuesped.estado_civil}
            onChange={(v) => updateHuesped('estado_civil', v)}
            allowDeselect={false}
            data={['Soltero', 'Casado', 'Divorciado', 'Viudo', 'Concubino']} 
            styles={{ input: { backgroundColor: '#ffffff', color: 'black', height: '34px', minHeight: '34px', fontSize: '14px', fontFamily: ROBOTO_FONT } }} flex={1} 
          />
        </Group>


        <Group wrap="nowrap" align="center" gap={8}>
          <Text size={LABEL_SIZE} c="white" fw={500} w="30%" tt="uppercase" style={{ fontFamily: ROBOTO_FONT }}>Teléfono</Text>
          <Group 
            gap={0} 
            flex={1}
            style={{ 
              borderRadius: '6px',
              overflow: 'hidden',
              backgroundColor: '#ffffff'
            }}
          >
            <Select 
              value={currentHuesped.codigo_telefono}
              onChange={(v) => updateHuesped('codigo_telefono', v)}
              allowDeselect={false}
              data={['+58', '+1', '+57', '+34', '+54']} 
              w={75}
              styles={{ 
                input: { 
                  backgroundColor: 'transparent', color: 'black', height: INPUT_HEIGHT, minHeight: INPUT_HEIGHT, fontSize: INPUT_SIZE, fontFamily: ROBOTO_FONT, 
                  border: 'none', borderTopRightRadius: 0, borderBottomRightRadius: 0 
                } 
              }}
            />
            <TextInput 
              value={currentHuesped.telefono}
              onChange={(e) => updateHuesped('telefono', e.target.value)}
              placeholder="0412..."
              styles={{ 
                input: { 
                  backgroundColor: 'transparent', color: 'black', height: INPUT_HEIGHT, minHeight: INPUT_HEIGHT, fontSize: INPUT_SIZE, fontFamily: ROBOTO_FONT, 
                  border: 'none', borderLeft: '1px solid rgba(0,0,0,0.05)', borderTopLeftRadius: 0, borderBottomLeftRadius: 0 
                } 
              }} 
              flex={1} 
            />
          </Group>
        </Group>

        <Textarea 
          value={currentHuesped.observaciones}
          onChange={(e) => updateHuesped('observaciones', e.target.value)}
          placeholder="Observaciones sobre el huésped..." 
          minRows={3} maxRows={4} autosize mt={2} 
          styles={{ input: { backgroundColor: '#ffffff', color: 'black', border: '1px solid #ccc', fontSize: '14px', fontFamily: ROBOTO_FONT } }} 
        />

        <Group grow gap={4} mt={2}>
          <Button 
            h={36} 
            fw={700}
            onClick={() => {
              const newRep = currentHuesped.reputacion === 'positivo' ? 'negativo' : 'positivo';
              updateHuesped('reputacion', newRep);
              const cedulaFull = `${currentHuesped.tipo_cedula}${currentHuesped.cedula}`;
              if (currentHuesped.cedula) {
                fetch(`http://192.168.0.123:8000/api/clientes/${cedulaFull}/reputacion`, {
                  method: 'PATCH',
                  headers: { 'Content-Type': 'application/json' },
                  body: JSON.stringify({ reputacion: newRep })
                }).catch(console.error);
              }
            }}
            style={{
              background: currentHuesped.reputacion === 'positivo' 
                ? ACCENT_GRADIENT 
                : 'linear-gradient(135deg, rgb(242, 5, 5) 0%, rgb(150, 2, 2) 100%)',
              color: 'white',
              border: 'none',
            }}
            leftSection={currentHuesped.reputacion === 'positivo' ? <IconCheck size={16} /> : <IconX size={16} />}
            styles={{ root: { textTransform: 'uppercase', fontSize: '11px', fontFamily: ROBOTO_FONT } }}
          >
            {currentHuesped.reputacion === 'positivo' ? "Positiva" : "Negativa"}
          </Button>

          <Button 
            h={36} 
            fw={700}
            color="dark"
            variant="filled"
            leftSection={<IconHistory size={16} />}
            styles={{ root: { textTransform: 'uppercase', fontSize: '11px', fontFamily: ROBOTO_FONT } }}
            onClick={handleFetchHistorial}
          >
            Vino {huespedes[activePersona].visitas || 0} veces
          </Button>
        </Group>

        <Divider color="#2a2a2a" my={1} />

        <Group wrap="nowrap" align="center" gap={8}>
          <Text size="13px" c="white" fw={500} w="30%" tt="uppercase" style={{ fontFamily: ROBOTO_FONT }}>Procedencia</Text>
          <Autocomplete 
            data={ESTADOS_VENEZUELA} 
            value={procedencia}
            onChange={setProcedencia}
            placeholder="Escriba o seleccione..."
            styles={{ input: { backgroundColor: '#ffffff', color: 'black', height: '34px', minHeight: '34px', fontSize: '14px', fontFamily: ROBOTO_FONT } }} 
            flex={1}
          />
        </Group>

        <Group wrap="nowrap" align="center" gap={8}>
          <Text size="13px" c="white" fw={500} w="30%" tt="uppercase" style={{ fontFamily: ROBOTO_FONT }}>Destino</Text>
          <Autocomplete 
            data={ESTADOS_VENEZUELA} 
            value={destino}
            onChange={setDestino}
            placeholder="Escriba o seleccione..."
            styles={{ input: { backgroundColor: '#ffffff', color: 'black', height: '34px', minHeight: '34px', fontSize: '14px', fontFamily: ROBOTO_FONT } }} 
            flex={1}
          />
        </Group>

        <Group wrap="nowrap" align="center" gap={8}>
          <Text size="13px" c="white" fw={500} w="30%" tt="uppercase" style={{ fontFamily: ROBOTO_FONT }}>Entrada</Text>
          <DateTimePicker 
            placeholder="Seleccione fecha y hora"
            value={fechaEntrada} 
            onChange={(v: any) => v && setFechaEntrada(new Date(v))}
            valueFormat="DD-MM-YYYY HH:mm"
            styles={{ input: { backgroundColor: '#ffffff', color: 'black', height: '34px', minHeight: '34px', fontSize: '14px', fontFamily: ROBOTO_FONT } }} 
            flex={1}
          />
        </Group>

        <Group wrap="nowrap" align="center" gap={8}>
          <Text size="13px" c="white" fw={500} w="30%" tt="uppercase" style={{ fontFamily: ROBOTO_FONT }}>Salida</Text>
          <DateTimePicker 
            placeholder="Cálculo automático"
            value={fechaSalidaCalculada} 
            onChange={(v: any) => setFechaSalidaCalculada(v ? new Date(v) : null)}
            valueFormat="DD-MM-YYYY HH:mm"
            readOnly
            styles={{ input: { backgroundColor: '#ffffff', color: 'black', height: '34px', minHeight: '34px', fontSize: '14px', fontFamily: ROBOTO_FONT } }} 
            flex={1}
          />
        </Group>

        <Group wrap="nowrap" align="center" gap={8}>
          <Text size="13px" c="white" fw={500} w="30%" tt="uppercase" style={{ fontFamily: ROBOTO_FONT }}>Días</Text>
          <NumberInput 
            value={tipoEstadia === 'parcial' ? 0 : dias}
            onChange={(v) => setDias(Number(v))}
            min={tipoEstadia === 'parcial' ? 0 : 1} 
            max={99}
            disabled={tipoEstadia === 'parcial' || habitacion?.estado_actual !== 'Libre'}
            styles={{ input: { backgroundColor: (tipoEstadia === 'parcial' || habitacion?.estado_actual !== 'Libre') ? '#f1f3f5' : '#ffffff', color: 'black', height: '34px', minHeight: '34px', fontSize: '14px', fontFamily: ROBOTO_FONT } }} 
            flex={1}
          />
        </Group>

        <Group grow mt="auto" pt="sm">
          <Button 
            disabled={habitacion?.estado_actual !== 'Libre'}
            onClick={() => { setTipoEstadia('parcial'); setDias(0); }} 
            style={{ opacity: habitacion?.estado_actual !== 'Libre' ? 0.7 : 1, background: 'linear-gradient(135deg, rgb(180, 20, 20) 0%, rgb(60, 0, 0) 100%)', color: 'white', border: tipoEstadia === 'parcial' ? '2px solid white' : 'none' }} 
            h={36} fw={500}
          >
            Parcial
          </Button>
          <Button 
            disabled={habitacion?.estado_actual !== 'Libre'}
            onClick={() => { setTipoEstadia('hospedaje'); setDias(1); }} 
            style={{ opacity: habitacion?.estado_actual !== 'Libre' ? 0.7 : 1, background: 'linear-gradient(135deg, rgb(189, 195, 199) 0%, rgb(36, 54, 70) 100%)', color: 'white', border: tipoEstadia === 'hospedaje' ? '2px solid white' : 'none' }} 
            h={36} fw={500}
          >
            Hospedaje
          </Button>
        </Group>
      </Stack>
    </Paper>
  );

  const renderColumnaPago = () => (
    <Paper bg="#1e1e1e" p="md" radius="md" style={{ border: '1px solid #2a2a2a', height: '720px', display: 'flex', flexDirection: 'column' }}>
      <Stack gap="xs" style={{ flex: 1 }}>
        <Box 
          p="sm" 
          style={{ 
            background: tipoEstadia === 'parcial' ? 'linear-gradient(135deg, rgb(180, 20, 20) 0%, rgb(60, 0, 0) 100%)' : tipoEstadia === 'hospedaje' ? 'linear-gradient(135deg, rgb(189, 195, 199) 0%, rgb(36, 54, 70) 100%)' : '#111', 
            borderRadius: '6px', 
            border: '1px solid #333', 
            textAlign: 'center',
            transition: 'all 0.3s ease',
            marginBottom: '4px'
          }}
        >
          <Text size="sm" fw={500} c={tipoEstadia ? 'rgba(255,255,255,0.8)' : 'dimmed'} tt="uppercase" mb={4} style={{ fontFamily: ROBOTO_FONT, fontSize: LABEL_SIZE }}>Estadia Tipo: {tipoEstadia || '???'}</Text>
          <Title order={1} c="white" style={{ fontSize: '2.5rem', lineHeight: 1, fontWeight: 500 }}>{costoTotalDolares.toFixed(2)}$</Title>
          <Text size="lg" c={tipoEstadia ? 'rgba(255,255,255,0.9)' : '#b3b3b3'} fw={500} mt={4}>{(costoTotalDolares * TASA).toFixed(2)} Bs</Text>
        </Box>

        <Group justify="space-between" align="center">
          <Text size={LABEL_SIZE} c="white" fw={500} tt="uppercase" style={{ fontFamily: ROBOTO_FONT }}>Métodos de Pago</Text>
          <ActionIcon color="#38ef7d" variant="light" onClick={addPago}><IconPlus size={16} /></ActionIcon>
        </Group>

        <Divider color="#2a2a2a" my={1} />

        <ScrollArea h={180} scrollbarSize={4}>
          <Stack gap="xs">
            {pagos.map((pago) => {
              const metodoData = metodosPagoDisponibles.find(m => m.nombre === pago.metodo);
              const colorBorde = metodoData?.color || '#ccc';
              
              return (
                <Group key={pago.id} gap="xs" wrap="nowrap" align="flex-end">
                  <Select 
                    data={metodosPagoDisponibles.length > 0 ? metodosPagoDisponibles.map(m => m.nombre) : ['Dolar', 'Bancaribe', 'Bancamiga', 'Punto A', 'Efectivo', 'Tesoro', 'Zelle']} 
                    value={pago.metodo}
                    onChange={(v) => v && updatePago(pago.id, 'metodo', v)}
                    allowDeselect={false}
                    styles={{ 
                      input: { 
                        backgroundColor: '#ffffff', 
                        color: 'black', 
                        fontWeight: 600,
                        height: INPUT_HEIGHT, 
                        minHeight: INPUT_HEIGHT, 
                        fontSize: INPUT_SIZE, 
                        fontFamily: ROBOTO_FONT,
                        border: `2px solid ${colorBorde}`,
                        opacity: 1
                      } 
                    }} 
                    flex={1}
                    renderOption={({ option, checked }) => {
                      const mData = metodosPagoDisponibles.find(m => m.nombre === option.label);
                      return (
                        <Group gap="xs" wrap="nowrap">
                          <Box style={{ width: 12, height: 12, borderRadius: '50%', backgroundColor: mData?.color || '#ccc' }} />
                          <Text size="sm">{option.label}</Text>
                        </Group>
                      );
                    }}
                  />
                  <NumberInput 
                    placeholder="Monto"
                    value={pago.monto}
                    onChange={(v) => updatePago(pago.id, 'monto', v)}
                    decimalScale={2}
                    hideControls
                    rightSection={<Text size="sm" c="dimmed" pr={4} fw={700} style={{ color: colorBorde }}>{metodoData?.moneda === 'VES' ? 'Bs' : '$'}</Text>}
                    rightSectionWidth={30}
                    styles={{ 
                      input: { 
                        backgroundColor: '#ffffff', 
                        color: 'black', 
                        fontWeight: 600,
                        height: INPUT_HEIGHT, 
                        minHeight: INPUT_HEIGHT, 
                        fontSize: INPUT_SIZE, 
                        fontFamily: ROBOTO_FONT, 
                        textAlign: 'right', 
                        paddingRight: '35px',
                        border: `2px solid ${colorBorde}`
                      } 
                    }} w={110} 
                  />
                  <TextInput 
                    placeholder="#Ref" 
                    value={pago.referencia}
                    onChange={(e) => updatePago(pago.id, 'referencia', e.target.value)}
                    styles={{ 
                      input: { 
                        backgroundColor: '#ffffff', 
                        color: 'black', 
                        fontWeight: 600,
                        height: INPUT_HEIGHT, 
                        minHeight: INPUT_HEIGHT, 
                        fontSize: INPUT_SIZE, 
                        fontFamily: ROBOTO_FONT,
                        border: `2px solid ${colorBorde}`
                      } 
                    }} w={70} 
                  />
                  <ActionIcon color="red" variant="filled" onClick={() => removePago(pago.id)} h={34} w={34} radius="md"><IconTrash size={16} /></ActionIcon>
                </Group>
              );
            })}
          </Stack>
        </ScrollArea>

        <Paper bg="#141414" p="xs" radius="sm" style={{ border: '1px solid #333' }}>
          <Stack gap={4}>
            <Group justify="space-between">
              <Text size="xs" c="dimmed" style={{ fontFamily: ROBOTO_FONT }}>Habitación (USD)</Text>
              <Text size="sm" fw={600} c="white">${costoDolar.toFixed(2)}</Text>
            </Group>
            {totalExtras > 0 && (
              <Group justify="space-between">
                <Text size="xs" c="dimmed" style={{ fontFamily: ROBOTO_FONT }}>Extras</Text>
                <Text size="sm" fw={600} c="white">${totalExtras.toFixed(2)}</Text>
              </Group>
            )}
            {appliedVoucher && (
              <Group justify="space-between">
                <Text size="xs" c="teal" style={{ fontFamily: ROBOTO_FONT }}>Dcto. Cupón ({appliedVoucher.codigo})</Text>
                <Text size="sm" fw={600} c="teal">-${montoDescuento.toFixed(2)}</Text>
              </Group>
            )}
            <Group justify="space-between">
              <Text size="xs" c="dimmed">Total Pagado</Text>
              <Text size="sm" fw={600} c="#38ef7d">-${totalPagadoDolares.toFixed(2)}</Text>
            </Group>
            <Divider color="#333" my={1} />
            <Group justify="space-between">
              <Text size={INPUT_SIZE} fw={700} c="white" style={{ fontFamily: ROBOTO_FONT }}>POR PAGAR</Text>
              <Text size="lg" fw={800} c={restanteDolares > 0.01 ? "red" : "#38ef7d"}>${restanteDolares.toFixed(2)}</Text>
            </Group>
          </Stack>
        </Paper>

        <Group justify="space-between" align="center" mt="xs">
          <Text size={LABEL_SIZE} c="white" fw={500} tt="uppercase" style={{ fontFamily: ROBOTO_FONT }}>Gastos Adicionales</Text>
          <ActionIcon color="orange" variant="light" onClick={addExtra}><IconPlus size={16} /></ActionIcon>
        </Group>

        <ScrollArea h={80} scrollbarSize={4}>
          <Stack gap={4}>
            {extras.map((ex) => (
              <Group key={ex.id} gap="xs" wrap="nowrap" align="center">
                <Select 
                  data={['Lencería', 'Limpieza Extra', 'Daño Material', 'Consumo']} 
                  value={ex.descripcion}
                  onChange={(v) => updateExtra(ex.id, 'descripcion', v || 'Lencería')}
                  styles={{ input: { backgroundColor: '#ffffff', color: 'black', height: '32px', minHeight: '32px', fontSize: INPUT_SIZE, fontFamily: ROBOTO_FONT } }} flex={1}
                />
                <NumberInput 
                  placeholder="Monto"
                  value={ex.monto}
                  onChange={(v) => updateExtra(ex.id, 'monto', v)}
                  decimalScale={2}
                  hideControls
                  rightSection={<Text size="sm" c="dimmed" pr={4}>$</Text>}
                  rightSectionWidth={20}
                  styles={{ input: { backgroundColor: '#ffffff', color: 'black', height: '32px', minHeight: '32px', fontSize: INPUT_SIZE, fontFamily: ROBOTO_FONT, textAlign: 'right', paddingRight: '25px' } }} w={110} 
                />
                <ActionIcon color="red" variant="subtle" onClick={() => removeExtra(ex.id)}><IconTrash size={14} /></ActionIcon>
              </Group>
            ))}
          </Stack>
        </ScrollArea>

        <Group wrap="nowrap" mt="auto">
          <Text size={LABEL_SIZE} c="white" fw={500} tt="uppercase" style={{ fontFamily: ROBOTO_FONT }}>Cód. Descuento</Text>
          <TextInput 
            value={voucher}
            onChange={(e) => setVoucher(e.target.value)}
            placeholder="Introduce código secreto..."
            disabled={!!appliedVoucher}
            autoComplete="off"
            name="voucher_code_secret"
            styles={{ input: { backgroundColor: '#ffffff', color: 'black', height: INPUT_HEIGHT, minHeight: INPUT_HEIGHT, fontSize: INPUT_SIZE, fontFamily: ROBOTO_FONT, textTransform: 'uppercase' } }} 
            flex={1} 
          />
          {appliedVoucher ? (
            <ActionIcon color="red" variant="filled" size="md" onClick={handleRemoveVoucher} h={34} w={34}>
              <IconX size={18} />
            </ActionIcon>
          ) : (
            <ActionIcon 
              color="teal" 
              variant="filled" 
              size="md" 
              onClick={handleValidateVoucher} 
              h={34} 
              w={34}
              disabled={!voucher.trim()}
            >
              <IconCheck size={18} />
            </ActionIcon>
          )}
        </Group>
      </Stack>
    </Paper>
  );

  const renderColumnaGestion = () => (
    <Paper bg="#1e1e1e" p="md" radius="md" style={{ border: '1px solid #2a2a2a', height: '720px', display: 'flex', flexDirection: 'column' }}>
      <Stack gap="md" style={{ height: '100%', display: 'flex' }}>
        <Group justify="space-between" mb="xs">
          <Box>
            <Text size="sm" fw={500} c="dimmed" tt="uppercase">Habitación</Text>
            <Text size="xl" fw={600} c="white">{habitacion?.numero}</Text>
          </Box>
          <Box style={{ textAlign: 'right' }}>
            <Text size="sm" fw={500} c="dimmed" tt="uppercase">Tipo</Text>
            <Text size="xl" fw={500} c="white">{habitacion?.tipo}</Text>
          </Box>
        </Group>
        <Textarea 
          placeholder="Observaciones de limpieza/estado a la habitación..."
          minRows={2}
          maxRows={3}
          autosize
          styles={{ input: { backgroundColor: '#ffffff', color: 'black', border: '1px solid #ccc', fontSize: INPUT_SIZE, fontFamily: ROBOTO_FONT } }}
        />
        <Group grow mt="sm" gap="xs">
          <Button 
            variant="filled" 
            fw={500} 
            leftSection={<IconLock size={16}/>}
            onClick={() => {
              setBloquearMotivo('');
              setNuevaHabitacionId(null);
              setShowBloquearModal(true);
            }}
            style={{ backgroundColor: '#2d2e33', color: 'white', border: 'none' }}
          >
            Bloquear
          </Button>
          <Button 
            variant="filled" 
            fw={500} 
            leftSection={<IconHistory size={16}/>}
            onClick={handleFetchRoomHistory}
            style={{ backgroundColor: '#2C2E33', color: 'white' }}
          >
            Historial
          </Button>
        </Group>
        <Box mt={4} style={{ display: (habitacion?.estado_actual === 'Hospedaje' || habitacion?.estado_actual === 'Parcial' || habitacion?.estado_actual === 'Retoque') ? 'block' : 'none' }}>
          <Group grow gap="xs">
            <Button 
                variant="filled" 
                fw={500} 
                onClick={() => setShowCambiarHabitacionModal(true)}
                style={{ backgroundColor: '#2d2e33', color: 'white', border: 'none' }}
                disabled={habitacion?.estado_actual === 'Retoque'}
                leftSection={<IconArrowsExchange size={16} />}
            >
                Mover
            </Button>
            <Button 
                variant="filled" 
                fw={500} 
                onClick={() => {
                    if (habitacion?.estado_actual === 'Retoque') {
                        handleFinalizarRetoque();
                    } else {
                        setShowRetoqueModal(true);
                    }
                }}
                leftSection={<IconClock size={16} />}
                style={{ backgroundColor: habitacion?.estado_actual === 'Retoque' ? '#38ef7d' : '#2d2e33', color: habitacion?.estado_actual === 'Retoque' ? 'black' : 'white', border: 'none' }}
                loading={loading}
            >
                {habitacion?.estado_actual === 'Retoque' ? 'Ya Limpia' : 'Retoque'}
            </Button>
          </Group>
        </Box>

        <Divider color="#2a2a2a" my={1} />

        <Box style={{ flex: 1, flexDirection: 'column', display: habitacion?.estado_actual === 'Libre' ? 'none' : 'flex' }}>
          <Group justify="space-between" mb="xs">
            <Text size="sm" fw={500} c="dimmed" tt="uppercase">Estado Huésped</Text>
            <Badge color={huespedes[activePersona].estado === 'ausente' ? 'gray' : 'green'} size="lg" variant="dot">
              {huespedes[activePersona].estado === 'ausente' ? 'Ausente' : 'Presente'}
            </Badge>
          </Group>
          <Button 
            variant="filled" 
            fw={500} 
            fullWidth 
            mb="sm" 
            onClick={handleFetchAccessHistory}
            leftSection={<IconHistory size={16} />}
            style={{ backgroundColor: '#2d2e33', color: 'white', border: 'none' }}
          >
            Registro Entradas/Salidas
          </Button>

          <Accordion variant="separated" styles={{ 
            item: { backgroundColor: '#1a1a1a', border: '1px solid #2a2a2a', marginTop: 8 },
            label: { color: 'white' },
          }}>
            <Accordion.Item value="observaciones">
              <Accordion.Control icon={<IconEye size={16} color="#38ef7d" />}>
                <Text size="sm" fw={500}>Observaciones de Transacción</Text>
              </Accordion.Control>
              <Accordion.Panel>
                <Textarea 
                  value={observacionesTransaccion}
                  onChange={(e) => setObservacionesTransaccion(e.target.value)}
                  placeholder="Facturas, quejas, detalles extra..."
                  minRows={2}
                  styles={{ 
                    input: { backgroundColor: '#ffffff', color: 'black', border: '1px solid #ccc', fontSize: INPUT_SIZE, fontFamily: ROBOTO_FONT },
                  }}
                />
              </Accordion.Panel>
            </Accordion.Item>
          </Accordion>
        </Box>

        <Stack gap="xs" mt="auto">
          {habitacion?.estado_actual === 'Parcial' && (
             <Button 
               h={50} 
               fw={600} 
               fullWidth 
               loading={loading}
               onClick={handlePasarAHospedaje}
               leftSection={<IconBed size={20} />}
               style={{ 
                 background: 'linear-gradient(135deg, rgb(189, 195, 199) 0%, rgb(36, 54, 70) 100%)', 
                 color: 'white',
                 border: 'none'
               }}
             >
               PASAR A HOSPEDAJE
             </Button>
          )}
          
          <Button 
            h={50}
            fullWidth 
            fw={700} 
            onClick={handleLiberar}
            loading={loading}
            disabled={habitacion?.estado_actual === 'Retoque' || restanteDolares > 0.01}
            style={{ 
              background: (habitacion?.estado_actual === 'Retoque' || restanteDolares > 0.01) ? '#555' : ACCENT_GRADIENT, 
              color: 'white', 
              border: 'none',
              fontSize: '1.2rem',
              display: habitacion?.estado_actual === 'Libre' ? 'none' : 'block'
            }}
          >
            {habitacion?.estado_actual === 'Retoque' ? 'EN RETOQUE' : (restanteDolares > 0.01 ? 'DEUDA PENDIENTE' : 'EGRESAR')}
          </Button>

          <Button 
            h={50}
            fullWidth 
            fw={700} 
            loading={loading}
            onClick={handleIngresar}
            style={{ 
              background: esReserva ? 'linear-gradient(135deg, rgb(20, 171, 169) 0%, rgb(10, 60, 130) 100%)' : ACCENT_GRADIENT, 
              color: 'white', 
              border: 'none',
              fontSize: '1.2rem',
              display: habitacion?.estado_actual === 'Libre' ? 'block' : 'none'
            }}
          >
            {esReserva ? 'REALIZAR RESERVA' : 'INGRESAR'}
          </Button>
        </Stack>
      </Stack>
    </Paper>
  );

  return (
    <>
    <style dangerouslySetInnerHTML={{ __html: `
      @keyframes shake {
        10%, 90% { transform: translate3d(-1px, 0, 0); }
        20%, 80% { transform: translate3d(2px, 0, 0); }
        30%, 50%, 70% { transform: translate3d(-3px, 0, 0); }
        40%, 60% { transform: translate3d(3px, 0, 0); }
      }
    `}} />
    <Modal
      opened={opened}
      onClose={handleClose}
      size={isFullScreen ? "100%" : isMobile ? "100%" : "1400px"}
      centered
      padding={isMobile ? 0 : "md"}
      fullScreen={isFullScreen || isMobile}
      title={
        <Group gap="xs" align="center" justify="space-between" style={{ width: '100%', paddingRight: '10px' }}>
          <Group gap="xs">
            <Text size="xl" c="white" style={{ fontWeight: 500 }}>
              Habitación {habitacion?.numero}
            </Text>
            <Text size="sm" c="dimmed" style={{ borderLeft: '1px solid #444', paddingLeft: '10px', marginLeft: '5px' }}>
              Atendido por Libia
            </Text>
          </Group>
          {!isMobile && (
            <ActionIcon 
              variant="subtle" 
              color="gray" 
              onClick={() => setIsFullScreen(!isFullScreen)}
              title={isFullScreen ? "Salir de pantalla completa" : "Pantalla completa"}
              size="lg"
              style={{ marginRight: '34px' }}
            >
              {isFullScreen ? <IconMinimize size={20} /> : <IconMaximize size={20} />}
            </ActionIcon>
          )}
        </Group>
      }
      styles={{
        content: { backgroundColor: '#141414', border: '1px solid #2a2a2a', display: 'flex', flexDirection: 'column' },
        body: { padding: '2vh 1rem', overflow: 'hidden', flex: 1 },
        header: { backgroundColor: '#1a1a1a', borderBottom: '1px solid #2a2a2a', padding: '0.5rem 1rem' },
        title: { color: 'white' },
        close: { color: '#a1a1aa', '&:hover': { backgroundColor: '#2a2a2a', color: 'white' } }
      }}
    >
      <Box pos="relative" style={{ minHeight: '400px', display: 'flex', flexDirection: 'column', height: '100%' }}>
        {isMobile ? (
          <Box style={{ height: 'calc(100vh - 60px)', display: 'flex', flexDirection: 'column' }}>
          <Tabs defaultValue="cliente" variant="pills" p="xs" styles={{ 
            tab: { flex: 1, backgroundColor: '#2a2a2a', color: '#888' },
            list: { borderBottom: 'none' }
          }}>
            <Tabs.List grow mb="md">
              <Tabs.Tab value="cliente" leftSection={<IconUser size={16} />}>Cliente</Tabs.Tab>
              <Tabs.Tab value="pagos" leftSection={<IconCash size={16} />}>Pagos</Tabs.Tab>
              <Tabs.Tab value="gestion" leftSection={<IconBed size={16} />}>Habitación</Tabs.Tab>
            </Tabs.List>

            <ScrollArea h="calc(100vh - 140px)">
              <Tabs.Panel value="cliente" px="xs">
                {renderColumnaCliente()}
              </Tabs.Panel>
              
              <Tabs.Panel value="pagos" px="xs" style={{ height: '100%' }}>
                {renderColumnaPago()}
              </Tabs.Panel>
              
              <Tabs.Panel value="gestion" px="xs" style={{ height: '100%' }}>
                {renderColumnaGestion()}
              </Tabs.Panel>
            </ScrollArea>
          </Tabs>
        </Box>
      ) : (
        <Grid gutter="sm">
          <Grid.Col span={4}>
            {renderColumnaCliente()}
          </Grid.Col>
          <Grid.Col span={4}>
            {renderColumnaPago()}
          </Grid.Col>
          <Grid.Col span={4} style={{ display: 'flex', flexDirection: 'column' }}>
            {renderColumnaGestion()}
          </Grid.Col>
        </Grid>
      )}
      </Box>
    </Modal>

    <Modal 
      opened={showWarningModal} 
      onClose={() => setShowWarningModal(false)} 
      title="Pago Incompleto"
      centered
      overlayProps={{ backgroundOpacity: 0.55, blur: 3 }}
      styles={{ content: { backgroundColor: '#1e1e1e', color: 'white', border: '1px solid #333' }, header: { backgroundColor: '#1e1e1e' } }}
    >
      <Stack>
        <Text>El monto pagado es inferior al costo total. ¿Desea continuar con el ingreso de todas formas?</Text>
        <Group justify="flex-end">
          <Button variant="light" color="gray" onClick={() => setShowWarningModal(false)}>Cancelar</Button>
          <Button color="orange" onClick={executeIngresar} loading={loading}>Continuar e Ingresar</Button>
        </Group>
      </Stack>
    </Modal>

    <Modal 
      opened={showReputacionModal} 
      onClose={() => setShowReputacionModal(false)} 
      title={<Group gap="xs"><IconX color="red" /><Text fw={700} c="red">Atención: Mala Reputación</Text></Group>}
      centered
      overlayProps={{ backgroundOpacity: 0.55, blur: 3 }}
      styles={{ 
        content: { backgroundColor: '#1e1e1e', color: 'white', border: '1px solid #ff6b6b' }, 
        header: { backgroundColor: '#1e1e1e', borderBottom: '1px solid #2a2a2a' } 
      }}
    >
      <Stack>
        <Text fw={500}>Este cliente tiene marcada una <span style={{color: '#ff6b6b', fontWeight: 800}}>MALA REPUTACIÓN</span>.</Text>
        <Text size="sm" c="dimmed">Puede continuar con el proceso bajo su propio riesgo o tomar las precauciones necesarias.</Text>
        <Group justify="flex-end" mt="md">
          <Button color="red" onClick={() => setShowReputacionModal(false)}>Entendido, proceder con cuidado</Button>
        </Group>
      </Stack>
    </Modal>

    <Modal 
      opened={showCambiarHabitacionModal} 
      onClose={() => {setShowCambiarHabitacionModal(false); setNuevaHabitacionId(null); setCambioMotivo('');}} 
      title={<Text fw={700} c="white">Cambiar de Habitación</Text>}
      centered
      overlayProps={{ backgroundOpacity: 0.55, blur: 3 }}
      styles={{ 
        content: { backgroundColor: '#1e1e1e', color: 'white', border: '1px solid #333' }, 
        header: { backgroundColor: '#1e1e1e', borderBottom: '1px solid #2a2a2a' },
        title: { color: 'white' }
      }}
    >
      <Stack>
        <Select
          label={<Text size={LABEL_SIZE} c="white" fw={500} style={{ fontFamily: ROBOTO_FONT }}>¿A qué habitación desea cambiarlo?</Text>}
          placeholder="Seleccione habitación libre"
          data={habitacionesLibres}
          value={nuevaHabitacionId}
          onChange={setNuevaHabitacionId}
          searchable
          styles={{ input: { backgroundColor: '#ffffff', color: 'black', height: INPUT_HEIGHT, minHeight: INPUT_HEIGHT, fontSize: INPUT_SIZE, fontFamily: ROBOTO_FONT } }}
          required
        />
        <Textarea
          label={<Text size={LABEL_SIZE} c="white" fw={500} style={{ fontFamily: ROBOTO_FONT }}>Motivo del cambio</Text>}
          placeholder="Ej: Problemas con el aire acondicionado..."
          value={cambioMotivo}
          onChange={(e) => setCambioMotivo(e.currentTarget.value)}
          minRows={3}
          styles={{ input: { backgroundColor: '#ffffff', color: 'black', fontSize: INPUT_SIZE, fontFamily: ROBOTO_FONT } }}
          required
        />
        <Group justify="flex-end" mt="md">
          <Button variant="light" color="gray" onClick={() => {setShowCambiarHabitacionModal(false); setNuevaHabitacionId(null); setCambioMotivo('');}}>Cancelar</Button>
          <Button color="grape" onClick={handleCambioHabitacion} loading={loadingCambio} disabled={!nuevaHabitacionId || !cambioMotivo.trim()}>Cambiar</Button>
        </Group>
      </Stack>
      </Modal>
      
      <DataTableModal 
        opened={showHistorialModal} 
        onClose={() => setShowHistorialModal(false)}
        title={`Historial de Visitas - ${currentHuesped.nombre || currentHuesped.cedula}`}
        columns={historialColumns}
        data={historialData}
        loading={loadingHistorial}
      />

      <DataTableModal 
        opened={showRoomHistoryModal} 
        onClose={() => setShowRoomHistoryModal(false)}
        title={`Historial de Habitación ${habitacion?.numero}`}
        columns={roomHistoryColumns}
        data={roomHistoryData}
        loading={loadingRoomHistory}
      />

      <DataTableModal 
        opened={showAccessHistoryModal} 
        onClose={() => setShowAccessHistoryModal(false)}
        title={`Registro de Entrada/Salida - ${currentHuesped.nombre || currentHuesped.cedula}`}
        columns={accessHistoryColumns}
        data={accessHistoryData}
        loading={loadingAccessHistory}
      />

      <Modal
          opened={showBloquearModal}
          onClose={() => {setShowBloquearModal(false); setBloquearMotivo(''); setNuevaHabitacionId(null);}}
          title={`Bloquear Habitación ${habitacion?.numero}`}
          centered
          radius="md"
          styles={{
            header: { backgroundColor: '#1a1a1a', color: 'white' },
            content: { backgroundColor: '#141414', color: 'white' },
            title: { fontWeight: 700 }
          }}
        >
          <Stack>
            <Text size="sm">Ingrese el motivo del bloqueo de esta habitación:</Text>
            <Textarea
              placeholder="Ej: Mantenimiento de aire acondicionado, Filtración, etc."
              value={bloquearMotivo}
              onChange={(e) => setBloquearMotivo(e.target.value)}
              minRows={3}
              styles={{ input: { backgroundColor: '#ffffff', color: 'black', fontSize: INPUT_SIZE, fontFamily: ROBOTO_FONT } }}
              required
            />

            {(habitacion?.estado_actual !== 'Libre' && habitacion?.estado_actual !== 'Bloqueada' && habitacion?.estado_actual !== 'Sucia' && habitacion?.estado_actual !== 'Retoque') && (
              <Box mt="sm">
                <Divider label="Huésped Presente" labelPosition="center" color="red" mb="sm" />
                <Select
                  label={<Text size={LABEL_SIZE} c="white" fw={500} style={{ fontFamily: ROBOTO_FONT }}>¿A qué habitación desea mover al cliente?</Text>}
                  placeholder="Seleccione habitación libre"
                  data={habitacionesLibres}
                  value={nuevaHabitacionId}
                  onChange={setNuevaHabitacionId}
                  searchable
                  styles={{ input: { backgroundColor: '#ffffff', color: 'black', height: INPUT_HEIGHT, minHeight: INPUT_HEIGHT, fontSize: INPUT_SIZE, fontFamily: ROBOTO_FONT } }}
                  required
                />
                <Text size="xs" c="dimmed" mt={4}>
                  Al bloquear una habitación ocupada, el cliente será movido automáticamente a la nueva habitación seleccionada.
                </Text>
              </Box>
            )}

            <Group justify="flex-end" mt="md">
              <Button variant="subtle" color="gray" onClick={() => setShowBloquearModal(false)}>Cancelar</Button>
              <Button 
                color="red" 
                loading={loadingBloqueo} 
                onClick={handleBloquear} 
                leftSection={<IconLock size={16}/>}
                disabled={!bloquearMotivo.trim() || (habitacion?.estado_actual !== 'Libre' && habitacion?.estado_actual !== 'Bloqueada' && habitacion?.estado_actual !== 'Sucia' && !nuevaHabitacionId)}
              >
                Bloquear {habitacion?.estado_actual !== 'Libre' && habitacion?.estado_actual !== 'Bloqueada' && habitacion?.estado_actual !== 'Sucia' ? 'y Mover' : 'Habitación'}
              </Button>
            </Group>
          </Stack>
        </Modal>

        <Modal 
          opened={showRetoqueModal} 
          onClose={() => {setShowRetoqueModal(false); setCamareraId(null);}} 
          title={<Text fw={700} c="white">Solicitar Retoque</Text>}
          centered
          overlayProps={{ backgroundOpacity: 0.55, blur: 3 }}
          styles={{ 
            content: { backgroundColor: '#1e1e1e', color: 'white', border: '1px solid #333' }, 
            header: { backgroundColor: '#1e1e1e', borderBottom: '1px solid #2a2a2a' },
            title: { color: 'white' }
          }}
        >
          <Stack>
            <Text size="sm">¿Está seguro que desea poner la habitación en retoque? El estado visual cambiará y no podrá egresarla hasta finalizar.</Text>
            <Select
              label={<Text size={LABEL_SIZE} c="white" fw={500} style={{ fontFamily: ROBOTO_FONT }}>Seleccione la camarera</Text>}
              placeholder="Seleccione camarera"
              data={camareras}
              value={camareraId}
              onChange={setCamareraId}
              styles={{ input: { backgroundColor: '#ffffff', color: 'black', height: INPUT_HEIGHT, minHeight: INPUT_HEIGHT, fontSize: INPUT_SIZE, fontFamily: ROBOTO_FONT } }}
              required
            />
            <Group justify="flex-end" mt="md">
              <Button variant="light" color="gray" onClick={() => setShowRetoqueModal(false)}>Cancelar</Button>
              <Button color="grape" onClick={handleRetoque} loading={loadingRetoque} disabled={!camareraId}>Confirmar Retoque</Button>
            </Group>
          </Stack>
        </Modal>
    </>
  );
}
