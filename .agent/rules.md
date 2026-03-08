# Reglas del Proyecto: Modernización Sistema Esmeralda (V2)

## Contexto del Proyecto
- Estamos migrando un sistema hotelero legacy hecho en PySide6 (Python) de 10,000 líneas (un solo archivo) a una WebApp moderna.
- El objetivo es unificar la lógica de escritorio antigua y la web en un solo ecosistema y de ser posible mejorarla para usar codigo profesional y moderno.

## Stack Tecnológico Objetivo
- **Backend:** Python (FastAPI) para mantener la compatibilidad con la lógica legacy pero organizada en módulos.
- **Frontend:** Next.js + React + Mantine (Diseño Premium, Dark Mode, Animaciones) y tabler icons para los iconos.
- **Base de Datos:** Local-First (sincronización entre hoteles y servidor central en casa).

## Reglas de Codificación
1. **Modularidad Estricta:** Nada de archivos gigantes. Cada clase o función del archivo legacy de 10k líneas debe convertirse en un componente o servicio independiente.
2. **Clean Architecture:** Separar claramente la lógica de negocio de la lógica de la base de datos y de la interfaz de usuario.
3. **Seguridad:** Implementar autenticación robusta (JWT) desde el inicio.
4. **Resiliencia:** El sistema debe funcionar localmente en cada hotel y sincronizar datos de forma asíncrona. Ten en cuanta que este sera un sistema que debe ser capaz de venderse en diferentes hoteles, de forma relativamente sencilla. Todos se sincornizarian con un servidor central, pero podemos dejar eso de ultimo al finalizar con la app como tal, no se si seria lo mas conveniente.

## Proceso de Trabajo
- El usuario pasará secciones (clases o funciones) del archivo legacy.
- La IA debe:
  A) Analizar la lógica actual y proponer mejoras.
  B) Traducir la lógica a un Endpoint de FastAPI.
  C) Sugerir o crear el componente de UI correspondiente en Next.js con Mantine.
