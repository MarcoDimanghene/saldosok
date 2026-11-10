import { useCallback, useEffect, useMemo, useState } from 'react';
import { useDispatch } from 'react-redux';
import * as authService from '../services/authService';
import { getMyTenant, registerTenant, updateMyTenant } from '../services/tenantService';
import { clearToken, getToken, setToken } from '../util/tokenStorage';
import { AuthContext } from './authContext';
import { clearFinance } from '../store';

export function AuthProvider({ children }) {
  const dispatch = useDispatch();
  const [token, setTokenState] = useState(() => getToken());
  const [user, setUser] = useState(null);
  const [tenant, setTenant] = useState(null);
  const [isAuthenticated, setIsAuthenticated] = useState(() => Boolean(getToken()));
  const [isLoading, setIsLoading] = useState(() => Boolean(getToken()));

  const applySession = (newToken, newUser, newTenant) => {
    setToken(newToken);
    setTokenState(newToken);
    setUser(newUser);
    setTenant(newTenant);
    setIsAuthenticated(true);
    setIsLoading(false);
  };

  const login = useCallback(async (username, password) => {
    const data = await authService.login(username, password);
    dispatch(clearFinance());
    setIsLoading(true);
    setToken(data.access_token);

    try {
      const [currentUser, myTenant] = await Promise.all([
        authService.getCurrentUser(),
        getMyTenant(),
      ]);
      applySession(data.access_token, currentUser, myTenant);
    } catch (error) {
      clearToken();
      setTokenState(null);
      setUser(null);
      setTenant(null);
      setIsAuthenticated(false);
      setIsLoading(false);
      throw error;
    }
    return data;
  }, [dispatch]);

  const register = useCallback(async (formData) => {
    dispatch(clearFinance());
    return registerTenant(formData);
  }, [dispatch]);

  const updateTenant = useCallback(async (updates) => {
    const updatedTenant = await updateMyTenant(updates);
    setTenant(updatedTenant);
    return updatedTenant;
  }, []);

  const logout = useCallback(() => {
    dispatch(clearFinance());
    clearToken();
    setTokenState(null);
    setUser(null);
    setTenant(null);
    setIsAuthenticated(false);
    setIsLoading(false);
  }, [dispatch]);

  useEffect(() => {
    if (token && (!user || !tenant)) {
      Promise.all([authService.getCurrentUser(), getMyTenant()])
        .then(([currentUser, currentTenant]) => {
          setUser(currentUser);
          setTenant(currentTenant);
          setIsAuthenticated(true);
        })
        .catch(logout)
        .finally(() => setIsLoading(false));
    }
  }, [token, tenant, user, logout]);

  const value = useMemo(
    () => ({ token, user, tenant, isAuthenticated, isLoading, login, register, updateTenant, logout }),
    [token, user, tenant, isAuthenticated, isLoading, login, register, updateTenant, logout]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}
