import styled from 'styled-components';
import { COLORS, RADIUS } from '../../styles/palette';

export const PageHeader = styled.header`
  margin-bottom: 1.75rem;

  h1 {
    margin-bottom: 0.5rem;
    color: #00e5ff;
    font-size: 1.8rem;
  }

  p {
    color: rgba(255, 255, 255, 0.72);
  }
`;

export const ContentGrid = styled.div`
  display: grid;
  grid-template-columns: minmax(250px, 0.8fr) minmax(0, 1.5fr);
  gap: 1.25rem;
  align-items: start;

  @media (max-width: 900px) {
    grid-template-columns: 1fr;
  }
`;

export const Panel = styled.section`
  min-width: 0;
  padding: 1.5rem;
  border: 1px solid rgba(0, 229, 255, 0.15);
  border-radius: ${RADIUS.LG};
  background: ${COLORS.PRIMARY_CONTAINER};
  box-shadow: 0 12px 32px rgba(0, 0, 0, 0.16);

  h2 {
    margin-bottom: 1.25rem;
    font-size: 1.15rem;
  }
`;

export const QuotaText = styled.p`
  margin-bottom: 1.25rem;
  color: rgba(255, 255, 255, 0.75);

  strong {
    color: #00e5ff;
  }
`;

export const UserForm = styled.form`
  display: flex;
  flex-direction: column;
  gap: 1rem;
`;

export const FormField = styled.div`
  display: flex;
  flex-direction: column;
  gap: 0.4rem;

  label {
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

export const PrimaryButton = styled.button`
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
    opacity: 0.55;
  }
`;

export const SecondaryButton = styled.button`
  padding: 0.45rem 0.7rem;
  border: 1px solid ${COLORS.OUTLINE};
  border-radius: ${RADIUS.MD};
  background: transparent;
  color: ${COLORS.SURFACE_CARD};
  font: inherit;

  &:hover {
    border-color: #00e5ff;
    color: #00e5ff;
  }
`;

export const UserList = styled.ul`
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  list-style: none;
`;

export const UserRow = styled.li`
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  padding: 1rem;
  border: 1px solid rgba(255, 255, 255, 0.09);
  border-radius: ${RADIUS.MD};
  background: rgba(0, 0, 0, 0.12);

  @media (max-width: 540px) {
    align-items: flex-start;
    flex-direction: column;
  }
`;

export const UserDetails = styled.div`
  min-width: 0;

  strong,
  span {
    display: block;
    overflow-wrap: anywhere;
  }

  span {
    margin-top: 0.25rem;
    color: rgba(255, 255, 255, 0.68);
    font-size: 0.88rem;
  }
`;

export const UserActions = styled.div`
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
`;

export const StatusMessage = styled.p`
  margin: 0.75rem 0;
  color: ${({ $error }) => ($error ? '#fda4af' : '#5eead4')};
`;
