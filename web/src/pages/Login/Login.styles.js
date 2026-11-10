import styled from 'styled-components';
import { Link } from 'react-router-dom';
import { COLORS, RADIUS } from '../../styles/palette';

export const LoginContainer = styled.main`
  min-height: 100vh;
  padding: 2rem 1rem;
  display: flex;
  justify-content: center;
  align-items: center;
  background: ${COLORS.PRIMARY};
`;

export const LoginCard = styled.section`
  width: min(100%, 440px);
  padding: 2.5rem;
  border: 1px solid rgba(0, 229, 255, 0.15);
  border-radius: ${RADIUS.LG};
  background: ${COLORS.PRIMARY_CONTAINER};
  color: ${COLORS.SURFACE_CARD};
  box-shadow: 0 16px 48px rgba(0, 0, 0, 0.25);

  @media (max-width: 480px) {
    padding: 1.75rem 1.25rem;
  }
`;

export const LoginBrand = styled.p`
  margin-bottom: 1.5rem;
  color: #00e5ff;
  font-size: 0.85rem;
  font-weight: 700;
  letter-spacing: 0.12em;
`;

export const LoginTitle = styled.h1`
  margin-bottom: 0.5rem;
  color: ${COLORS.SURFACE_CARD};
  font-size: 2rem;
`;

export const LoginDescription = styled.p`
  margin-bottom: 2rem;
  color: rgba(255, 255, 255, 0.75);
`;

export const LoginForm = styled.form`
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
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

export const FormInput = styled.input`
  width: 100%;
  min-height: 46px;
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

export const FieldError = styled.span`
  color: #fda4af;
  font-size: 0.85rem;
`;

export const FormError = styled.p`
  color: #fda4af;
  font-size: 0.9rem;
`;

export const SubmitButton = styled.button`
  width: 100%;
  min-height: 48px;
  border: 0;
  border-radius: ${RADIUS.MD};
  background: #00e5ff;
  color: ${COLORS.PRIMARY};
  font: inherit;
  font-weight: 700;

  &:hover:not(:disabled) {
    background: #67efff;
  }

  &:disabled {
    cursor: wait;
    opacity: 0.65;
  }
`;

export const LoginLinks = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.85rem;
  margin-top: 1.5rem;
`;

export const LoginLink = styled(Link)`
  color: #00e5ff;
  font-size: 0.9rem;
  text-align: center;
  text-decoration: underline;
  text-underline-offset: 3px;
`;
