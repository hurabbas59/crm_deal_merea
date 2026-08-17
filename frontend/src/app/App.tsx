import { Navigate, Route, Routes } from "react-router-dom";

import { AppLayout } from "../components/layout/AppLayout";
import { ContactsPage } from "../pages/ContactsPage";
import { DashboardPage } from "../pages/DashboardPage";
import { DealDetailPage } from "../pages/DealDetailPage";
import { MapPage } from "../pages/MapPage";
import { PipelinePage } from "../pages/PipelinePage";
import { TasksPage } from "../pages/TasksPage";

export function App() {
  return (
    <AppLayout>
      <Routes>
        <Route path="/" element={<Navigate to="/dashboard" replace />} />
        <Route path="/dashboard" element={<DashboardPage />} />
        <Route path="/pipeline" element={<PipelinePage />} />
        <Route path="/deals/:dealId" element={<DealDetailPage />} />
        <Route path="/contacts" element={<ContactsPage />} />
        <Route path="/map" element={<MapPage />} />
        <Route path="/tasks" element={<TasksPage />} />
      </Routes>
    </AppLayout>
  );
}

