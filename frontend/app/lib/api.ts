const BASE_URL = typeof window !== 'undefined' 
  ? `http://${window.location.hostname}:8000/api` 
  : 'http://192.168.0.123:8000/api';

async function request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
  const response = await fetch(`${BASE_URL}${endpoint}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
    throw new Error(error.detail || `HTTP error! status: ${response.status}`);
  }

  return response.json();
}

export const api = {
  // Configuracion
  getConfig: (clave: string) => request<{ clave: string; valor: string }>(`/configuracion/settings/${clave}`),
  updateConfig: (clave: string, valor: string) => request(`/configuracion/settings/${clave}`, { method: 'PUT', body: JSON.stringify({ valor }) }),
  getMetodosPago: () => request<any[]>(`/configuracion/metodos_pago`),
  getUsuarios: () => request<any[]>(`/configuracion/usuarios`),
  refreshBcv: () => request<{ price: number }>(`/configuracion/refresh-bcv`, { method: 'POST' }),

  // Habitaciones
  getHabitaciones: () => request<any[]>(`/habitaciones`),
  updateHabitacionPrecios: (id: number, data: any) => request(`/configuracion/habitaciones/${id}/precios`, { method: 'PUT', body: JSON.stringify(data) }),

  // Accesos
  getAccesos: (s?: string, start?: string, end?: string, skip: number = 0, limit: number = 20) => {
    const params = new URLSearchParams();
    if (s) params.set('s', s);
    if (start) params.set('start', start);
    if (end) params.set('end', end);
    params.set('skip', skip.toString());
    params.set('limit', limit.toString());
    return request<any[]>(`/acceso/historial?${params.toString()}`);
  },

  // Estancias
  getEstanciasHistorial: (s?: string, start?: string, end?: string, skip: number = 0, limit: number = 20) => {
    const params = new URLSearchParams();
    if (s) params.set('s', s);
    if (start) params.set('start', start);
    if (end) params.set('end', end);
    params.set('skip', skip.toString());
    params.set('limit', limit.toString());
    return request<any[]>(`/habitaciones/historial/global?${params.toString()}`);
  },

  // Novedades
  getNovedades: (s?: string, start?: string, end?: string, skip: number = 0, limit: number = 20) => {
    const params = new URLSearchParams();
    if (s) params.set('s', s);
    if (start) params.set('start', start);
    if (end) params.set('end', end);
    params.set('skip', skip.toString());
    params.set('limit', limit.toString());
    return request<any[]>(`/novedades?${params.toString()}`);
  },

  // Turnos / Resumen
  getTurnos: (s?: string, start?: string, end?: string) => {
    const params = new URLSearchParams();
    if (s) params.set('s', s);
    if (start) params.set('start', start);
    if (end) params.set('end', end);
    return request<any[]>(`/turnos/historial?${params.toString()}`);
  },
  getResumenHoy: () => request<any>(`/turnos/resumen/hoy`),
  createNovedad: (data: any) => request(`/novedades`, { method: 'POST', body: JSON.stringify(data) }),
  resolverAveria: (id: number) => request(`/novedades/${id}/resolver`, { method: 'PUT' }),
};
