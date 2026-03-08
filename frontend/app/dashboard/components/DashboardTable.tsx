"use client";
import { Box, Stack, Table, Text, Group, Paper, Pagination } from '@mantine/core';
import { IconRefresh } from '@tabler/icons-react';
import { useEffect, useRef } from 'react';

interface DashboardTableProps {
  columns: { key: string; label: string; width?: number | string; textAlign?: 'left' | 'center' | 'right' }[];
  data: any[];
  renderRow: (item: any, index: number, runningCounter: number) => React.ReactNode;
  pagination?: { total: number; page: number; onChange: (page: number) => void };
  shiftDivider?: (item: any, index: number) => { fin: string; inicio: string; hora: string } | null;
  verticalSpacing?: number | string;
  renderCard?: (item: any, index: number) => React.ReactNode;
  onLoadMore?: () => void;
  hasMore?: boolean;
}

export function DashboardTable({
  columns,
  data,
  renderRow,
  pagination,
  shiftDivider,
  verticalSpacing = 20,
  renderCard,
  onLoadMore,
  hasMore,
}: DashboardTableProps) {
  const observerRef = useRef<IntersectionObserver | null>(null);
  const sentinelRef = useRef<any>(null);

  // Infinite scroll observer – uses window as root for natural page scroll
  useEffect(() => {
    if (!onLoadMore || !hasMore) return;
    if (observerRef.current) observerRef.current.disconnect();

    observerRef.current = new IntersectionObserver((entries) => {
      if (entries[0].isIntersecting && hasMore) {
        onLoadMore();
      }
    }, { root: null, threshold: 0.1 });

    if (sentinelRef.current) observerRef.current.observe(sentinelRef.current);
    return () => observerRef.current?.disconnect();
  }, [onLoadMore, hasMore, data.length]);

  return (
    <Box className="dashboard-table-container">
      {/* Mobile cards view – shown only on small screens via CSS */}
      {renderCard && (
        <Stack className="mobile-cards-view" gap="xs" p={0}>
          {data.map((item, index) => {
            const shiftInfo = shiftDivider ? shiftDivider(item, index) : null;
            return (
              <Box key={item.id || index}>
                {shiftInfo && (
                  <Paper bg="rgba(40, 190, 100, 0.08)" p="xs" mb="sm" style={{ border: '1px solid rgba(40, 190, 100, 0.2)' }}>
                    <Stack gap={4} align="center">
                      <Text fw={700} size="xs" c="#24cb7c">TURNO: {shiftInfo.inicio} - {shiftInfo.fin}</Text>
                      <Text size="10px" c="dimmed">{shiftInfo.hora}</Text>
                    </Stack>
                  </Paper>
                )}
                {renderCard(item, index)}
              </Box>
            );
          })}
          {/* End of list message for mobile */}
          {!hasMore && data.length > 0 && (
            <Box py="xl">
              <Text ta="center" size="xs" c="dimmed" style={{ opacity: 0.5, letterSpacing: '0.5px' }}>
                FIN DE LA LISTA • {data.length} REGISTROS
              </Text>
            </Box>
          )}
        </Stack>
      )}

      {/* Desktop table view – shown on larger screens via CSS */}
      <Box className="desktop-table-view">
        <Table
          horizontalSpacing="lg"
          styles={{
            thead: { backgroundColor: '#2a2a2a' },
            th: {
              color: '#aaa',
              borderBottom: '1px solid #2a2a2a',
              textTransform: 'uppercase',
              fontSize: '11px',
              fontWeight: 700,
              padding: '12px 20px',
            },
            td: {
              borderBottom: '1px solid #25262b',
              color: '#ccc',
              paddingTop: `${verticalSpacing}px`,
              paddingBottom: `${verticalSpacing}px`,
              paddingLeft: '20px',
              paddingRight: '20px',
            },
            tr: { '&:hover': { backgroundColor: 'rgba(255,255,255,0.01)' } },
          }}
        >
          <Table.Thead>
            <Table.Tr>
              {columns.map((col) => (
                <Table.Th key={col.key} w={col.width} ta={col.textAlign || 'left'}>
                  {col.label}
                </Table.Th>
              ))}
            </Table.Tr>
          </Table.Thead>
          <Table.Tbody>
            {(() => {
              const rows: React.ReactNode[] = [];
              let currentShiftEvents: any[] = [];
              const flushShift = (shiftInfo: any, shiftIdx: number) => {
                const count = currentShiftEvents.length;
                currentShiftEvents.forEach((item, i) => {
                  rows.push(renderRow(item, i, count - i));
                });
                currentShiftEvents = [];
                if (shiftInfo) {
                  rows.push(
                    <Table.Tr key={`turno-${shiftIdx}`} bg="rgba(40, 190, 100, 0.08)">
                      <Table.Td colSpan={columns.length} p={0}>
                        <Group justify="center" gap="xl" h={60} style={{ color: '#24cb7c' }}>
                          <Group gap={8}>
                            <IconRefresh size={18} stroke={2.5} />
                            <Text fw={700} size="sm">FIN DE TURNO: <Text span c="white" inherit>{shiftInfo.fin}</Text></Text>
                          </Group>
                          <Group gap={8}>
                            <IconRefresh size={18} stroke={2.5} />
                            <Text fw={700} size="sm">INICIO DE TURNO: <Text span c="white" inherit>{shiftInfo.inicio}</Text></Text>
                          </Group>
                          <Text fw={700} size="sm" c="dimmed">{shiftInfo.hora}</Text>
                        </Group>
                      </Table.Td>
                    </Table.Tr>
                  );
                }
              };

              data.forEach((item, index) => {
                const shiftInfo = shiftDivider ? shiftDivider(item, index) : null;
                if (shiftInfo) {
                  flushShift(shiftInfo, index);
                } else {
                  currentShiftEvents.push(item);
                }
              });
              flushShift(null, -1);
              return rows;
            })()}
            {/* End of list message for desktop */}
            {!hasMore && data.length > 0 && (
              <Table.Tr>
                <Table.Td colSpan={columns.length} align="center" py="xl">
                  <Text size="xs" c="dimmed" style={{ opacity: 0.5, letterSpacing: '0.5px' }}>
                    FIN DE LA LISTA • {data.length} REGISTROS
                  </Text>
                </Table.Td>
              </Table.Tr>
            )}
          </Table.Tbody>
        </Table>
      </Box>

      {/* Shared sentinel for infinite scroll (visible in both views) */}
      {hasMore && (
        <Box ref={sentinelRef} py="xl">
          <Group justify="center">
            <Text size="sm" c="dimmed">Cargando más registros...</Text>
          </Group>
        </Box>
      )}

      {/* Pagination controls – only shown when pagination prop is provided */}
      {pagination && (
        <Box p="md" bg="#1e1e1e" style={{ borderTop: '1px solid #2a2a2a' }}>
          <Group justify="space-between">
            <Text size="xs" c="dimmed">Registros del sistema</Text>
            <Pagination
              value={pagination.page}
              onChange={pagination.onChange}
              total={pagination.total}
              color="teal"
              size="sm"
              styles={{
                control: {
                  backgroundColor: '#2a2a2a',
                  border: '1px solid #333',
                  color: 'white',
                  '&:hover': { backgroundColor: '#333' },
                },
              }}
            />
          </Group>
        </Box>
      )}
    </Box>
  );
}
