'use client';

import { 
  Box, Title, Text, Badge, Group, Stack, ActionIcon, Tooltip, Table, Loader, Center, Card, Divider, Button
} from '@mantine/core';
import { 
  IconAlertCircle, IconTools, IconInfoCircle, IconCheck, IconTrash, IconPlus, IconSearch, IconArrowLeft
} from '@tabler/icons-react';
import { useState, useEffect, Suspense } from 'react';
import { useSearchParams, useRouter } from 'next/navigation';
import { DashboardTable } from '../components/DashboardTable';
import { api } from '../../lib/api';


function NovedadesContent() {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [data, setData] = useState<any[]>([]);
  const [hasMore, setHasMore] = useState(true);
  const [skip, setSkip] = useState(0);
  const LIMIT = 20;

  // Function to format dates in 24h
  const formatDate24 = (dateStr: string) => {
    if (!dateStr) return 'N/A';
    const d = new Date(dateStr);
    return d.toLocaleString('es-VE', { 
      hour12: false,
      day: '2-digit', 
      month: '2-digit', 
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const searchParams = useSearchParams();

  useEffect(() => {
    setData([]);
    setSkip(0);
    setHasMore(true);
    fetchNovedades(0);
  }, [searchParams]);

  const fetchNovedades = async (currentSkip: number) => {
    if (loading) return;
    setLoading(true);
    try {
      const s = searchParams.get('s') || undefined;
      const start = searchParams.get('start') || undefined;
      const end = searchParams.get('end') || undefined;
      
      const [response, shifts] = await Promise.all([
        api.getNovedades(s, start, end, currentSkip, LIMIT),
        currentSkip === 0 ? api.getTurnos(s, start, end) : Promise.resolve([])
      ]);
      
      const mapped = response.map(item => ({ ...item, timestamp: item.fecha }));
      const turnoMapped = shifts.map(s => ({
        id: `turno-${s.id}`,
        tipo: 'turno',
        timestamp: s.inicio,
        fin_nombre: s.worker_out,
        inicio_nombre: s.worker,
        hora: formatDate24(s.inicio)
      }));

      const combined = [...mapped, ...turnoMapped].sort((a,b) => 
        new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime()
      );

      if (currentSkip === 0) {
        setData(combined);
      } else {
        setData(prev => [...prev, ...mapped].sort((a,b) => 
          new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime()
        ));
      }

      if (response.length < LIMIT) {
        setHasMore(false);
      }
    } catch (error) {
      console.error('Error fetching novedades:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleLoadMore = () => {
    if (hasMore && !loading) {
      const nextSkip = skip + LIMIT;
      setSkip(nextSkip);
      fetchNovedades(nextSkip);
    }
  };

  const handleResolver = async (id: number) => {
    try {
      await api.resolverAveria(id);
      fetchNovedades(0); // Refresh from start
    } catch (error) {
      console.error('Error resolving averia:', error);
    }
  };

  const columns = [
    { key: 'num', label: '#', width: 40, textAlign: 'center' as const },
    { key: 'tipo', label: 'Tipo', width: 140 },
    { key: 'sujeto', label: 'Sujeto / Título', width: 250 },
    { key: 'descripcion', label: 'Descripción' },
    { key: 'fecha', label: 'Fecha/Hora', width: 200 },
    { key: 'registrado', label: 'Registrado Por' },
    { key: 'estado', label: 'Estado', textAlign: 'center' as const },
    { key: 'acciones', label: '', width: 80 },
  ];

  const renderCard = (item: any) => {
    const isAveria = item.tipo === 'averia';
    const estado = (item.estado || 'PENDIENTE').toUpperCase();
    const titulo = item.texto?.split(':')[0] || 'Sin Título';
    const desc = item.texto?.split(':')[1] || item.texto;

    return (
      <Card shadow="none" radius={0} bg="#1e1e1e" style={{ borderBottom: '1px solid #2a2a2a', marginBottom: 4 }} p="md">
        <Group justify="space-between" mb="xs">
          <Group gap="xs">
            {isAveria ? <IconTools size={18} color="#ff6b6b" /> : <IconInfoCircle size={18} color="#339af0" />}
            <Text fw={800} size="sm" c={isAveria ? '#ff6b6b' : '#339af0'} tt="uppercase">
              {isAveria ? 'Avería' : 'Novedad'}
            </Text>
          </Group>
          <Badge 
            variant="light" 
            color={estado === 'PENDIENTE' ? 'red' : 'teal'}
            styles={{ root: { fontWeight: 900 } }}
          >
            {estado}
          </Badge>
        </Group>

        <Text fw={700} c="white" size="md" mb={4}>{titulo}</Text>
        <Text size="sm" c="dimmed" mb="md">{desc}</Text>

        <Divider color="#2a2a2a" mb="md" />

        <Group justify="space-between">
           <Stack gap={0}>
             <Text size="10px" c="dimmed" tt="uppercase" fw={800}>Fecha</Text>
             <Text size="xs" c="white">{formatDate24(item.fecha)}</Text>
           </Stack>
           <Stack gap={0} align="flex-end">
             <Text size="10px" c="dimmed" tt="uppercase" fw={800}>Por</Text>
             <Text size="xs" c="white">{item.usuario || 'Sistema'}</Text>
           </Stack>
        </Group>

        {(isAveria && estado === 'PENDIENTE') && (
           <Button 
            fullWidth 
            mt="md" 
            variant="light" 
            color="teal" 
            leftSection={<IconCheck size={16} />}
            onClick={() => handleResolver(item.id)}
            styles={{ root: { fontWeight: 800 } }}
           >
             MARCAR COMO RESUELTO
           </Button>
        )}
      </Card>
    );
  };

  const renderRow = (item: any, index: number, runningCounter: number) => {
    const isAveria = item.tipo === 'averia';
    const estado = (item.estado || 'PENDIENTE').toUpperCase();
    
    return (
      <Table.Tr key={`novedad-${item.id}`}>
        <Table.Td style={{ textAlign: 'center', color: '#888', fontWeight: 500 }}>{runningCounter}</Table.Td>
        <Table.Td>
          <Group gap="xs">
            {isAveria ? (
              <IconTools size={16} color="#ff6b6b" />
            ) : (
              <IconInfoCircle size={16} color="#339af0" />
            )}
            <Text size="xs" fw={700} c={isAveria ? '#ff6b6b' : '#339af0'} tt="uppercase">
              {isAveria ? 'Avería' : 'Novedad'}
            </Text>
          </Group>
        </Table.Td>
        <Table.Td>
          <Text size="sm" fw={700} c="white">{item.texto?.split(':')[0] || 'Sin Título'}</Text>
        </Table.Td>
        <Table.Td>
          <Text size="sm" c="dimmed" style={{ maxWidth: 400 }} truncate="end">
            {item.texto?.split(':')[1] || item.texto}
          </Text>
        </Table.Td>
        <Table.Td>
          <Text size="sm" style={{ opacity: 0.8 }}>
            {formatDate24(item.fecha)}
          </Text>
        </Table.Td>
        <Table.Td><Text size="sm" fw={500}>{item.usuario || 'Sistema'}</Text></Table.Td>
        <Table.Td>
          <Group justify="center">
            <Badge 
              variant="light" 
              size="md"
              radius="sm"
              color={
                estado === 'PENDIENTE' ? 'red' : 
                estado === 'RESUELTO' || estado === 'COMPLETADO' || estado === 'ARREGLADA' ? 'teal' : 'blue'
              }
              styles={{ root: { border: 'none', fontWeight: 800, padding: '12px 16px' } }}
            >
              {estado}
            </Badge>
          </Group>
        </Table.Td>
        <Table.Td>
          <Group gap={4} justify="flex-end">
            {isAveria && (estado === 'PENDIENTE' || estado === 'PENDIENTE') && (
              <Tooltip label="Marcar como resuelto">
                <ActionIcon variant="subtle" color="teal" size="sm" onClick={() => handleResolver(item.id)}>
                  <IconCheck size={16} />
                </ActionIcon>
              </Tooltip>
            )}
            <ActionIcon variant="subtle" color="red" size="sm">
              <IconTrash size={16} />
            </ActionIcon>
          </Group>
        </Table.Td>
      </Table.Tr>
    );
  };

  const getShiftDivider = (item: any) => {
    if (item.tipo === 'turno') {
      return { fin: item.fin_nombre, inicio: item.inicio_nombre, hora: item.hora };
    }
    return null;
  };

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
            <Title order={2} c="white" style={{ fontFamily: 'Poppins, sans-serif' }}>Novedades y Averías</Title>
            <Text size="sm" c="dimmed">Registro de incidencias, reportes técnicos y novedades operativas del hotel.</Text>
          </Box>
        </Group>

        {loading ? (
          <Center h={400}>
            <Stack align="center">
              <Loader color="teal" size="lg" type="bars" />
              <Text c="dimmed" size="sm">Sincronizando novedades...</Text>
            </Stack>
          </Center>
        ) : (
          <DashboardTable 
            columns={columns}
            data={data}
            renderRow={renderRow}
            renderCard={renderCard}
            onLoadMore={handleLoadMore}
            hasMore={hasMore}
            shiftDivider={getShiftDivider}
          />
        )}
      </Stack>
    </Box>
  );
}

export default function NovedadesSection() {
  return (
    <Suspense fallback={<Center h={400}><Loader color="teal" size="lg" type="bars" /></Center>}>
      <NovedadesContent />
    </Suspense>
  );
}
