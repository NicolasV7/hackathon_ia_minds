import { Toaster } from "@/components/ui/toaster";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import LandingPage from "./pages/LandingPage";
import DashboardLayout from "./components/dashboard/DashboardLayout";
import DashboardPage from "./pages/dashboard/DashboardPage";
import AnalyticsPage from "./pages/dashboard/AnalyticsPage";
import ModelosPage from "./pages/dashboard/ModelosPage";
import AlertasPage from "./pages/dashboard/AlertasPage";
import BalancesPage from "./pages/dashboard/BalancesPage";
import ExplicabilidadPage from "./pages/dashboard/ExplicabilidadPage";

import ApiTestPage from "./pages/dashboard/ApiTestPage";
import NotFound from "./pages/NotFound";

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 5 * 60 * 1000, // 5 minutes
      refetchOnWindowFocus: false,
    },
  },
});

const App = () => (
  <QueryClientProvider client={queryClient}>
    <TooltipProvider>
      <Toaster />
      <Sonner />
      <BrowserRouter>
        <div style={{ minHeight: '100vh' }}>
          <Routes>
            <Route path="/" element={<LandingPage />} />
            <Route path="/dashboard" element={<DashboardLayout><DashboardPage /></DashboardLayout>} />
            <Route path="/dashboard/analytics" element={<DashboardLayout><AnalyticsPage /></DashboardLayout>} />
            <Route path="/dashboard/balances" element={<DashboardLayout><BalancesPage /></DashboardLayout>} />
            <Route path="/dashboard/modelos" element={<DashboardLayout><ModelosPage /></DashboardLayout>} />
            <Route path="/dashboard/alertas" element={<DashboardLayout><AlertasPage /></DashboardLayout>} />
            <Route path="/dashboard/explicabilidad" element={<DashboardLayout><ExplicabilidadPage /></DashboardLayout>} />
            <Route path="/dashboard/api-test" element={<DashboardLayout><ApiTestPage /></DashboardLayout>} />
            <Route path="*" element={<NotFound />} />
          </Routes>
        </div>
      </BrowserRouter>
    </TooltipProvider>
  </QueryClientProvider>
);

export default App;
