'use client';

import { 
  Box, Title, Text, SimpleGrid, Paper, Group, Stack, Badge, Modal, 
  ActionIcon, Divider, Avatar, Center, ThemeIcon, Loader, ScrollArea
} from '@mantine/core';
import { useDisclosure, useMediaQuery } from '@mantine/hooks';
import { 
  IconUsers, IconCash, IconAlertTriangle, IconChevronLeft, IconChevronRight,
  IconArrowRight, IconClock, IconPointFilled, IconInfoCircle, IconUser
} from '@tabler/icons-react';
import { useSearchParams } from 'next/navigation';
import { useState, useEffect, useMemo, Suspense } from 'react';
import { api } from '../../lib/api';

function ResumenContent() {
  const searchParams = useSearchParams();
  const [opened, { open, close }] = useDisclosure(false);
  const [selectedTurno, setSelectedTurno] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const isMobile = useMediaQuery('(max-width: 48em)');
  const [turnosData, setTurnosData] = useState<any[]>([]);
  
  // Calendar Navigation State
  const [currentDate, setCurrentDate] = useState(new Date());

  useEffect(() => {
    const fetchHistory = async () => {
      setLoading(true);
      try {
        const s = searchParams.get('s') || undefined;
        const start = searchParams.get('start') || undefined;
        const end = searchParams.get('end') || undefined;
        
        const history = await api.getTurnos(s, start, end);
        setTurnosData(history);
      } catch (error) {
        console.error('Error fetching turn history:', error);
      } finally {
        setLoading(false);
      }
    };
    fetchHistory();
  }, [searchParams]);

  const handleTurnoClick = (turno: any) => {
    if (!turno || turno.isPlaceholder) return;
    setSelectedTurno(turno);
    open();
  };

  const daysLabels = ['Lu', 'Ma', 'Mi', 'Ju', 'Vi', 'Sá', 'Do'];

  // CALENDAR LOGIC
  const calendarDays = useMemo(() => {
    const year = currentDate.getFullYear();
    const month = currentDate.getMonth();

    // First day of the month
    const firstDayOfMonth = new Date(year, month, 1);
    // Last day of the month
    const lastDayOfMonth = new Date(year, month + 1, 0);
    
    // Get start day (0 = Sunday, 1 = Monday, ..., 6 = Saturday)
    // Convert to (0 = Monday, ..., 6 = Sunday)
    let startDayIdx = firstDayOfMonth.getDay() - 1;
    if (startDayIdx === -1) startDayIdx = 6; // Sunday

    const days = [];

    // 1. Padding from previous month
    const prevMonthLastDay = new Date(year, month, 0).getDate();
    for (let i = startDayIdx; i > 0; i--) {
      days.push({
        dia: prevMonthLastDay - i + 1,
        month: 'prev',
        isPlaceholder: true,
        fullDate: new Date(year, month - 1, prevMonthLastDay - i + 1)
      });
    }

    // 2. Days of current month
    for (let i = 1; i <= lastDayOfMonth.getDate(); i++) {
      const fullDate = new Date(year, month, i);
      // Find turn(s) for this day
      const turnsForDay = turnosData.filter(t => {
        const tDate = new Date(t.inicio);
        return tDate.getDate() === i && tDate.getMonth() === month && tDate.getFullYear() === year;
      });

      days.push({
        dia: i,
        month: 'current',
        fullDate,
        turns: turnsForDay,
        isToday: new Date().toDateString() === fullDate.toDateString()
      });
    }

    // 3. Padding for next month
    const remaining = 42 - days.length; // 6 weeks total grid
    for (let i = 1; i <= remaining; i++) {
        days.push({
          dia: i,
          month: 'next',
          isPlaceholder: true,
          fullDate: new Date(year, month + 1, i)
        });
    }

    return days;
  }, [currentDate, turnosData]);

  const changeMonth = (offset: number) => {
    const newDate = new Date(currentDate.getFullYear(), currentDate.getMonth() + offset, 1);
    setCurrentDate(newDate);
  };

  const monthName = currentDate.toLocaleString('es-VE', { month: 'long' });
  const capitalizedMonth = monthName.charAt(0).toUpperCase() + monthName.slice(1);

  return (
    <Box>
      <Stack gap="xl">
        <Box>
          <Title order={2} c="white" style={{ fontFamily: 'Poppins, sans-serif' }}>Resumen de Desempeño</Title>
          <Text size="sm" c="dimmed">Monitoreo de turnos, ingresos y estadísticas operativas.</Text>
        </Box>

        {loading ? (
          <Center h={400}>
            <Stack align="center">
              <Loader color="teal" size="lg" type="bars" />
              <Text c="dimmed" size="sm">Obteniendo métricas de rendimiento...</Text>
            </Stack>
          </Center>
        ) : (
          <SimpleGrid cols={{ base: 1, md: 2 }} spacing="xl">
            {/* CALENDAR SECTION */}
            <Paper p={{ base: 'md', sm: 'xl' }} radius="md" bg="#1e1e1e" style={{ border: '1px solid #2a2a2a', overflow: 'hidden' }}>
              <Stack gap="lg">
                <Group justify="space-between">
                  <ActionIcon variant="subtle" color="gray" onClick={() => changeMonth(-1)}><IconChevronLeft size={20} /></ActionIcon>
                  <Text fw={700} size="lg" c="white">{capitalizedMonth} {currentDate.getFullYear()}</Text>
                  <ActionIcon variant="subtle" color="gray" onClick={() => changeMonth(1)}><IconChevronRight size={20} /></ActionIcon>
                </Group>

                <ScrollArea w="100%" type="auto">
                  <Box style={{ minWidth: isMobile ? '350px' : 'none' }}>
                    <SimpleGrid cols={7} spacing="xs">
                  {daysLabels.map((day) => (
                    <Text key={day} ta="center" size="sm" c="dimmed" fw={700} mb="xs">{day}</Text>
                  ))}
                  
                  {calendarDays.map((day, idx) => {
                    const hasTurns = day.turns && day.turns.length > 0;
                    const primaryTurn = hasTurns ? day.turns[0] : null;

                    return (
                      <Box 
                        key={`${day.month}-${day.dia}-${idx}`} 
                        p="xs" 
                        ta="center" 
                        style={{ 
                          cursor: day.isPlaceholder ? 'default' : 'pointer',
                          borderRadius: 8,
                          backgroundColor: day.month !== 'current' ? 'transparent' : (day.isToday ? 'rgba(36, 203, 124, 0.08)' : 'transparent'),
                          border: day.isToday ? '1px solid rgba(36, 203, 124, 0.3)' : '1px solid transparent',
                          transition: 'all 0.2s',
                          opacity: day.month === 'current' ? 1 : 0.2,
                          minHeight: 60,
                          display: 'flex',
                          flexDirection: 'column',
                          justifyContent: 'center'
                        }}
                        className={!day.isPlaceholder ? 'calendar-day-hover' : ''}
                        onClick={() => hasTurns && handleTurnoClick(primaryTurn)}
                      >
                        <Text size="md" fw={700} c={day.isToday ? '#24cb7c' : 'white'}>{day.dia}</Text>
                        {hasTurns ? (
                          <Text size="10px" fw={800} c="#24cb7c" truncate="end" style={{ letterSpacing: '0.2px' }}>
                            {primaryTurn.worker}
                          </Text>
                        ) : (
                          !day.isPlaceholder && <Text size="10px" c="dimmed" style={{ opacity: 0.3 }}>-</Text>
                        )}
                      </Box>
                    );
                  })}
                    </SimpleGrid>
                  </Box>
                </ScrollArea>

                <Divider color="#2a2a2a" />

                <Group justify="space-around" pt="xs">
                  <Stack gap={0} align="center">
                    <Group gap={4}><IconUsers size={16} color="#24cb7c" /><Text size="xs" fw={700} c="#24cb7c">Turnos (Sync)</Text></Group>
                    <Text fw={800} c="white">{turnosData.length}</Text>
                  </Stack>
                  <Stack gap={0} align="center">
                    <Group gap={4}><IconCash size={16} color="#24cb7c" /><Text size="xs" fw={700} c="#24cb7c">USD Global</Text></Group>
                    <Text fw={800} c="#24cb7c">${turnosData.reduce((acc, t) => acc + (t.usd || 0), 0).toFixed(2)}</Text>
                  </Stack>
                </Group>
              </Stack>
            </Paper>

            {/* QUICK STATS CARDS */}
            <Stack gap="md">
              <SimpleGrid cols={2} spacing="md">
                <Paper p="md" radius="md" bg="#1e1e1e" style={{ border: '1px solid #2a2a2a' }}>
                  <Text size="xs" c="dimmed" tt="uppercase" fw={700}>Ocupación Real</Text>
                  <Text size="xl" fw={700} c="white">Sincronizada</Text>
                  <Text size="xs" c="teal">SQLite Activo</Text>
                </Paper>
                <Paper p="md" radius="md" bg="#1e1e1e" style={{ border: '1px solid #2a2a2a' }}>
                  <Text size="xs" c="dimmed" tt="uppercase" fw={700}>Último Registro</Text>
                  <Text size="xl" fw={700} c="#24cb7c">{turnosData[0]?.worker || 'N/A'}</Text>
                  <Text size="xs" c="dimmed">{turnosData[0]?.isActual ? 'En progreso' : 'Cerrado'}</Text>
                </Paper>
              </SimpleGrid>
              
              <Paper p="md" radius="md" bg="#1e1e1e" style={{ border: '1px solid #2a2a2a', flex: 1 }}>
                <Text fw={700} c="white" mb="md">Alertas Recientes</Text>
                <Stack gap="xs">
                  <Group p="xs" bg="#2a2a2a" style={{ borderRadius: 6 }}>
                    <ThemeIcon color="teal" variant="light" size="sm"><IconInfoCircle size={14} /></ThemeIcon>
                    <Text size="sm">Historial de {turnosData.length} turnos recuperado.</Text>
                  </Group>
                  <Group p="xs" bg="#2a2a2a" style={{ borderRadius: 6 }}>
                    <ThemeIcon color="blue" variant="light" size="sm"><IconClock size={14} /></ThemeIcon>
                    <Text size="sm">Formato de hora 24h aplicado globalmente.</Text>
                  </Group>
                </Stack>
              </Paper>
            </Stack>
          </SimpleGrid>
        )}
      </Stack>

      <Modal 
        opened={opened} 
        onClose={close} 
        size="lg" 
        centered 
        title={<Text fw={900} size="xl" style={{ letterSpacing: '1px' }}>RESUMEN DE TURNO</Text>}
        styles={{ 
          content: { backgroundColor: '#141414', color: 'white', border: '1px solid #333' },
          header: { backgroundColor: '#141414', borderBottom: '1px solid #2a2a2a' }
        }}
      >
        {selectedTurno && (
          <Stack gap="md">
            <Paper p="md" radius="md" bg="#1e1e1e" style={{ border: '1px solid #2a2a2a' }}>
              <Group justify="space-between" align="center">
                <Stack gap={4} align="center">
                  <Text size="10px" fw={900} c="dimmed" tt="uppercase">Operador de Guardia</Text>
                  <Group gap="xs">
                    <Avatar radius="xl" color="teal" size="sm">{selectedTurno.worker.charAt(0)}</Avatar>
                    <Text fw={700} size="lg" c="white">{selectedTurno.worker}</Text>
                  </Group>
                </Stack>
                <IconArrowRight color="#24cb7c" size={24} />
                <Stack gap={4} align="center">
                  <Text size="10px" fw={900} c="dimmed" tt="uppercase">Estado</Text>
                  <Badge variant="filled" color={selectedTurno.isActual ? 'teal' : 'dark'} size="lg" radius="sm">
                    {selectedTurno.isActual ? 'ACTIVO' : 'SINCERADO'}
                  </Badge>
                </Stack>
              </Group>

              <Divider my="md" variant="dotted" color="#2a2a2a" />

              <Group justify="center" gap="xl">
                <Stack gap={0} align="center">
                  <Text size="10px" fw={900} c="dimmed" tt="uppercase">Entrada (24H)</Text>
                  <Text fw={800} c="white">{new Date(selectedTurno.inicio).toLocaleString('es-VE', { hour12: false })}</Text>
                </Stack>
                <Stack gap={0} align="center">
                  <Text size="10px" fw={900} c="dimmed" tt="uppercase">Salida (24H)</Text>
                  <Text fw={800} c="white">{selectedTurno.fin === 'Actual' ? 'En progreso' : new Date(selectedTurno.fin).toLocaleString('es-VE', { hour12: false })}</Text>
                </Stack>
              </Group>
            </Paper>

            <SimpleGrid cols={2} spacing="md">
              <Paper p="md" radius="md" bg="#1e1e1e" style={{ border: '1px solid #2a2a2a' }}>
                <Group gap="xs" mb="md">
                  <ThemeIcon color="blue" variant="light" size="sm"><IconUsers size={14} /></ThemeIcon>
                  <Text fw={700} size="sm" c="white">Registros</Text>
                </Group>
                <Stack gap={8}>
                  <Group justify="space-between"><Text size="sm" c="dimmed">Clientes Atendidos</Text><Text fw={800} c="white">{selectedTurno.clients}</Text></Group>
                  <Group justify="space-between"><Text size="sm" c="dimmed">Incidentes/Nov.</Text><Text fw={800} c="white">{selectedTurno.novedades}</Text></Group>
                  <Divider color="#2a2a2a" />
                  <Text size="10px" c="dimmed" ta="center">Sincronizado con Host Local</Text>
                </Stack>
              </Paper>

              <Paper p="md" radius="md" bg="#1e1e1e" style={{ border: '1px solid #2a2a2a' }}>
                <Group gap="xs" mb="md">
                  <ThemeIcon color="green" variant="light" size="sm"><IconCash size={14} /></ThemeIcon>
                  <Text fw={700} size="sm" c="white">Flujo de Caja (USD)</Text>
                </Group>
                <Stack gap={8}>
                  <Group justify="space-between"><Text size="sm" c="dimmed">Efectivo</Text><Text fw={800} c="white">${selectedTurno.ptoA.toFixed(2)}</Text></Group>
                  <Group justify="space-between"><Text size="sm" c="dimmed">Transferencias</Text><Text fw={800} c="white">${selectedTurno.bcaribe.toFixed(2)}</Text></Group>
                  <Divider color="#2a2a2a" />
                  <Group justify="space-between"><Text fw={900} c="white" size="md">Balance</Text><Text fw={900} c="#24cb7c" size="lg">${selectedTurno.usd.toFixed(2)}</Text></Group>
                </Stack>
              </Paper>
            </SimpleGrid>
          </Stack>
        )}
      </Modal>

      <style jsx global>{`
        .calendar-day-hover:hover {
          background-color: rgba(255, 255, 255, 0.04) !important;
          transform: translateY(-2px);
          box-shadow: 0 4px 12px rgba(0,0,0,0.5);
        }
      `}</style>
    </Box>
  );
}

export default function ResumenSection() {
  return (
    <Suspense fallback={<Center h={400}><Loader color="teal" size="lg" type="bars" /></Center>}>
      <ResumenContent />
    </Suspense>
  );
}
