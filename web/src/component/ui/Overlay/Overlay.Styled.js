import styled from "styled-components";
import { motion } from "framer-motion";
import { COLORS, RADIUS } from '../../../styles/palette';

export const ModalOverlay = styled(motion.div)`
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  backdrop-filter: blur(4px);
`;
export const ModalContent = styled(motion.div)`
  background: ${COLORS.PRIMARY_CONTAINER};
  border-radius: ${RADIUS.LG};
  width: 90%;
  max-width: 500px;
  max-height: 80vh;
  overflow-y: auto;
  padding: 2rem;
  color: ${COLORS.SURFACE_CARD};
  box-shadow: 0px 8px 32px rgba(0, 0, 0, 0.5);
  transform: scale(0.9) translateY(20px);
  transition: transform 0.3s ease;
`;

export const ModalCloseButton = styled(motion.button)`
  position: absolute;
  top: 1rem;
  right: 1.5rem;
  background: transparent;
  color: ${COLORS.SURFACE_CARD};
  font-size: 1.5rem;
  border: none;
  cursor: pointer;
  padding: 0.5rem;
  transition: transform 0.2s ease;

  &:hover {
    transform: rotate(90deg);
  }
`;

export const FormTitle = styled(motion.h2)`
  color: #00e5ff;
  font-size: 1.5rem;
  font-weight: bold;
  text-align: center;
  margin-bottom: 1.5rem;
`;

export const FormGroup = styled(motion.div)`
  margin-bottom: 1.5rem;
`;

export const FormLabel = styled(motion.label)`
  display: block;
  margin-bottom: 0.5rem;
  font-size: 0.9rem;
  color: ${COLORS.SURFACE_CARD};
`;

export const FormInput = styled(motion.input)`
  width: 100%;
  padding: 0.75rem;
  border-radius: ${RADIUS.LG};
  border: 1px solid ${COLORS.OUTLINE};
  background-color: rgba(0, 0, 0, 0.3);
  color: ${COLORS.SURFACE_CARD};
  font-size: 1rem;
  &::placeholder {
    color: rgba(255, 255, 255, 0.5);
  }
`;

export const FormTextarea = styled(motion.textarea)`
  width: 100%;
  min-height: 120px;
  padding: 0.75rem;
  border-radius: ${RADIUS.LG};
  border: 1px solid ${COLORS.OUTLINE};
  background-color: rgba(0, 0, 0, 0.3);
  color: ${COLORS.SURFACE_CARD};
  font-size: 1rem;
  resize: vertical;
  &::placeholder {
    color: rgba(255, 255, 255, 0.5);
  }
`;

export const FormSubmit = styled(motion.button)`
  width: 100%;
  padding: 0.75rem;
  background-color: #00e5ff;
  color: ${COLORS.PRIMARY};
  border: none;
  border-radius: ${RADIUS.LG};
  font-size: 1rem;
  font-weight: bold;
  cursor: pointer;
  margin-top: 1rem;
  transition: background-color 0.3s ease;

  &:hover {
    background-color: #00b8d4;
  }
`;