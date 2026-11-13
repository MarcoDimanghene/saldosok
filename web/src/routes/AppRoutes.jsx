import { Routes, Route, Navigate } from 'react-router-dom';
import Login from '../pages/Login/Login';
import Dashboard from '../pages/Dashboard/Dashboard';
import Users from '../pages/Users/Users';
import Companies from '../pages/Companies/Companies';
import Invoices from '../pages/Invoices/Invoices';
import Reports from '../pages/Reports/Reports';
import AuditLog from '../pages/Audit/AuditLog';
import ImportExcel from '../pages/ImportExcel/ImportExcel';
import EmailVerification from '../pages/EmailVerification/EmailVerification';
import ForgotPassword from '../pages/ForgotPassword/ForgotPassword';
import ResetPassword from '../pages/ResetPassword/ResetPassword';
import Profile from '../pages/Profile/Profile';
import AppLayout from '../component/layout/AppLayout';
import ProtectedRoute from './ProtectedRoute';

const AppRoutes = () => {
  return (
    <Routes>
      <Route path="/" element={<Navigate to="/login" replace />} />
      <Route path="/login" element={<Login />} />
      <Route path="/verify-email" element={<EmailVerification />} />
      <Route path="/forgot-password" element={<ForgotPassword />} />
      <Route path="/reset-password" element={<ResetPassword />} />
      <Route
        element={(
          <ProtectedRoute>
            <AppLayout />
          </ProtectedRoute>
        )}
      >
        <Route path="/dashboard" element={<Dashboard />} />
        <Route
          path="/profile"
          element={(
            <ProtectedRoute adminOnly>
              <Profile />
            </ProtectedRoute>
          )}
        />
        <Route path="/companies" element={<Companies />} />
        <Route path="/invoices" element={<Invoices />} />
        <Route path="/imports" element={<ImportExcel />} />
        <Route path="/reports" element={<Reports />} />
        <Route
          path="/audit"
          element={(
            <ProtectedRoute adminOnly>
              <AuditLog />
            </ProtectedRoute>
          )}
        />
        <Route
          path="/users"
          element={(
            <ProtectedRoute adminOnly>
              <Users />
            </ProtectedRoute>
          )}
        />
      </Route>
      <Route path="*" element={<Navigate to="/login" replace />} />
    </Routes>
  );
};

export default AppRoutes;
