// src/router/AppRouter.tsx
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { Role } from "../config/roles";
import { ProtectedRoute } from "./ProtectedRoute";
import { useAuth } from "../hooks/useAuth";

import Login           from "../pages/Login";
import Layout          from "../components/layout/Layout";
import Dashboard       from "../pages/dashboard/Dashboard";
import Logs            from "../pages/logs/Logs";
import LogDetail       from "../pages/logs/LogDetail";
import Investigations  from "../pages/investigations/Investigations";
import InvestigationDetail from "../pages/investigations/InvestigationDetail";
import Users           from "../pages/admin/Users";
import Purge           from "../pages/admin/Purge";
import Archive         from "../pages/archive/Archive";
import ArchiveChain    from "../pages/archive/ArchiveChain";
import Profile         from "../pages/Profile";

const RootRedirect = () => {
  const { isAuthenticated, redirectPath } = useAuth();
  return <Navigate to={isAuthenticated ? redirectPath() : "/login"} replace />;
};

const AppRouter = () => (
  <BrowserRouter>
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route path="/" element={<RootRedirect />} />

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
        <Route path="*" element={<Navigate to="/" replace />} />
      </Route>
    </Routes>
  </BrowserRouter>
);

export default AppRouter;