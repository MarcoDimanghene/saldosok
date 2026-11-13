import styled from 'styled-components';
import { Card } from '../../component/ui/UIComponents';
import { COLORS, RADIUS } from '../../styles/palette';

export const AuditContainer = styled.main`
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
`;

export const AuditHeader = styled.header`
  h1 {
    margin-bottom: 0.45rem;
    color: #00e5ff;
    font-size: 1.8rem;
  }

  p {
    color: rgba(255, 255, 255, 0.72);
  }
`;

export const AuditPanel = styled(Card)`
  min-width: 0;
  padding: 0;
  overflow: hidden;
  border-color: rgba(255, 255, 255, 0.1);
  background: ${COLORS.PRIMARY_CONTAINER};
`;

export const AuditTableWrap = styled.div`
  overflow-x: auto;
`;

export const AuditTable = styled.table`
  width: 100%;
  min-width: 860px;
  border-collapse: collapse;
  text-align: left;

  th,
  td {
    padding: 0.9rem 1rem;
    border-bottom: 1px solid rgba(255, 255, 255, 0.09);
    vertical-align: top;
  }

  th {
    color: rgba(255, 255, 255, 0.72);
    font-size: 0.8rem;
    text-transform: uppercase;
  }

  td {
    color: ${COLORS.SURFACE_CARD};
    font-size: 0.9rem;
  }

  tr:last-child td {
    border-bottom: 0;
  }
`;

export const AuditDetails = styled.ul`
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  min-width: 240px;
  padding-left: 1rem;
  color: rgba(255, 255, 255, 0.78);

  li {
    overflow-wrap: anywhere;
  }
`;

export const AuditFooter = styled.div`
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  padding: 1rem;

  @media (max-width: 560px) {
    align-items: stretch;
    flex-direction: column;
  }
`;

export const LoadMoreButton = styled.button`
  min-height: 42px;
  padding: 0.6rem 1rem;
  border: 1px solid #00e5ff;
  border-radius: ${RADIUS.MD};
  background: transparent;
  color: #00e5ff;
  font: inherit;
  font-weight: 600;

  &:disabled {
    cursor: not-allowed;
    opacity: 0.55;
  }
`;

export const AuditMessage = styled.p`
  padding: 1rem;
  color: ${({ $error }) => ($error ? '#fda4af' : 'rgba(255, 255, 255, 0.72)')};
`;
