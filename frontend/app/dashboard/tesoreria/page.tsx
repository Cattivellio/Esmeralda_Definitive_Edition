'use client';

import { 
  Box, Title, Text, Group, Stack, Table, Badge, Card, SimpleGrid, 
  Button, Tabs, ActionIcon, Tooltip, rem, Select, NumberInput, 
  TextInput, Modal, Divider, Loader, Center, ColorSwatch, ColorInput, Switch, Paper, Popover, FileInput
} from '@mantine/core';
import { 
  IconWallet, IconArrowsExchange, IconArrowDownLeft, IconArrowUpRight, 
  IconPlus, IconArrowLeft, IconSettings, IconSearch, IconCalendar, IconUser, 
  IconChevronRight, IconTrash, IconPencil, IconCheck, IconLink, IconChevronDown, IconChevronUp, IconChartPie, IconPhoto
} from '@tabler/icons-react';
import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { api } from '../../lib/api';
import { DashboardTable } from '../components/DashboardTable';
import dayjs from 'dayjs';

export default function TesoreriaPage() {
  const router = useRouter();
  const [activeTab, setActiveTab] = useState<string | null>('movimientos');
  const [loading, setLoading] = useState(true);
  const [cuentas, setCuentas] = useState<any[]>([]);
  const [transacciones, setTransacciones] = useState<any[]>([]);
  
  // Modals
  const [modalTransaccion, setModalTransaccion] = useState(false);
  const [modalMetodoFull, setModalMetodoFull] = useState(false);

  // Form states
  const [nuevaTrans, setNuevaTrans] = useState<any>({ tipo: 'Ingreso', monto: 0, moneda: 'USD', metodo_pago_id: '', metodo_pago_destino_id: '', descripcion: '', justificacion: '', categoria: '', factura_url: '' });
  const [fileToUpload, setFileToUpload] = useState<File | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [nuevoMetodo, setNuevoMetodo] = useState({ nombre: '', moneda: 'USD', color: '#ffffff', activo: true, saldo_inicial: 0 });
  const [editingMetodo, setEditingMetodo] = useState<any>(null);

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

  // Grouped totals calculation
  const totalsByCurrency = cuentas.reduce((acc: any, c) => {
    const cur = c.moneda || 'USD';
    if (!acc[cur]) acc[cur] = 0;
    acc[cur] += c.saldo_actual || 0;
    return acc;
  }, {});

  useEffect(() => {
    fetchData();
  }, [activeTab]);

  const fetchData = async () => {
    setLoading(true);
    try {
      const [c, t, shifts] = await Promise.all([
        api.getTesoreriaCuentas(),
        api.getTesoreriaTransacciones(),
        api.getTurnos()
      ]);
      setCuentas(c);
      
      const combined = [
        ...t.map(item => ({ ...item, timestamp: item.fecha })),
        ...shifts.map((s: any) => ({
          tipo: 'turno',
          timestamp: s.inicio,
          fin_nombre: s.worker_out,
          inicio_nombre: s.worker,
          hora: formatDate24(s.inicio)
        }))
      ];
      combined.sort((a,b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime());
      setTransacciones(combined);
    } catch (error) {
      console.error('Error fetching data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateTransaccion = async () => {
     try {
       setIsUploading(true);
       let finalFacturaUrl = nuevaTrans.factura_url;
       
       if (fileToUpload) {
         const res = await api.uploadFactura(fileToUpload);
         finalFacturaUrl = res.url;
       }

       if (nuevaTrans.tipo === 'Transferencia') {
         await api.createTesoreriaTransferencia({
           metodo_pago_origen_id: parseInt(nuevaTrans.metodo_pago_id),
           metodo_pago_destino_id: parseInt(nuevaTrans.metodo_pago_destino_id || ''),
           monto: nuevaTrans.monto,
           descripcion: nuevaTrans.descripcion
         });
       } else {
         await api.createTesoreriaTransaccion({
           ...nuevaTrans,
           metodo_pago_id: parseInt(nuevaTrans.metodo_pago_id),
           factura_url: finalFacturaUrl,
           usuario_id: JSON.parse(localStorage.getItem('activeUser') || '{}').id || 1
         });
       }
       setModalTransaccion(false);
       setNuevaTrans({ tipo: 'Ingreso', monto: 0, moneda: 'USD', metodo_pago_id: '', metodo_pago_destino_id: '', descripcion: '', justificacion: '', categoria: '', factura_url: '' });
       setFileToUpload(null);
       fetchData();
     } catch (error) {
        console.error(error);
     } finally {
        setIsUploading(false);
     }
  };


  const handleSaveMetodo = async () => {
    try {
      if (editingMetodo) {
        await api.updateMetodoPago(editingMetodo.id, nuevoMetodo);
      } else {
        await api.createMetodoPago(nuevoMetodo);
      }
      setModalMetodoFull(false);
      fetchData();
    } catch (error) {
      console.error(error);
    }
  };

  const handleDeleteMetodo = async (id: number) => {
    if (confirm('¿Estás seguro de eliminar este método/cuenta?')) {
      try {
        await api.deleteMetodoPago(id);
        fetchData();
      } catch (error) {
        console.error(error);
      }
    }
  };

  const renderTransactionRow = (item: any, index: number, counter: number) => {
    const isIngreso = item.tipo === 'Ingreso';
    const isEgreso = item.tipo === 'Egreso';
    const isTransf = item.tipo === 'Transferencia';

    return (
      <Table.Tr key={item.id}>
        <Table.Td style={{ color: '#888' }}>{counter}</Table.Td>
        <Table.Td>
          <Group gap="xs">
            {isIngreso && <IconArrowDownLeft color="#36ea7e" size={16} />}
            {isEgreso && <IconArrowUpRight color="#ff6b6b" size={16} />}
            {isTransf && <IconArrowsExchange color="#339af0" size={16} />}
            <Text size="xs" fw={700} tt="uppercase" c={isIngreso ? 'green' : isEgreso ? 'red' : 'blue'}>
              {item.tipo}
            </Text>
          </Group>
        </Table.Td>
        <Table.Td>
          <Stack gap={0}>
            <Group gap="xs">
              <Text size="sm" fw={700} c="white">{item.descripcion}</Text>
              {item.categoria && <Badge size="xs" color="gray" variant="dot">{item.categoria}</Badge>}
              {item.factura_url && (
                <ActionIcon 
                  size="xs" 
                  variant="subtle" 
                  color="blue" 
                  component="a" 
                  href={`http://${window.location.hostname}:8000${item.factura_url}`} 
                  target="_blank"
                >
                  <IconPhoto size={12} />
                </ActionIcon>
              )}
            </Group>
            {item.justificacion && <Text size="10px" c="dimmed">{item.justificacion}</Text>}
          </Stack>
        </Table.Td>
        <Table.Td>
           <Text size="sm" fw={800} c={isIngreso ? '#36ea7e' : isEgreso ? '#ff6b6b' : 'white'}>
             {isEgreso ? '-' : ''}{item.monto.toLocaleString()} {item.moneda}
           </Text>
        </Table.Td>
        <Table.Td>
           <Group gap={4}>
             <Badge size="xs" color="gray" variant="outline">
               {item.metodo_pago_nombre}
             </Badge>
             {isTransf && (
               <>
                 <IconChevronRight size={10} color="#888" />
                 <Badge size="xs" color="blue" variant="outline">
                    {item.metodo_pago_destino_nombre}
                 </Badge>
               </>
             )}
           </Group>
        </Table.Td>
        <Table.Td>
          <Text size="xs" c="dimmed">{dayjs(item.fecha).format('DD/MM/YY HH:mm')}</Text>
        </Table.Td>
        <Table.Td>
           <Text size="xs" fw={500}>{item.referencia || '-'}</Text>
        </Table.Td>
      </Table.Tr>
    );
  };

  const columns = [
    { key: 'num', label: '#', width: 40 },
    { key: 'tipo', label: 'Tipo', width: 120 },
    { key: 'concepto', label: 'Concepto' },
    { key: 'monto', label: 'Monto', width: 120 },
    { key: 'cuenta', label: 'Método/Cuenta', width: 180 },
    { key: 'fecha', label: 'Fecha/Hora', width: 140 },
    { key: 'ref', label: 'Referencia', width: 100 },
  ];

  if (loading && cuentas.length === 0) {
    return (
      <Center h={400}>
        <Loader color="teal" size="lg" type="bars" />
      </Center>
    );
  }

  return (
    <Box>
      <Group justify="space-between" align="flex-start" mb="xl">
        <Group align="flex-start" gap="lg">
          <ActionIcon 
            variant="light" 
            color="teal" 
            size="xl" 
            onClick={() => router.push('/dashboard/configuracion')}
            style={{ marginTop: 5 }}
          >
            <IconArrowLeft size={24} />
          </ActionIcon>
          <Box>
            <Title order={2} c="white" style={{ fontFamily: 'Poppins, sans-serif' }}>Tesorería</Title>
            <Text size="sm" c="dimmed">Control unificado de métodos de pago y saldos de caja.</Text>
          </Box>
        </Group>

        <Group>
          <Button 
            variant="gradient" 
            gradient={{ from: 'teal', to: 'green' }}
            leftSection={<IconPlus size={18} />}
            onClick={() => setModalTransaccion(true)}
          >
            NUEVO MOVIMIENTO
          </Button>
        </Group>
      </Group>

      <Paper bg="#1e1e1e" p="md" radius="md" mb="xl" style={{ border: '1px solid #2a2a2a' }}>
        <Group gap="xs" mb="md">
          <IconChartPie size={20} color="#36ea7e" />
          <Text fw={700} c="white">BALANCE POR MONEDA</Text>
          <Text size="10px" c="dimmed">(Click en el monto para ver el desglose)</Text>
        </Group>
        
        <SimpleGrid cols={{ base: 1, sm: 2, md: 3 }} spacing="lg">
          {Object.entries(totalsByCurrency).map(([currency, total]: [string, any]) => (
            <Popover key={currency} width={250} position="bottom" withArrow shadow="md" styles={{ dropdown: { backgroundColor: '#252525', border: '1px solid #333' } }}>
              <Popover.Target>
                <Group 
                  p="xs" 
                  style={{ 
                    borderLeft: '3px solid #36ea7e', 
                    background: 'rgba(54, 234, 126, 0.05)', 
                    borderRadius: '4px',
                    cursor: 'pointer'
                  }}
                >
                  <Box>
                    <Text size="xs" c="dimmed" fw={700} tt="uppercase">TOTAL {currency}</Text>
                    <Title order={2} c="white">{total.toLocaleString()} <Text span size="xs" fw={400}>{currency}</Text></Title>
                  </Box>
                </Group>
              </Popover.Target>
              <Popover.Dropdown>
                <Stack gap="xs">
                  <Text size="xs" fw={700} c="dimmed" tt="uppercase" mb={4}>Detalle {currency}</Text>
                  {cuentas.filter(c => c.moneda === currency).map(c => (
                    <Group key={c.id} justify="space-between" wrap="nowrap">
                      <Text size="sm" fw={500} c="white">{c.nombre}</Text>
                      <Text size="sm" fw={700} c="#36ea7e">{c.saldo_actual.toLocaleString()}</Text>
                    </Group>
                  ))}
                  <Divider color="#444" my={4} />
                  <Group justify="space-between">
                    <Text size="xs" fw={700} c="white">TOTAL</Text>
                    <Text size="xs" fw={900} c="#36ea7e">{total.toLocaleString()} {currency}</Text>
                  </Group>
                </Stack>
              </Popover.Dropdown>
            </Popover>
          ))}
        </SimpleGrid>
      </Paper>

      <Tabs value={activeTab} onChange={setActiveTab} color="teal" variant="pills" radius="md">
        <Tabs.List mb="md">
          <Tabs.Tab value="movimientos" leftSection={<IconCalendar size={16} />}>Movimientos</Tabs.Tab>
          <Tabs.Tab value="metodos" leftSection={<IconSettings size={16} />}>Configuración de Métodos</Tabs.Tab>
        </Tabs.List>

        <Tabs.Panel value="movimientos">
          <DashboardTable 
            columns={columns}
            data={transacciones}
            renderRow={renderTransactionRow}
            shiftDivider={(item) => item.tipo === 'turno' ? { fin: item.fin_nombre, inicio: item.inicio_nombre, hora: item.hora } : null}
          />
        </Tabs.Panel>

        <Tabs.Panel value="metodos">
           <Card bg="#1e1e1e" p="xl" radius="md">
              <Group justify="space-between" mb="lg">
                <Title order={4} c="white">Gestión de Métodos y Cuentas</Title>
                <Button variant="gradient" size="xs" gradient={{ from: 'teal', to: 'blue' }} leftSection={<IconPlus size={16} />} onClick={() => {
                  setEditingMetodo(null);
                  setNuevoMetodo({ nombre: '', moneda: 'USD', color: '#ffffff', activo: true, saldo_inicial: 0 });
                  setModalMetodoFull(true);
                }}>AGREGAR MÉTODO</Button>
              </Group>
              <SimpleGrid cols={{ base: 1, sm: 2, md: 3 }}>
                {cuentas.map(m => (
                  <Card key={m.id} bg="#252525" p="md" radius="sm">
                    <Group justify="space-between" mb="xs">
                      <Group gap="xs">
                         <ColorSwatch color={m.color} size={12} />
                         <Text fw={700} size="sm" c="white">{m.nombre}</Text>
                      </Group>
                      <Badge size="xs" variant="light" color={m.activo ? 'teal' : 'red'}>{m.activo ? 'Activo' : 'Inactivo'}</Badge>
                    </Group>
                    
                    <Group justify="space-between" mb="xs">
                       <Text size="10px" c="dimmed">{m.moneda}</Text>
                       <Group gap={4}>
                         <ActionIcon variant="transparent" color="blue" size="sm" onClick={() => {
                            setEditingMetodo(m);
                            setNuevoMetodo({ nombre: m.nombre, moneda: m.moneda, color: m.color, activo: m.activo, saldo_inicial: m.saldo_inicial });
                            setModalMetodoFull(true);
                         }}><IconPencil size={14} /></ActionIcon>
                         <ActionIcon variant="transparent" color="red" size="sm" onClick={() => handleDeleteMetodo(m.id)}><IconTrash size={14} /></ActionIcon>
                       </Group>
                    </Group>

                    <Divider color="#333" mb="sm" />
                    
                    <Stack gap={2}>
                      <Text size="10px" c="dimmed" tt="uppercase">Saldo Actual</Text>
                      <Text size="sm" fw={700} c="teal">{m.saldo_actual.toLocaleString()} {m.moneda}</Text>
                    </Stack>
                  </Card>
                ))}
              </SimpleGrid>
           </Card>
        </Tabs.Panel>
      </Tabs>

      {/* MODALS */}
      
      {/* Nuevo Movimiento */}
      <Modal opened={modalTransaccion} onClose={() => setModalTransaccion(false)} title="Registrar Movimiento" centered size="lg" styles={{ content: { backgroundColor: '#1e1e1e', color: 'white' }, header: { backgroundColor: '#1e1e1e' } }}>
         <Stack gap="md">
            <Group grow>
              <Select label="Tipo de Movimiento" data={['Ingreso', 'Egreso', 'Transferencia']} value={nuevaTrans.tipo} onChange={(v) => setNuevaTrans({ ...nuevaTrans, tipo: v || 'Ingreso' })} styles={{ label: { color: 'white' }, input: { backgroundColor: 'white', border: '1px solid #ced4da', color: 'black' } }} />
              <Select label={nuevaTrans.tipo === 'Transferencia' ? "Método Origen" : "Método/Cuenta"} data={cuentas.map(c => ({ value: c.id.toString(), label: `${c.nombre} (${c.moneda})` }))} value={nuevaTrans.metodo_pago_id} onChange={(v) => setNuevaTrans({ ...nuevaTrans, metodo_pago_id: v || '' })} styles={{ label: { color: 'white' }, input: { backgroundColor: 'white', border: '1px solid #ced4da', color: 'black' } }} />
            </Group>
           
            {nuevaTrans.tipo === 'Transferencia' && (
              <Select 
                label="Método Destino" 
                placeholder="Seleccione destino"
                data={cuentas.filter(c => c.id.toString() !== nuevaTrans.metodo_pago_id).map(c => ({ value: c.id.toString(), label: `${c.nombre} (${c.moneda})` }))} 
                value={nuevaTrans.metodo_pago_destino_id} 
                onChange={(v) => setNuevaTrans({ ...nuevaTrans, metodo_pago_destino_id: v || '' })} 
                styles={{ label: { color: 'white' }, input: { backgroundColor: 'white', border: '1px solid #ced4da', color: 'black' } }} 
              />
            )}

            <Group grow>
              <NumberInput label="Monto" value={nuevaTrans.monto} onChange={(v) => setNuevaTrans({ ...nuevaTrans, monto: Number(v) })} styles={{ label: { color: 'white' }, input: { backgroundColor: 'white', border: '1px solid #ced4da', color: 'black' } }} />
              <TextInput label="Concepto / Referencia" placeholder="Ej: Pago servicio, Transferencia interna..." value={nuevaTrans.descripcion} onChange={(e) => setNuevaTrans({ ...nuevaTrans, descripcion: e.target.value })} styles={{ label: { color: 'white' }, input: { backgroundColor: 'white', border: '1px solid #ced4da', color: 'black' } }} />
            </Group>

            {nuevaTrans.tipo === 'Egreso' && (
              <Group grow>
                <Select 
                  label="Categoría de Gasto" 
                  data={['Suministros', 'Servicios', 'Comida/Bebida', 'Mantenimiento', 'Sueldos', 'Publicidad', 'Otros']} 
                  placeholder="Elija una categoría"
                  value={nuevaTrans.categoria}
                  onChange={(v) => setNuevaTrans({...nuevaTrans, categoria: v})}
                  styles={{ label: { color: 'white' }, input: { backgroundColor: 'white', border: '1px solid #ced4da', color: 'black' } }}
                />
                <FileInput 
                  label="Foto Factura / Comprobante" 
                  placeholder="Subir archivo" 
                  leftSection={<IconPhoto size={16} />}
                  value={fileToUpload}
                  onChange={setFileToUpload}
                  styles={{ label: { color: 'white' }, input: { backgroundColor: 'white', border: '1px solid #ced4da', color: 'black' } }}
                />
              </Group>
            )}
           
            {nuevaTrans.tipo !== 'Transferencia' && (
              <TextInput label="Justificación Detallada" placeholder="Opcional" value={nuevaTrans.justificacion} onChange={(e) => setNuevaTrans({ ...nuevaTrans, justificacion: e.target.value })} styles={{ label: { color: 'white' }, input: { backgroundColor: 'white', border: '1px solid #ced4da', color: 'black' } }} />
            )}

           <Button fullWidth onClick={handleCreateTransaccion} loading={isUploading} variant="gradient" gradient={nuevaTrans.tipo === 'Transferencia' ? { from: 'blue', to: 'cyan' } : { from: 'teal', to: 'green' }} mt="md">
             {nuevaTrans.tipo === 'Transferencia' ? 'EJECUTAR TRANSFERENCIA' : 'REGISTRAR MOVIMIENTO'}
           </Button>
         </Stack>
      </Modal>


      {/* Nuevo/Editar Método Full */}
      <Modal opened={modalMetodoFull} onClose={() => setModalMetodoFull(false)} title={editingMetodo ? "Editar Método/Cuenta" : "Nuevo Método/Cuenta"} centered styles={{ content: { backgroundColor: '#1e1e1e', color: 'white' }, header: { backgroundColor: '#1e1e1e' } }}>
         <Stack gap="md">
            <TextInput label="Nombre" placeholder="Zelle, Efectivo, etc." value={nuevoMetodo.nombre} onChange={(e) => setNuevoMetodo({ ...nuevoMetodo, nombre: e.target.value })} styles={{ label: { color: 'white' }, input: { backgroundColor: 'white', border: '1px solid #ced4da', color: 'black' } }} />
            <Select label="Moneda" data={['USD', 'VES']} value={nuevoMetodo.moneda} onChange={(v) => setNuevoMetodo({ ...nuevoMetodo, moneda: v || 'USD' })} styles={{ label: { color: 'white' }, input: { backgroundColor: 'white', border: '1px solid #ced4da', color: 'black' } }} />
            {!editingMetodo && (
              <NumberInput label="Saldo Inicial" value={nuevoMetodo.saldo_inicial} onChange={(v) => setNuevoMetodo({ ...nuevoMetodo, saldo_inicial: Number(v) })} styles={{ label: { color: 'white' }, input: { backgroundColor: 'white', border: '1px solid #ced4da', color: 'black' } }} />
            )}
            <ColorInput label="Color Identificador" value={nuevoMetodo.color} onChange={(v) => setNuevoMetodo({ ...nuevoMetodo, color: v })} styles={{ label: { color: 'white' }, input: { backgroundColor: 'white', border: '1px solid #ced4da', color: 'black' } }} />
           <Switch label="Activo" checked={nuevoMetodo.activo} onChange={(e) => setNuevoMetodo({ ...nuevoMetodo, activo: e.currentTarget.checked })} color="teal" />
           <Button fullWidth onClick={handleSaveMetodo} variant="gradient" gradient={{ from: 'teal', to: 'blue' }} mt="md">{editingMetodo ? "ACTUALIZAR" : "CREAR"}</Button>
         </Stack>
      </Modal>
    </Box>
  );
}
