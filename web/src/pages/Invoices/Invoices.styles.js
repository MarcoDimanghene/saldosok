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

export const Tabs = styled.div`
  display: flex;
  gap: 0.5rem;
  margin-bottom: 1.25rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
`;

export const TabButton = styled.button`
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.8rem 1rem;
  border: 0;
  border-bottom: 2px solid ${({ $active }) => ($active ? '#00e5ff' : 'transparent')};
  background: transparent;
  color: ${({ $active }) => ($active ? '#00e5ff' : 'rgba(255, 255, 255, 0.65)')};
  cursor: pointer;
  font: inherit;
  font-weight: 600;

  &:focus-visible {
    outline: 2px solid #00e5ff;
    outline-offset: 2px;
  }
`;

export const Panel = styled(Card)`
  min-width: 0;
  margin-bottom: 1.25rem;
  padding: 1.5rem;
  border-color: rgba(255, 255, 255, 0.1);
  background: ${COLORS.PRIMARY_CONTAINER};
  color: ${COLORS.SURFACE_CARD};
`;

export const SectionHeading = styled.div`
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 0.5rem 1rem;
  margin-bottom: 1.25rem;

  h2 {
    font-size: 1.1rem;
  }

  > span {
    color: rgba(255, 255, 255, 0.62);
    font-size: 0.82rem;
  }
`;

export const Form = styled.form`
  display: flex;
  flex-direction: column;
  gap: 1.15rem;
`;

export const FormGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 1rem;

  @media (max-width: 600px) {
    grid-template-columns: 1fr;
  }
`;

export const FormField = styled.div`
  display: flex;
  min-width: 0;
  flex-direction: column;
  gap: 0.4rem;

  label {
    font-size: 0.88rem;
    font-weight: 600;
  }
`;

export const FormInput = styled.input`
  box-sizing: border-box;
  width: 100%;
  min-width: 0;
  min-height: 44px;
  padding: 0.65rem 0.75rem;
  border: 1px solid ${COLORS.OUTLINE};
  border-radius: ${RADIUS.MD};
  background: rgba(0, 0, 0, 0.2);
  color: ${COLORS.SURFACE_CARD};
  font: inherit;

  &:focus {
    outline: 2px solid #00e5ff;
    outline-offset: 1px;
  }

  option {
    background: ${COLORS.PRIMARY_CONTAINER};
    color: ${COLORS.SURFACE_CARD};
  }
`;

export const InvoiceList = styled.div`
  width: 100%;
  overflow-x: auto;
  border-radius: ${RADIUS.MD};

  table {
    min-width: 780px;
    background: transparent;
    color: ${COLORS.SURFACE_CARD};
  }

  th {
    border-color: rgba(255, 255, 255, 0.1);
    color: rgba(255, 255, 255, 0.62);
  }

  td {
    border-color: rgba(255, 255, 255, 0.08);
    background: transparent;
    color: rgba(255, 255, 255, 0.82);
    vertical-align: top;
  }

  tr:hover td {
    background: rgba(255, 255, 255, 0.035);
  }

  td span {
    display: block;
    margin-top: 0.25rem;
    color: rgba(255, 255, 255, 0.58);
    font-size: 0.78rem;
  }

  td.numeric {
    font-variant-numeric: tabular-nums;
    white-space: nowrap;
  }
`;

export const ActionCell = styled.div`
  display: flex;
  min-width: 170px;
  flex-direction: column;
  align-items: flex-start;
  gap: 0.5rem;
`;

export const ActionForm = styled.form`
  display: flex;
  width: min(100%, 260px);
  flex-direction: column;
  gap: 0.5rem;
`;

export const EmptyState = styled.p`
  padding: 0.5rem 0;
  color: rgba(255, 255, 255, 0.68);
  font-size: 0.9rem;

  a {
    color: #00e5ff;
  }
`;

export const StatusMessage = styled.p`
  margin-bottom: 1rem;
  color: ${({ $error }) => ($error ? '#fda4af' : '#5eead4')};
`;
