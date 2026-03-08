'use client';

import { Modal, Text, Group, Button } from '@mantine/core';
import { IconMaximize, IconMinimize } from '@tabler/icons-react';
import { useState } from 'react';
import DataTable from './DataTable';

interface Column {
  key: string;
  label: string;
  render?: (value: any, row: any) => React.ReactNode;
}

interface DataTableModalProps {
  opened: boolean;
  onClose: () => void;
  title: string;
  columns: Column[];
  data: any[];
  loading?: boolean;
  pageSize?: number;
}

export default function DataTableModal({ 
  opened, 
  onClose, 
  title, 
  columns, 
  data, 
  loading,
  pageSize = 10 
}: DataTableModalProps) {
  const [isFullScreen, setIsFullScreen] = useState(false);

  return (
    <Modal
      opened={opened}
      onClose={onClose}
      title={
        <Group justify="space-between" style={{ width: '100%' }}>
          <Text fw={700} size="lg">{title}</Text>
        </Group>
      }
      fullScreen={isFullScreen}
      size="95%"
      centered
      radius="md"
      overlayProps={{
        backgroundOpacity: 0.55,
        blur: 3,
      }}
      styles={{
        header: { backgroundColor: '#1a1b1e', color: 'white', borderBottom: '1px solid #2C2E33', padding: '15px 20px' },
        content: { backgroundColor: '#101113', color: 'white', overflow: 'hidden' },
        body: { padding: '20px' }
      }}
    >
      <DataTable 
        columns={columns} 
        data={data} 
        loading={loading} 
        pageSize={pageSize}
        maxHeight={500}
        searchPlaceholder="Buscar en todos los campos..."
        onFullScreenToggle={setIsFullScreen}
        isFullScreen={isFullScreen}
      />
    </Modal>
  );
}
