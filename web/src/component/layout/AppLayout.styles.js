import styled from 'styled-components';
import { COLORS } from '../../styles/palette';

export const AppLayoutContainer = styled.div`
  display: flex;
  min-height: 100vh;
  background: ${COLORS.PRIMARY};
`;

export const AppMain = styled.main`
  flex: 1;
  min-width: 0;
  padding: 2rem;
  color: ${COLORS.SURFACE_CARD};

  @media (max-width: 700px) {
    padding: 1.25rem 1rem;
  }
`;
