import { Link, useLocation, useNavigate } from 'react-router-dom';
import {
  TbBuilding,
  TbBuildingBank,
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
          <NavItem
            as={Link}
            to="/companies"
            $active={isActive('/companies')}
            aria-current={isActive('/companies') ? 'page' : undefined}
            title="Empresas"
          >
            <TbBuilding aria-hidden="true" />
            <NavLabel>Empresas</NavLabel>
          </NavItem>
          {user?.is_tenant_admin && (
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
          {user?.is_tenant_admin && (
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
            title="Ventas y compras"
          >
            <TbFileInvoice aria-hidden="true" />
            <NavLabel>Ventas y compras</NavLabel>
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
          {user?.is_tenant_admin && (
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
