'use client';

import { useEffect, useState } from 'react';
import { Box, Group, TypographyStylesProvider, Text, AppShell, Stack, Title, Paper, SegmentedControl, Divider, Badge, Select, Button, NumberInput, ActionIcon, Drawer, ScrollArea, Tooltip, Modal, PasswordInput } from '@mantine/core';
import { IconRefresh, IconChevronUp, IconLayoutDashboard, IconUser, IconCalendar, IconChartBar, IconCheck, IconAlertCircle, IconDoorEnter, IconDoorExit, IconLayoutGrid, IconMap, IconBell } from '@tabler/icons-react';
import { useRouter } from 'next/navigation';
import { notifications } from '@mantine/notifications';
import { useMediaQuery } from '@mantine/hooks';
import CroquisGrid from '../components/CroquisGrid';
import ModernGrid from '../components/ModernGrid';
import HabitacionModal from '../components/HabitacionModal';
import { DirtyRoomModal, BlockedRoomModal } from '../components/RoomActionModals';
import AccesoModal from '../components/AccesoModal';
import CambioTurnoModal from '../components/CambioTurnoModal';
import NovedadesModal from '../components/NovedadesModal';
import ReservasModal from '../components/ReservasModal';
import { api } from './lib/api';
import { Habitacion } from '../types';
import { IconCalculator } from '@tabler/icons-react';

const ROBOTO_FONT = 'Roboto, sans-serif';
const POPPINS_FONT = 'Poppins, sans-serif';
const LABEL_SIZE = '13px';
const INPUT_SIZE = '14px';
const INPUT_HEIGHT = '34px';

export default function Home() {
  const router = useRouter();
  const [habitaciones, setHabitaciones] = useState<Habitacion[]>([]);
  const [loading, setLoading] = useState(true);
  const [viewMode, setViewMode] = useState('croquis');
  const isMobile = useMediaQuery('(max-width: 767px)'); // Breakpoint ajustado para móviles
  const [mobileDrawerOpen, setMobileDrawerOpen] = useState(false);
  const [selectedHabitacionData, setSelectedHabitacionData] = useState<{hab: Habitacion, details: any} | null>(null);
  const [dirtyRoom, setDirtyRoom] = useState<Habitacion | null>(null);
  const [blockedRoom, setBlockedRoom] = useState<Habitacion | null>(null);
  const [bcv, setBcv] = useState<number>(0);
  const [users, setUsers] = useState<any[]>([]);
  const [activeUser, setActiveUser] = useState<any>({ username: 'Usuario', rol: 'cargo' });
  const [pendingUser, setPendingUser] = useState<string | null>('Usuario');
  const [isCambioTurnoOpen, setIsCambioTurnoOpen] = useState(false);
  const [refreshing, setRefreshing] = useState(false);
  const [firstLoad, setFirstLoad] = useState(true);
  const [isAccesoOpen, setIsAccesoOpen] = useState(false);
  const [accesoTipo, setAccesoTipo] = useState<'entrada' | 'salida'>('entrada');
  const [isNovedadesOpen, setIsNovedadesOpen] = useState(false);
  const [password, setPassword] = useState('');
  const [currentTime, setCurrentTime] = useState(new Date());
  const [isReservasOpen, setIsReservasOpen] = useState(false);
  const [numReservas, setNumReservas] = useState(0);

  useEffect(() => {
    const timer = setInterval(() => setCurrentTime(new Date()), 30000); // 30s
    return () => clearInterval(timer);
  }, []);

  const checkAccess = () => {
    if (activeUser.username === 'Usuario') {
      notifications.show({
        title: 'Acceso Denegado',
        message: 'Debe asignar un turno válido antes de acceder al sistema.',
        color: 'red',
        icon: <IconAlertCircle size={18} />
      });
      return false;
    }

    const r = activeUser.rol ? activeUser.rol.toLowerCase() : '';
    const rolesAutorizados = ['recepcionista', 'socio', 'administrador', 'admin'];
    if (!rolesAutorizados.includes(r)) {
      notifications.show({
        title: 'Acceso Restringido',
        message: `El cargo "${activeUser.rol}" no tiene permisos para operar el sistema.`,
        color: 'red',
        icon: <IconAlertCircle size={18} />
      });
      return false;
    }

    if (bcv <= 0) {
      notifications.show({
        title: 'Acceso Denegado',
        message: 'Debe actualizar el valor del BCV antes de acceder al sistema.',
        color: 'red',
        icon: <IconAlertCircle size={18} />
      });
      return false;
    }
    return true;
  };

  const handleRoomClick = async (hab: Habitacion) => {
    if (!checkAccess()) return;

    if (hab.estado_actual === 'Sucia') {
      setDirtyRoom(hab);
      return;
    }
    if (hab.estado_actual === 'Bloqueada') {
      setBlockedRoom(hab);
      return;
    }

    if (hab.estado_actual !== 'Libre') {
      document.body.style.cursor = 'wait';
      try {
        const data = await api.getEstanciaActiva(hab.id);
        setSelectedHabitacionData({ hab, details: data });
      } catch (err) {
        console.error("Error al cargar estancia activa:", err);
        setSelectedHabitacionData({ hab, details: null });
        document.body.style.cursor = 'default';
      }
    } else {
      setSelectedHabitacionData({ hab, details: null });
    }
  };

  // Colores para las etiquetas de estado
  const estadoColores = {
    Libres: 'linear-gradient(135deg, rgb(5, 117, 230) 0%, rgb(2, 27, 121) 100%)',
    Parciales: 'linear-gradient(135deg, rgb(180, 20, 20) 0%, rgb(60, 0, 0) 100%)',
    Hospedajes: 'linear-gradient(135deg, rgb(189, 195, 199) 0%, rgb(36, 54, 70) 100%)',
    Reservadas: 'linear-gradient(135deg, rgb(20, 171, 169) 0%, rgb(10, 60, 130) 100%)',
    Retoque: 'linear-gradient(135deg, rgb(120, 40, 240) 0%, rgb(60, 10, 100) 100%)',
    Sucias: 'linear-gradient(135deg, rgb(220, 82, 45) 0%, rgb(70, 40, 20) 100%)',
    Bloqueadas: 'linear-gradient(135deg, #444 0%, #000 100%)',
  };

  const loadHabitaciones = () => {
    // Solo mostramos el loader visual la primera vez para evitar flikers
    if (firstLoad) {
      setLoading(true);
      document.body.style.cursor = 'wait';
    }
    
    api.getHabitaciones()
      .then((data) => {
        setHabitaciones(data);
        setLoading(false);
        setFirstLoad(false);
        document.body.style.cursor = 'default';
      })
      .catch((err) => {
        console.error("Error cargando habitaciones:", err);
        notifications.show({
           title: 'Error de Red',
           message: 'No se pudieron cargar las habitaciones del servidor.',
           color: 'red'
        });
        setLoading(false);
        document.body.style.cursor = 'default';
      });

    api.getReservasProximas()
      .then(data => setNumReservas(data.length))
      .catch(console.error);
  };

  const loadSettingsAndUsers = async () => {
    try {
      const dataBcv = await api.getConfig('bcv');
      setBcv(parseFloat(dataBcv.valor) || 0);

      const dataUsers = await api.getUsuarios();
      setUsers(dataUsers);
    } catch (err) {
      console.error("Error loading settings/users/turno:", err);
    }
  };

  const handleRefreshBcv = async () => {
    setRefreshing(true);
    try {
      const data = await api.refreshBcv();
      setBcv(data.price);
      notifications.show({
        title: 'Tasa Actualizada',
        message: `El dólar se actualizó a ${data.price} Bs`,
        color: 'teal',
        icon: <IconCheck size={18} />,
      });
    } catch (err: any) {
      notifications.show({
        title: 'Error de conexión',
        message: err.message || 'No se pudo contactar con el servidor.',
        color: 'red',
        icon: <IconAlertCircle size={18} />,
      });
    } finally {
      setRefreshing(false);
    }
  };

  // Cargar sesión y configuración desde cache al iniciar
  useEffect(() => {
    const cachedUser = localStorage.getItem('activeUser');
    if (cachedUser) {
      try {
        const user = JSON.parse(cachedUser);
        setActiveUser(user);
        setPendingUser(user.username);
      } catch (e) {
        console.error("Error al restaurar usuario de cache:", e);
      }
    }

    const cachedBcv = localStorage.getItem('bcv');
    if (cachedBcv) {
      setBcv(parseFloat(cachedBcv));
    }

    loadHabitaciones();
    loadSettingsAndUsers();
  }, []);

  // Persistir activeUser y bcv en localStorage cuando cambien
  useEffect(() => {
    if (activeUser && activeUser.username !== 'Usuario') {
      localStorage.setItem('activeUser', JSON.stringify(activeUser));
    } else {
      localStorage.removeItem('activeUser');
    }
  }, [activeUser]);

  useEffect(() => {
    if (bcv > 0) {
      localStorage.setItem('bcv', bcv.toString());
    }
  }, [bcv]);

  useEffect(() => {
    if (selectedHabitacionData) {
      document.body.style.cursor = 'default';
    }
  }, [selectedHabitacionData]);

  const countState = (state: string) => habitaciones.filter(h => h.estado_actual === state).length;

  const renderCounters = (isRow = false) => {
    const labelToState: Record<string, string> = {
      Libres: 'Libre', Parciales: 'Parcial', Hospedajes: 'Hospedaje',
      Reservadas: 'Reservada', Retoque: 'Retoque', Sucias: 'Sucia', Bloqueadas: 'Bloqueada'
    };

    // Calcular todos los conteos primero para saber el máximo de dígitos
    const counts = Object.values(labelToState).map(state => countState(state));
    const maxVal = Math.max(...counts, 0);
    const maxDigits = Math.max(String(maxVal).length, 2); // Mínimo 2 dígitos para estética

    return Object.entries(estadoColores).map(([label, color]) => {
      const isReservada = label === 'Reservadas';
      const currentCount = isReservada ? numReservas : countState(labelToState[label]);
      const displayValue = loading ? '-' : String(currentCount).padStart(maxDigits, '0');
      
      return (
        <Box 
          key={label} 
          ta="center" 
          style={{ 
            display: 'flex', 
            flexDirection: 'column', 
            flex: isRow ? '0 0 auto' : '0 0 auto', 
            width: isRow ? '60px' : 'auto',
            cursor: isReservada ? 'pointer' : 'default'
          }}
          onClick={() => {
            if (isReservada) setIsReservasOpen(true);
          }}
        >
          <Text fw={600} size={isRow ? "10px" : "15px"} mb={isRow ? 2 : 6} lh={1} c="white" style={{ textTransform: 'uppercase', letterSpacing: '1px', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis', fontFamily: POPPINS_FONT }}>{label}</Text>
          <Paper 
            shadow="none" 
            style={{ 
              background: color, 
              height: isRow ? '35px' : '65px', 
              display: 'flex', 
              alignItems: 'center', 
              justifyContent: 'center',
              boxShadow: isReservada ? '0 0 15px rgba(20, 171, 169, 0.3)' : 'none',
              transition: 'transform 0.2s ease'
            }} 
            radius="md"
            onMouseEnter={(e) => { if(isReservada) e.currentTarget.style.transform = 'scale(1.02)'; }}
            onMouseLeave={(e) => { if(isReservada) e.currentTarget.style.transform = 'scale(1)'; }}
          >
            <Text fw={400} c="white" style={{ fontSize: isRow ? '1.2rem' : '3.2rem', lineHeight: 1, fontFamily: POPPINS_FONT }}>
              {displayValue}
            </Text>
          </Paper>
        </Box>
      )
    });
  };

  const renderLeftPanelContent = () => (
    <Stack justify="space-between" h="100%">
      <Box>
        <Box mb="xl" mt="md">
          <img src="/banner.svg" alt="Esmeralda Software Banner" style={{ width: '100%', height: 'auto', display: 'block' }} />
        </Box>

        <Stack gap={"md"} style={{ marginBottom: '1rem' }}>
          {renderCounters(false)}
        </Stack>
      </Box>

      {/* Selector de modo (Croquis / Cuadrícula) con iconos ajustados al ancho */}
      <Group grow gap="xs" mb="xs">
        <Tooltip label="Modo Croquis Físico" position="top" withArrow>
          <ActionIcon 
            h={42}
            variant={viewMode === 'croquis' ? 'filled' : 'light'} 
            color={viewMode === 'croquis' ? 'rgb(40, 190, 100)' : 'gray'}
            onClick={() => setViewMode('croquis')}
            style={{ 
              transition: 'all 0.2s ease',
              border: viewMode === 'croquis' ? 'none' : '1px solid rgba(255,255,255,0.1)',
              background: viewMode === 'croquis' ? 'linear-gradient(135deg, #36ea7e 0%, #11998e 100%)' : undefined
            }}
          >
            <IconMap size={24} />
          </ActionIcon>
        </Tooltip>
        
        <Tooltip label="Modo Cuadrícula Dinámica" position="top" withArrow>
          <ActionIcon 
            h={42}
            variant={viewMode === 'grid' ? 'filled' : 'light'} 
            color={viewMode === 'grid' ? 'rgb(40, 190, 100)' : 'gray'}
            onClick={() => setViewMode('grid')}
            style={{ 
              transition: 'all 0.2s ease',
              border: viewMode === 'grid' ? 'none' : '1px solid rgba(255,255,255,0.1)',
              background: viewMode === 'grid' ? 'linear-gradient(135deg, #36ea7e 0%, #11998e 100%)' : undefined
            }}
          >
            <IconLayoutGrid size={24} />
          </ActionIcon>
        </Tooltip>
      </Group>
    </Stack>
  );

  const renderRightPanelContent = () => {
    const salidasPendientes = habitaciones
      .map(h => {
        if (!h.hora_salida) return null;
        const horaSalida = new Date(h.hora_salida);
        const diffMinutes = Math.floor((horaSalida.getTime() - currentTime.getTime()) / 60000);
        
        const isParcial = h.estado_actual === 'Parcial';
        const isHospedaje = h.estado_actual === 'Hospedaje';
        
        // Agregamos Hospedajes solo si les queda poco tiempo (60 min) o se pasó el tiempo
        if (isParcial || (isHospedaje && diffMinutes <= 60)) {
          return {
            habitacion: h.numero,
            horaSalida,
            diffMinutes,
          };
        }
        return null;
      })
      .filter((s): s is NonNullable<typeof s> => s !== null)
      .sort((a, b) => a.diffMinutes - b.diffMinutes);

    const formatTime = (date: Date) => {
      return date.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit', hour12: false });
    };

    return (
    <Stack gap="sm">
      <Box>
        <Title order={2} c="white" style={{ fontWeight: 500, fontSize: 'clamp(1.4rem, 1.8vw, 2.2rem)', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
          {activeUser.username || 'Sistema'}
        </Title>
        <Text size="sm" c="white" tt="uppercase" fw={500} style={{ letterSpacing: '0.5px' }}>
          {activeUser.rol || '...'}
        </Text>
      </Box>

      <Group grow gap="sm">
        <Select
          data={(() => {
            const systemUsers = users
              .filter(u => u.rol && ['recepcionista', 'socio', 'administrador', 'admin'].includes(u.rol.toLowerCase()))
              .map(u => u.username);
            // Aseguramos que 'Usuario' siempre esté presente y que no haya duplicados
            const uniqueOptions = Array.from(new Set(['Usuario', ...systemUsers]));
            return uniqueOptions;
          })()}
          searchable
          placeholder="Seleccionar Usuario"
          value={pendingUser}
          onChange={setPendingUser}
          radius="md"
          autoComplete="off"
          styles={{
            input: { backgroundColor: '#ffffff', color: '#111', fontWeight: 600, border: '1px solid #ccc', fontSize: INPUT_SIZE, fontFamily: ROBOTO_FONT, height: INPUT_HEIGHT, minHeight: INPUT_HEIGHT }
          }}
        />
        <PasswordInput
          placeholder="Clave"
          value={password}
          onChange={(event) => setPassword(event.currentTarget.value)}
          radius="md"
          autoComplete="new-password"
          styles={{
            input: { backgroundColor: '#ffffff', color: '#111', fontWeight: 600, border: '1px solid #ccc', fontSize: INPUT_SIZE, fontFamily: ROBOTO_FONT, height: INPUT_HEIGHT, minHeight: INPUT_HEIGHT }
          }}
        />
      </Group>

      <NumberInput
        value={bcv}
        onChange={(v) => {
           const newVal = parseFloat(v.toString()) || 45.62;
           setBcv(newVal);
           api.updateConfig('bcv', newVal.toString());
        }}
        decimalScale={2}
        fixedDecimalScale
        suffix=" Bs"
        step={0.5}
        radius="md"
        hideControls
        rightSection={
          <Tooltip label="Actualizar desde BCV" position="top">
            <Text 
              fw={600} 
              size="sm" 
              c="dimmed"
              style={{ cursor: 'pointer', userSelect: 'none', marginRight: '10px' }}
              onClick={handleRefreshBcv}
            >
              BCV
            </Text>
          </Tooltip>
        }
        rightSectionWidth={42}
        styles={{
          input: { backgroundColor: '#ffffff', color: '#111', fontWeight: 600, border: '1px solid #ccc', fontSize: INPUT_SIZE, fontFamily: ROBOTO_FONT, height: INPUT_HEIGHT, minHeight: INPUT_HEIGHT }
        }}
      />

      <Button 
        radius="md" 
        fullWidth 
        style={{ background: 'linear-gradient(135deg, #36ea7e 0%, #11998e 100%)', color: 'white', fontWeight: 600, fontSize: '18px', fontFamily: ROBOTO_FONT, height: '48px', transition: 'all 0.2s', border: 'none' }}
        onClick={() => {
          if (!checkAccess()) return;
          if (!activeUser.rol || activeUser.rol.toLowerCase() !== 'recepcionista') {
            notifications.show({
              title: 'Acceso Restringido',
              message: 'Solo el personal de recepción puede cambiar de turno.',
              color: 'red',
              icon: <IconAlertCircle size={18} />
            });
            return;
          }
          setIsCambioTurnoOpen(true);
        }}
      >
        Cambiar de Turno
      </Button>
      <Text 
        ta="center" 
        size="sm" 
        c="dimmed" 
        style={{ cursor: refreshing ? 'not-allowed' : 'pointer', textDecoration: 'underline' }}
        onClick={async () => {
          if (refreshing) return;
          setRefreshing(true);
          try {
            // Sincronizar UI con el usuario seleccionado
            const uData = users.find(u => u.username === pendingUser) || { username: pendingUser, rol: 'Recepcionista' };
            setActiveUser(uData);

            // Refrescar habitaciones
            loadHabitaciones();

            // Tomar el monto del input y guardarlo como referencia oficial
            await api.updateConfig('bcv', bcv.toString());

            notifications.show({ 
              title: 'Sistema Sincronizado', 
              message: `Usuario confirmado: ${pendingUser}. Dólar fijado en ${bcv} Bs`, 
              color: 'blue' 
            });
          } catch (err) {
            console.error(err);
          } finally {
            setRefreshing(false);
          }
        }}
      >
        {refreshing ? 'Sincronizando...' : 'Forzar Actualización'}
      </Text>

      <Divider color="#2a2a2a" />

      <Box style={{ flex: 1, display: 'flex', flexDirection: 'column', minHeight: isMobile ? '250px' : 0 }}>
        <Group justify="space-between" mb="xs" px="4px">
          <Text size="md" fw={500} c="white" tt="uppercase">Salidas Pendientes</Text>
          <Badge size="sm" color="red" variant="light">{salidasPendientes.length}</Badge>
        </Group>

        <Paper bg="#141414" radius="md" style={{ border: '1px solid #2a2a2a', overflow: 'hidden', flex: 1, display: 'flex', flexDirection: 'column' }}>
          <Group justify="space-between" p="8px 12px" bg="#1a1a1a" style={{ borderBottom: '1px solid #2a2a2a' }}>
            <Text size="sm" fw={500} c="white">Hab</Text>
            <Text size="sm" fw={500} c="white">Hora / Restante</Text>
          </Group>
          
          <ScrollArea style={{ flex: 1 }}>
            <Box style={{ display: 'flex', flexDirection: 'column' }}>
              {salidasPendientes.length === 0 ? (
                <Text p="sm" ta="center" c="dimmed" size="sm">No hay salidas pendientes</Text>
              ) : (
                salidasPendientes.map((salida, idx) => (
                  <Group key={idx} justify="space-between" p="clamp(8px, 1vh, 12px) clamp(10px, 1.5vh, 16px)" style={{ borderBottom: '1px solid rgba(255,255,255,0.02)' }}>
                    <Text fw={700} c="white" style={{ fontSize: 'clamp(0.9rem, 1.2vw, 1.4rem)' }}>{salida.habitacion}</Text>
                    <Text fw={600} c={salida.diffMinutes < 0 ? "#ff3333" : salida.diffMinutes <= 15 ? "#ff9933" : "#a1a1aa"} style={{ fontSize: 'clamp(0.9rem, 1.2vw, 1.4rem)' }}>
                      {formatTime(salida.horaSalida)} / {Math.abs(salida.diffMinutes)}m
                    </Text>
                  </Group>
                ))
              )}
            </Box>
          </ScrollArea>
        </Paper>
      </Box>
    </Stack>
  );
  };

  return (
    <AppShell
      styles={{
        main: { backgroundColor: '#141414', color: '#e4e4e7', height: '100vh', overflow: 'hidden', display: 'flex', flexDirection: 'column' },
      }}
    >
      <AppShell.Main>
        <Group align="flex-start" wrap="nowrap" p="0" style={{ flex: 1, minHeight: 0, w: '100%', gap: isMobile ? '0' : 'clamp(0.5rem, 1.5vw, 2rem)', boxSizing: 'border-box' }}>
          
          {/* PANEL IZQUIERDO: Oculto en móvil */}
          {!isMobile && (
            <Stack w="clamp(150px, 12vw, 240px)" bg="#1e1e1e" style={{ borderRight: '1px solid #2a2a2a', padding: 'clamp(0.5rem, 1vw, 1.5rem)', height: '100%' }}>
              {renderLeftPanelContent()}
            </Stack>
          )}

          {/* PANEL CENTRAL */}
          <Box flex={1} style={{ height: '100%', display: 'flex', flexDirection: 'column', gap: isMobile ? '0.5rem' : '1rem', overflow: 'hidden', padding: isMobile ? '0.5rem' : 'clamp(0.5rem, 1.5vw, 2rem) 0' }}>
            
            {/* Cabecera Móvil: Contadores */}
            {isMobile && (
              <Box mb={0}>
                <Group wrap="nowrap" gap="xs" style={{ overflowX: 'auto', paddingBottom: '4px', WebkitOverflowScrolling: 'touch' }}>
                  {renderCounters(true)}
                </Group>
              </Box>
            )}


            
            <Box pos="relative" style={{ flex: 1, overflow: 'hidden' }}>
                {(loading && firstLoad) ? (
                  <Box style={{ height: '100vh' }} />
                ) : viewMode === 'croquis' ? (
                  <Box style={{ height: '100%', width: '100%', display: 'flex', flexDirection: 'column' }}>
                    <CroquisGrid habitaciones={habitaciones} onRoomClick={handleRoomClick} bcv={bcv} />
                  </Box>
                ) : (
                  <ScrollArea h="100%" type="scroll" offsetScrollbars>
                    <ModernGrid habitaciones={habitaciones} onRoomClick={handleRoomClick} bcv={bcv} />
                  </ScrollArea>
                )}
            </Box>
          </Box>

          {/* PANEL DERECHO: Oculto en Móvil */}
          {!isMobile && (
            <Stack w="clamp(260px, 16vw, 300px)" bg="#1e1e1e" style={{ borderLeft: '1px solid #2a2a2a', padding: 'clamp(0.5rem, 1vw, 1.5rem)', height: '100%' }}>
              {renderRightPanelContent()}
            </Stack>
          )}
        </Group>

        {/* BOTTOM BAR PARA MÓVIL */}
        {isMobile && !selectedHabitacionData && (
          <Group 
            onClick={() => setMobileDrawerOpen(true)}
            wrap="nowrap"
            justify="space-between"
            style={{ 
              position: 'relative', 
              bottom: 0, 
              left: 0, 
              right: 0, 
              height: '60px',
              minHeight: '60px',
              background: '#1e1e1e',
              borderTop: '1px solid #2a2a2a',
              display: 'flex',
              alignItems: 'center',
              padding: '0 16px',
              cursor: 'pointer',
              zIndex: 10,
              borderTopLeftRadius: '16px',
              borderTopRightRadius: '16px'
            }}
          >
            <Box>
               <Text fw={800} c="white" size="sm" lh={1.2}>{activeUser.username || 'Sistema'}</Text>
               <Text fw={500} c="white" size="xs" tt="uppercase" lh={1.2}>{activeUser.rol || '...'}</Text>
            </Box>
            
            <Group gap="sm" wrap="nowrap" align="center">
              <Text fw={300} c="white" style={{ fontSize: '2.2rem', lineHeight: 0.8 }}>{bcv.toFixed(2)} Bs</Text>
              <IconChevronUp color="#a1a1aa" size={24} />
            </Group>
          </Group>
        )}

        <Drawer
          opened={mobileDrawerOpen}
          onClose={() => setMobileDrawerOpen(false)}
          position="bottom"
          size="95%"
          title={<Text fw={700} c="white" size="lg">Panel de Control</Text>}
          styles={{
            content: { backgroundColor: '#141414', borderTopRightRadius: '24px', borderTopLeftRadius: '24px' },
            header: { backgroundColor: '#1e1e1e', borderBottom: '1px solid #2a2a2a', borderTopRightRadius: '24px', borderTopLeftRadius: '24px' },
            title: { color: 'white' },
            close: { color: 'white' }
          }}
        >
          <Box p="xs">
            {/* MENÚ DE ACCIONES RÁPIDAS DENTRO DEL DRAWER */}
            <ScrollArea w="100%" h={90} type="hover" offsetScrollbars={false} mb="md">
              <Group wrap="nowrap" gap="sm" pt="xs" pb="xs" h="100%" align="center" style={{ minWidth: 'max-content' }}>
                <Button
                  h={60}
                  variant="filled"
                  radius="md"
                  px="xl"
                  style={{ background: 'linear-gradient(135deg, #28be64 0%, #11998e 100%)' }}
                  leftSection={<IconDoorEnter size={24} />}
                  onClick={() => { if (!checkAccess()) return; setAccesoTipo('entrada'); setIsAccesoOpen(true); }}
                >
                  ENTRADA
                </Button>

                <Button
                  h={60}
                  variant="filled"
                  radius="md"
                  px="xl"
                  style={{ background: 'linear-gradient(135deg, #f20505 0%, #a10000 100%)' }}
                  leftSection={<IconDoorExit size={24} />}
                  onClick={() => { if (!checkAccess()) return; setAccesoTipo('salida'); setIsAccesoOpen(true); }}
                >
                  SALIDA
                </Button>

                <Divider orientation="vertical" color="#444" h={40} mx="xs" />

                <ActionIcon size={60} radius="xl" variant="filled" color="dark" style={{ border: '1px solid #444', background: '#222' }} onClick={() => { if (!checkAccess()) return; router.push('/dashboard'); }}>
                  <IconLayoutDashboard size={28} />
                </ActionIcon>

                <ActionIcon size={60} radius="xl" variant="filled" color="dark" style={{ border: '1px solid #444', background: '#222' }} onClick={() => { if (!checkAccess()) return; setIsNovedadesOpen(true); }}>
                  <IconBell size={28} />
                </ActionIcon>

                <ActionIcon size={60} radius="xl" variant="filled" color="dark" style={{ border: '1px solid #444', background: '#222' }}>
                  <IconCalendar size={28} />
                </ActionIcon>

                <ActionIcon size={60} radius="xl" variant="filled" color="dark" style={{ border: '1px solid #444', background: '#222' }}>
                  <IconUser size={28} />
                </ActionIcon>

                <Box style={{ width: 20 }} />
              </Group>
            </ScrollArea>

            <Divider color="#2a2a2a" mb="lg" />

            {isMobile && (
              <Group justify="center" mb="lg">
                <ActionIcon 
                  size={54} radius="md" variant={viewMode === 'croquis' ? 'filled' : 'light'} 
                  color={viewMode === 'croquis' ? 'teal' : 'gray'}
                  onClick={() => setViewMode('croquis')}
                >
                  <IconMap size={28} />
                </ActionIcon>
                <ActionIcon 
                  size={54} radius="md" variant={viewMode === 'grid' ? 'filled' : 'light'} 
                  color={viewMode === 'grid' ? 'teal' : 'gray'}
                  onClick={() => setViewMode('grid')}
                >
                  <IconLayoutGrid size={28} />
                </ActionIcon>
              </Group>
            )}
            {renderRightPanelContent()}
          </Box>
        </Drawer>

        {/* EL NUEVO COMPONENTE MAESTRO: Ventana de Ventas / Gestión */}
        <HabitacionModal
          habitacion={selectedHabitacionData?.hab || null}
          initialData={selectedHabitacionData?.details || null}
          opened={selectedHabitacionData !== null}
          onClose={() => setSelectedHabitacionData(null)}
          onSuccess={loadHabitaciones}
          bcv={bcv}
          currentUser={users.find(u => u.username === activeUser.username) || activeUser}
        />

        <ReservasModal
          opened={isReservasOpen}
          onClose={() => setIsReservasOpen(false)}
          onSuccess={loadHabitaciones}
        />

        <DirtyRoomModal 
          habitacion={dirtyRoom} 
          onClose={() => setDirtyRoom(null)} 
          onSuccess={loadHabitaciones} 
        />

        <BlockedRoomModal 
          habitacion={blockedRoom} 
          onClose={() => setBlockedRoom(null)} 
          onSuccess={loadHabitaciones} 
        />

        <CambioTurnoModal
          opened={isCambioTurnoOpen}
          onClose={() => setIsCambioTurnoOpen(false)}
          users={users}
          currentUser={activeUser.username}
          onSuccess={(newUser) => {
            const uData = users.find(u => u.username === newUser) || { username: newUser, rol: 'Recepcionista' };
            setActiveUser(uData);
            setPendingUser(newUser);
          }}
        />

        <AccesoModal 
          opened={isAccesoOpen} 
          onClose={() => setIsAccesoOpen(false)} 
          tipo={accesoTipo} 
        />

        <NovedadesModal
          opened={isNovedadesOpen}
          onClose={() => setIsNovedadesOpen(false)}
          activeUser={activeUser.username}
        />

        {/* BOTONES DE ACCIÓN RÁPIDA (SOLO ESCRITORIO) */}
        {!isMobile && !selectedHabitacionData && (
          <Stack 
            gap="sm" 
            style={{ 
              position: 'fixed', 
              bottom: '24px', 
              right: 'calc(clamp(0.5rem, 1vw, 1.5rem))', 
              zIndex: 100,
              width: 'calc(clamp(260px, 16vw, 300px) - calc(clamp(0.5rem, 1vw, 1.5rem) * 2))'
            }}
          >
            <Group gap="xs" justify="space-between" wrap="nowrap" w="100%">
              <Tooltip label="Dashboard / Ajustes" position="top" withArrow>
                <ActionIcon 
                  size={50} radius="xl" variant="filled" color="dark" 
                  style={{ border: '1px solid #333', background: 'rgba(26, 26, 26, 0.9)', backdropFilter: 'blur(8px)' }}
                  onClick={() => { if (!checkAccess()) return; router.push('/dashboard'); }}
                >
                  <IconLayoutDashboard size={24} />
                </ActionIcon>
              </Tooltip>
              <ActionIcon size={50} radius="xl" variant="filled" color="dark" style={{ border: '1px solid #333', background: 'rgba(26, 26, 26, 0.9)', backdropFilter: 'blur(8px)' }}>
                <IconUser size={26} />
              </ActionIcon>
              <Tooltip label="Calculadora Rápida" position="top" withArrow>
                <ActionIcon 
                  size={50} radius="xl" variant="filled" color="dark" 
                  style={{ border: '1px solid #333', background: 'rgba(26, 26, 26, 0.9)', backdropFilter: 'blur(8px)' }}
                  onClick={() => window.dispatchEvent(new CustomEvent('toggle-calculator'))}
                >
                  <IconCalculator size={26} />
                </ActionIcon>
              </Tooltip>
              <ActionIcon 
                size={50} radius="xl" variant="filled" color="dark" 
                style={{ border: '1px solid #333', background: 'rgba(26, 26, 26, 0.9)', backdropFilter: 'blur(8px)' }}
                onClick={() => { if (!checkAccess()) return; setIsNovedadesOpen(true); }}
              >
                <IconBell size={26} />
              </ActionIcon>
            </Group>
            <Group grow wrap="wrap" gap="xs" w="100%">
              <Button h={54} radius="md" style={{ backgroundColor: 'rgb(40, 190, 100)' }} leftSection={<IconDoorEnter size={20} />} onClick={() => { if (!checkAccess()) return; setAccesoTipo('entrada'); setIsAccesoOpen(true); }}>ENTRADA</Button>
              <Button h={54} radius="md" style={{ backgroundColor: 'rgb(242, 5, 5)' }} leftSection={<IconDoorExit size={20} />} onClick={() => { if (!checkAccess()) return; setAccesoTipo('salida'); setIsAccesoOpen(true); }}>SALIDA</Button>
            </Group>
          </Stack>
        )}
      </AppShell.Main>
    </AppShell>
  );
}
