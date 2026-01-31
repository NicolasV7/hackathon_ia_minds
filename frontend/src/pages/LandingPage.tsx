import { Link } from 'react-router-dom';
import { Building2, Users, Layers, Database, ArrowRight, Zap, MapPin } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { MapaSedes } from '@/components/landing/MapaSedes';

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
          
          <div className="w-full h-[500px] rounded-xl overflow-hidden border border-border shadow-lg">
            <MapaSedes className="w-full h-full" />
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
