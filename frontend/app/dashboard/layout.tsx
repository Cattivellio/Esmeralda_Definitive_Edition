'use client';

export const dynamic = 'force-dynamic';

import { useState, useEffect } from 'react';
import { 
  AppShell, 
  Box, 
  Group, 
  Stack, 
  Text, 
  ActionIcon, 
  Tooltip, 
  TextInput, 
  NavLink,
  Title,
  Divider,
  Button,
  Collapse,
  Burger,
  ScrollArea
} from '@mantine/core';
import { useDisclosure, useMediaQuery } from '@mantine/hooks';
import { DatePickerInput } from '@mantine/dates';
import { 
  IconSearch, 
  IconCalendar, 
  IconChartBar, 
  IconDoorEnter, 
  IconLockAccess, 
  IconBell, 
  IconSettings,
  IconArrowLeft,
  IconClock,
  IconChevronDown,
  IconChevronUp,
  IconWallet
} from '@tabler/icons-react';
import { useRouter, usePathname } from 'next/navigation';
import dayjs from 'dayjs';
import 'dayjs/locale/es';

dayjs.locale('es');

const ROBOTO_FONT = 'Roboto, sans-serif';
const POPPINS_FONT = 'Poppins, sans-serif';

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const pathname = usePathname();
  
  const [opened, { toggle, close }] = useDisclosure();
  const isMobile = useMediaQuery('(max-width: 48em)');
  const [searchTerm, setSearchTerm] = useState('');
  const [dateRange, setDateRange] = useState<[Date | null, Date | null]>([null, null]);
  const [time, setTime] = useState<string | null>(null);
  const [filtersOpened, setFiltersOpened] = useState(false);

  useEffect(() => {
    // Initialize from URL on client side only
    const params = new URLSearchParams(window.location.search);
    const s = params.get('s') || '';
    const start = params.get('start') ? new Date(params.get('start')!) : null;
    const end = params.get('end') ? new Date(params.get('end')!) : null;
    
    setSearchTerm(s);
    setDateRange([start, end]);
    
    // Initial clock set
    setTime(new Date().toLocaleTimeString());
    
    // Update every second
    const timer = setInterval(() => {
      setTime(new Date().toLocaleTimeString());
    }, 1000);

    return () => clearInterval(timer);
  }, []);

  const handleSearch = () => {
    const params = new URLSearchParams();
    if (searchTerm) params.set('s', searchTerm);
    if (dateRange[0]) params.set('start', dateRange[0].toISOString());
    if (dateRange[1]) params.set('end', dateRange[1].toISOString());
    
    router.push(`${pathname}?${params.toString()}`);
  };

  const navItems = [
    { label: 'Resumen', icon: IconChartBar, path: '/dashboard/resumen' },
    { label: 'Estancias', icon: IconDoorEnter, path: '/dashboard/estancias' },
    { label: 'Accesos', icon: IconLockAccess, path: '/dashboard/accesos' },
    { label: 'Novedades', icon: IconBell, path: '/dashboard/novedades' },
    { label: 'Configuración', icon: IconSettings, path: '/dashboard/configuracion' },
  ];

  return (
    <AppShell
      padding="md"
      header={{ height: 60, collapsed: !isMobile }}
      navbar={{
        width: 280,
        breakpoint: 'sm',
        collapsed: { mobile: !opened },
      }}
      styles={{
        main: { backgroundColor: '#141414', color: '#e4e4e7' },
        navbar: { backgroundColor: '#1e1e1e', borderRight: '1px solid #2a2a2a', zIndex: 200 },
        header: { backgroundColor: '#1e1e1e', borderBottom: '1px solid #2a2a2a', zIndex: 190 },
      }}
    >
      <AppShell.Header p="md">
        <Group h="100%" justify="space-between">
          <Group>
            <Burger opened={opened} onClick={toggle} size="sm" color="teal" />
            <Text fw={800} c="white" style={{ fontFamily: POPPINS_FONT, letterSpacing: '-0.5px' }}>
              ESMERALDA
            </Text>
          </Group>
          <ActionIcon variant="subtle" color="gray" onClick={() => router.push('/')}>
            <IconArrowLeft size={20} />
          </ActionIcon>
        </Group>
      </AppShell.Header>
      <AppShell.Navbar p="md">
        <ScrollArea h="100%" offsetScrollbars>
          <Stack gap="md">
          <Box mb="sm">
            <Group justify="space-between" mb="xs">
              <Title order={3} c="white" style={{ fontFamily: POPPINS_FONT, fontWeight: 700, letterSpacing: '-0.5px' }}>
                ESMERALDA
              </Title>
              <Tooltip label="Volver al Inicio">
                <ActionIcon 
                  variant="subtle" 
                  color="gray" 
                  onClick={() => router.push('/')}
                >
                  <IconArrowLeft size={18} />
                </ActionIcon>
              </Tooltip>
            </Group>
            <Text size="xs" c="dimmed" tt="uppercase" fw={700} style={{ letterSpacing: '1px' }}>Dashboard</Text>
          </Box>

          <Divider color="#2a2a2a" />

          {/* Global Filters in Sidebar */}
          <Box mb="xs">
            <Group 
              justify="space-between" 
              style={{ cursor: 'pointer', padding: '4px 0' }} 
              onClick={() => setFiltersOpened((o) => !o)}
            >
              <Text size="xs" fw={700} c="dimmed" tt="uppercase">Búsqueda y Filtros</Text>
              {filtersOpened ? <IconChevronUp size={14} color="#888" /> : <IconChevronDown size={14} color="#888" />}
            </Group>
            
            <Collapse in={filtersOpened}>
              <Stack gap="xs" mt="xs">
                <TextInput
                  placeholder="Buscar..."
                  leftSection={<IconSearch size={16} />}
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.currentTarget.value)}
                  onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
                  styles={{
                    input: { 
                      backgroundColor: '#2a2a2a', 
                      color: 'white', 
                      border: '1px solid #333',
                      '&:focus': { borderColor: '#24cb7c' }
                    }
                  }}
                />
                <DatePickerInput
                  type="range"
                  placeholder="Rango de fechas"
                  locale="es"
                  clearable
                  leftSection={<IconCalendar size={16} />}
                  value={dateRange}
                  onChange={(val) => setDateRange(val as [Date | null, Date | null])}
                  styles={{
                    input: { 
                      backgroundColor: '#2a2a2a', 
                      color: 'white', 
                      border: '1px solid #333' 
                    }
                  }}
                />
                <Button 
                  fullWidth 
                  onClick={handleSearch}
                  mt="4px"
                  style={{ 
                    fontWeight: 700, 
                    fontFamily: POPPINS_FONT,
                    background: 'linear-gradient(135deg, #36ea7e 0%, #11998e 100%)',
                    height: '36px',
                    fontSize: '12px',
                    letterSpacing: '0.5px',
                    border: 'none',
                    color: 'white'
                  }}
                >
                  BUSCAR
                </Button>
              </Stack>
            </Collapse>
          </Box>

          <Divider color="#2a2a2a" />

          <Stack gap="xs">
            <Text size="xs" fw={700} c="dimmed" tt="uppercase">Navegación</Text>
            {navItems.map((item) => (
              <NavLink
                key={item.path}
                label={item.label}
                leftSection={<item.icon size={20} />}
                active={pathname === item.path}
                onClick={() => {
                  router.push(item.path);
                  if (isMobile) close();
                }}
                variant="light"
                color="teal"
                styles={{
                  root: {
                    borderRadius: '8px',
                    color: pathname === item.path ? 'white' : '#888',
                    transition: 'all 0.2s ease',
                    background: pathname === item.path 
                      ? 'linear-gradient(135deg, rgba(54, 234, 126, 0.15) 0%, rgba(17, 153, 142, 0.15) 100%)' 
                      : 'transparent',
                    borderLeft: pathname === item.path ? '3px solid #36ea7e' : '3px solid transparent',
                    '&:hover': {
                      backgroundColor: '#2a2a2a',
                      color: 'white',
                      background: pathname === item.path 
                        ? 'linear-gradient(135deg, rgba(54, 234, 126, 0.25) 0%, rgba(17, 153, 142, 0.25) 100%)' 
                        : '#2a2a2a',
                    }
                  },
                  label: { fontWeight: pathname === item.path ? 700 : 500, fontFamily: POPPINS_FONT },
                  section: { color: pathname === item.path ? '#36ea7e' : 'inherit' }
                }}
              />
            ))}
          </Stack>

          <Box mt="auto">
            <Divider mb="md" color="#2a2a2a" />
            <Group gap="xs" px="xs">
              <IconClock size={16} color="#888" />
              <Text size="xs" c="dimmed">
                {time || '--:--:--'}
              </Text>
            </Group>
          </Box>
        </Stack>
      </ScrollArea>
    </AppShell.Navbar>

      <AppShell.Main>
        <Box p="md" style={{ minHeight: '100vh' }}>
          {children}
        </Box>
      </AppShell.Main>
    </AppShell>
  );
}
