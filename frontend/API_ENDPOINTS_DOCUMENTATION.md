# API Endpoints - UPTC Energy Platform

Esta documentación detalla todos los endpoints que el backend FastAPI debe implementar para la plataforma UPTC Energy.

## Base URL
```
http://localhost:8000
```

---

## 1. Health Check

### `GET /health`
**Descripción:** Verifica el estado del servidor
**Parámetros:** Ninguno
**Respuesta:**
```json
{
  "status": "ok" | "online"
}
```

---

## 2. Predicciones

### `POST /api/v1/predictions/`
**Descripción:** Crear una nueva predicción
**Body:**
```json
{
  "sede": "string",
  "sector": "string", 
  "fecha": "string",
  "energia_real": "number",
  "agua_real": "number",
  "co2_real": "number"
}
```
**Respuesta:**
```json
{
  "id": "string",
  "sede": "string",
  "sector": "string",
  "fecha": "string",
  "energia_real": "number",
  "energia_predicha": "number",
  "agua_real": "number", 
  "agua_predicha": "number",
  "co2_real": "number",
  "co2_predicha": "number"
}
```

### `POST /api/v1/predictions/batch`
**Descripción:** Crear predicciones en lote
**Body:** Array de objetos de predicción
**Respuesta:** Array de predicciones creadas

### `GET /api/v1/predictions/sede/{sede}`
**Descripción:** Obtener todas las predicciones de una sede
**Parámetros:** 
- `sede` (path): ID de la sede
**Respuesta:** Array de predicciones

### `GET /api/v1/predictions/sede/{sede}/latest`
**Descripción:** Obtener las últimas predicciones de una sede
**Parámetros:** 
- `sede` (path): ID de la sede
**Respuesta:** Array de predicciones recientes

### `GET /api/v1/predictions/range`
**Descripción:** Obtener predicciones por rango de fechas
**Parámetros:** 
- `start` (query): Fecha de inicio (YYYY-MM-DD)
- `end` (query): Fecha de fin (YYYY-MM-DD)
**Respuesta:** Array de predicciones

---

## 3. Detección de Anomalías

### `POST /api/v1/anomalies/detect`
**Descripción:** Detectar anomalías en tiempo real
**Body:**
```json
{
  "sede": "string (opcional)",
  "sector": "string (opcional)"
}
```
**Respuesta:** Array de anomalías detectadas

### `GET /api/v1/anomalies/sede/{sede}`
**Descripción:** Obtener anomalías de una sede específica
**Parámetros:** 
- `sede` (path): ID de la sede
**Respuesta:**
```json
[
  {
    "id": "string",
    "sede": "string",
    "sector": "string",
    "fecha": "string",
    "tipo": "string",
    "severidad": "critica" | "alta" | "media" | "baja",
    "estado": "pendiente" | "revisada" | "resuelta",
    "descripcion": "string",
    "valor_detectado": "number",
    "valor_esperado": "number"
  }
]
```

### `GET /api/v1/anomalies/sede/{sede}/summary`
**Descripción:** Resumen de anomalías por sede
**Parámetros:** 
- `sede` (path): ID de la sede
**Respuesta:**
```json
{
  "total": "number",
  "por_estado": {
    "pendiente": "number",
    "revisada": "number", 
    "resuelta": "number"
  },
  "por_severidad": {
    "critica": "number",
    "alta": "number",
    "media": "number",
    "baja": "number"
  }
}
```

### `GET /api/v1/anomalies/unresolved`
**Descripción:** Obtener todas las anomalías no resueltas
**Parámetros:** Ninguno
**Respuesta:** Array de anomalías pendientes y en revisión

### `GET /api/v1/anomalies/range`
**Descripción:** Obtener anomalías por rango de fechas
**Parámetros:** 
- `start` (query): Fecha de inicio
- `end` (query): Fecha de fin
**Respuesta:** Array de anomalías

### `PATCH /api/v1/anomalies/{anomaly_id}/status`
**Descripción:** Actualizar estado de una anomalía
**Parámetros:**
- `anomaly_id` (path): ID de la anomalía
**Body:**
```json
{
  "estado": "pendiente" | "revisada" | "resuelta"
}
```
**Respuesta:** Anomalía actualizada

---

## 4. Recomendaciones

### `POST /api/v1/recommendations/generate`
**Descripción:** Generar recomendaciones automáticas
**Body:**
```json
{
  "sede": "string (opcional)",
  "sector": "string (opcional)"
}
```
**Respuesta:**
```json
[
  {
    "id": "string",
    "sede": "string", 
    "sector": "string",
    "tipo": "string",
    "descripcion": "string",
    "ahorro_estimado": "number",
    "prioridad": "alta" | "media" | "baja",
    "estado": "pendiente" | "implementada" | "rechazada"
  }
]
```

### `GET /api/v1/recommendations/sede/{sede}`
**Descripción:** Obtener recomendaciones por sede
**Parámetros:**
- `sede` (path): ID de la sede
**Respuesta:** Array de recomendaciones

### `GET /api/v1/recommendations/pending`
**Descripción:** Obtener recomendaciones pendientes
**Parámetros:** Ninguno
**Respuesta:** Array de recomendaciones pendientes

### `PATCH /api/v1/recommendations/{recommendation_id}/status`
**Descripción:** Actualizar estado de recomendación
**Parámetros:**
- `recommendation_id` (path): ID de la recomendación
**Body:**
```json
{
  "estado": "pendiente" | "implementada" | "rechazada"
}
```
**Respuesta:** Recomendación actualizada

---

## 5. Analítica

### `GET /api/v1/analytics/dashboard/all`
**Descripción:** KPIs generales del dashboard
**Parámetros:** Ninguno
**Respuesta:**
```json
{
  "sedes_monitoreadas": "number",
  "promedio_energia": "number",
  "promedio_agua": "number", 
  "huella_carbono": "number",
  "score_sostenibilidad": "number",
  "alertas_activas": "number",
  "total_emisiones": "number",
  "indice_eficiencia": "number"
}
```

### `GET /api/v1/analytics/dashboard/{sede}`
**Descripción:** KPIs específicos de una sede
**Parámetros:**
- `sede` (path): ID de la sede
**Respuesta:** Mismo formato que `/all` pero para sede específica

### `GET /api/v1/analytics/consumption/trends/{sede}`
**Descripción:** Tendencias de consumo por sede
**Parámetros:**
- `sede` (path): ID de la sede
**Respuesta:**
```json
[
  {
    "fecha": "string",
    "energia_real": "number",
    "energia_predicha": "number",
    "agua_real": "number",
    "agua_predicha": "number", 
    "co2_real": "number",
    "co2_predicha": "number"
  }
]
```

### `GET /api/v1/analytics/consumption/sectors/{sede}`
**Descripción:** Desglose de consumo por sector
**Parámetros:**
- `sede` (path): ID de la sede  
**Respuesta:**
```json
[
  {
    "sector": "string",
    "energia": "number",
    "agua": "number",
    "co2": "number", 
    "porcentaje": "number"
  }
]
```

### `GET /api/v1/analytics/patterns/hourly/{sede}`
**Descripción:** Patrones de consumo por hora
**Parámetros:**
- `sede` (path): ID de la sede
**Respuesta:**
```json
[
  {
    "hora": "string",
    "energia": "number",
    "agua": "number", 
    "co2": "number"
  }
]
```

### `GET /api/v1/analytics/efficiency/score/{sede}`
**Descripción:** Puntaje de eficiencia de una sede
**Parámetros:**
- `sede` (path): ID de la sede
**Respuesta:**
```json
{
  "score": "number",
  "detalles": {
    "energia": "number",
    "agua": "number",
    "co2": "number"
  }
}
```

### `GET /api/v1/analytics/correlations/{sede}`
**Descripción:** Matriz de correlación entre variables
**Parámetros:**
- `sede` (path): ID de la sede
**Respuesta:**
```json
{
  "variables": ["Energia", "Agua", "CO2", "Temperatura"],
  "matrix": [
    [1.0, 0.82, 0.95, -0.45],
    [0.82, 1.0, 0.78, -0.32], 
    [0.95, 0.78, 1.0, -0.41],
    [-0.45, -0.32, -0.41, 1.0]
  ]
}
```

### `GET /api/v1/analytics/academic-periods`
**Descripción:** Consumo por períodos académicos
**Parámetros:** Ninguno
**Respuesta:**
```json
[
  {
    "periodo": "string",
    "energia": "number", 
    "agua": "number",
    "co2": "number"
  }
]
```

---

## 6. Modelos de ML

### `GET /api/v1/models/metrics`
**Descripción:** Métricas de todos los modelos ML
**Parámetros:** Ninguno
**Respuesta:**
```json
[
  {
    "nombre": "string",
    "mae": "number",
    "rmse": "number",
    "r2_score": "number", 
    "tiempo_entrenamiento": "string",
    "activo": "boolean",
    "version": "string",
    "framework": "string",
    "fecha_entrenamiento": "string",
    "datos_entrenamiento": "number",
    "hiperparametros": {},
    "feature_importance": {}
  }
]
```

### `GET /api/v1/models/{model_name}/predictions`
**Descripción:** Comparación de predicciones vs valores reales
**Parámetros:**
- `model_name` (path): Nombre del modelo
**Respuesta:**
```json
{
  "real": [4.5, 5.2, 6.1, 7.3, 8.2],
  "predicho": [4.3, 5.0, 6.3, 7.1, 8.5]
}
```

---

## 7. Optimización

### `GET /api/v1/optimization/opportunities`
**Descripción:** Oportunidades de optimización
**Parámetros:** Ninguno
**Respuesta:**
```json
[
  {
    "area": "string",
    "potencial_ahorro": "number",
    "descripcion": "string"
  }
]
```

### `GET /api/v1/optimization/savings-projection`
**Descripción:** Proyección de ahorros (gráfico waterfall)
**Parámetros:** Ninguno
**Respuesta:**
```json
[
  {
    "categoria": "string",
    "valor": "number", 
    "tipo": "ahorro" | "total"
  }
]
```

### `GET /api/v1/optimization/sustainability`
**Descripción:** Contribución a sostenibilidad
**Parámetros:** Ninguno
**Respuesta:**
```json
{
  "arboles_salvados": "number",
  "agua_ahorrada": "number",
  "co2_reducido": "number"
}
```

### `GET /api/v1/optimization/pareto`
**Descripción:** Análisis de Pareto de desperdicios
**Parámetros:** Ninguno
**Respuesta:**
```json
[
  {
    "causa": "string",
    "porcentaje": "number",
    "acumulado": "number"
  }
]
```

---

## 8. Alertas

### `GET /api/v1/alerts/evolution`
**Descripción:** Evolución de alertas en el tiempo
**Parámetros:** Ninguno
**Respuesta:**
```json
[
  {
    "mes": "string",
    "anomalias": "number",
    "desbalances": "number",
    "criticas": "number"
  }
]
```

---

## 9. Explicabilidad

### `GET /api/v1/explainability/shap/{variable}`
**Descripción:** Valores SHAP para explicabilidad del modelo
**Parámetros:**
- `variable` (path): "energia" | "agua" | "co2"
**Respuesta:**
```json
[
  {
    "feature": "string",
    "value": "number"
  }
]
```

### `GET /api/v1/explainability/confidence`
**Descripción:** Métricas de confianza del modelo
**Parámetros:** Ninguno
**Respuesta:**
```json
{
  "confianza_prediccion": "number",
  "certeza_recomendacion": "number", 
  "modelo_activo": "string"
}
```

---

## 10. Chat IA

### `POST /api/v1/chat`
**Descripción:** Enviar mensaje al asistente de IA
**Body:**
```json
{
  "message": "string"
}
```
**Respuesta:**
```json
{
  "response": "string"
}
```

---

## 11. Sedes

### `GET /api/v1/sedes`
**Descripción:** Información de todas las sedes UPTC
**Parámetros:** Ninguno
**Respuesta:**
```json
[
  {
    "id": "string",
    "nombre": "string",
    "estudiantes": "number",
    "lat": "number",
    "lng": "number",
    "consumo_energia": "number",
    "consumo_agua": "number",
    "emisiones_co2": "number"
  }
]
```

---

## Configuración CORS

Para que el frontend pueda conectarse correctamente, el backend debe configurar CORS:

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## Notas Importantes

1. **Fallback automático**: Si algún endpoint no está implementado, el frontend usa datos mock automáticamente
2. **Formato de fechas**: Usar formato ISO 8601 (YYYY-MM-DDTHH:mm:ss)
3. **Códigos de error**: Usar códigos HTTP estándar (200, 400, 404, 500)
4. **Paginación**: Implementar si hay grandes volúmenes de datos
5. **Rate limiting**: Considerar límites de rate para endpoints de ML

## Testing

Usar la página de pruebas del frontend: `http://localhost:8080/dashboard/api-test`