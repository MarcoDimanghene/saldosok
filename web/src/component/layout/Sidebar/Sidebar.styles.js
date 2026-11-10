import styled from 'styled-components';
import { Link } from 'react-router-dom';
import { COLORS, RADIUS } from '../../../styles/palette';
import { Button } from '../../ui/UIComponents';

export const SidebarContainer = styled.aside`
  position: sticky;
  top: 0;
  display: flex;
  flex: 0 0 260px;
  flex-direction: column;
  justify-content: space-between;
  box-sizing: border-box;
  width: 260px;
  height: 100vh;
  padding: 1.5rem 1rem;
  background: ${COLORS.PRIMARY};

  @media (max-width: 900px) {
    flex-basis: 220px;
    width: 220px;
    padding: 1.25rem 0.75rem;
  }

  @media (max-width: 700px) {
    flex-basis: 72px;
    width: 72px;
    padding: 1rem 0.5rem;
  }
`;

export const SidebarHeader = styled.div`
  display: flex;
  align-items: center;
  gap: 0.75rem;
  min-width: 0;
  margin-bottom: 2rem;

  @media (max-width: 700px) {
    justify-content: center;
  }
`;

export const SidebarLogo = styled.div`
  display: flex;
  flex: 0 0 2.5rem;
  align-items: center;
  justify-content: center;
  width: 2.5rem;
  height: 2.5rem;
  border-radius: ${RADIUS.MD};
  background: #00e5ff;
  color: ${COLORS.PRIMARY};
  box-shadow: 0 0 15px rgba(0, 229, 255, 0.22);
`;

export const BrandInfo = styled.div`
  display: flex;
  min-width: 0;
  flex-direction: column;

  h1 {
    color: #00e5ff;
    font-size: 1.15rem;
    font-weight: 700;
    letter-spacing: 0.04em;
    line-height: 1.2;
  }

  span {
    overflow: hidden;
    margin-top: 0.2rem;
    color: ${COLORS.OUTLINE};
    font-size: 0.68rem;
    font-weight: 600;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  @media (max-width: 700px) {
    display: none;
  }
`;

export const NavList = styled.nav`
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
`;

export const NavItem = styled(Link)`
  display: flex;
  align-items: center;
  gap: 0.85rem;
  min-height: 44px;
  padding: 0.65rem 0.85rem;
  border-left: 3px solid ${({ $active }) => ($active ? '#00e5ff' : 'transparent')};
  border-radius: ${RADIUS.MD};
  background: ${({ $active }) => ($active ? 'rgba(0, 229, 255, 0.08)' : 'transparent')};
  color: ${({ $active }) => ($active ? '#00e5ff' : 'rgba(255, 255, 255, 0.68)')};
  font-size: 0.88rem;
  font-weight: 600;
  text-decoration: none;
  transition: background 0.15s ease, color 0.15s ease;

  &:hover {
    background: rgba(255, 255, 255, 0.06);
    color: ${({ $active }) => ($active ? '#00e5ff' : '#ffffff')};
  }

  &:focus-visible {
    outline: 2px solid #00e5ff;
    outline-offset: 2px;
  }

  svg {
    flex-shrink: 0;
    font-size: 1.25rem;
  }

  @media (max-width: 700px) {
    justify-content: center;
    padding: 0.65rem 0.4rem;
  }
`;

export const NavLabel = styled.span`
  @media (max-width: 700px) {
    display: none;
  }
`;

export const SidebarFooter = styled.div`
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  margin-top: 2rem;
  padding-top: 1rem;
  border-top: 1px solid rgba(255, 255, 255, 0.08);

  @media (max-width: 700px) {
    align-items: center;
  }
`;

export const AccountName = styled.span`
  overflow: hidden;
  color: ${COLORS.SURFACE_CARD};
  font-size: 0.8rem;
  text-overflow: ellipsis;
  white-space: nowrap;

  @media (max-width: 700px) {
    display: none;
  }
`;

export const LogoutButton = styled(Button)`
  width: 100%;
  min-height: 44px;
  padding: 0.65rem 0.75rem;
  border-radius: ${RADIUS.MD};
  background: transparent;
  color: rgba(255, 255, 255, 0.72);
  font-size: 0.82rem;

  &:hover {
    background: rgba(255, 255, 255, 0.07);
    color: #ffffff;
  }

  &:focus-visible {
    outline: 2px solid #00e5ff;
    outline-offset: 2px;
  }

  svg {
    flex-shrink: 0;
    font-size: 1.15rem;
  }

  @media (max-width: 700px) {
    justify-content: center;
    padding: 0.65rem 0.4rem;
  }
`;
