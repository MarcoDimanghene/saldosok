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

export const CompanyGrid = styled.div`
  display: grid;
  grid-template-columns: minmax(250px, 0.8fr) minmax(0, 1.4fr);
  gap: 1.25rem;
  align-items: start;

  @media (max-width: 900px) {
    grid-template-columns: 1fr;
  }
`;

export const Panel = styled(Card)`
  min-width: 0;
  padding: 1.5rem;
  border-color: rgba(255, 255, 255, 0.1);
  background: ${COLORS.PRIMARY_CONTAINER};
  color: ${COLORS.SURFACE_CARD};

  h2 {
    margin-bottom: 1.25rem;
    font-size: 1.1rem;
  }
`;

export const Form = styled.form`
  display: flex;
  flex-direction: column;
  gap: 1rem;
`;

export const FormField = styled.div`
  display: flex;
  flex-direction: column;
  gap: 0.4rem;

  label,
  > span {
    font-size: 0.9rem;
    font-weight: 600;
  }
`;

export const FormInput = styled.input`
  width: 100%;
  min-height: 44px;
  padding: 0.7rem 0.8rem;
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

export const CompanyRoles = styled.div`
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;

  > span {
    display: inline-flex;
    align-items: center;
    gap: 0.3rem;
    padding: 0.35rem 0.6rem;
    border-radius: ${RADIUS.FULL};
    background: rgba(0, 229, 255, 0.1);
    color: #a2eeff;
    font-size: 0.75rem;
  }
`;

export const RoleChoice = styled.label`
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  padding: 0.45rem 0.65rem;
  border: 1px solid rgba(255, 255, 255, 0.12);
  border-radius: ${RADIUS.MD};
  color: rgba(255, 255, 255, 0.78);
  font-size: 0.82rem;

  input {
    accent-color: #00e5ff;
  }
`;

export const CompanyList = styled.ul`
  display: flex;
  flex-direction: column;
  list-style: none;
`;

export const CompanyItem = styled.li`
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 1rem;
  padding: 1rem 0;
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);

  &:first-child {
    padding-top: 0;
  }

  &:last-child {
    border-bottom: 0;
  }

  @media (max-width: 560px) {
    flex-direction: column;
  }
`;

export const CompanyName = styled.div`
  display: flex;
  min-width: 0;
  align-items: flex-start;
  gap: 0.7rem;

  > svg {
    flex-shrink: 0;
    margin-top: 0.15rem;
    color: #00e5ff;
  }

  strong,
  span {
    display: block;
    overflow-wrap: anywhere;
  }

  span {
    margin-top: 0.3rem;
    color: rgba(255, 255, 255, 0.62);
    font-size: 0.8rem;
  }
`;

export const StatusMessage = styled.p`
  margin-bottom: 1rem;
  color: ${({ $error }) => ($error ? '#fda4af' : '#5eead4')};
`;
