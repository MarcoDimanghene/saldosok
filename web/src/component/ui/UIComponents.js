import styled, { css } from 'styled-components';
import { COLORS, TYPOGRAPHY, RADIUS } from '../../styles/palette';

// -----------------------------------------------------------------------------
// TARJETAS / CONTENEDORES
// -----------------------------------------------------------------------------
export const Card = styled.div`
  background-color: ${COLORS.SURFACE_CARD};
  border-radius: ${RADIUS.MD};
  padding: 24px;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
  border: 1px solid ${COLORS.BORDER_LIGHT};
`;

// -----------------------------------------------------------------------------
// BOTONES (Primary, Secondary, Ghost)
// -----------------------------------------------------------------------------
export const Button = styled.button`
  border-radius: ${RADIUS.MD};
  padding: 10px 18px;
  font-size: ${TYPOGRAPHY.BODY_MD.fontSize};
  font-weight: 600;
  transition: all 0.2s ease-in-out;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;

  /* Botón Primario */
  ${(props) =>
    (!props.$variant || props.$variant === 'primary') &&
    css`
      background-color: ${COLORS.PRIMARY};
      color: #ffffff;
      border: none;

      &:hover {
        background-color: ${COLORS.PRIMARY_CONTAINER};
      }
    `}

  /* Botón Secundario */
  ${(props) =>
    props.$variant === 'secondary' &&
    css`
      background-color: ${COLORS.SURFACE_CARD};
      color: ${COLORS.PRIMARY};
      border: 1px solid ${COLORS.PRIMARY};

      &:hover {
        background-color: ${COLORS.BACKGROUND};
      }
    `}

  /* Botón Ghost */
  ${(props) =>
    props.$variant === 'ghost' &&
    css`
      background-color: transparent;
      color: ${COLORS.PRIMARY};
      border: none;

      &:hover {
        background-color: rgba(0, 0, 0, 0.04);
      }
    `}
`;

// -----------------------------------------------------------------------------
// STATUS BADGES (Saldada, Pendiente, Vencida)
// -----------------------------------------------------------------------------
export const StatusBadge = styled.span`
  display: inline-flex;
  align-items: center;
  padding: 4px 12px;
  border-radius: ${RADIUS.FULL};
  font-size: ${TYPOGRAPHY.LABEL_MD.fontSize};
  font-weight: ${TYPOGRAPHY.LABEL_MD.fontWeight};
  letter-spacing: ${TYPOGRAPHY.LABEL_MD.letterSpacing};
  text-transform: uppercase;

  ${(props) =>
    props.$status === 'saldada' &&
    css`
      background-color: ${COLORS.SUCCESS_BG};
      color: ${COLORS.SUCCESS};
    `}

  ${(props) =>
    props.$status === 'pendiente' &&
    css`
      background-color: ${COLORS.PENDING_BG};
      color: ${COLORS.PENDING};
    `}

  ${(props) =>
    props.$status === 'vencida' &&
    css`
      background-color: ${COLORS.DANGER_BG};
      color: ${COLORS.DANGER};
    `}
`;

// -----------------------------------------------------------------------------
// TABLA DE DATOS LIMPIA (Clean-row sin líneas verticales)
// -----------------------------------------------------------------------------
export const StyledTable = styled.table`
  width: 100%;
  border-collapse: collapse;
  text-align: left;
  background-color: ${COLORS.SURFACE_CARD};
`;

export const TableHeader = styled.th`
  padding: 12px 16px;
  font-size: ${TYPOGRAPHY.LABEL_MD.fontSize};
  font-weight: ${TYPOGRAPHY.LABEL_MD.fontWeight};
  color: ${COLORS.ON_SURFACE_VARIANT};
  text-transform: uppercase;
  border-bottom: 1px solid ${COLORS.BORDER_LIGHT};
`;

export const TableRow = styled.tr`
  border-bottom: 1px solid ${COLORS.BORDER_LIGHT};

  &:last-child {
    border-bottom: none;
  }

  &:hover {
    background-color: ${COLORS.BACKGROUND};
  }
`;

export const TableCell = styled.td`
  padding: 16px;
  font-size: ${TYPOGRAPHY.BODY_MD.fontSize};
  color: ${COLORS.ON_SURFACE};

  &.numeric {
    font-weight: 600;
  }
`;