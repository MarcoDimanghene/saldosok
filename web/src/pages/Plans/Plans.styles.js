import styled from 'styled-components';
import { COLORS, RADIUS } from '../../styles/palette';

export const PlansContainer = styled.div``;

export const PlanHeader = styled.header`
  margin-bottom: 1.75rem;

  h1 {
    margin-bottom: 0.5rem;
    color: #00e5ff;
    font-size: 1.8rem;
  }

  p {
    margin-top: 0.5rem;
    color: rgba(255, 255, 255, 0.72);
  }
`;

export const PlanGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 1rem;
`;

export const PlanCard = styled.section`
  display: flex;
  flex-direction: column;
  gap: 1rem;
  padding: 1.5rem;
  border: 1px solid ${({ $selected }) => ($selected ? '#00e5ff' : 'rgba(0, 229, 255, 0.15)')};
  border-radius: ${RADIUS.LG};
  background: ${COLORS.PRIMARY_CONTAINER};

  h2 {
    color: ${({ $selected }) => ($selected ? '#00e5ff' : COLORS.SURFACE_CARD)};
  }

  p {
    min-height: 3rem;
    color: rgba(255, 255, 255, 0.72);
  }
`;

export const PlanSelectButton = styled.button`
  min-height: 44px;
  padding: 0.65rem 1rem;
  border: 0;
  border-radius: ${RADIUS.MD};
  background: #00e5ff;
  color: ${COLORS.PRIMARY};
  font: inherit;
  font-weight: 700;

  &:disabled {
    cursor: not-allowed;
    opacity: 0.6;
  }
`;

export const PlanMessage = styled.p`
  margin: 0.75rem 0;
  color: ${({ $error }) => ($error ? '#fda4af' : '#5eead4')};
`;
