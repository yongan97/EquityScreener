"use client";

import { useState } from "react";
import Link from "next/link";
import { useAuth, AuthModal } from "@/components/auth";
import { Button } from "@/components/ui/button";
import {
  TrendingUp,
  BarChart3,
  Brain,
  Zap,
  Shield,
  Clock,
  ArrowRight,
  CheckCircle2,
  LineChart,
  Target,
  Sparkles,
  ChevronRight,
} from "lucide-react";

export default function LandingPage() {
  const { user, isPremium } = useAuth();
  const [showAuthModal, setShowAuthModal] = useState(false);

  return (
    <div className="flex flex-col">
      {/* Hero Section */}
      <section className="relative overflow-hidden">
        {/* Background gradient */}
        <div className="absolute inset-0 bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-100 dark:from-slate-950 dark:via-blue-950 dark:to-indigo-950" />
        <div className="absolute inset-0 bg-[url('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNjAiIGhlaWdodD0iNjAiIHZpZXdCb3g9IjAgMCA2MCA2MCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48ZyBmaWxsPSJub25lIiBmaWxsLXJ1bGU9ImV2ZW5vZGQiPjxnIGZpbGw9IiMyMjI4M2QiIGZpbGwtb3BhY2l0eT0iMC4wMyI+PHBhdGggZD0iTTM2IDM0djItSDI0di0yaDEyek0zNiAyNHYySDI0di0yaDEyeiIvPjwvZz48L2c+PC9zdmc+')] opacity-50" />

        <div className="relative container mx-auto px-4 py-24 md:py-32 lg:py-40">
          <div className="max-w-4xl mx-auto text-center">
            {/* Badge */}
            <div className="inline-flex items-center gap-2 bg-blue-100 dark:bg-blue-900/50 text-blue-700 dark:text-blue-300 rounded-full px-4 py-1.5 text-sm font-medium mb-8">
              <Sparkles className="h-4 w-4" />
              AI-Powered Stock Screening
            </div>

            {/* Main headline */}
            <h1 className="text-4xl md:text-5xl lg:text-6xl font-bold tracking-tight mb-6">
              Encuentra las mejores acciones
              <span className="block text-transparent bg-clip-text bg-gradient-to-r from-blue-600 to-indigo-600 dark:from-blue-400 dark:to-indigo-400">
                con inteligencia artificial
              </span>
            </h1>

            {/* Subheadline */}
            <p className="text-xl md:text-2xl text-muted-foreground max-w-2xl mx-auto mb-10">
              Screening automatico diario usando la estrategia GARP.
              Analisis IA completo con ideas de trade profesionales.
            </p>

            {/* CTA Buttons */}
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              {user ? (
                <Button size="lg" className="text-lg px-8 py-6" asChild>
                  <Link href="/dashboard">
                    Ir al Dashboard
                    <ArrowRight className="ml-2 h-5 w-5" />
                  </Link>
                </Button>
              ) : (
                <Button
                  size="lg"
                  className="text-lg px-8 py-6 bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700"
                  onClick={() => setShowAuthModal(true)}
                >
                  Comenzar Gratis
                  <ArrowRight className="ml-2 h-5 w-5" />
                </Button>
              )}
              <Button size="lg" variant="outline" className="text-lg px-8 py-6" asChild>
                <Link href="/dashboard">
                  Ver Demo
                </Link>
              </Button>
            </div>

            {/* Trust indicators */}
            <div className="flex flex-wrap justify-center gap-8 mt-12 text-sm text-muted-foreground">
              <div className="flex items-center gap-2">
                <CheckCircle2 className="h-5 w-5 text-green-500" />
                Actualizacion diaria
              </div>
              <div className="flex items-center gap-2">
                <CheckCircle2 className="h-5 w-5 text-green-500" />
                100+ acciones analizadas
              </div>
              <div className="flex items-center gap-2">
                <CheckCircle2 className="h-5 w-5 text-green-500" />
                Sin tarjeta requerida
              </div>
            </div>
          </div>
        </div>

        {/* Wave divider */}
        <div className="absolute bottom-0 left-0 right-0">
          <svg viewBox="0 0 1440 120" fill="none" xmlns="http://www.w3.org/2000/svg" className="w-full h-auto">
            <path d="M0 120L60 105C120 90 240 60 360 45C480 30 600 30 720 37.5C840 45 960 60 1080 67.5C1200 75 1320 75 1380 75L1440 75V120H1380C1320 120 1200 120 1080 120C960 120 840 120 720 120C600 120 480 120 360 120C240 120 120 120 60 120H0Z" className="fill-background"/>
          </svg>
        </div>
      </section>

      {/* Stats Section */}
      <section className="py-16 bg-background">
        <div className="container mx-auto px-4">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8 max-w-4xl mx-auto">
            <div className="text-center">
              <div className="text-4xl md:text-5xl font-bold text-blue-600 dark:text-blue-400">100+</div>
              <div className="text-muted-foreground mt-2">Acciones diarias</div>
            </div>
            <div className="text-center">
              <div className="text-4xl md:text-5xl font-bold text-blue-600 dark:text-blue-400">6</div>
              <div className="text-muted-foreground mt-2">Factores IA</div>
            </div>
            <div className="text-center">
              <div className="text-4xl md:text-5xl font-bold text-blue-600 dark:text-blue-400">6AM</div>
              <div className="text-muted-foreground mt-2">Pre-market</div>
            </div>
            <div className="text-center">
              <div className="text-4xl md:text-5xl font-bold text-blue-600 dark:text-blue-400">$5</div>
              <div className="text-muted-foreground mt-2">Por mes</div>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-24 bg-muted/30">
        <div className="container mx-auto px-4">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold mb-4">
              Todo lo que necesitas para invertir mejor
            </h2>
            <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
              Herramientas profesionales de analisis, ahora accesibles para todos.
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8 max-w-6xl mx-auto">
            {/* Feature 1 */}
            <div className="bg-card rounded-2xl p-8 shadow-sm border hover:shadow-md transition-shadow">
              <div className="w-12 h-12 bg-blue-100 dark:bg-blue-900/50 rounded-xl flex items-center justify-center mb-6">
                <Brain className="h-6 w-6 text-blue-600 dark:text-blue-400" />
              </div>
              <h3 className="text-xl font-semibold mb-3">Scoring IA Avanzado</h3>
              <p className="text-muted-foreground">
                6 factores ponderados: fundamentales, valuacion, crecimiento,
                momentum, sentimiento y calidad. Score de 0 a 10.
              </p>
            </div>

            {/* Feature 2 */}
            <div className="bg-card rounded-2xl p-8 shadow-sm border hover:shadow-md transition-shadow">
              <div className="w-12 h-12 bg-green-100 dark:bg-green-900/50 rounded-xl flex items-center justify-center mb-6">
                <Target className="h-6 w-6 text-green-600 dark:text-green-400" />
              </div>
              <h3 className="text-xl font-semibold mb-3">Trade Ideas Completas</h3>
              <p className="text-muted-foreground">
                Tesis de inversion, puntos de entrada, niveles de riesgo
                y catalizadores. Listo para copiar y ejecutar.
              </p>
            </div>

            {/* Feature 3 */}
            <div className="bg-card rounded-2xl p-8 shadow-sm border hover:shadow-md transition-shadow">
              <div className="w-12 h-12 bg-purple-100 dark:bg-purple-900/50 rounded-xl flex items-center justify-center mb-6">
                <TrendingUp className="h-6 w-6 text-purple-600 dark:text-purple-400" />
              </div>
              <h3 className="text-xl font-semibold mb-3">Estrategia GARP</h3>
              <p className="text-muted-foreground">
                Growth At Reasonable Price. Acciones con alto crecimiento
                pero valuacion razonable. Lo mejor de dos mundos.
              </p>
            </div>

            {/* Feature 4 */}
            <div className="bg-card rounded-2xl p-8 shadow-sm border hover:shadow-md transition-shadow">
              <div className="w-12 h-12 bg-amber-100 dark:bg-amber-900/50 rounded-xl flex items-center justify-center mb-6">
                <Clock className="h-6 w-6 text-amber-600 dark:text-amber-400" />
              </div>
              <h3 className="text-xl font-semibold mb-3">Actualizacion Diaria</h3>
              <p className="text-muted-foreground">
                Cada dia a las 6AM EST, antes de la apertura del mercado.
                Siempre con datos frescos y relevantes.
              </p>
            </div>

            {/* Feature 5 */}
            <div className="bg-card rounded-2xl p-8 shadow-sm border hover:shadow-md transition-shadow">
              <div className="w-12 h-12 bg-red-100 dark:bg-red-900/50 rounded-xl flex items-center justify-center mb-6">
                <BarChart3 className="h-6 w-6 text-red-600 dark:text-red-400" />
              </div>
              <h3 className="text-xl font-semibold mb-3">Graficos TradingView</h3>
              <p className="text-muted-foreground">
                Graficos interactivos con indicadores tecnicos.
                Analisis tecnico integrado en cada accion.
              </p>
            </div>

            {/* Feature 6 */}
            <div className="bg-card rounded-2xl p-8 shadow-sm border hover:shadow-md transition-shadow">
              <div className="w-12 h-12 bg-cyan-100 dark:bg-cyan-900/50 rounded-xl flex items-center justify-center mb-6">
                <LineChart className="h-6 w-6 text-cyan-600 dark:text-cyan-400" />
              </div>
              <h3 className="text-xl font-semibold mb-3">Historial Completo</h3>
              <p className="text-muted-foreground">
                Tracking de scores historicos, variaciones de precio
                (1D, 1W, 1M, YTD, 52W) y tendencias.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* How It Works Section */}
      <section className="py-24 bg-background">
        <div className="container mx-auto px-4">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold mb-4">
              Como funciona
            </h2>
            <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
              Tres pasos simples para empezar a invertir de forma inteligente.
            </p>
          </div>

          <div className="max-w-4xl mx-auto">
            <div className="grid md:grid-cols-3 gap-8">
              {/* Step 1 */}
              <div className="relative">
                <div className="text-center">
                  <div className="w-16 h-16 bg-blue-600 text-white rounded-2xl flex items-center justify-center text-2xl font-bold mx-auto mb-6">
                    1
                  </div>
                  <h3 className="text-xl font-semibold mb-3">Registrate Gratis</h3>
                  <p className="text-muted-foreground">
                    Crea tu cuenta en segundos. Sin tarjeta de credito requerida.
                  </p>
                </div>
                <ChevronRight className="hidden md:block absolute top-8 -right-4 h-8 w-8 text-muted-foreground/30" />
              </div>

              {/* Step 2 */}
              <div className="relative">
                <div className="text-center">
                  <div className="w-16 h-16 bg-blue-600 text-white rounded-2xl flex items-center justify-center text-2xl font-bold mx-auto mb-6">
                    2
                  </div>
                  <h3 className="text-xl font-semibold mb-3">Explora los Picks</h3>
                  <p className="text-muted-foreground">
                    Revisa las acciones seleccionadas por nuestra IA cada manana.
                  </p>
                </div>
                <ChevronRight className="hidden md:block absolute top-8 -right-4 h-8 w-8 text-muted-foreground/30" />
              </div>

              {/* Step 3 */}
              <div>
                <div className="text-center">
                  <div className="w-16 h-16 bg-blue-600 text-white rounded-2xl flex items-center justify-center text-2xl font-bold mx-auto mb-6">
                    3
                  </div>
                  <h3 className="text-xl font-semibold mb-3">Toma Decisiones</h3>
                  <p className="text-muted-foreground">
                    Usa los Trade Ideas y analisis para informar tus inversiones.
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* AI Score Breakdown Section */}
      <section className="py-24 bg-gradient-to-br from-slate-900 to-blue-900 text-white">
        <div className="container mx-auto px-4">
          <div className="grid lg:grid-cols-2 gap-16 items-center max-w-6xl mx-auto">
            <div>
              <h2 className="text-3xl md:text-4xl font-bold mb-6">
                Scoring IA con 6 Factores
              </h2>
              <p className="text-xl text-blue-100 mb-8">
                Nuestro algoritmo analiza cada accion desde multiples angulos
                para darte una vision completa.
              </p>

              <div className="space-y-4">
                <div className="flex items-center gap-4">
                  <div className="w-2 h-2 bg-green-400 rounded-full" />
                  <span><strong>Fundamental (20%)</strong> - ROE, margenes, liquidez</span>
                </div>
                <div className="flex items-center gap-4">
                  <div className="w-2 h-2 bg-blue-400 rounded-full" />
                  <span><strong>Valuacion (25%)</strong> - PEG, P/E vs sector</span>
                </div>
                <div className="flex items-center gap-4">
                  <div className="w-2 h-2 bg-purple-400 rounded-full" />
                  <span><strong>Crecimiento (20%)</strong> - EPS historico y proyectado</span>
                </div>
                <div className="flex items-center gap-4">
                  <div className="w-2 h-2 bg-amber-400 rounded-full" />
                  <span><strong>Momentum (15%)</strong> - Tendencias tecnicas</span>
                </div>
                <div className="flex items-center gap-4">
                  <div className="w-2 h-2 bg-red-400 rounded-full" />
                  <span><strong>Sentimiento (10%)</strong> - Analisis de noticias</span>
                </div>
                <div className="flex items-center gap-4">
                  <div className="w-2 h-2 bg-cyan-400 rounded-full" />
                  <span><strong>Calidad (10%)</strong> - FCF, cash vs deuda</span>
                </div>
              </div>
            </div>

            <div className="bg-white/10 backdrop-blur rounded-2xl p-8">
              <div className="text-center mb-6">
                <div className="text-6xl font-bold text-white">8.5</div>
                <div className="text-blue-200">AI Score</div>
              </div>
              <div className="space-y-4">
                <ScoreBar label="Fundamental" value={85} color="bg-green-400" />
                <ScoreBar label="Valuacion" value={90} color="bg-blue-400" />
                <ScoreBar label="Crecimiento" value={75} color="bg-purple-400" />
                <ScoreBar label="Momentum" value={80} color="bg-amber-400" />
                <ScoreBar label="Sentimiento" value={70} color="bg-red-400" />
                <ScoreBar label="Calidad" value={95} color="bg-cyan-400" />
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-24 bg-background">
        <div className="container mx-auto px-4">
          <div className="max-w-3xl mx-auto text-center">
            <h2 className="text-3xl md:text-4xl font-bold mb-6">
              Empieza a invertir de forma mas inteligente
            </h2>
            <p className="text-xl text-muted-foreground mb-10">
              Unete a inversores que usan IA para tomar mejores decisiones.
              Prueba gratis hoy.
            </p>

            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              {user ? (
                <Button size="lg" className="text-lg px-8 py-6" asChild>
                  <Link href="/dashboard">
                    Ir al Dashboard
                    <ArrowRight className="ml-2 h-5 w-5" />
                  </Link>
                </Button>
              ) : (
                <Button
                  size="lg"
                  className="text-lg px-8 py-6 bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700"
                  onClick={() => setShowAuthModal(true)}
                >
                  Comenzar Gratis
                  <ArrowRight className="ml-2 h-5 w-5" />
                </Button>
              )}
              <Button size="lg" variant="outline" className="text-lg px-8 py-6" asChild>
                <Link href="/pricing">
                  Ver Planes
                </Link>
              </Button>
            </div>

            <p className="text-sm text-muted-foreground mt-6">
              Sin tarjeta de credito. Cancela cuando quieras.
            </p>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-muted/50 border-t">
        <div className="container mx-auto px-4 py-12">
          <div className="grid md:grid-cols-4 gap-8">
            <div className="md:col-span-2">
              <h3 className="text-xl font-bold mb-4">Stock Screener GARP</h3>
              <p className="text-muted-foreground mb-4 max-w-md">
                Screening de acciones con inteligencia artificial.
                Estrategia GARP para encontrar crecimiento a precio razonable.
              </p>
              <p className="text-sm text-muted-foreground">
                Datos actualizados diariamente a las 6:00 AM EST
              </p>
            </div>

            <div>
              <h4 className="font-semibold mb-4">Producto</h4>
              <ul className="space-y-2 text-muted-foreground">
                <li><Link href="/dashboard" className="hover:text-foreground transition-colors">Dashboard</Link></li>
                <li><Link href="/pricing" className="hover:text-foreground transition-colors">Precios</Link></li>
                <li><Link href="/history" className="hover:text-foreground transition-colors">Historial</Link></li>
              </ul>
            </div>

            <div>
              <h4 className="font-semibold mb-4">Legal</h4>
              <ul className="space-y-2 text-muted-foreground">
                <li><span className="cursor-pointer hover:text-foreground transition-colors">Terminos de Uso</span></li>
                <li><span className="cursor-pointer hover:text-foreground transition-colors">Privacidad</span></li>
                <li><span className="cursor-pointer hover:text-foreground transition-colors">Disclaimer</span></li>
              </ul>
            </div>
          </div>

          <div className="border-t mt-8 pt-8 text-center text-sm text-muted-foreground">
            <p>
              Este sitio es informativo y no constituye asesoramiento financiero.
              Consulte a su asesor antes de invertir.
            </p>
            <p className="mt-2">
              © {new Date().getFullYear()} Stock Screener GARP. Todos los derechos reservados.
            </p>
          </div>
        </div>
      </footer>

      <AuthModal
        isOpen={showAuthModal}
        onClose={() => setShowAuthModal(false)}
        defaultMode="signup"
      />
    </div>
  );
}

function ScoreBar({ label, value, color }: { label: string; value: number; color: string }) {
  return (
    <div>
      <div className="flex justify-between text-sm mb-1">
        <span className="text-blue-100">{label}</span>
        <span className="text-white font-medium">{(value / 10).toFixed(1)}</span>
      </div>
      <div className="h-2 bg-white/20 rounded-full overflow-hidden">
        <div className={`h-full ${color} rounded-full`} style={{ width: `${value}%` }} />
      </div>
    </div>
  );
}
