"use client";

import * as React from "react";
import maplibregl from "maplibre-gl";
import "maplibre-gl/dist/maplibre-gl.css";

const MAP_STYLES = {
  light: "https://basemaps.cartocdn.com/gl/positron-gl-style/style.json",
  dark: "https://basemaps.cartocdn.com/gl/dark-matter-gl-style/style.json",
  streets: "https://basemaps.cartocdn.com/gl/voyager-gl-style/style.json",
};

// Hook to detect system/document dark mode
function useTheme() {
  const [isDark, setIsDark] = React.useState(() => {
    if (typeof window === "undefined") return false;
    return (
      document.documentElement.classList.contains("dark") ||
      window.matchMedia("(prefers-color-scheme: dark)").matches
    );
  });

  React.useEffect(() => {
    // Watch for class changes on html element
    const observer = new MutationObserver(() => {
      setIsDark(document.documentElement.classList.contains("dark"));
    });
    observer.observe(document.documentElement, {
      attributes: true,
      attributeFilter: ["class"],
    });

    // Watch for system preference changes
    const mediaQuery = window.matchMedia("(prefers-color-scheme: dark)");
    const handleChange = (e: MediaQueryListEvent) => {
      if (!document.documentElement.classList.contains("dark") && 
          !document.documentElement.classList.contains("light")) {
        setIsDark(e.matches);
      }
    };
    mediaQuery.addEventListener("change", handleChange);

    return () => {
      observer.disconnect();
      mediaQuery.removeEventListener("change", handleChange);
    };
  }, []);

  return isDark;
}

// Coordenadas de las sedes UPTC
const SEDES_DATA = [
  {
    id: "tunja",
    nombre: "Tunja (Principal)",
    estudiantes: 18000,
    lat: 5.5353,
    lng: -73.3678,
    consumo_energia: 45000,
    consumo_agua: 9500,
    emisiones_co2: 68.5,
    color: "#ef4444", // red-500
    nivel: "Alto",
  },
  {
    id: "duitama",
    nombre: "Duitama",
    estudiantes: 5500,
    lat: 5.8267,
    lng: -73.0333,
    consumo_energia: 18200,
    consumo_agua: 3800,
    emisiones_co2: 27.3,
    color: "#f97316", // orange-500
    nivel: "Medio-alto",
  },
  {
    id: "sogamoso",
    nombre: "Sogamoso",
    estudiantes: 6000,
    lat: 5.7147,
    lng: -72.9314,
    consumo_energia: 15500,
    consumo_agua: 3200,
    emisiones_co2: 23.2,
    color: "#eab308", // yellow-500
    nivel: "Medio",
  },
  {
    id: "chiquinquira",
    nombre: "Chiquinquira",
    estudiantes: 2000,
    lat: 5.6167,
    lng: -73.8167,
    consumo_energia: 6800,
    consumo_agua: 1400,
    emisiones_co2: 10.2,
    color: "#22c55e", // green-500
    nivel: "Bajo",
  },
];

interface MapaSedesProps {
  className?: string;
}

export function MapaSedes({ className }: MapaSedesProps) {
  const containerRef = React.useRef<HTMLDivElement>(null);
  const mapRef = React.useRef<maplibregl.Map | null>(null);
  const markersRef = React.useRef<maplibregl.Marker[]>([]);
  const popupRef = React.useRef<maplibregl.Popup | null>(null);
  const isDark = useTheme();

  // Update map style when theme changes
  React.useEffect(() => {
    if (mapRef.current) {
      mapRef.current.setStyle(isDark ? MAP_STYLES.dark : MAP_STYLES.light);
    }
  }, [isDark]);

  React.useEffect(() => {
    if (!containerRef.current || mapRef.current) return;

    // Centro del mapa (Boyacá)
    const center = { lat: 5.7, lng: -73.2 };

    const map = new maplibregl.Map({
      container: containerRef.current,
      style: isDark ? MAP_STYLES.dark : MAP_STYLES.light,
      center: [center.lng, center.lat],
      zoom: 9,
      minZoom: 8,
      maxZoom: 15,
      attributionControl: false,
    });

    map.addControl(
      new maplibregl.AttributionControl({ compact: true }),
      "bottom-right"
    );

    map.addControl(new maplibregl.NavigationControl(), "top-right");

    mapRef.current = map;

    // Agregar marcadores de sedes
    SEDES_DATA.forEach((sede) => {
      const el = document.createElement("div");
      el.className = "sede-marker";
      el.innerHTML = `
        <div class="relative cursor-pointer transition-all hover:scale-110">
          <div class="w-8 h-8 rounded-full border-3 border-white shadow-lg flex items-center justify-center"
               style="background-color: ${sede.color};">
            <svg class="w-4 h-4 text-white" fill="currentColor" viewBox="0 0 20 20">
              <path d="M10 2a6 6 0 00-6 6c0 3.314 6 10 6 10s6-6.686 6-10a6 6 0 00-6-6zm0 8a2 2 0 110-4 2 2 0 010 4z"/>
            </svg>
          </div>
          <div class="absolute -bottom-1 left-1/2 transform -translate-x-1/2 w-0 h-0 border-l-[6px] border-l-transparent border-r-[6px] border-r-transparent border-t-[8px] border-t-white"></div>
        </div>
      `;

      const marker = new maplibregl.Marker({ element: el })
        .setLngLat([sede.lng, sede.lat])
        .addTo(map);

      // Popup al hacer click
      el.addEventListener("click", (e) => {
        e.stopPropagation();

        if (popupRef.current) {
          popupRef.current.remove();
        }

        const isDarkMode = document.documentElement.classList.contains("dark");
        const bgClass = isDarkMode ? "bg-gray-900 text-gray-100" : "bg-white text-gray-900";
        const textMuted = isDarkMode ? "text-gray-400" : "text-gray-600";
        const borderColor = isDarkMode ? "border-gray-700" : "border-gray-200";

        const popupContent = `
          <div class="sede-popup ${bgClass}" style="min-width: 280px;">
            <div class="p-4">
              <div class="flex items-center gap-2 mb-3">
                <div class="w-3 h-3 rounded-full" style="background-color: ${sede.color};"></div>
                <h3 class="font-bold text-lg">${sede.nombre}</h3>
              </div>
              
              <div class="space-y-2 text-sm">
                <div class="flex items-center justify-between">
                  <span class="${textMuted}">Estudiantes:</span>
                  <span class="font-semibold tabular-nums">${sede.estudiantes.toLocaleString()}</span>
                </div>
                
                <div class="flex items-center justify-between">
                  <span class="${textMuted}">Energia:</span>
                  <span class="font-semibold tabular-nums">${sede.consumo_energia.toLocaleString()} kWh/mes</span>
                </div>
                
                <div class="flex items-center justify-between">
                  <span class="${textMuted}">Agua:</span>
                  <span class="font-semibold tabular-nums">${sede.consumo_agua.toLocaleString()} m3/mes</span>
                </div>
                
                <div class="flex items-center justify-between">
                  <span class="${textMuted}">CO2:</span>
                  <span class="font-semibold tabular-nums">${sede.emisiones_co2} ton/mes</span>
                </div>
              </div>
              
              <div class="mt-3 pt-3 border-t ${borderColor}">
                <div class="flex items-center justify-between">
                  <span class="text-xs ${textMuted}">Nivel de consumo:</span>
                  <span class="text-xs font-medium px-2 py-1 rounded-full text-white" 
                        style="background-color: ${sede.color};">${sede.nivel}</span>
                </div>
              </div>
            </div>
          </div>
        `;

        const popup = new maplibregl.Popup({
          offset: [0, -10],
          closeButton: true,
          closeOnClick: false,
          className: "sede-popup-container",
          maxWidth: "320px",
        })
          .setLngLat([sede.lng, sede.lat])
          .setHTML(popupContent)
          .addTo(map);

        popupRef.current = popup;
      });

      markersRef.current.push(marker);
    });

    return () => {
      markersRef.current.forEach((marker) => marker.remove());
      markersRef.current = [];
      if (popupRef.current) {
        popupRef.current.remove();
      }
      map.remove();
      mapRef.current = null;
    };
  }, []);

  return (
    <div className={`relative w-full h-full ${className}`}>
      <div ref={containerRef} className="absolute inset-0 w-full h-full rounded-xl overflow-hidden" />
      
      {/* Leyenda */}
      <div className="absolute bottom-4 right-4 bg-white/95 dark:bg-gray-900/95 backdrop-blur-sm border border-gray-200 dark:border-gray-700 rounded-lg p-4 shadow-lg z-10">
        <h4 className="font-semibold text-sm mb-3 text-gray-800 dark:text-gray-100">Consumo Energetico</h4>
        <div className="space-y-2">
          {[
            { color: "#ef4444", label: "Alto (+40k kWh/mes)", range: "+40,000" },
            { color: "#f97316", label: "Medio-alto (15-40k)", range: "15k-40k" },
            { color: "#eab308", label: "Medio (10-15k)", range: "10k-15k" },
            { color: "#22c55e", label: "Bajo (-10k kWh/mes)", range: "-10,000" },
          ].map((item) => (
            <div key={item.label} className="flex items-center gap-2">
              <div 
                className="w-4 h-4 rounded-full border-2 border-white dark:border-gray-800 shadow-sm"
                style={{ backgroundColor: item.color }}
              />
              <span className="text-xs text-gray-600 dark:text-gray-400">{item.label}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Titulo */}
      <div className="absolute top-4 left-4 bg-white/95 dark:bg-gray-900/95 backdrop-blur-sm border border-gray-200 dark:border-gray-700 rounded-lg px-4 py-2 shadow-lg z-10">
        <div className="text-sm font-semibold text-gray-800 dark:text-gray-100">Sedes UPTC - Boyaca</div>
        <div className="text-xs text-gray-500 dark:text-gray-400">4 sedes universitarias</div>
      </div>
    </div>
  );
}
