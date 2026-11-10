import styled from "styled-components";
import { motion } from "framer-motion";
import { COLORS, RADIUS } from '../../styles/palette';

export const LandingContainer = styled(motion.div)`
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 2rem;
  min-height: 100vh;
  width: 100%;
  background-color: ${COLORS.PRIMARY};
`;

export const HeroContainer = styled(motion.div)`
  display: flex;
  align-items: center;
  justify-content: center;
  flex-direction: column;
  max-width: 1800px;
  height: 80%;
  margin: 2rem;
  padding: 1.5rem;
  border-radius: ${RADIUS.LG};
  box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.1);
  background-color: ${COLORS.PENDING_BG};
  gap: 2rem;
`;

export const Headerstyled = styled(motion.div)`
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 70%;
  height: 30%;
`;

export const Sectionstyled = styled(motion.div)`
  display: flex;
  align-items: center;
  justify-content: space-around;
  background-color: ${COLORS.PRIMARY_CONTAINER};
  width: 98%;
  height: auto;
  border-radius: ${RADIUS.LG};
  box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.1);
`;

export const LogoContainer = styled(motion.div)`
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  cursor: pointer;
  margin-bottom: 2rem;
`;

export const UserContainer = styled(motion.div)`
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  margin-bottom: 2rem;
  cursor: pointer;
`;

export const SectionTitle = styled(motion.h2)`
  color: ${COLORS.SURFACE_CARD};
  font-size: 3rem;
  font-weight: 600;
  text-align: center;
  margin-bottom: 1rem;
`;

export const SectionContent = styled(motion.span)`
  color: #00e5ff;
  font-size: 3rem;
  text-align: center;
  font-weight: bold;
  margin-top: 0.5rem;
`;

export const Textcontent = styled(motion.div)`
  display: flex;
  align-items: center;
  justify-content: center;
  flex-direction: column;
  height: 100%;
  width: 40%;
`;

export const ImgCont = styled(motion.div)`
  display: flex;
  align-items: center;
  justify-content: center;
  flex-direction: column;
  height: 70%;
  padding: 1rem;
  
`;

export const SpanLi = styled(motion.span)`
  color: #00e5ff;
  font-size: 1rem;
  font-weight: bold;
  padding: 0.5rem 1rem;
  border-radius: 20px;
  background-color: rgba(0, 229, 255, 0.1);
  margin-bottom: 1rem;
`;

export const TextP = styled(motion.p)`
  color: ${COLORS.SURFACE_CARD};
  font-size: 1rem;
  text-align: left;
  margin-top: 0.5rem;
  margin-bottom: 0.5rem;
  padding: 0rem 1.5rem;
  letter-spacing: -0.02em;
`;

export const LandingButton = styled(motion.button)`
  background-color: transparent;
  color: #00e5ff;
  font-size: 1rem;
  font-weight: bold;
  padding: 0.5rem 2rem;
  border-radius: ${RADIUS.LG};
  border: 2px solid #00e5ff;
  cursor: pointer;
  margin-left: 1rem;
  transition: all 0.3s ease;
  backdrop-filter: blur(10px);

  &:hover {
    background-color: rgba(255, 255, 255, 0.1);
    border-color:${COLORS.SURFACE_CARD};
    color: ${COLORS.SURFACE_CARD};
    transform: translateY(-2px);
    box-shadow: 0px 4px 12px rgba(0, 229, 255, 0.3);
  }

  &:active {
    transform: translateY(1px);
    box-shadow: none;
  }
`;

export const ButtonContainer = styled(motion.div)`
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100%;
  padding: 1rem;
  margin-top: 1rem;
  border-top: 1px solid ${COLORS.OUTLINE};
`;

export const S2container = styled(motion.div)`
  display: flex;
  align-items: center;
  justify-content: center;
  flex-direction: column;
  width: 100%;
  padding: 2rem;
  gap: 1rem;
  background: linear-gradient(135deg, rgba(9, 20, 38, 0.8), rgba(14, 22, 42, 0.9));
  border-radius: ${RADIUS.LG};
`;

export const cardVariants = {
  initial: { x: -50, opacity: 0 },
  animate: { x: 0, opacity: 1 },

};

export const CardContainer = styled(motion.div)`
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
  padding: 1rem;
  gap: 1.5rem;
  flex-wrap: wrap;

`;

export const Card = styled(motion.div)`
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 280px;
  width: 30%;
  border-radius: ${RADIUS.LG};
  box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.3);
  padding: 1.5rem;
  background: ${COLORS.PRIMARY_CONTAINER};
  backdrop-filter: blur(12px);
  border: 1px solid rgba(0, 229, 255, 0.1);
  transition: all 0.3s ease;
  cursor: pointer;
  &:hover {
    transform: translateY(-8px);
    box-shadow: 0 0 20px rgba(0, 229, 255, 0.2);
    border-color: rgba(0, 229, 255, 0.3);
  }
`;