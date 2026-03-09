'use client';

export const dynamic = 'force-dynamic';

import { 
  Box, Title, Text, Badge, Group, ActionIcon, Image, Modal, Stack, Tooltip, Table, Loader, Center, Card, Divider
} from '@mantine/core';
import { Suspense } from 'react';
import { Carousel } from '@mantine/carousel';
import { useDisclosure } from '@mantine/hooks';
import { 
  IconEye, IconTrash, IconDoorEnter, IconDoorExit, IconChevronRight, IconChevronLeft, IconPhoto, IconPlus, IconSearch, IconArrowLeft
} from '@tabler/icons-react';
import { useState, useEffect } from 'react';
import { useSearchParams, useRouter } from 'next/navigation';
import { DashboardTable } from '../components/DashboardTable';
import { api } from '../../lib/api';

function RowCarousel({ images, onZoom, fullWidth }: { images: string[], onZoom: (url: string) => void, fullWidth?: boolean }) {
  const [activeSlide, setActiveSlide] = useState(0);

  if (!images || images.length === 0) {
    return (
      <Center style={{ width: fullWidth ? '100%' : 160, height: fullWidth ? 180 : 90, borderRadius: 4, backgroundColor: '#2a2a2a', border: '1px solid #333' }}>
        <Text size="xs" c="dimmed" fw={700}>SIN CAPTURA</Text>
      </Center>
    );
  }

  return (
    <Box style={{ position: 'relative', width: fullWidth ? '100%' : 160, height: fullWidth ? 180 : 90, borderRadius: 4, overflow: 'hidden', border: '1px solid #333', backgroundColor: '#000' }}>
      <Carousel
        withIndicators={false}
        slideSize="100%"
        height={fullWidth ? 180 : 90}
        slideGap="xs"
        onSlideChange={setActiveSlide}
        nextControlIcon={<IconChevronRight size={16} />}
        previousControlIcon={<IconChevronLeft size={16} />}
        styles={{
          control: {
            backgroundColor: 'rgba(0,0,0,0.6)',
            color: 'white',
            border: 'none',
            '&:hover': { backgroundColor: 'rgba(0,0,0,0.8)' },
          },
        }}
      >
        {images.map((img, i) => (
          <Carousel.Slide key={i}>
            <Image src={img} alt={`Captura de acceso ${i + 1}`} fallbackSrc="https://placehold.co/160x90/222/555?text=SIN+FOTO" fit="cover" h="100%" style={{ cursor: 'pointer' }} onClick={() => onZoom(img)} />
          </Carousel.Slide>
        ))}
      </Carousel>
      {images.length > 1 && (
        <Box style={{ position: 'absolute', bottom: 4, right: 4, backgroundColor: 'rgba(0,0,0,0.7)', padding: '2px 6px', borderRadius: 10, zIndex: 2, pointerEvents: 'none' }}>
          <Text size="10px" fw={700} c="white">{activeSlide + 1}/{images.length}</Text>
        </Box>
      )}
    </Box>
  );
}

function AccesosContent() {
  const router = useRouter();
  const [selectedImage, setSelectedImage] = useState<string | null>(null);
  const [opened, { open, close }] = useDisclosure(false);
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
    fetchAccesos(0);
  }, [searchParams]);

  const fetchAccesos = async (currentSkip: number) => {
    if (loading) return;
    setLoading(true);
    try {
      const s = searchParams.get('s') || undefined;
      const start = searchParams.get('start') || undefined;
      const end = searchParams.get('end') || undefined;
      
      const [response, shifts] = await Promise.all([
        api.getAccesos(s, start, end, currentSkip, LIMIT),
        currentSkip === 0 ? api.getTurnos(s, start, end) : Promise.resolve([])
      ]);

      const mapped = response.map(item => ({
        id: item.id,
        tipo: 'acceso',
        sujeto: item.nombre,
        rol: item.cedula,
        fecha: formatDate24(item.timestamp),
        timestamp: item.timestamp,
        fotos: [], 
        porton: item.tipo,
        registrado_por: 'Sistema',
        observaciones: '-'
      }));

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

      if (mapped.length < LIMIT) {
        setHasMore(false);
      }
    } catch (error) {
      console.error('Error fetching accesos:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleLoadMore = () => {
    if (hasMore && !loading) {
      const nextSkip = skip + LIMIT;
      setSkip(nextSkip);
      fetchAccesos(nextSkip);
    }
  };

  const handleShowImage = (url: string | null) => {
    setSelectedImage(url);
    open();
  };

  const columns = [
    { key: 'num', label: '#', width: 40, textAlign: 'center' as const },
    { key: 'foto', label: 'Fotos', width: 200 },
    { key: 'persona', label: 'Persona' },
    { key: 'fecha', label: 'Fecha/Hora' },
    { key: 'porton', label: 'Portón', textAlign: 'center' as const },
    { key: 'registrado', label: 'Registrado Por' },
    { key: 'obs', label: 'Observaciones' },
  ];

  const renderRow = (item: any, index: number, runningCounter: number) => (
    <Table.Tr key={`acceso-${item.id}`}>
      <Table.Td style={{ textAlign: 'center', color: '#888', fontWeight: 500 }}>{runningCounter}</Table.Td>
      <Table.Td><RowCarousel images={item.fotos} onZoom={handleShowImage} /></Table.Td>
      <Table.Td>
        <Stack gap={2}>
          <Text fw={700} c="white" size="md">{item.sujeto}</Text>
          <Text size="xs" c="dimmed" tt="uppercase" fw={600}>{item.rol}</Text>
        </Stack>
      </Table.Td>
      <Table.Td><Text size="sm" fw={500} style={{ opacity: 0.8 }}>{item.fecha}</Text></Table.Td>
      <Table.Td>
        <Group justify="center">
          <Badge variant="filled" size="xl" radius="sm" leftSection={item.porton === 'entrada' ? <IconDoorEnter size={16} /> : <IconDoorExit size={16} />} 
            styles={{ root: { backgroundColor: item.porton === 'entrada' ? '#24cb7c' : '#eceef0', color: item.porton === 'entrada' ? 'white' : '#495057', width: 110, height: 32, fontSize: '12px', border: 'none' } }}
          >
            {item.porton?.toUpperCase()}
          </Badge>
        </Group>
      </Table.Td>
      <Table.Td><Text size="sm" fw={500}>{item.registrado_por}</Text></Table.Td>
      <Table.Td><Text size="sm" fw={800} style={{ letterSpacing: '0.8px', color: '#eee' }}>{item.observaciones}</Text></Table.Td>
    </Table.Tr>
  );

  const renderCard = (item: any) => (
    <Card shadow="none" radius={0} bg="#1e1e1e" style={{ borderBottom: '1px solid #2a2a2a', marginBottom: 4 }} p="md">
      {item.fotos && item.fotos.length > 0 ? (
        <Card.Section>
          <RowCarousel images={item.fotos} onZoom={handleShowImage} fullWidth />
        </Card.Section>
      ) : (
        <Card.Section bg="#25262b" h={140} style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', borderBottom: '1px solid #333' }}>
           <Stack align="center" gap={4}>
             <IconPhoto size={32} color="#444" />
             <Text size="xs" c="dimmed" fw={700}>SIN CAPTURA</Text>
           </Stack>
        </Card.Section>
      )}
      
      <Stack gap="sm" mt="md">
        <Group justify="space-between" align="flex-start">
          <Stack gap={2}>
            <Text fw={800} c="white" size="lg">{item.sujeto}</Text>
            <Text size="xs" c="dimmed" tt="uppercase" fw={600} style={{ letterSpacing: '0.5px' }}>{item.rol}</Text>
          </Stack>
          <Badge variant="filled" size="lg" radius="sm" leftSection={item.porton === 'entrada' ? <IconDoorEnter size={14} /> : <IconDoorExit size={14} />} 
            styles={{ root: { backgroundColor: item.porton === 'entrada' ? '#24cb7c' : '#444', color: 'white', border: 'none' } }}
          >
            {item.porton?.toUpperCase()}
          </Badge>
        </Group>

        <Divider color="#2a2a2a" />

        <Group justify="space-between">
          <Stack gap={0}>
            <Text size="10px" c="dimmed" tt="uppercase" fw={800}>Fecha y Hora</Text>
            <Text size="sm" fw={600} c="white">{item.fecha}</Text>
          </Stack>
          <Stack gap={0} align="flex-end">
            <Text size="10px" c="dimmed" tt="uppercase" fw={800}>Registrado Por</Text>
            <Text size="sm" fw={600} c="white">{item.registrado_por}</Text>
          </Stack>
        </Group>

        {item.observaciones !== '-' && (
           <Box p="xs" bg="#141414" style={{ borderRadius: 4, borderLeft: '3px solid #24cb7c' }}>
             <Text size="xs" c="dimmed" fs="italic">{item.observaciones}</Text>
           </Box>
        )}
      </Stack>
    </Card>
  );

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
            <Title order={2} c="white" style={{ fontFamily: 'Poppins, sans-serif' }}>Registro de Accesos (Portón)</Title>
            <Text size="sm" c="dimmed">Monitoreo de entradas y salidas con captura fotográfica automática.</Text>
          </Box>
        </Group>

        {loading ? (
          <Center h={400}>
            <Stack align="center">
              <Loader color="teal" size="lg" type="bars" />
              <Text c="dimmed" size="sm">Recuperando historial de accesos...</Text>
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

      <Modal opened={opened} onClose={close} size="lg" centered title={<Text fw={700}>Captura de Acceso</Text>} 
        styles={{ content: { backgroundColor: '#141414', color: 'white' }, header: { backgroundColor: '#1e1e1e', borderBottom: '1px solid #2a2a2a' } }}>
        {selectedImage ? (
          <Stack>
            <Image src={selectedImage} alt="Captura de acceso ampliada" radius="md" fallbackSrc="https://placehold.co/640x360/222/555?text=SIN+FOTO" />
            <Group justify="space-between"><Text size="xs" c="dimmed">ID: ACC-2026-XQW - Cámara Portón Principal</Text><ActionIcon variant="light" color="red"><IconTrash size={18} /></ActionIcon></Group>
          </Stack>
        ) : (
          <Center h={300} bg="#000" style={{ borderRadius: 8 }}>
            <Text c="dimmed">Imagen no disponible para este registro</Text>
          </Center>
        )}
      </Modal>
    </Box>
  );
}

export default function AccesosSection() {
  return (
    <Suspense fallback={<Center h={400}><Loader color="teal" size="lg" type="bars" /></Center>}>
      <AccesosContent />
    </Suspense>
  );
}
