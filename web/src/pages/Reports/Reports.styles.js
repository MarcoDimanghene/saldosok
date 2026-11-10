import styled from 'styled-components';
import { Card } from '../../component/ui/UIComponents';
import { COLORS } from '../../styles/palette';

export const ReportsContainer = styled.main`
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
`;

export const ReportsHeader = styled.header`
  h1 {
    margin-bottom: 0.45rem;
    color: #00e5ff;
    font-size: 1.8rem;
  }

  p {
    color: rgba(255, 255, 255, 0.72);
  }
`;

export const ReportGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(min(100%, 220px), 1fr));
  gap: 1rem;
`;

export const ReportCard = styled(Card)`
  min-width: 0;
  padding: 1.25rem;
  border-color: rgba(255, 255, 255, 0.1);
  background: ${COLORS.PRIMARY_CONTAINER};
  color: ${COLORS.SURFACE_CARD};

  h2 {
    margin-bottom: 0.6rem;
    color: rgba(255, 255, 255, 0.72);
    font-size: 0.9rem;
    font-weight: 600;
  }

  strong {
    display: block;
    color: #00e5ff;
    font-size: 1.55rem;
    overflow-wrap: anywhere;
  }
`;

export const ReportSection = styled(ReportCard)`
  h2 {
    color: ${COLORS.SURFACE_CARD};
    font-size: 1.05rem;
  }
`;

export const ReportRows = styled.ul`
  display: flex;
  flex-direction: column;
  gap: 0.7rem;
  list-style: none;

  li {
    display: flex;
    justify-content: space-between;
    gap: 1rem;
    padding-bottom: 0.65rem;
    border-bottom: 1px solid rgba(255, 255, 255, 0.08);
  }

  li:last-child {
    padding-bottom: 0;
    border-bottom: 0;
  }

  span:last-child {
    text-align: right;
  }
`;

export const ReportMessage = styled.p`
  color: ${({ $error }) => ($error ? '#fda4af' : 'rgba(255, 255, 255, 0.72)')};
`;
