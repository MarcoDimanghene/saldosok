import { useContext } from 'react';
import { AuthContext } from '../contex/authContext';

export const useAuth = () => useContext(AuthContext);
