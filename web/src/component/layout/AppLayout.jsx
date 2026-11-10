import { Outlet } from 'react-router-dom';
import Sidebar from './Sidebar/Sidebar';
import { AppLayoutContainer, AppMain } from './AppLayout.styles';

const AppLayout = () => (
  <AppLayoutContainer>
    <Sidebar />
    <AppMain>
      <Outlet />
    </AppMain>
  </AppLayoutContainer>
);

export default AppLayout;
