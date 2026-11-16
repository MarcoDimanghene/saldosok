import { Navigate, useLocation } from 'react-router-dom';
import { useAuth } from '../hook/useAuth';

const ProtectedRoute = ({ children, adminOnly = false }) => {
  const { isAuthenticated, isLoading, user } = useAuth();
  const location = useLocation();

  if (isLoading) return <p role="status">Cargando sesión...</p>;
  if (!isAuthenticated) {
    return <Navigate to="/login" replace state={{ from: location }} />;
  }
  if (adminOnly && !user?.is_tenant_admin) {
    return <Navigate to="/dashboard" replace />;
  }
  if (!user?.is_tenant_admin && !['venta', 'compra'].includes(user?.perfil)) {
    return <p role="alert">Tu perfil todavía no tiene acceso habilitado.</p>;
  }
  if (
    !user?.is_tenant_admin
    && !['/invoices', '/companies'].includes(location.pathname)
  ) {
    return <Navigate to="/invoices" replace />;
  }

  return children;
};

export default ProtectedRoute;
