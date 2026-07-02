// src/router/AppRouter.tsx
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { Role } from "../config/roles";
import { ProtectedRoute } from "./ProtectedRoute";

import Login           from "../pages/Login";
import Layout          from "../components/layout/Layout";
import Dashboard       from "../pages/dashboard/Dashboard";
import Logs            from "../pages/logs/Logs";
import LogDetail       from "../pages/logs/LogDetail";
import Investigations  from "../pages/investigations/Investigations";
import InvestigationDetail from "../pages/investigations/InvestigationDetail";
import Users           from "../pages/admin/Users";
import Rules           from "../pages/admin/Rules";
import Playbooks      from "../pages/admin/Playbooks";
import System         from "../pages/admin/System";
import Purge           from "../pages/admin/Purge";
import Archive         from "../pages/archive/Archive";
import ArchiveChain    from "../pages/archive/ArchiveChain";
import Profile         from "../pages/Profile";
import AuditLogs      from "../pages/audit/Logs";
import AuditVerify    from "../pages/audit/Verify";

const AppRouter = () => (
  <BrowserRouter>
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route path="/" element={<Navigate to="/dashboard" replace />} />

      <Route element={<Layout />}>
        <Route path="/dashboard" element={
          <ProtectedRoute><Dashboard /></ProtectedRoute>
        }/>

        <Route path="/logs" element={
          <ProtectedRoute allowedRoles={[Role.ANALYSTE, Role.ADMINISTRATEUR, Role.LECTEUR]}>
            <Logs />
          </ProtectedRoute>
        }/>
        <Route path="/logs/:id" element={
          <ProtectedRoute allowedRoles={[Role.ANALYSTE, Role.ADMINISTRATEUR, Role.LECTEUR]}>
            <LogDetail />
          </ProtectedRoute>
        }/>

        <Route path="/investigations" element={
          <ProtectedRoute allowedRoles={[Role.ANALYSTE, Role.ADMINISTRATEUR]}>
            <Investigations />
          </ProtectedRoute>
        }/>
        <Route path="/investigations/:id" element={
          <ProtectedRoute allowedRoles={[Role.ANALYSTE, Role.ADMINISTRATEUR]}>
            <InvestigationDetail />
          </ProtectedRoute>
        }/>

        <Route path="/admin/users" element={
          <ProtectedRoute allowedRoles={[Role.ADMINISTRATEUR]}>
            <Users />
          </ProtectedRoute>
        }/>
        <Route path="/admin/purge" element={
          <ProtectedRoute allowedRoles={[Role.ADMINISTRATEUR]}>
            <Purge />
          </ProtectedRoute>
        }/>
        <Route path="/admin/rules" element={
          <ProtectedRoute allowedRoles={[Role.ADMINISTRATEUR]}>
            <Rules />
          </ProtectedRoute>
        }/>
        <Route path="/admin/playbooks" element={
          <ProtectedRoute allowedRoles={[Role.ADMINISTRATEUR]}>
            <Playbooks />
          </ProtectedRoute>
        }/>
        <Route path="/admin/system" element={
          <ProtectedRoute allowedRoles={[Role.ADMINISTRATEUR]}>
            <System />
          </ProtectedRoute>
        }/>

        <Route path="/audit/logs" element={
          <ProtectedRoute allowedRoles={[Role.AUDITEUR, Role.ADMINISTRATEUR]}>
            <AuditLogs />
          </ProtectedRoute>
        }/>
        <Route path="/audit/verify" element={
          <ProtectedRoute allowedRoles={[Role.AUDITEUR, Role.ADMINISTRATEUR]}>
            <AuditVerify />
          </ProtectedRoute>
        }/>

        <Route path="/archive" element={
          <ProtectedRoute allowedRoles={[Role.ADMINISTRATEUR]}>
            <Archive />
          </ProtectedRoute>
        }/>
        <Route path="/archive/chain" element={
          <ProtectedRoute allowedRoles={[Role.ADMINISTRATEUR]}>
            <ArchiveChain />
          </ProtectedRoute>
        }/>

        <Route path="/profile" element={
          <ProtectedRoute><Profile /></ProtectedRoute>
        }/>

        <Route path="/unauthorized" element={
          <div className="flex h-screen items-center justify-center text-destructive">
            Accès non autorisé
          </div>
        }/>
        <Route path="*" element={<Navigate to="/dashboard" replace />} />
      </Route>
    </Routes>
  </BrowserRouter>
);

export default AppRouter;