'use client';

import { 
  Modal, 
  Box, 
  Group, 
  Stack, 
  Text, 
  ActionIcon, 
  Button, 
  ScrollArea, 
  Divider,
  Paper,
  Kbd,
  SimpleGrid,
  Tooltip,
  Select
} from '@mantine/core';
import { 
  IconCalculator, 
  IconHistory, 
  IconTrash, 
  IconX, 
  IconArrowRight, 
  IconCurrencyDollar,
  IconVariable
} from '@tabler/icons-react';
import { useState, useEffect, useRef } from 'react';

interface CalculadoraModalProps {
  opened: boolean;
  onClose: () => void;
  tasa?: number;
  roomPrices?: { tipo: string, parcial: number, hospedaje: number }[];
}

export default function CalculadoraModal({ opened, onClose, tasa = 0, roomPrices = [] }: CalculadoraModalProps) {
  const [display, setDisplay] = useState('0');
  const [expression, setExpression] = useState('');
  const [currency, setCurrency] = useState<'USD' | 'Bs'>('USD');
  const [shouldReset, setShouldReset] = useState(false);
  const [history, setHistory] = useState<{ calc: string, result: string, timestamp: number }[]>([]);
  const scrollRef = useRef<HTMLDivElement>(null);
  
  // Dragging state
  const [position, setPosition] = useState({ 
    x: typeof window !== 'undefined' ? window.innerWidth - 490 : 400, 
    y: typeof window !== 'undefined' ? window.innerHeight - 560 : 300 
  });
  const [isDragging, setIsDragging] = useState(false);
  const dragStartPos = useRef({ x: 0, y: 0 });
  const windowPosStart = useRef({ x: 0, y: 0 });

  // Refs to handle keyboard events without unnecessary re-renders
  const stateRef = useRef({ display, expression, opened, currency, shouldReset });
  
  useEffect(() => {
    stateRef.current = { display, expression, opened, currency, shouldReset };
  }, [display, expression, opened, currency, shouldReset]);

  useEffect(() => {
    // Reset position if window resized and it's out of bounds
    const handleResize = () => {
      setPosition(prev => ({
        x: Math.min(prev.x, window.innerWidth - 100),
        y: Math.min(prev.y, window.innerHeight - 100)
      }));
    };
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  const toggleCurrency = () => {
    if (!tasa) return;
    const { display: currentDisplay, currency: currentCurrency } = stateRef.current;
    
    let val = parseFloat(currentDisplay);
    if (isNaN(val)) val = 0;

    if (currentCurrency === 'USD') {
      const result = (val * tasa).toFixed(2);
      setDisplay(result);
      setCurrency('Bs');
    } else {
      const result = (val / tasa).toFixed(2);
      setDisplay(result);
      setCurrency('USD');
    }
    setShouldReset(true);
  };

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      // Global toggle: Alt + C opens it everywhere if it's imported in layout
      // But here we only handle internal keys if opened
      if (!stateRef.current.opened) return;

      const key = e.key;
      const { display: currentDisplay, expression: currentExpr } = stateRef.current;

      if (/^[0-9]$/.test(key)) {
        e.preventDefault();
        appendNumber(key);
      } else if (['+', '-', '*', '/'].includes(key)) {
        e.preventDefault();
        appendOperator(key);
      } else if (key === '.' || key === ',') {
        e.preventDefault();
        appendDecimal();
      } else if (key === 'Enter' || key === '=') {
        e.preventDefault();
        calculate();
      } else if (key === 'Backspace') {
        e.preventDefault();
        backspace();
      } else if (key === 'Escape') {
        e.preventDefault();
        if (currentDisplay === '0' && currentExpr === '') {
          onClose();
        } else {
          clear();
        }
      } else if (key.toLowerCase() === 't' || key === 'Tab') {
        e.preventDefault();
        toggleCurrency();
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [onClose]);

  const handleMouseDown = (e: React.MouseEvent) => {
    setIsDragging(true);
    dragStartPos.current = { x: e.clientX, y: e.clientY };
    windowPosStart.current = { x: position.x, y: position.y };
  };

  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      if (!isDragging) return;
      const dx = e.clientX - dragStartPos.current.x;
      const dy = e.clientY - dragStartPos.current.y;
      setPosition({
        x: windowPosStart.current.x + dx,
        y: windowPosStart.current.y + dy
      });
    };

    const handleMouseUp = () => {
      setIsDragging(false);
    };

    if (isDragging) {
      window.addEventListener('mousemove', handleMouseMove);
      window.addEventListener('mouseup', handleMouseUp);
    }
    return () => {
      window.removeEventListener('mousemove', handleMouseMove);
      window.removeEventListener('mouseup', handleMouseUp);
    };
  }, [isDragging]);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTo({ top: scrollRef.current.scrollHeight, behavior: 'smooth' });
    }
  }, [history]);

  const appendNumber = (num: string) => {
    setDisplay(prev => {
      if (prev === '0' || shouldReset) {
        setShouldReset(false);
        return num;
      }
      return prev + num;
    });
  };

  const appendOperator = (op: string) => {
    setExpression(prev => prev + display + ' ' + op + ' ');
    setDisplay('0');
    setShouldReset(false);
  };

  const appendDecimal = () => {
    if (shouldReset) {
      setDisplay('0.');
      setShouldReset(false);
      return;
    }
    if (!display.includes('.')) {
      setDisplay(prev => prev + '.');
    }
  };

  const backspace = () => {
    if (shouldReset) {
      clear();
      return;
    }
    setDisplay(prev => prev.length > 1 ? prev.slice(0, -1) : '0');
  };

  const clear = () => {
    setDisplay('0');
    setExpression('');
    setShouldReset(false);
  };

  const calculate = () => {
    try {
      const fullExpr = expression + display;
      const sanitized = fullExpr.replace(/[^-+*/.0-9 ]/g, '');
      const resultValue = eval(sanitized); 
      const resultStr = Number.isInteger(resultValue) ? resultValue.toString() : resultValue.toFixed(2);
      
      setHistory(prev => [...prev.slice(-19), { calc: `${fullExpr} (${currency})`, result: `${resultStr} ${currency}`, timestamp: Date.now() }]);
      setDisplay(resultStr);
      setExpression('');
      setShouldReset(true);
    } catch (e) {
      setDisplay('Error');
      setTimeout(clear, 1000);
    }
  };

  const clearHistory = () => {
    setHistory([]);
  };

  if (!opened) return null;

  // Flatten room prices into select options
  const roomOptions = (roomPrices || []).flatMap(rp => [
    { value: `${rp.tipo}_parcial_${rp.parcial}`, label: `${rp.tipo} - PARCIAL ($${rp.parcial})` },
    { value: `${rp.tipo}_hospedaje_${rp.hospedaje}`, label: `${rp.tipo} - HOSPEDAJE ($${rp.hospedaje})` }
  ]);

  const handlePriceSelect = (val: string | null) => {
    if (!val) return;
    const parts = val.split('_');
    const price = parts[parts.length - 1];
    
    // Always load in USD for these presets
    setCurrency('USD');
    setDisplay(price);
    setShouldReset(true);
  };

  return (
    <Paper 
      shadow="xl"
      p="md"
      radius="md"
      bg="#141414"
      style={{ 
        position: 'fixed',
        left: position.x,
        top: position.y,
        width: 480, // Slightly wider for the select
        zIndex: 9999,
        border: '1px solid #333',
        boxShadow: '0 10px 30px rgba(0,0,0,0.5)',
        display: 'flex',
        flexDirection: 'column',
        userSelect: isDragging ? 'none' : 'auto',
        cursor: isDragging ? 'grabbing' : 'auto',
        transition: 'none'
      }}
    >
      <Group 
        justify="space-between" 
        mb="sm" 
        style={{ 
          borderBottom: '1px solid #282828', 
          paddingBottom: 8,
          cursor: isDragging ? 'grabbing' : 'grab'
        }}
        onMouseDown={handleMouseDown}
      >
        <Group gap="xs">
          <IconCalculator size={20} color="#80e28a" />
          <Text fw={700} size="sm" style={{ fontFamily: 'Poppins, sans-serif' }}>CALCULADORA RÁPIDA</Text>
        </Group>
        <ActionIcon variant="subtle" color="gray" size="sm" onClick={onClose} onMouseDown={(e) => e.stopPropagation()}>
          <IconX size={16} />
        </ActionIcon>
      </Group>

      <Group align="flex-start" wrap="nowrap" gap="md">
        {/* Main Calculator */}
        <Stack gap="xs" style={{ flex: 1.5 }}>
          <Paper p="sm" bg="#1a1a1a" radius="md" style={{ border: '1px solid #333', position: 'relative' }}>
            <Group justify="flex-end" mb={2}>
              <Text size="10px" c="dimmed" ta="right" h={14} style={{ fontFamily: 'monospace', flex: 1 }}>
                {expression}
              </Text>
            </Group>
            <Group justify="flex-end" align="baseline" gap={4}>
              <Text size="22px" fw={700} ta="right" c="white" style={{ fontFamily: 'monospace' }}>
                {display}
              </Text>
              <Text size="xs" fw={700} color="#80e28a">{currency}</Text>
            </Group>
          </Paper>

          <SimpleGrid cols={4} spacing="xs">
            {/* Row 1 */}
            <Button variant="light" color="red" size="xs" onClick={clear}>C</Button>
            <Button variant="light" color="gray" size="xs" onClick={backspace}>←</Button>
            <Button variant="light" color="#80e28a" size="xs" onClick={() => appendOperator('/')}>/</Button>
            <Button variant="light" color="#80e28a" size="xs" onClick={() => appendOperator('*')}>*</Button>

            {/* Row 2 */}
            <Button variant="filled" color="dark" size="xs" onClick={() => appendNumber('7')}>7</Button>
            <Button variant="filled" color="dark" size="xs" onClick={() => appendNumber('8')}>8</Button>
            <Button variant="filled" color="dark" size="xs" onClick={() => appendNumber('9')}>9</Button>
            <Button variant="light" color="#80e28a" size="xs" onClick={() => appendOperator('-')}>-</Button>

            {/* Row 3 */}
            <Button variant="filled" color="dark" size="xs" onClick={() => appendNumber('4')}>4</Button>
            <Button variant="filled" color="dark" size="xs" onClick={() => appendNumber('5')}>5</Button>
            <Button variant="filled" color="dark" size="xs" onClick={() => appendNumber('6')}>6</Button>
            <Button variant="light" color="#80e28a" size="xs" onClick={() => appendOperator('+')}>+</Button>

            {/* Row 4 */}
            <Button variant="filled" color="dark" size="xs" onClick={() => appendNumber('1')}>1</Button>
            <Button variant="filled" color="dark" size="xs" onClick={() => appendNumber('2')}>2</Button>
            <Button variant="filled" color="dark" size="xs" onClick={() => appendNumber('3')}>3</Button>
            <Button variant="filled" color="teal" size="xs" styles={{ root: { backgroundColor: '#80e28a', color: '#111' } }} onClick={calculate} style={{ gridRow: 'span 2', height: 'auto' }}>=</Button>

            {/* Row 5 */}
            <Button variant="filled" color="dark" size="xs" onClick={() => appendNumber('0')} style={{ gridColumn: 'span 2' }}>0</Button>
            <Button variant="filled" color="dark" size="xs" onClick={appendDecimal}>.</Button>
          </SimpleGrid>

          <Divider my="xs" label="Tarifas y Tasa" labelPosition="center" color="#333" />

          <Stack gap={6}>
            <Select
              placeholder="Habitación..."
              data={roomOptions}
              searchable={false}
              size="xs"
              onChange={handlePriceSelect}
              styles={{
                input: { backgroundColor: '#1a1a1a', border: '1px solid #333', color: 'white' },
                dropdown: { backgroundColor: '#1a1a1a', border: '1px solid #333', color: 'white', zIndex: 10000 },
              }}
            />
            <Button 
              fullWidth
              variant="gradient" 
              gradient={{ from: '#36ea7e', to: '#11998e' }} 
              leftSection={<IconVariable size={14} />}
              onClick={toggleCurrency}
              size="xs"
              styles={{ label: { color: 'white' } }}
            >
              Cerrar en {currency === 'USD' ? 'USD' : 'Bs'} <Text size="9px" ml="xs" opacity={0.7}>[T]</Text>
            </Button>
          </Stack>
        </Stack>

        {/* History Panel */}
        <Stack gap="xs" style={{ flex: 1, height: '100%' }}>
          <Group justify="space-between" px="xs">
            <Group gap={4}>
              <IconHistory size={12} color="#888" />
              <Text size="9px" fw={700} c="dimmed">HISTORIAL</Text>
            </Group>
            <ActionIcon variant="subtle" color="gray" size="xs" onClick={clearHistory}>
              <IconTrash size={10} />
            </ActionIcon>
          </Group>
          
          <Paper p="xs" bg="#0a0a0a" radius="md" style={{ border: '1px solid #222', flex: 1, minHeight: 180 }}>
            <ScrollArea h={170} viewportRef={scrollRef}>
              <Stack gap={6}>
                {history.length === 0 ? (
                  <Text size="9px" c="dimmed" ta="center" mt="md">Vacío</Text>
                ) : (
                  history.map((item, idx) => (
                    <Box key={idx} p="2px 4px" style={{ borderBottom: '1px solid #1a1a1a' }}>
                      <Text size="8px" c="dimmed" truncate>{item.calc}</Text>
                      <Text size="xs" fw={700} color="#80e28a" ta="right">={item.result}</Text>
                    </Box>
                  ))
                )}
              </Stack>
            </ScrollArea>
          </Paper>
          
          <Box mt="4">
            <Group justify="center" gap={4}>
              <Kbd size="xs" style={{ fontSize: '8px', padding: '1px 4px' }}>Alt+C</Kbd>
              <Text size="8px" c="dimmed">Cerrar</Text>
            </Group>
          </Box>
        </Stack>
      </Group>
    </Paper>
  );
}

