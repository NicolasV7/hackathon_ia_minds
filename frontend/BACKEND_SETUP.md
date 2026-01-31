# Scripts de Desarrollo para UPTC Energy Platform

## Conectividad con Backend

### 1. Verificar estado del backend
```bash
curl -X GET http://localhost:8000/health
```

### 2. Verificar endpoints principales
```bash
# Sedes
curl -X GET http://localhost:8000/api/v1/sedes

# Dashboard KPIs
curl -X GET http://localhost:8000/api/v1/analytics/dashboard/all

# Anomalías
curl -X GET http://localhost:8000/api/v1/anomalies/unresolved
```

### 3. Configuración de CORS (para el backend)
Si el backend no está configurado para CORS, agregar en main.py:

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### 4. Variables de entorno disponibles
- `VITE_API_URL`: URL del backend (default: http://localhost:8000)
- `VITE_DEBUG`: Habilita logs de debug (default: false)
- `VITE_NODE_ENV`: Entorno de desarrollo

### 5. Acceso a página de pruebas
- Frontend: http://localhost:8080/dashboard/api-test
- Permite probar todos los endpoints y ver resultados

### 6. Fallback automático
El frontend está configurado con datos mock como fallback automático.
Si el backend no está disponible, la aplicación seguirá funcionando con datos de prueba.