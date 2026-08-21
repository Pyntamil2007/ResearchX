import React, { useState } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import { ToastProvider } from './context/ToastContext';
import { ProtectedRoute } from './components/ProtectedRoute';
import { Navbar } from './components/Navbar';
import { Sidebar } from './components/Sidebar';

// Pages
import { Login } from './pages/Login';
import { Register } from './pages/Register';
import { ForgotPassword } from './pages/ForgotPassword';
import { ResetPassword } from './pages/ResetPassword';
import { Dashboard } from './pages/Dashboard';
import { UploadPaper } from './pages/UploadPaper';
import { Papers } from './pages/Papers';
import { PaperDetails } from './pages/PaperDetails';
import { AnalysisReport } from './pages/AnalysisReport';
import { History } from './pages/History';
import { Profile } from './pages/Profile';
import { AdminDashboard } from './pages/AdminDashboard';
import { Users } from './pages/Users';
import { AdminPapers } from './pages/AdminPapers';

// Styles
import './styles/index.css';
import './styles/layout.css';
import './styles/components.css';
import './styles/dashboard.css';
import './styles/report.css';

const AppLayout = ({ children, adminOnly = false }) => {
  const [sidebarOpen, setSidebarOpen] = useState(false);

  return (
    <ProtectedRoute adminOnly={adminOnly}>
      <div className="app-container">
        <Sidebar isOpen={sidebarOpen} onClose={() => setSidebarOpen(false)} />
        <div className="main-content-wrapper">
          <Navbar onToggleSidebar={() => setSidebarOpen(!sidebarOpen)} />
          <main className="page-body">
            {children}
          </main>
        </div>
      </div>
    </ProtectedRoute>
  );
};

export default function App() {
  return (
    <AuthProvider>
      <ToastProvider>
        <BrowserRouter>
          <Routes>
            {/* Root Route -> Redirects to Login */}
            <Route path="/" element={<Navigate to="/login" replace />} />

            {/* Public Auth Routes */}
            <Route path="/login" element={<Login />} />
            <Route path="/register" element={<Register />} />
            <Route path="/forgot-password" element={<ForgotPassword />} />
            <Route path="/reset-password" element={<ResetPassword />} />

            {/* Protected User / Researcher Routes */}
            <Route
              path="/dashboard"
              element={
                <AppLayout>
                  <Dashboard />
                </AppLayout>
              }
            />

            <Route
              path="/upload"
              element={
                <AppLayout>
                  <UploadPaper />
                </AppLayout>
              }
            />

            <Route
              path="/papers"
              element={
                <AppLayout>
                  <Papers />
                </AppLayout>
              }
            />

            <Route
              path="/papers/:id"
              element={
                <AppLayout>
                  <PaperDetails />
                </AppLayout>
              }
            />

            <Route
              path="/analysis/:id"
              element={
                <AppLayout>
                  <AnalysisReport />
                </AppLayout>
              }
            />

            <Route
              path="/history"
              element={
                <AppLayout>
                  <History />
                </AppLayout>
              }
            />

            <Route
              path="/profile"
              element={
                <AppLayout>
                  <Profile />
                </AppLayout>
              }
            />

            {/* Protected Admin Routes */}
            <Route
              path="/admin/dashboard"
              element={
                <AppLayout adminOnly={true}>
                  <AdminDashboard />
                </AppLayout>
              }
            />

            <Route
              path="/admin/users"
              element={
                <AppLayout adminOnly={true}>
                  <Users />
                </AppLayout>
              }
            />

            <Route
              path="/admin/papers"
              element={
                <AppLayout adminOnly={true}>
                  <AdminPapers />
                </AppLayout>
              }
            />

            {/* Fallback */}
            <Route path="*" element={<Navigate to="/login" replace />} />
          </Routes>
        </BrowserRouter>
      </ToastProvider>
    </AuthProvider>
  );
}
