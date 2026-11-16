import styled from 'styled-components';
import { COLORS, RADIUS } from '../../styles/palette';

export const PageContainer = styled.div`
  min-width: 0;
`;

export const PageHeader = styled.header`
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 1rem;
  margin-bottom: 1.5rem;

  h1 {
    margin-bottom: 0.45rem;
    color: #00e5ff;
    font-size: 1.8rem;
  }

  p {
    color: rgba(255, 255, 255, 0.72);
  }
`;

export const Panel = styled.section`
  margin-bottom: 1.25rem;
  padding: 1.5rem;
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: ${RADIUS.MD};
  background: ${COLORS.PRIMARY_CONTAINER};
  color: ${COLORS.SURFACE_CARD};
`;

export const Form = styled.form`
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto;
  align-items: end;
  gap: 1rem;

  @media (max-width: 620px) {
    grid-template-columns: 1fr;
  }
`;

export const FilterBar = styled.div`
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr)) auto;
  gap: 0.75rem;
  margin-bottom: 1.25rem;

  @media (max-width: 760px) {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  @media (max-width: 480px) {
    grid-template-columns: 1fr;
  }
`;

export const FilterField = styled.label`
  display: flex;
  min-width: 0;
  flex-direction: column;
  gap: 0.35rem;
  color: rgba(255, 255, 255, 0.72);
  font-size: 0.82rem;
  font-weight: 600;
`;

export const FormField = styled.label`
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
  font-size: 0.88rem;
  font-weight: 600;
`;

export const FormInput = styled.input`
  box-sizing: border-box;
  width: 100%;
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
`;

export const Preview = styled.p`
  grid-column: 1 / -1;
  margin: 0;
  color: rgba(255, 255, 255, 0.72);

  strong {
    color: #a5f3fc;
  }
`;

export const TableWrap = styled.div`
  width: 100%;
  overflow-x: auto;
  border-radius: ${RADIUS.MD};

  table {
    min-width: 940px;
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
    vertical-align: middle;
  }

  tr:hover td {
    background-color: #123143;
    color: #fff;
  }

  td.numeric {
    font-variant-numeric: tabular-nums;
    white-space: nowrap;
  }
`;

export const ResultsHeading = styled.div`
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  gap: 1rem;
  margin-bottom: 1rem;

  h2 {
    margin: 0;
  }

  span {
    color: rgba(255, 255, 255, 0.62);
    font-size: 0.85rem;
  }

  @media (max-width: 480px) {
    align-items: flex-start;
    flex-direction: column;
  }
`;

export const Message = styled.p`
  margin: 0.75rem 0;
  color: ${({ $error }) => ($error ? '#fda4af' : 'rgba(255, 255, 255, 0.72)')};
`;
