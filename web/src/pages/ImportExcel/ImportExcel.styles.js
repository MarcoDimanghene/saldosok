import styled from 'styled-components';
import { Card } from '../../component/ui/UIComponents';
import { COLORS, RADIUS } from '../../styles/palette';

export const PageHeader = styled.header`
  margin-bottom: 1.75rem;

  h1 {
    margin-bottom: 0.45rem;
    color: #00e5ff;
    font-size: 1.8rem;
  }

  p {
    color: rgba(255, 255, 255, 0.72);
  }
`;

export const Panel = styled(Card)`
  margin-bottom: 1.25rem;
  padding: 1.5rem;
  border-color: rgba(255, 255, 255, 0.1);
  background: ${COLORS.PRIMARY_CONTAINER};
  color: ${COLORS.SURFACE_CARD};
`;

export const ActionRow = styled.div`
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 0.75rem;
  margin-top: 1rem;
`;

export const FileInput = styled.input`
  width: 100%;
  max-width: 520px;
  padding: 0.65rem;
  border: 1px solid ${COLORS.OUTLINE};
  border-radius: ${RADIUS.MD};
  color: ${COLORS.SURFACE_CARD};
  font: inherit;
`;

export const Guidance = styled.ul`
  display: grid;
  gap: 0.65rem;
  padding-left: 1.25rem;
  color: rgba(255, 255, 255, 0.72);
  line-height: 1.5;

  a {
    color: #00e5ff;
  }
`;

export const StatusMessage = styled.div`
  margin-top: 1rem;
  padding: 0.9rem 1rem;
  border: 1px solid ${({ $error }) => ($error ? 'rgba(248, 113, 113, 0.35)' : 'rgba(45, 212, 191, 0.35)')};
  border-radius: ${RADIUS.MD};
  background: ${({ $error }) => ($error ? 'rgba(127, 29, 29, 0.2)' : 'rgba(15, 118, 110, 0.15)')};
  color: ${({ $error }) => ($error ? '#fecaca' : '#99f6e4')};
`;

export const ErrorList = styled.ul`
  display: grid;
  gap: 0.5rem;
  max-height: 340px;
  overflow: auto;
  margin: 0.75rem 0 0;
  padding-left: 1.25rem;
  color: #fecaca;
`;
