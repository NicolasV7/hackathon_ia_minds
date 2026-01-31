import { useEffect, useState } from 'react';
import { MapContainer, TileLayer, CircleMarker, Popup } from 'react-leaflet';
import { getSedesInfo, type SedeInfo } from '@/services/api';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import 'leaflet/dist/leaflet.css';

// Fix for default markers
import L from 'leaflet';

// Arreglar iconos por defecto de Leaflet
delete (L.Icon.Default.prototype as any)._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon-2x.png',
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-shadow.png',
});

// Función para calcular el tamaño del círculo basado en el consumo de energía
const getCircleSize = (consumo: number, maxConsumo: number) => {
  return Math.max(10, (consumo / maxConsumo) * 30);
};

// Función para obtener el color basado en el consumo de energía
const getCircleColor = (consumo: number, maxConsumo: number) => {
  const ratio = consumo / maxConsumo;
  if (ratio > 0.8) return '#ef4444'; // Rojo para alto consumo
  if (ratio > 0.6) return '#f97316'; // Naranja para consumo medio-alto
  if (ratio > 0.4) return '#eab308'; // Amarillo para consumo medio
  return '#22c55e'; // Verde para consumo bajo
};

export default function GeoVisor() {
  const [sedes, setSedes] = useState<SedeInfo[]>([]);
  const [loading, setLoading] = useState(true);
  const [maxConsumo, setMaxConsumo] = useState(0);
  const [mapError, setMapError] = useState(false);

  useEffect(() => {
    async function fetchSedes() {
      try {
        const data = await getSedesInfo();
        setSedes(data);
        const max = Math.max(...data.map(s => s.consumo_energia));
        setMaxConsumo(max);
      } catch (error) {
        console.error('Error fetching sedes:', error);
        // Mock data fallback
        const mockData = [
          { 
            id: 'tunja', 
            nombre: 'Tunja (Principal)', 
            estudiantes: 18000, 
            lat: 5.5353, 
            lng: -73.3678, 
            consumo_energia: 45000, 
            consumo_agua: 9500, 
            emisiones_co2: 68 
          },
          { 
            id: 'duitama', 
            nombre: 'Duitama', 
            estudiantes: 5500, 
            lat: 5.8267, 
            lng: -73.0333, 
            consumo_energia: 18200, 
            consumo_agua: 3800, 
            emisiones_co2: 27 
          },
          { 
            id: 'sogamoso', 
            nombre: 'Sogamoso', 
            estudiantes: 6000, 
            lat: 5.7147, 
            lng: -72.9314, 
            consumo_energia: 15500, 
            consumo_agua: 3200, 
            emisiones_co2: 23 
          },
          { 
            id: 'chiquinquira', 
            nombre: 'Chiquinquira', 
            estudiantes: 2000, 
            lat: 5.6167, 
            lng: -73.8167, 
            consumo_energia: 6800, 
            consumo_agua: 1400, 
            emisiones_co2: 10 
          },
        ];
        setSedes(mockData);
        const max = Math.max(...mockData.map(s => s.consumo_energia));
        setMaxConsumo(max);
      } finally {
        setLoading(false);
      }
    }
    fetchSedes();
  }, []);

  if (loading) {
    return (
      <div className="w-full h-96 bg-card rounded-xl flex items-center justify-center">
        <div className="text-muted-foreground">Cargando mapa...</div>
      </div>
    );
  }

  // Centro del mapa en Boyacá
  const center: [number, number] = [5.6, -73.1];

  // Si hay error con el mapa, mostrar vista alternativa
  if (mapError || typeof window === 'undefined') {
    return (
      <div className="w-full h-96 bg-card rounded-xl p-6">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 h-full">
          <div className="space-y-4">
            <h3 className="text-lg font-semibold text-foreground">Sedes UPTC</h3>
            {sedes.map((sede) => (
              <div key={sede.id} className="p-4 bg-secondary/50 rounded-lg">
                <h4 className="font-medium text-foreground">{sede.nombre}</h4>
                <p className="text-sm text-muted-foreground">{sede.estudiantes.toLocaleString()} estudiantes</p>
                <div className="text-xs text-muted-foreground mt-2">
                  <div>Energía: {sede.consumo_energia.toLocaleString()} kWh/mes</div>
                  <div>Agua: {sede.consumo_agua.toLocaleString()} m³/mes</div>
                  <div>CO2: {sede.emisiones_co2} ton/mes</div>
                </div>
              </div>
            ))}
          </div>
          <div className="bg-secondary/20 rounded-lg flex items-center justify-center">
            <div className="text-center text-muted-foreground">
              <div className="text-4xl mb-2">🗺️</div>
              <div>Mapa de Boyacá</div>
              <div className="text-sm mt-1">Sedes UPTC</div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="w-full h-96 bg-card rounded-xl overflow-hidden" style={{ minHeight: '384px' }}>
      <MapContainer
        center={center}
        zoom={8}
        scrollWheelZoom={false}
        className="h-full w-full"
        style={{ height: '100%', width: '100%', minHeight: '384px', borderRadius: '0.75rem' }}
        whenCreated={(mapInstance) => {
          // Forzar un resize del mapa después de la carga
          setTimeout(() => {
            mapInstance.invalidateSize();
          }, 100);
        }}
        onError={() => setMapError(true)}
      >
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        
        {sedes.map((sede) => {
          const size = getCircleSize(sede.consumo_energia, maxConsumo);
          const color = getCircleColor(sede.consumo_energia, maxConsumo);
          
          return (
            <CircleMarker
              key={sede.id}
              center={[sede.lat, sede.lng]}
              radius={size}
              fillColor={color}
              color={color}
              weight={2}
              opacity={0.8}
              fillOpacity={0.6}
            >
              <Popup>
                <Card className="border-0 shadow-none max-w-xs">
                  <CardHeader className="pb-3">
                    <CardTitle className="text-lg">{sede.nombre}</CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-3">
                    <div className="flex items-center justify-between">
                      <span className="text-sm text-muted-foreground">Estudiantes:</span>
                      <Badge variant="secondary">{sede.estudiantes.toLocaleString()}</Badge>
                    </div>
                    
                    <div className="space-y-2">
                      <div className="flex items-center justify-between">
                        <span className="text-sm text-muted-foreground">Energía:</span>
                        <span className="text-sm font-medium">{sede.consumo_energia.toLocaleString()} kWh/mes</span>
                      </div>
                      
                      <div className="flex items-center justify-between">
                        <span className="text-sm text-muted-foreground">Agua:</span>
                        <span className="text-sm font-medium">{sede.consumo_agua.toLocaleString()} m³/mes</span>
                      </div>
                      
                      <div className="flex items-center justify-between">
                        <span className="text-sm text-muted-foreground">Emisiones CO2:</span>
                        <span className="text-sm font-medium">{sede.emisiones_co2} ton/mes</span>
                      </div>
                    </div>
                    
                    <div className="pt-2 border-t">
                      <div className="flex items-center gap-2">
                        <div 
                          className="w-3 h-3 rounded-full" 
                          style={{ backgroundColor: color }}
                        />
                        <span className="text-xs text-muted-foreground">
                          Nivel de consumo: {sede.consumo_energia > maxConsumo * 0.8 ? 'Alto' : 
                                           sede.consumo_energia > maxConsumo * 0.6 ? 'Medio-Alto' :
                                           sede.consumo_energia > maxConsumo * 0.4 ? 'Medio' : 'Bajo'}
                        </span>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </Popup>
            </CircleMarker>
          );
        })}
      </MapContainer>
    </div>
  );
}
