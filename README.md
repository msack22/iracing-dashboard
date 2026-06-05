# iRacing Dashboard

Dashboard personal para iRacing: garage, recomendaciones de compra y análisis de carreras.

## Stack

- **Backend**: Node.js + TypeScript + Express (Clean Architecture)
- **Frontend**: React + Vite + shadcn/ui + Tailwind CSS

## Requisitos previos

- Node.js >= 18
- npm o pnpm

## Configuración

### 1. Credenciales iRacing OAuth

Solicitá las credenciales OAuth en: https://members.iracing.com/membersite/account/home.do  
(Settings → API Access → Request OAuth Client)

Copiá `backend/.env.example` a `backend/.env` y completá:

```
IRACING_CLIENT_ID=tu_client_id
IRACING_CLIENT_SECRET=tu_client_secret
USE_MOCK=true   # cambiá a false cuando tengas credenciales reales
```

### 2. Instalar dependencias

```bash
cd backend && npm install
cd ../frontend && npm install
```

### 3. Levantar en desarrollo

```bash
# Terminal 1 - Backend (puerto 3001)
cd backend && npm run dev

# Terminal 2 - Frontend (puerto 5173)
cd frontend && npm run dev
```

## Descuentos iRacing

| Cantidad | Descuento |
|----------|-----------|
| 3–5 items | 10% |
| 6+ items | 15% |
| 40+ licenciados | 20% loyalty |

## Features

- **Dashboard**: iRating, Safety Rating, próximas carreras disponibles
- **Garage**: Autos propios filtrados por categoría y licencia
- **Mis Pistas**: Tracks disponibles con configuraciones
- **Shop Advisor**: Recomendaciones de compra en bundles de 3 con ahorro calculado
- **Carreras**: Historial con laptimes, incidentes y evolución de iRating
