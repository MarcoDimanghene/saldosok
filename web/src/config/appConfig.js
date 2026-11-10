export const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export const PLANES = [
  {
    id: 'basico',
    nombre: 'Básico',
    usuarios: 1,
    descripcion: 'Ideal para emprendedores individuales',
  },
  {
    id: 'moderado',
    nombre: 'Moderado',
    usuarios: 5,
    descripcion: 'Para equipos en crecimiento',
  },
  {
    id: 'premium',
    nombre: 'Premium',
    usuarios: 10,
    descripcion: 'Para empresas con equipos amplios',
  },
];

export const CONDICIONES_IVA = [
  'Responsable Inscripto',
  'Monotributo',
  'Exento',
  'Consumidor Final',
];
