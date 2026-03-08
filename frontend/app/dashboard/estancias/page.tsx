'use client';

import { 
  Box, Title, Text, Badge, Group, ActionIcon, Image, Modal, Stack, Tooltip, Table, Loader, Center, Card, Divider
} from '@mantine/core';
import { Carousel } from '@mantine/carousel';
import { useDisclosure } from '@mantine/hooks';
import { 
  IconChevronRight, IconChevronLeft, IconTrash, IconPhoto
} from '@tabler/icons-react';
import { useState, useEffect } from 'react';
import { useSearchParams } from 'next/navigation';
import { DashboardTable } from '../components/DashboardTable';
import { api } from '../../lib/api';

function RowCarousel({ images, onZoom, fullWidth }: { images: string[], onZoom: (url: string) => void, fullWidth?: boolean }) {
  const [activeSlide, setActiveSlide] = useState(0);

  if (!images || images.length === 0) {
    return (
      <Center style={{ width: fullWidth ? '100%' : 160, height: fullWidth ? 180 : 90, borderRadius: 4, backgroundColor: '#2a2a2a', border: '1px solid #333' }}>
        <Text size="xs" c="dimmed" fw={700}>SIN FOTOS</Text>
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
            <Image src={img} fallbackSrc="https://placehold.co/160x90/222/555?text=SIN+FOTO" fit="cover" h="100%" style={{ cursor: 'pointer' }} onClick={() => onZoom(img)} />
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

export default function EstanciasSection() {
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
    fetchEstancias(0);
  }, [searchParams]);

  const fetchEstancias = async (currentSkip: number) => {
    if (loading) return;
    setLoading(true);
    try {
      const s = searchParams.get('s') || undefined;
      const start = searchParams.get('start') || undefined;
      const end = searchParams.get('end') || undefined;
      const response = await api.getEstanciasHistorial(s, start, end, currentSkip, LIMIT);
      
      if (currentSkip === 0) {
        setData(response);
      } else {
        setData(prev => [...prev, ...response]);
      }

      if (response.length < LIMIT) {
        setHasMore(false);
      }
    } catch (error) {
      console.error('Error fetching estancias:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleLoadMore = () => {
    if (hasMore && !loading) {
      const nextSkip = skip + LIMIT;
      setSkip(nextSkip);
      fetchEstancias(nextSkip);
    }
  };

  const columns = [
    { key: 'num', label: '#', width: 40, textAlign: 'center' as const },
    { key: 'fotos', label: 'Fotos', width: 200 },
    { key: 'tipo', label: 'Tipo' },
    { key: 'hab', label: 'Habitación', textAlign: 'center' as const },
    { key: 'fecha', label: 'Fecha/Hora' },
    { key: 'estado', label: 'Estado', textAlign: 'center' as const },
    { key: 'cat', label: 'Categoría' },
    { key: 'monto', label: 'Monto', textAlign: 'right' as const },
  ];

  const handleShowImage = (url: string | null) => {
    setSelectedImage(url);
    open();
  };

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
             <Text size="xs" c="dimmed" fw={700}>SIN FOTOS</Text>
           </Stack>
        </Card.Section>
      )}

      <Stack gap="sm" mt="md">
        <Group justify="space-between" align="flex-start">
          <Stack gap={2}>
            <Text fw={800} c="white" size="lg">{item.cliente}</Text>
            <Text size="xs" c="dimmed" tt="uppercase" fw={600}>{item.label}</Text>
          </Stack>
          <Badge variant="filled" size="xl" radius="sm"
            styles={{ root: { backgroundColor: item.estado === 'ACTIVA' ? '#24cb7c' : '#444', color: 'white', border: 'none', height: 32 } }}
          >
            {item.estado}
          </Badge>
        </Group>

        <Divider color="#2a2a2a" />

        <Group justify="space-between">
           <Group gap="xs">
             <Box bg="#24cb7c" w={4} h={24} style={{ borderRadius: 2 }} />
             <Stack gap={0}>
               <Text size="10px" c="dimmed" tt="uppercase" fw={800}>Habitación</Text>
               <Text fw={800} size="xl" c="white" style={{ lineHeight: 1 }}>{item.hab}</Text>
             </Stack>
           </Group>
           <Stack gap={0} align="flex-end">
             <Text size="10px" c="dimmed" tt="uppercase" fw={800}>Monto Total</Text>
             <Text fw={800} size="xl" c="#24cb7c" style={{ lineHeight: 1 }}>${item.monto}</Text>
           </Stack>
        </Group>

        <Group justify="space-between">
           <Stack gap={0}>
             <Text size="10px" c="dimmed" tt="uppercase" fw={800}>Fecha Entrada</Text>
             <Text size="xs" fw={600} c="white" style={{ opacity: 0.8 }}>{formatDate24(item.fecha)}</Text>
           </Stack>
           <Stack gap={0} align="flex-end">
             <Text size="10px" c="dimmed" tt="uppercase" fw={800}>Categoría</Text>
             <Text size="xs" fw={600} c="white">{item.cat}</Text>
           </Stack>
        </Group>
      </Stack>
    </Card>
  );

  const renderRow = (item: any, index: number, runningCounter: number) => (
    <Table.Tr key={`estancia-${item.id}`}>
      <Table.Td style={{ textAlign: 'center', color: '#888', fontWeight: 500 }}>{runningCounter}</Table.Td>
      <Table.Td><RowCarousel images={item.fotos} onZoom={handleShowImage} /></Table.Td>
      <Table.Td>
        <Stack gap={2}>
           <Text size="sm" c="white" fw={700}>{item.cliente}</Text>
           <Text size="xs" c="dimmed">{item.label}</Text>
        </Stack>
      </Table.Td>
      <Table.Td style={{ textAlign: 'center' }}><Text fw={700} size="xl" c="white" style={{ fontSize: '20px' }}>{item.hab}</Text></Table.Td>
      <Table.Td><Text size="sm" style={{ opacity: 0.8 }}>{formatDate24(item.fecha)}</Text></Table.Td>
      <Table.Td style={{ textAlign: 'center' }}>
        <Badge variant="filled" radius="sm" size="sm"
          styles={{ root: { backgroundColor: item.estado === 'ACTIVA' ? '#e6fcf5' : '#f1f3f5', color: item.estado === 'ACTIVA' ? '#099268' : '#868e96', fontWeight: 700, border: 'none' } }}
        >
          {item.estado}
        </Badge>
      </Table.Td>
      <Table.Td><Text size="sm" c="dimmed">{item.cat}</Text></Table.Td>
      <Table.Td style={{ textAlign: 'right' }}><Text fw={700} size="md" c="white">${item.monto}</Text></Table.Td>
    </Table.Tr>
  );

  const getShiftDivider = (item: any) => {
    if (item.tipo === 'turno') {
      return { fin: item.fin, inicio: item.inicio, hora: item.hora };
    }
    return null;
  };

  return (
    <Box>
      <Stack gap="xl">
        <Box pb="md" mb="xl">
          <Title order={2} c="white" style={{ fontFamily: 'Poppins, sans-serif' }}>Control de Estancias</Title>
          <Text size="sm" c="dimmed">Historial de hospedajes unificado bajo el mismo estándar visual.</Text>
        </Box>

        {loading ? (
          <Center h={400}>
            <Stack align="center">
              <Loader color="teal" size="lg" type="bars" />
              <Text c="dimmed" size="sm">Cargando historial de estancias...</Text>
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

      <Modal opened={opened} onClose={close} size="lg" centered title={<Text fw={700}>Captura Registrada</Text>}
        styles={{ content: { backgroundColor: '#141414', color: 'white' }, header: { backgroundColor: '#1e1e1e', borderBottom: '1px solid #2a2a2a' } }}>
        {selectedImage && (
          <Stack>
            <Image src={selectedImage} radius="md" />
            <Group justify="space-between"><Text size="xs" c="dimmed">Seguridad - Captura de Portón</Text><ActionIcon variant="light" color="red"><IconTrash size={18} /></ActionIcon></Group>
          </Stack>
        )}
      </Modal>
    </Box>
  );
}
