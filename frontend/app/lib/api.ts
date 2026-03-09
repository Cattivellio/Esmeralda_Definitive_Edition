export const BASE_URL = typeof window !== 'undefined' 
  ? `http://${window.location.hostname}:8000/api` 
  : 'http://localhost:8000/api';

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
  getAllSettings: () => request<any[]>(`/configuracion/all-settings`),
  updateConfig: (clave: string, valor: string) => request(`/configuracion/settings/${clave}`, { method: 'PUT', body: JSON.stringify({ valor }) }),
  getMetodosPago: () => request<any[]>(`/configuracion/metodos_pago`),
  getCliente: (cedula: string) => request<any>(`/clientes/${cedula}`),
  getClienteHistorial: (cedula: string) => request<any[]>(`/clientes/${cedula}/historial`),
  getClienteDatosPasados: (cedula: string) => request<any>(`/clientes/${cedula}/datos-pasados`),
  getUsuarios: () => request<any[]>(`/configuracion/usuarios`),
  createUsuario: (data: any) => request(`/configuracion/usuarios`, { method: 'POST', body: JSON.stringify(data) }),
  updateUsuario: (id: number, data: any) => request(`/configuracion/usuarios/${id}`, { method: 'PUT', body: JSON.stringify(data) }),
  deleteUsuario: (id: number) => request(`/configuracion/usuarios/${id}`, { method: 'DELETE' }),
  getVoucher: (codigo: string) => request<any>(`/configuracion/vouchers/${codigo}`),
  refreshBcv: () => request<{ price: number }>(`/configuracion/refresh-bcv`, { method: 'POST' }),
  createMetodoPago: (data: any) => request(`/configuracion/metodos_pago`, { method: 'POST', body: JSON.stringify(data) }),
  updateMetodoPago: (id: number, data: any) => request(`/configuracion/metodos_pago/${id}`, { method: 'PUT', body: JSON.stringify(data) }),
  deleteMetodoPago: (id: number) => request(`/configuracion/metodos_pago/${id}`, { method: 'DELETE' }),

  // Habitaciones
  getHabitaciones: () => request<any[]>(`/habitaciones`),
  getEstanciaActiva: (id: number) => request<any>(`/habitaciones/${id}/estancia-activa`),
  getReservasProximas: () => request<any[]>(`/habitaciones/reservas/proximas`),
  updateHabitacionPrecios: (id: number, data: any) => request(`/configuracion/habitaciones/${id}/precios`, { method: 'PUT', body: JSON.stringify(data) }),
  bloquearHabitacion: (id: number, data: any) => request(`/habitaciones/${id}/bloquear`, { method: 'POST', body: JSON.stringify(data) }),
  getHabitacionHistorial: (id: number) => request<any[]>(`/habitaciones/${id}/historial`),
  getCamarerasPresentes: () => request<any[]>(`/habitaciones/camareras-presentes`),
  cambiarHabitacion: (id: number, data: any) => request(`/habitaciones/${id}/cambiar_habitacion`, { method: 'POST', body: JSON.stringify(data) }),
  ingresarCliente: (id: number, data: any) => request(`/habitaciones/${id}/ingresar`, { method: 'POST', body: JSON.stringify(data) }),
  checkIn: (id: number) => request(`/habitaciones/${id}/checkin`, { method: 'POST' }),
  checkOut: (id: number) => request(`/habitaciones/${id}/checkout`, { method: 'POST' }),
  updateEstancia: (id: number, data: any) => request(`/habitaciones/${id}/estancia`, { method: 'PUT', body: JSON.stringify(data) }),

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
  getAccesoHistorialCliente: (cedula: string) => request<any[]>(`/acceso/historial/${cedula}`),
  registrarAcceso: (data: any) => request(`/acceso/registrar`, { method: 'POST', body: JSON.stringify(data) }),

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
  getInspecciones: () => request<any[]>(`/configuracion/inspecciones`),
  createInspeccion: (data: any) => request(`/configuracion/inspecciones`, { method: 'POST', body: JSON.stringify(data) }),

  // Tesorería
  getTesoreriaCuentas: () => request<any[]>(`/tesoreria/cuentas`),
  getTesoreriaTransacciones: (metodoId?: number, tipo?: string, limit: number = 100) => {
    const params = new URLSearchParams();
    if (metodoId) params.set('metodo_pago_id', metodoId.toString());
    if (tipo) params.set('tipo', tipo);
    params.set('limit', limit.toString());
    return request<any[]>(`/tesoreria/transacciones?${params.toString()}`);
  },
  createTesoreriaTransaccion: (data: any) => request(`/tesoreria/transacciones`, { method: 'POST', body: JSON.stringify(data) }),
  createTesoreriaTransferencia: (data: any) => request(`/tesoreria/transferencias`, { method: 'POST', body: JSON.stringify(data) }),
  getMetodosPagoFull: () => request<any[]>(`/tesoreria/metodos-pago-full`),
  uploadFactura: (file: File) => {
    const formData = new FormData();
    formData.append('file', file);
    return fetch(`${BASE_URL}/tesoreria/upload-factura`, {
      method: 'POST',
      body: formData
    }).then(res => res.json());
  },
  uploadUserPhoto: (file: File) => {
    const formData = new FormData();
    formData.append('file', file);
    return fetch(`${BASE_URL}/configuracion/usuarios/upload-foto`, {
      method: 'POST',
      body: formData
    }).then(res => res.json());
  },
  getLogs: () => request<any[]>(`/configuracion/logs`),
  downloadBackup: () => `${BASE_URL}/configuracion/backup/download`,
  // Inventario
  getInventario: () => request<any[]>(`/configuracion/inventario`),
  createInventarioItem: (data: any) => request(`/configuracion/inventario`, { method: 'POST', body: JSON.stringify(data) }),
  updateInventarioItem: (id: number, data: any) => request(`/configuracion/inventario/${id}`, { method: 'PUT', body: JSON.stringify(data) }),
  deleteInventarioItem: (id: number) => request(`/configuracion/inventario/${id}`, { method: 'DELETE' }),
  registrarMovimiento: (data: any) => request(`/configuracion/inventario/movimiento`, { method: 'POST', body: JSON.stringify(data) }),
  getMovimientosInventario: (itemId?: number) => request<any[]>(`/configuracion/inventario/movimientos${itemId ? `?item_id=${itemId}` : ''}`),

  // Acceso Detalle
  getCargosResumen: () => request<any[]>(`/acceso/cargos-resumen`),
  getPersonasPorCargo: (cargo: string) => request<Persona[]>(`/acceso/personas/${cargo}`),

  // Habitaciones Adicionales
  limpiarHabitacion: (id: number, camarera_id: number) => request(`/habitaciones/${id}/limpiar`, { method: 'POST', body: JSON.stringify({ camarera_id }) }),
  desbloquearHabitacion: (id: number) => request(`/habitaciones/${id}/desbloquear`, { method: 'POST' }),
  setRetoque: (id: number, camarera_id: number) => request(`/habitaciones/${id}/retoque`, { method: 'POST', body: JSON.stringify({ camarera_id }) }),
  finalizarRetoque: (id: number) => request(`/habitaciones/${id}/finalizar_retoque`, { method: 'POST' }),
  liberarHabitacion: (id: number) => request(`/habitaciones/${id}/liberar`, { method: 'POST' }),
  pasarAHospedaje: (id: number) => request(`/habitaciones/${id}/pasar_a_hospedaje`, { method: 'POST' }),

  // Reservas
  cancelarReserva: (id: string) => request(`/habitaciones/reservas/${id}/cancelar`, { method: 'POST' }),
  activarReserva: (id: string) => request(`/habitaciones/reservas/${id}/activar`, { method: 'POST' }),

  // Turnos Adicionales
  realizarCambioTurno: (data: any) => request(`/turnos/cambio`, { method: 'POST', body: JSON.stringify(data) }),
};

interface Persona {
  nombre: string;
  cedula: string;
  cargo: string;
  estado: string;
}
