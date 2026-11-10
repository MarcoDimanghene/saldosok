import React from 'react';
import { useNavigate } from 'react-router-dom';
import { ImgCont, ButtonContainer,   Textcontent, LandingContainer, Sectionstyled, Headerstyled, SectionContent, LogoContainer, SectionTitle, UserContainer, HeroContainer, SpanLi, TextP, S2container, CardContainer, Card, cardVariants,  LandingButton } from './Landing.styles';
import { IoWalletSharp } from "react-icons/io5";
import { FaArrowRight } from "react-icons/fa6";
import landingImage from '../../assets/landing/hero.png';
import { FaUser } from "react-icons/fa";
import { IoReceiptSharp } from "react-icons/io5";
import { IoBarChartSharp } from "react-icons/io5";
import { FaBuilding } from "react-icons/fa6";
import Overlay from '../../component/ui/Overlay/Overlay';

const Landing = () => {
    const [isModalOpen, setIsModalOpen] = React.useState(false);
    const navigate = useNavigate();

    return (
        <LandingContainer>
          <Headerstyled
            variants={cardVariants} 
            initial="initial" 
            animate="animate" 
            whileHover="hover" 
            transition={{ delay: 0.3 }}
          >
            <LogoContainer>
              <IoWalletSharp size={48} color="#00e5ff" />
              <h1 style={{ color: "#00e5ff", fontSize: "2rem", fontWeight: "bold" }}>SALDOS OK</h1>
            </LogoContainer>
            <UserContainer>
              <LandingButton
                type="button"
                onClick={() => navigate('/login')}
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
              >
                INICIA SESIÓN
                <FaUser size={16} style={{ marginLeft: "0.5rem" }} />
              </LandingButton>
            </UserContainer>
          </Headerstyled>

          <HeroContainer>
            <Sectionstyled>
              <Textcontent
                variants={cardVariants} 
                initial="initial" 
                animate="animate" 
                whileHover="hover" 
                transition={{ delay: 0.3 }}
              >
                <SpanLi>
                  <p>SISTEMA OPERATIVO FINANCIERO</p>
                </SpanLi>
                <SectionTitle>Domina tu flujo de caja con <SectionContent>Precisión Técnica</SectionContent></SectionTitle>
                <TextP>
                  El terminal para la gestión de liquidez. Automatiza el procesamiento de facturas, pagos y cobros, optimizando tu flujo de caja y maximizando la eficiencia financiera. 
                  Seguimiento de pagos y cobros en tiempo real, con alertas y notificaciones para mantener tu negocio siempre al día.
                </TextP>
                <ButtonContainer>
                  <LandingButton
                    type="button"
                    onClick={() => navigate('/register')}
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                  >
                    REGÍSTRATE
                    <FaArrowRight size={16} color="#00e5ff" style={{ marginLeft: "0.5rem" }} />
                  </LandingButton>
                  <LandingButton onClick={() => setIsModalOpen(true)}>
                    MÁS INFORMACIÓN
                  </LandingButton>
                </ButtonContainer>
              </Textcontent>
              {/* Renderizado limpio del Overlay factorizado */}
              {isModalOpen && <Overlay onClose={() => setIsModalOpen(false)} />}
              <ImgCont 
                variants={cardVariants} 
                initial="initial" 
                animate="animate" 
                whileHover="hover" 
                transition={{ delay: 0.3 }}>
                <img src={landingImage} alt="Hero" style={{ width: "100%", maxWidth: "400px", borderRadius: "8px", height: "70%" }} />
              </ImgCont>
            </Sectionstyled>
            
            <Sectionstyled>
              <S2container
                variants={cardVariants} 
                initial="initial" 
                animate="animate" 
                whileHover="hover" 
                transition={{ delay: 0.3 }}
              >
                <h2 style={{ color: "#00e5ff", fontSize: "1.5rem", fontWeight: "bold" }}>Módulo del SISTEMA</h2>
                <SectionTitle style={{ textAlign: "left", fontSize: "2rem" }}>Arquitectura diseñada para operaciones financieras de alta exigencia.</SectionTitle>
                
                <CardContainer>
                  <Card 
                    variants={cardVariants} 
                    initial="initial" 
                    animate="animate" 
                    whileHover="hover" 
                    transition={{ delay: 0.1 }}
                  >
                    <IoReceiptSharp size={32} color="#00e5ff" style={{ marginBottom: "1.5rem", marginTop: "0.5rem" }} />
                    <TextP style={{fontSize: "1.5rem", fontWeight: "bold"}}>Carga Inteligente</TextP>
                    <TextP>Motor OCR integrado que extrae metadatos críticos de PDFs e imágenes al instante, estructurando datos no conformes en entradas estandarizadas.</TextP>
                  </Card>

                  <Card 
                    variants={cardVariants} 
                    initial="initial" 
                    animate="animate" 
                    whileHover="hover" 
                    transition={{ delay: 0.2 }}
                  >
                    <IoBarChartSharp size={32} color="#00e5ff" style={{ marginBottom: "1.5rem", marginTop: "0.5rem" }} />
                    <TextP style={{fontSize: "1.5rem", fontWeight: "bold"}}>Conciliación en Segundos</TextP>
                    <TextP>Algoritmo de emparejamiento automatizado que procesa transacciones en tiempo real.</TextP>
                  </Card>

                  <Card 
                    variants={cardVariants} 
                    initial="initial" 
                    animate="animate" 
                    whileHover="hover" 
                    transition={{ delay: 0.3 }}
                  >
                    <FaBuilding size={32} color="#00e5ff" style={{ marginBottom: "1.5rem", marginTop: "0.5rem" }} />
                    <TextP style={{fontSize: "1.5rem", fontWeight: "bold"}}>Gestión Multi-Empresas</TextP>
                    <TextP>Controla múltiples empresas desde una única plataforma, facilitando la gestión centralizada de operaciones financieras.</TextP>
                  </Card>
                </CardContainer>
              </S2container>
            </Sectionstyled>
          </HeroContainer>
        </LandingContainer>
    );
};

export default Landing;