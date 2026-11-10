
import { 
  ModalOverlay, 
  ModalContent, 
  ModalCloseButton, 
  FormTitle, 
  FormGroup, 
  FormLabel, 
  FormInput, 
  FormTextarea, 
  FormSubmit
  } from  './Overlay.Styled'

const Overlay = ({ onClose }) => {
  return (
    <ModalOverlay onClick={onClose}>
      <ModalContent onClick={(e) => e.stopPropagation()}>
        <ModalCloseButton onClick={onClose}>&times;</ModalCloseButton>
        <FormTitle>Contacto</FormTitle>
        <FormGroup>
          <FormLabel>Nombre</FormLabel>
          <FormInput type="text" placeholder="Tu nombre" required />
        </FormGroup>
        <FormGroup>
          <FormLabel>Email</FormLabel>
          <FormInput type="email" placeholder="Tu email" required />
        </FormGroup>
        <FormGroup>
          <FormLabel>Mensaje</FormLabel>
          <FormTextarea placeholder="Tu mensaje" required />
        </FormGroup>
        <FormSubmit>Enviar mensaje</FormSubmit>
      </ModalContent>
    </ModalOverlay>
  );
};

export default Overlay;