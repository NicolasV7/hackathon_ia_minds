import { Link } from 'react-router-dom';
import { ArrowRight, Activity, Shield, BarChart3, Cpu, ChevronRight } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { MapaSedes } from '@/components/landing/MapaSedes';

// Metrics data with tabular numbers for alignment
const metrics = [
  { value: '4', unit: 'sedes', description: 'Campus monitoreados en Boyaca' },
  { value: '31.5K', unit: 'estudiantes', description: 'Poblacion universitaria activa' },
  { value: '85.5K', unit: 'kWh/mes', description: 'Consumo energetico total' },
  { value: '129', unit: 'ton CO2', description: 'Emisiones mensuales rastreadas' },
];

// Capabilities with clear value propositions
const capabilities = [
  {
    icon: BarChart3,
    title: 'Prediccion de Consumo',
    description: 'Modelos de machine learning entrenados con 7 anos de datos historicos. Precision del 99.8% en prediccion de energia.',
    metric: '99.8%',
    metricLabel: 'precision',
  },
  {
    icon: Activity,
    title: 'Deteccion de Anomalias',
    description: 'Isolation Forest identifica patrones de consumo irregular en tiempo real. Reduccion del 23% en desperdicios detectados.',
    metric: '-23%',
    metricLabel: 'desperdicios',
  },
  {
    icon: Cpu,
    title: 'Optimizacion Inteligente',
    description: 'Recomendaciones generadas por IA con estimaciones de ahorro concretas. ROI promedio de 18 meses por implementacion.',
    metric: '18',
    metricLabel: 'meses ROI',
  },
  {
    icon: Shield,
    title: 'Transparencia Total',
    description: 'SHAP values y metricas de confianza en cada prediccion. Decisiones auditables y explicables para stakeholders.',
    metric: '100%',
    metricLabel: 'explicable',
  },
];

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-background">
      {/* Skip to main content link for accessibility */}
      <a 
        href="#main-content" 
        className="sr-only focus:not-sr-only focus:absolute focus:top-4 focus:left-4 focus:z-50 focus:px-4 focus:py-2 focus:bg-primary focus:text-primary-foreground focus:rounded-md focus-visible:ring-2 focus-visible:ring-ring"
      >
        Saltar al contenido principal
      </a>

      {/* Header */}
      <header className="fixed top-0 left-0 right-0 z-50 border-b border-border/40 bg-background/80 backdrop-blur-lg supports-[backdrop-filter]:bg-background/60">
        <nav className="container mx-auto px-6 h-16 flex items-center justify-between" aria-label="Navegacion principal">
          <Link 
            to="/" 
            className="flex items-center gap-3 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 rounded-md"
            aria-label="UPTC EcoEnergy - Inicio"
          >
            <div className="w-9 h-9 rounded-lg bg-primary flex items-center justify-center" aria-hidden="true">
              <Activity className="w-5 h-5 text-primary-foreground" />
            </div>
            <div className="flex flex-col">
              <span className="text-base font-semibold leading-none tracking-tight">UPTC EcoEnergy</span>
              <span className="text-[11px] text-muted-foreground leading-none mt-0.5">Gestion Energetica</span>
            </div>
          </Link>
          
          <div className="hidden md:flex items-center gap-1">
            <a 
              href="#capacidades" 
              className="px-4 py-2 text-sm text-muted-foreground hover:text-foreground transition-colors rounded-md focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
            >
              Capacidades
            </a>
            <a 
              href="#mapa" 
              className="px-4 py-2 text-sm text-muted-foreground hover:text-foreground transition-colors rounded-md focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
            >
              Cobertura
            </a>
            <div className="w-px h-5 bg-border mx-2" aria-hidden="true" />
            <Link to="/dashboard">
              <Button 
                variant="default" 
                size="sm" 
                className="gap-2 font-medium focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
              >
                Acceder
                <ArrowRight className="w-4 h-4" aria-hidden="true" />
              </Button>
            </Link>
          </div>

          {/* Mobile menu button */}
          <Link to="/dashboard" className="md:hidden">
            <Button variant="default" size="sm" className="focus-visible:ring-2 focus-visible:ring-ring">
              Acceder
            </Button>
          </Link>
        </nav>
      </header>

      <main id="main-content">
        {/* Hero Section */}
        <section className="pt-32 pb-24 px-6 lg:pt-40 lg:pb-32">
          <div className="container mx-auto max-w-5xl">
            <div className="text-center">
              {/* Eyebrow */}
              <p className="inline-flex items-center gap-2 px-3 py-1 rounded-full border border-border bg-secondary/50 text-xs font-medium text-muted-foreground mb-8">
                <span className="w-1.5 h-1.5 rounded-full bg-success animate-pulse" aria-hidden="true" />
                Sistema operativo 24/7
              </p>
              
              {/* Headline */}
              <h1 className="text-4xl md:text-5xl lg:text-6xl font-bold tracking-tight mb-6 text-balance">
                Gestion energetica
                <br />
                <span className="bg-gradient-to-r from-primary via-primary to-amber-400 bg-clip-text text-transparent">
                  basada en datos
                </span>
              </h1>
              
              {/* Subheadline */}
              <p className="text-lg md:text-xl text-muted-foreground max-w-2xl mx-auto mb-10 text-pretty leading-relaxed">
                Plataforma de monitoreo y optimizacion para las 4 sedes de la UPTC. 
                Reduce consumo, minimiza emisiones y toma decisiones informadas con 
                modelos de machine learning.
              </p>
              
              {/* CTA Group */}
              <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
                <Link to="/dashboard">
                  <Button 
                    size="lg" 
                    className="gap-2 text-base px-8 h-12 font-medium shadow-lg shadow-primary/20 hover:shadow-xl hover:shadow-primary/30 transition-shadow focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
                  >
                    Ver Dashboard
                    <ArrowRight className="w-4 h-4" aria-hidden="true" />
                  </Button>
                </Link>
                <a 
                  href="#capacidades"
                  className="inline-flex items-center gap-2 text-sm font-medium text-muted-foreground hover:text-foreground transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring rounded-md px-2 py-1"
                >
                  Conocer capacidades
                  <ChevronRight className="w-4 h-4" aria-hidden="true" />
                </a>
              </div>
            </div>
          </div>
        </section>

        {/* Metrics Bar */}
        <section className="py-12 px-6 border-y border-border/40 bg-secondary/30" aria-labelledby="metrics-heading">
          <h2 id="metrics-heading" className="sr-only">Metricas principales</h2>
          <div className="container mx-auto">
            <div className="grid grid-cols-2 lg:grid-cols-4 gap-8 lg:gap-12">
              {metrics.map((metric, index) => (
                <div key={index} className="text-center lg:text-left">
                  <div className="flex items-baseline justify-center lg:justify-start gap-1.5 mb-1">
                    <span className="text-3xl md:text-4xl font-bold tracking-tight tabular-nums">
                      {metric.value}
                    </span>
                    <span className="text-sm font-medium text-muted-foreground">
                      {metric.unit}
                    </span>
                  </div>
                  <p className="text-sm text-muted-foreground">
                    {metric.description}
                  </p>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* Capabilities Section */}
        <section id="capacidades" className="py-24 px-6 scroll-mt-20" aria-labelledby="capabilities-heading">
          <div className="container mx-auto max-w-6xl">
            <header className="max-w-2xl mb-16">
              <h2 id="capabilities-heading" className="text-3xl md:text-4xl font-bold tracking-tight mb-4">
                Capacidades del Sistema
              </h2>
              <p className="text-lg text-muted-foreground text-pretty">
                Cuatro pilares tecnologicos que transforman datos de consumo en 
                decisiones estrategicas de ahorro energetico.
              </p>
            </header>

            <div className="grid md:grid-cols-2 gap-6">
              {capabilities.map((capability, index) => (
                <article 
                  key={index}
                  className="group relative p-6 rounded-xl border border-border bg-card hover:border-primary/30 transition-colors focus-within:ring-2 focus-within:ring-ring"
                >
                  <div className="flex items-start gap-4">
                    <div className="flex-shrink-0 w-10 h-10 rounded-lg bg-primary/10 flex items-center justify-center" aria-hidden="true">
                      <capability.icon className="w-5 h-5 text-primary" />
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-start justify-between gap-4 mb-2">
                        <h3 className="text-base font-semibold">{capability.title}</h3>
                        <div className="flex-shrink-0 text-right">
                          <span className="text-lg font-bold tabular-nums text-primary">
                            {capability.metric}
                          </span>
                          <span className="block text-[11px] text-muted-foreground uppercase tracking-wide">
                            {capability.metricLabel}
                          </span>
                        </div>
                      </div>
                      <p className="text-sm text-muted-foreground leading-relaxed">
                        {capability.description}
                      </p>
                    </div>
                  </div>
                </article>
              ))}
            </div>
          </div>
        </section>

        {/* Map Section */}
        <section id="mapa" className="py-24 px-6 bg-secondary/20 scroll-mt-20" aria-labelledby="map-heading">
          <div className="container mx-auto max-w-6xl">
            <header className="flex flex-col md:flex-row md:items-end md:justify-between gap-4 mb-8">
              <div>
                <h2 id="map-heading" className="text-3xl md:text-4xl font-bold tracking-tight mb-2">
                  Cobertura Regional
                </h2>
                <p className="text-muted-foreground">
                  Monitoreo en tiempo real de las 4 sedes universitarias en Boyaca
                </p>
              </div>
              <Link to="/dashboard">
                <Button 
                  variant="outline" 
                  size="sm" 
                  className="gap-2 focus-visible:ring-2 focus-visible:ring-ring"
                >
                  Ver detalles por sede
                  <ArrowRight className="w-4 h-4" aria-hidden="true" />
                </Button>
              </Link>
            </header>
            
            <div 
              className="w-full h-[480px] md:h-[540px] rounded-xl overflow-hidden border border-border shadow-2xl shadow-black/20"
              role="img"
              aria-label="Mapa interactivo de las sedes UPTC en Boyaca con indicadores de consumo energetico"
            >
              <MapaSedes className="w-full h-full" />
            </div>
          </div>
        </section>

        {/* CTA Section */}
        <section className="py-24 px-6" aria-labelledby="cta-heading">
          <div className="container mx-auto max-w-3xl text-center">
            <h2 id="cta-heading" className="text-2xl md:text-3xl font-bold tracking-tight mb-4">
              Inicia el monitoreo de tu sede
            </h2>
            <p className="text-muted-foreground mb-8 max-w-xl mx-auto">
              Accede al dashboard para visualizar consumo en tiempo real, 
              revisar predicciones y actuar sobre las recomendaciones de optimizacion.
            </p>
            <Link to="/dashboard">
              <Button 
                size="lg" 
                className="gap-2 font-medium focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
              >
                Acceder al Dashboard
                <ArrowRight className="w-4 h-4" aria-hidden="true" />
              </Button>
            </Link>
          </div>
        </section>
      </main>

      {/* Footer */}
      <footer className="py-8 px-6 border-t border-border" role="contentinfo">
        <div className="container mx-auto flex flex-col md:flex-row items-center justify-between gap-4">
          <p className="text-sm text-muted-foreground">
            Universidad Pedagogica y Tecnologica de Colombia
          </p>
          <p className="text-sm text-muted-foreground">
            Plataforma de Gestion Energetica Inteligente
          </p>
        </div>
      </footer>
    </div>
  );
}
