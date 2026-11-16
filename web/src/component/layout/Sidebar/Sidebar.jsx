import { Link, useLocation, useNavigate } from 'react-router-dom';
import {
  TbBuilding,
  TbBuildingBank,
  TbChartLine,
  TbFileInvoice,
  TbFileSpreadsheet,
  TbHistory,
  TbLayoutDashboard,
  TbLogout,
  TbSettings,
  TbReportAnalytics,
  TbUsers,
} from 'react-icons/tb';
import { useAuth } from '../../../hook/useAuth';
import {
  AccountName,
  BrandInfo,
  LogoutButton,
  NavItem,
  NavLabel,
  NavList,
  SidebarContainer,
  SidebarFooter,
  SidebarHeader,
  SidebarLogo,
} from './Sidebar.styles';

const Sidebar = () => {
  const { user, tenant, logout } = useAuth();
  const location = useLocation();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login', { replace: true });
  };

  const isActive = (path) => (
    location.pathname === path || location.pathname.startsWith(`${path}/`)
  );
  const isTenantAdmin = Boolean(user?.is_tenant_admin);
  const isSales = !isTenantAdmin && user?.perfil === 'venta';
  const isPurchase = !isTenantAdmin && user?.perfil === 'compra';

  return (
    <SidebarContainer aria-label="Navegación principal">
      <div>
        <SidebarHeader>
          <SidebarLogo aria-hidden="true"><TbBuildingBank size={24} /></SidebarLogo>
          <BrandInfo>
            <h1>Saldo Ok</h1>
            <span title={tenant?.razon_social || undefined}>
              {tenant?.razon_social || 'Mi espacio de trabajo'}
            </span>
          </BrandInfo>
        </SidebarHeader>
        <NavList>
          {isTenantAdmin && (
            <NavItem
              as={Link}
              to="/dashboard"
              $active={isActive('/dashboard')}
              aria-current={isActive('/dashboard') ? 'page' : undefined}
              title="Inicio"
            >
              <TbLayoutDashboard aria-hidden="true" />
              <NavLabel>Inicio</NavLabel>
            </NavItem>
          )}
          <NavItem
            as={Link}
            to="/companies"
            $active={isActive('/companies')}
            aria-current={isActive('/companies') ? 'page' : undefined}
            title={isSales ? 'Clientes' : isPurchase ? 'Proveedores' : 'Empresas'}
          >
            <TbBuilding aria-hidden="true" />
            <NavLabel>{isSales ? 'Clientes' : isPurchase ? 'Proveedores' : 'Empresas'}</NavLabel>
          </NavItem>
          {isTenantAdmin && (
            <NavItem
              as={Link}
              to="/profile"
              $active={isActive('/profile')}
              aria-current={isActive('/profile') ? 'page' : undefined}
              title="Perfil de organización"
            >
              <TbSettings aria-hidden="true" />
              <NavLabel>Perfil</NavLabel>
            </NavItem>
          )}
          {isTenantAdmin && (
            <NavItem
              as={Link}
              to="/audit"
              $active={isActive('/audit')}
              aria-current={isActive('/audit') ? 'page' : undefined}
              title="Auditoría"
            >
              <TbHistory aria-hidden="true" />
              <NavLabel>Auditoría</NavLabel>
            </NavItem>
          )}
          <NavItem
            as={Link}
            to="/invoices"
            $active={isActive('/invoices')}
            aria-current={isActive('/invoices') ? 'page' : undefined}
            title={isSales ? 'Ventas y cobros' : isPurchase ? 'Compras y pagos' : 'Ventas y compras'}
          >
            <TbFileInvoice aria-hidden="true" />
            <NavLabel>
              {isSales ? 'Ventas y cobros' : isPurchase ? 'Compras y pagos' : 'Ventas y compras'}
            </NavLabel>
          </NavItem>
          {isTenantAdmin && (
            <>
              <NavItem
                as={Link}
                to="/operating-results"
                $active={isActive('/operating-results')}
                aria-current={isActive('/operating-results') ? 'page' : undefined}
                title="Resultado Operativo"
              >
                <TbChartLine aria-hidden="true" />
                <NavLabel>Resultado Operativo</NavLabel>
              </NavItem>
              <NavItem
                as={Link}
                to="/reports"
                $active={isActive('/reports')}
                aria-current={isActive('/reports') ? 'page' : undefined}
                title="Informes"
              >
                <TbReportAnalytics aria-hidden="true" />
                <NavLabel>Informes</NavLabel>
              </NavItem>
              <NavItem
                as={Link}
                to="/imports"
                $active={isActive('/imports')}
                aria-current={isActive('/imports') ? 'page' : undefined}
                title="Importar Excel"
              >
                <TbFileSpreadsheet aria-hidden="true" />
                <NavLabel>Importar Excel</NavLabel>
              </NavItem>
            </>
          )}
          {isTenantAdmin && (
            <NavItem
              as={Link}
              to="/users"
              $active={isActive('/users')}
              aria-current={isActive('/users') ? 'page' : undefined}
              title="Usuarios"
            >
              <TbUsers aria-hidden="true" />
              <NavLabel>Usuarios</NavLabel>
            </NavItem>
          )}
        </NavList>
      </div>

      <SidebarFooter>
        <AccountName title={user?.nombre || user?.username}>
          {user?.nombre || user?.username}
        </AccountName>
        <LogoutButton type="button" $variant="sidebar" onClick={handleLogout}>
          <TbLogout aria-hidden="true" />
          <NavLabel>Cerrar sesión</NavLabel>
        </LogoutButton>
      </SidebarFooter>
    </SidebarContainer>
  );
};

export default Sidebar;
