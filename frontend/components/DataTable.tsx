'use client';

import { Table, ScrollArea, Text, Group, TextInput, Paper, Box, Pagination, Select, ActionIcon, Button, Tooltip } from '@mantine/core';
import { IconSearch, IconFilter, IconMaximize, IconMinimize } from '@tabler/icons-react';
import { useState, useEffect, useMemo } from 'react';

interface Column {
  key: string;
  label: string;
  render?: (value: any, row: any) => React.ReactNode;
  width?: string | number;
}

interface FilterOption {
  value: string;
  label: string;
}

interface DataTableProps {
  columns: Column[];
  data: any[];
  loading?: boolean;
  pageSize?: number;
  maxHeight?: number | string;
  withSearch?: boolean;
  searchPlaceholder?: string;
  filterOptions?: FilterOption[];
  filterKey?: string; // Key in data to filter by (e.g., 'tipo')
  onFullScreenToggle?: (isFull: boolean) => void;
  isFullScreen?: boolean;
}

export default function DataTable({ 
  columns, 
  data, 
  loading, 
  pageSize = 10, 
  maxHeight = 500,
  withSearch = true,
  searchPlaceholder = "Buscar...",
  filterOptions,
  filterKey,
  onFullScreenToggle,
  isFullScreen = false
}: DataTableProps) {
  const [search, setSearch] = useState('');
  const [filter, setFilter] = useState<string>('all');
  const [page, setPage] = useState(1);

  // Reset page when search or filter changes
  useEffect(() => {
    setPage(1);
  }, [search, filter]);

  const filteredData = useMemo(() => {
    return data.filter((item) => {
      // 1. Search filter
      const matchesSearch = Object.values(item).some(
        (value) => value && value.toString().toLowerCase().includes(search.toLowerCase())
      ) || (item.pagos && Object.keys(item.pagos).some(k => k.toLowerCase().includes(search.toLowerCase())));

      // 2. Type/Category filter
      const matchesFilter = filter === 'all' || !filterKey || item[filterKey] === filter;

      return matchesSearch && matchesFilter;
    });
  }, [data, search, filter, filterKey]);

  const totalPages = Math.ceil(filteredData.length / pageSize);
  
  const paginatedData = useMemo(() => {
    const start = (page - 1) * pageSize;
    const end = start + pageSize;
    return filteredData.slice(start, end);
  }, [filteredData, page, pageSize]);

  return (
    <Box>
      <Group mb="md" gap="xs" wrap="nowrap">
        {withSearch && (
          <TextInput
            placeholder={searchPlaceholder}
            leftSection={<IconSearch size={18} />}
            value={search}
            onChange={(e) => setSearch(e.currentTarget.value)}
            flex={1}
            styles={{
              input: { 
                backgroundColor: '#1a1b1e', 
                color: 'white', 
                border: '1px solid #2C2E33',
                height: '36px',
                fontSize: '14px'
              }
            }}
          />
        )}

        {filterOptions && (
          <Select
            placeholder="Filtrar"
            leftSection={<IconFilter size={16} />}
            data={[{ value: 'all', label: 'Todo' }, ...filterOptions]}
            value={filter}
            onChange={(v) => setFilter(v || 'all')}
            style={{ width: 150 }}
            styles={{
              input: { 
                backgroundColor: '#1a1b1e', 
                color: 'white', 
                border: '1px solid #2C2E33',
                height: '36px',
                fontSize: '13px'
              }
            }}
          />
        )}

        {onFullScreenToggle && (
          <Tooltip label={isFullScreen ? "Salir pantalla completa" : "Pantalla completa"}>
            <ActionIcon 
              variant="light" 
              color="gray" 
              size="36px"
              onClick={() => onFullScreenToggle(!isFullScreen)}
              style={{ border: '1px solid #2C2E33', backgroundColor: '#1a1b1e' }}
            >
              {isFullScreen ? <IconMinimize size={18} /> : <IconMaximize size={18} />}
            </ActionIcon>
          </Tooltip>
        )}
      </Group>

      <style dangerouslySetInnerHTML={{ __html: `
        .excel-table {
          width: 100% !important;
          min-width: 100% !important;
          table-layout: auto !important;
          border-collapse: collapse !important;
        }
        .excel-table th { 
          background-color: #25262b !important; 
          border-right: 1px solid #444 !important;
          border-bottom: 2px solid #555 !important;
          padding: 8px 12px !important;
          white-space: nowrap;
        }
        .excel-table td { 
          border-right: 1px solid #333 !important;
          border-bottom: 1px solid #333 !important;
          padding: 6px 12px !important;
          font-size: 13px !important;
          vertical-align: middle !important;
        }
        .excel-table tr:nth-of-type(odd) td { background-color: #1a1b1e !important; }
        .excel-table tr:nth-of-type(even) td { background-color: #141517 !important; }
        .excel-table tr:hover td { background-color: #2c2e33 !important; }

        /* Ensure ScrollArea viewport takes full width */
        [data-scroll-area-viewport] > div {
          display: block !important;
          width: 100% !important;
        }
      `}} />

      <Paper 
        radius="md" 
        withBorder 
        style={{ 
          backgroundColor: '#1a1b1e', 
          borderColor: '#444',
          overflow: 'hidden',
          width: '100%'
        }}
      >
        <ScrollArea h={isFullScreen ? 'calc(100vh - 280px)' : maxHeight} type="auto">
          {loading ? (
            <Box style={{ height: 200 }} />
          ) : (
            <Table 
              className="excel-table"
              verticalSpacing="xs" 
              horizontalSpacing="md"
              withColumnBorders
              withTableBorder
              styles={{
                table: { width: '100% !important', minWidth: '100%', color: '#e0e0e0', borderCollapse: 'collapse', borderSpacing: 0, border: '1px solid #444' },
                th: { color: '#fff !important', fontWeight: 700, textTransform: 'uppercase', fontSize: '11px', letterSpacing: '0.8px' },
              }}
            >
              <Table.Thead>
                <Table.Tr>
                  {columns.map((col) => (
                    <Table.Th key={col.key} style={{ width: col.width }}>{col.label}</Table.Th>
                  ))}
                </Table.Tr>
              </Table.Thead>
              <Table.Tbody>
                {paginatedData.length > 0 ? (
                  paginatedData.map((row, index) => (
                    <Table.Tr key={row.id || index}>
                      {columns.map((col) => (
                        <Table.Td key={col.key}>
                          <div style={{ minWidth: col.key.includes('pagos') ? '100px' : 'auto' }}>
                            {col.render ? col.render(col.key.startsWith('pagos.') ? row.pagos?.[col.key.split('.')[1]] : row[col.key], row) : row[col.key]}
                          </div>
                        </Table.Td>
                      ))}
                    </Table.Tr>
                  ))
                ) : (
                  <Table.Tr>
                    <Table.Td colSpan={columns.length} align="center" py="xl">
                      <Text c="dimmed" fs="italic">No se encontraron registros</Text>
                    </Table.Td>
                  </Table.Tr>
                )}
              </Table.Tbody>
            </Table>
          )}
        </ScrollArea>
      </Paper>

      {totalPages > 1 && (
        <Group justify="center" mt="xl">
          <Pagination 
            total={totalPages} 
            value={page} 
            onChange={setPage} 
            color="teal"
            size="md"
            radius="md"
            styles={{
              control: { 
                backgroundColor: '#1a1b1e', 
                border: '1px solid #333',
                color: 'white',
                '&[data-active]': {
                  background: 'linear-gradient(135deg, #36ea7e 0%, #11998e 100%)',
                  border: 'none'
                }
              }
            }}
          />
        </Group>
      )}
    </Box>
  );
}
