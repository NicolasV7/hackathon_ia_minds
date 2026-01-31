import { Link } from 'react-router-dom';
import { Building2, Users, Layers, Database, ArrowRight, Zap, MapPin } from 'lucide-react';
import { Button } from '@/components/ui/button';

const stats = [
  { icon: Building2, value: '4', label: 'Sedes', color: 'text-primary' },
  { icon: Users, value: '31.5K+', label: 'Estudiantes', color: 'text-primary' },
  { icon: Layers, value: '5', label: 'Sectores', color: 'text-primary' },
  { icon: Database, value: '2018-2025', label: 'Datos Historicos', color: 'text-primary' },
];

const features = [
  {
    title: 'Prediccion Inteligente',
    description: 'Modelos de ML que predicen consumo energetico, agua y emisiones CO2 con alta precision.',
    icon: '🎯',
  },
  {
    title: 'Deteccion de Anomalias',
    description: 'Identificacion automatica de desperdicios y uso ineficiente con Isolation Forest.',
    icon: '🔍',
  },
  {
    title: 'Recomendaciones IA',
    description: 'Motor de recomendaciones personalizadas con LLM para acciones concretas.',
    icon: '💡',
  },
  {
    title: 'Explicabilidad',
    description: 'Transparencia total con SHAP values y metricas de confianza del modelo.',
    icon: '📊',
  },
];

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="fixed top-0 left-0 right-0 z-50 glass-effect">
        <div className="container mx-auto px-6 py-4 flex items-center justify-between">
          <Link to="/" className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-lg bg-primary flex items-center justify-center">
              <Zap className="w-6 h-6 text-primary-foreground" />
            </div>
            <span className="text-xl font-bold">UPTC Energy</span>
          </Link>
          
          <nav className="hidden md:flex items-center gap-8">
            <a href="#caracteristicas" className="text-muted-foreground hover:text-foreground transition-colors">
              Caracteristicas
            </a>
            <a href="#estadisticas" className="text-muted-foreground hover:text-foreground transition-colors">
              Estadisticas
            </a>
            <Link to="/dashboard">
              <Button variant="default" className="gap-2">
                Ir al Dashboard
                <ArrowRight className="w-4 h-4" />
              </Button>
            </Link>
          </nav>
        </div>
      </header>

      {/* Hero Section */}
      <section className="pt-32 pb-20 px-6">
        <div className="container mx-auto text-center">
          <div>
            <span className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-primary/10 text-primary text-sm font-medium mb-6">
              <Zap className="w-4 h-4" />
              Plataforma de IA para Sostenibilidad
            </span>
            
            <h1 className="text-4xl md:text-6xl font-bold mb-6 leading-tight">
              Optimiza el{' '}
              <span className="gradient-text">consumo energetico</span>
              <br />de la UPTC
            </h1>
            
            <p className="text-lg text-muted-foreground max-w-2xl mx-auto mb-8">
              Plataforma inteligente que predice, optimiza y recomienda acciones 
              para reducir el consumo energetico y la huella de carbono en las 4 
              sedes de Boyaca.
            </p>
            
            <Link to="/dashboard">
              <Button size="lg" className="gap-2 text-lg px-8 py-6">
                Explorar Dashboard
                <ArrowRight className="w-5 h-5" />
              </Button>
            </Link>
          </div>
        </div>
      </section>

      {/* Stats Section */}
      <section id="estadisticas" className="py-12 px-6">
        <div className="container mx-auto">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {stats.map((stat, index) => (
              <div
                key={index}
                className="stat-card text-center"
              >
                <stat.icon className={`w-6 h-6 ${stat.color} mx-auto mb-3`} />
                <div className="text-2xl md:text-3xl font-bold mb-1">{stat.value}</div>
                <div className="text-sm text-muted-foreground">{stat.label}</div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* GeoVisor Section */}
      <section className="py-16 px-6">
        <div className="container mx-auto">
          <div className="text-center mb-8">
            <div className="flex items-center justify-center gap-2 mb-4">
              <MapPin className="w-6 h-6 text-primary" />
              <h2 className="text-3xl font-bold">Ubicacion de las Sedes UPTC</h2>
            </div>
            <p className="text-muted-foreground max-w-xl mx-auto">
              Visualiza en tiempo real el consumo energetico de las 4 sedes de la UPTC en Boyaca
            </p>
          </div>
          
          <div>
            <div className="w-full h-96 bg-gray-800 rounded-xl overflow-hidden relative border border-gray-700">
              
              {/* Título del mapa */}
              <div className="absolute top-4 left-4 bg-black/80 backdrop-blur border border-gray-600 rounded-lg px-3 py-2 z-10">
                <div className="text-sm font-semibold text-white">Sedes UPTC - Boyacá</div>
              </div>
              
              {/* Puntos interactivos de las sedes */}
              <div className="absolute inset-0">
                {/* Sede Tunja - Centro del mapa */}
                <div className="absolute" style={{ top: '45%', left: '52%', transform: 'translate(-50%, -50%)' }}>
                  <div className="group relative cursor-pointer z-20">
                    <div className="w-6 h-6 bg-red-500 border-2 border-white rounded-full shadow-lg hover:scale-125 transition-all duration-200 animate-pulse">
                    </div>
                    <div className="absolute -bottom-16 left-1/2 transform -translate-x-1/2 bg-black/90 backdrop-blur border border-gray-600 rounded-lg p-3 opacity-0 group-hover:opacity-100 transition-all duration-200 min-w-max shadow-xl z-30">
                      <div className="text-sm font-semibold text-white">🔴 Tunja (Principal)</div>
                      <div className="text-xs text-gray-300 mt-1">18,000 estudiantes</div>
                      <div className="text-xs text-gray-300">⚡ 45,000 kWh/mes</div>
                      <div className="text-xs text-gray-300">💧 9,500 m³/mes</div>
                      <div className="text-xs text-red-400 font-medium mt-1">Alto consumo</div>
                    </div>
                  </div>
                </div>
                
                {/* Sede Duitama - Norte */}
                <div className="absolute" style={{ top: '25%', left: '45%', transform: 'translate(-50%, -50%)' }}>
                  <div className="group relative cursor-pointer z-20">
                    <div className="w-5 h-5 bg-orange-500 border-2 border-white rounded-full shadow-lg hover:scale-125 transition-all duration-200 animate-pulse">
                    </div>
                    <div className="absolute -bottom-16 left-1/2 transform -translate-x-1/2 bg-black/90 backdrop-blur border border-gray-600 rounded-lg p-3 opacity-0 group-hover:opacity-100 transition-all duration-200 min-w-max shadow-xl z-30">
                      <div className="text-sm font-semibold text-white">🟠 Duitama</div>
                      <div className="text-xs text-gray-300 mt-1">5,500 estudiantes</div>
                      <div className="text-xs text-gray-300">⚡ 18,200 kWh/mes</div>
                      <div className="text-xs text-gray-300">💧 3,800 m³/mes</div>
                      <div className="text-xs text-orange-400 font-medium mt-1">Medio-alto</div>
                    </div>
                  </div>
                </div>
                
                {/* Sede Sogamoso - Noreste */}
                <div className="absolute" style={{ top: '30%', left: '65%', transform: 'translate(-50%, -50%)' }}>
                  <div className="group relative cursor-pointer z-20">
                    <div className="w-5 h-5 bg-yellow-500 border-2 border-white rounded-full shadow-lg hover:scale-125 transition-all duration-200 animate-pulse">
                    </div>
                    <div className="absolute -bottom-16 left-1/2 transform -translate-x-1/2 bg-black/90 backdrop-blur border border-gray-600 rounded-lg p-3 opacity-0 group-hover:opacity-100 transition-all duration-200 min-w-max shadow-xl z-30">
                      <div className="text-sm font-semibold text-white">🟡 Sogamoso</div>
                      <div className="text-xs text-gray-300 mt-1">6,000 estudiantes</div>
                      <div className="text-xs text-gray-300">⚡ 15,500 kWh/mes</div>
                      <div className="text-xs text-gray-300">💧 3,200 m³/mes</div>
                      <div className="text-xs text-yellow-400 font-medium mt-1">Consumo medio</div>
                    </div>
                  </div>
                </div>
                
                {/* Sede Chiquinquirá - Oeste */}
                <div className="absolute" style={{ top: '60%', left: '25%', transform: 'translate(-50%, -50%)' }}>
                  <div className="group relative cursor-pointer z-20">
                    <div className="w-4 h-4 bg-green-500 border-2 border-white rounded-full shadow-lg hover:scale-125 transition-all duration-200 animate-pulse">
                    </div>
                    <div className="absolute -bottom-16 left-1/2 transform -translate-x-1/2 bg-black/90 backdrop-blur border border-gray-600 rounded-lg p-3 opacity-0 group-hover:opacity-100 transition-all duration-200 min-w-max shadow-xl z-30">
                      <div className="text-sm font-semibold text-white">🟢 Chiquinquirá</div>
                      <div className="text-xs text-gray-300 mt-1">2,000 estudiantes</div>
                      <div className="text-xs text-gray-300">⚡ 6,800 kWh/mes</div>
                      <div className="text-xs text-gray-300">💧 1,400 m³/mes</div>
                      <div className="text-xs text-green-400 font-medium mt-1">Bajo consumo</div>
                    </div>
                  </div>
                </div>
              </div>
              
              {/* Leyenda */}
              <div className="absolute bottom-4 right-4 bg-black/80 backdrop-blur border border-gray-600 rounded-lg px-3 py-2 z-10">
                <div className="text-sm font-semibold text-white mb-2">Consumo energético</div>
                <div className="space-y-1">
                  <div className="flex items-center gap-2 text-xs text-gray-300">
                    <div className="w-3 h-3 bg-red-500 rounded-full border border-white"></div>
                    <span>Alto (+40k kWh/mes)</span>
                  </div>
                  <div className="flex items-center gap-2 text-xs text-gray-300">
                    <div className="w-3 h-3 bg-orange-500 rounded-full border border-white"></div>
                    <span>Medio-alto (15-40k)</span>
                  </div>
                  <div className="flex items-center gap-2 text-xs text-gray-300">
                    <div className="w-3 h-3 bg-yellow-500 rounded-full border border-white"></div>
                    <span>Medio (10-15k)</span>
                  </div>
                  <div className="flex items-center gap-2 text-xs text-gray-300">
                    <div className="w-3 h-3 bg-green-500 rounded-full border border-white"></div>
                    <span>Bajo (-10k kWh/mes)</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section id="caracteristicas" className="py-20 px-6">
        <div className="container mx-auto">
          <div className="text-center mb-12">
            <h2 className="text-3xl md:text-4xl font-bold mb-4">
              Tecnologia de Vanguardia
            </h2>
            <p className="text-muted-foreground max-w-2xl mx-auto">
              Combinamos modelos de Machine Learning con IA explicable para tomar decisiones 
              informadas sobre el consumo energetico.
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
            {features.map((feature, index) => (
              <div
                key={index}
                className="stat-card"
              >
                <div className="text-4xl mb-4">{feature.icon}</div>
                <h3 className="text-lg font-semibold mb-2">{feature.title}</h3>
                <p className="text-sm text-muted-foreground">{feature.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 px-6">
        <div className="container mx-auto">
          <div className="stat-card text-center py-16">
            <h2 className="text-3xl font-bold mb-4">
              Comienza a reducir tu huella de carbono
            </h2>
            <p className="text-muted-foreground mb-8 max-w-xl mx-auto">
              Accede al dashboard para visualizar metricas en tiempo real, 
              predicciones y recomendaciones personalizadas.
            </p>
            <Link to="/dashboard">
              <Button size="lg" className="gap-2">
                Acceder al Dashboard
                <ArrowRight className="w-5 h-5" />
              </Button>
            </Link>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="py-8 px-6 border-t border-border">
        <div className="container mx-auto text-center text-muted-foreground text-sm">
          <p>Universidad Pedagogica y Tecnologica de Colombia - UPTC</p>
          <p className="mt-2">Plataforma de Gestion Energetica Inteligente</p>
        </div>
      </footer>
    </div>
  );
}
