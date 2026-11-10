import styled from 'styled-components';
import { Link } from 'react-router-dom';
import { COLORS, RADIUS } from '../../styles/palette';

export const RegisterContainer = styled.main`
  min-height: 100vh;
  padding: 3rem 1rem;
  display: flex;
  justify-content: center;
  align-items: flex-start;
  background: ${COLORS.PRIMARY};

  @media (max-width: 600px) {
    padding: 1rem 0.75rem;
  }
`;

export const RegisterCard = styled.section`
  width: min(100%, 760px);
  padding: 2.5rem;
  border: 1px solid rgba(0, 229, 255, 0.15);
  border-radius: ${RADIUS.LG};
  background: ${COLORS.PRIMARY_CONTAINER};
  color: ${COLORS.SURFACE_CARD};
  box-shadow: 0 16px 48px rgba(0, 0, 0, 0.25);

  @media (max-width: 600px) {
    padding: 1.5rem 1rem;
  }
`;

export const RegisterTitle = styled.h1`
  margin-bottom: 0.5rem;
  color: #00e5ff;
  font-size: 2rem;
`;

export const RegisterDescription = styled.p`
  margin-bottom: 2rem;
  color: rgba(255, 255, 255, 0.75);
`;

export const RegisterForm = styled.form``;

export const FieldsGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 1.25rem;

  @media (max-width: 600px) {
    grid-template-columns: 1fr;
  }
`;

export const FormField = styled.div`
  display: flex;
  flex-direction: column;
  gap: 0.45rem;
`;

export const FormLabel = styled.label`
  font-size: 0.9rem;
  font-weight: 600;
`;

const formControlStyles = `
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

  &[aria-invalid='true'] {
    border-color: #fb7185;
  }
`;

export const FormInput = styled.input`${formControlStyles}`;

export const FormSelect = styled.select`
  ${formControlStyles}

  option {
    color: ${COLORS.ON_SURFACE};
  }
`;

export const FieldError = styled.span`
  color: #fda4af;
  font-size: 0.85rem;
`;

export const FormError = styled.p`
  margin-top: 1.25rem;
  color: #fda4af;
  font-size: 0.9rem;
`;

export const SubmitButton = styled.button`
  width: 100%;
  min-height: 48px;
  margin-top: 1.75rem;
  border: 0;
  border-radius: ${RADIUS.MD};
  background: #00e5ff;
  color: ${COLORS.PRIMARY};
  font: inherit;
  font-weight: 700;

  &:disabled {
    cursor: wait;
    opacity: 0.65;
  }
`;

export const BackLink = styled(Link)`
  display: block;
  margin-top: 1.25rem;
  color: #00e5ff;
  font-size: 0.9rem;
  text-align: center;
  text-decoration: underline;
  text-underline-offset: 3px;
`;
