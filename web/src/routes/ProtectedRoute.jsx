import { Navigate, useLocation } from 'react-router-dom';
import { useAuth } from '../hook/useAuth';

const ProtectedRoute = ({ children, fullAccessOnly = false, usersAdminOnly = false }) => {
  const { isAuthenticated, isLoading, user } = useAuth();
  const location = useLocation();
  const isTenantAdmin = Boolean(user?.is_tenant_admin);
  const hasFullAccess = isTenantAdmin || user?.perfil === 'analista';

  if (isLoading) return <p role="status">Cargando sesión...</p>;
  if (!isAuthenticated) {
    return <Navigate to="/login" replace state={{ from: location }} />;
  }
  if (fullAccessOnly && !hasFullAccess) {
    return <Navigate to="/invoices" replace />;
  }
  if (usersAdminOnly && !isTenantAdmin) {
    return <Navigate to="/invoices" replace />;
  }
  if (!isTenantAdmin && !['venta', 'compra', 'analista'].includes(user?.perfil)) {
    return <p role="alert">Tu perfil todavía no tiene acceso habilitado.</p>;
  }
  if (
    !hasFullAccess
    && !['/invoices', '/companies'].includes(location.pathname)
  ) {
    return <Navigate to="/invoices" replace />;
  }

  return children;
};

export default ProtectedRoute;
