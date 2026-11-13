import { useEffect, useState } from 'react';
import { MAX_USERS_PER_TENANT } from '../../config/appConfig';
import { useAuth } from '../../hook/useAuth';
import {
  createUser,
  deleteUser,
  getUsers,
  resendUserInvitation,
  updateUser,
} from '../../services/userService';
import {
  ContentGrid,
  FormField,
  FormInput,
  PageHeader,
  Panel,
  PrimaryButton,
  QuotaText,
  SecondaryButton,
  StatusMessage,
  UserActions,
  UserDetails,
  UserForm,
  UserList,
  UserRow,
} from './Users.styles';

const initialForm = { nombre: '', username: '', email: '' };

const Users = () => {
  const { user: currentUser, tenant } = useAuth();
  const [users, setUsers] = useState([]);
  const [form, setForm] = useState(initialForm);
  const [isLoading, setIsLoading] = useState(true);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [message, setMessage] = useState(null);

  const userLimit = MAX_USERS_PER_TENANT;
  const atLimit = users.length >= userLimit;

  useEffect(() => {
    let isMounted = true;
    getUsers()
      .then((loadedUsers) => {
        if (isMounted) setUsers(loadedUsers);
      })
      .catch((error) => {
        if (isMounted) {
          setMessage({
            error: true,
            text: error.message || 'No se pudieron cargar los usuarios.',
          });
        }
      })
      .finally(() => {
        if (isMounted) setIsLoading(false);
      });

    return () => {
      isMounted = false;
    };
  }, []);

  const loadUsers = async () => {
    setIsLoading(true);
    try {
      setUsers(await getUsers());
    } catch (error) {
      setMessage({ error: true, text: error.message || 'No se pudieron cargar los usuarios.' });
    } finally {
      setIsLoading(false);
    }
  };

  const handleCreateUser = async (event) => {
    event.preventDefault();
    setMessage(null);

    if (!form.nombre.trim()) {
      setMessage({ error: true, text: 'Ingresa el nombre del usuario.' });
      return;
    }
    if (!/^[a-zA-Z0-9_.-]{3,50}$/.test(form.username.trim())) {
      setMessage({ error: true, text: 'El usuario debe tener entre 3 y 50 letras, números, puntos, guiones o guiones bajos.' });
      return;
    }
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(form.email.trim())) {
      setMessage({ error: true, text: 'Ingresa un correo electrónico válido para el usuario.' });
      return;
    }
    setIsSubmitting(true);
    try {
      const result = await createUser({
        nombre: form.nombre.trim(),
        username: form.username.trim(),
        email: form.email.trim(),
      });
      setForm(initialForm);
      setMessage({ error: false, text: result.message || 'El usuario se creó correctamente.' });
      await loadUsers();
    } catch (error) {
      setMessage({ error: true, text: error.message || 'No se pudo crear el usuario.' });
      await loadUsers();
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleResendInvitation = async (account) => {
    setMessage(null);
    setIsSubmitting(true);
    try {
      const result = await resendUserInvitation(account.id);
      setMessage({ error: false, text: result.message });
      await loadUsers();
    } catch (error) {
      setMessage({ error: true, text: error.message || 'No se pudo reenviar la invitación.' });
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleToggleActive = async (account) => {
    setMessage(null);
    try {
      await updateUser(account.id, { is_active: !account.is_active });
      setMessage({
        error: false,
        text: account.is_active ? 'El usuario se desactivó.' : 'El usuario se activó.',
      });
      await loadUsers();
    } catch (error) {
      setMessage({ error: true, text: error.message || 'No se pudo actualizar el usuario.' });
    }
  };

  const handleDelete = async (account) => {
    if (!window.confirm(`¿Eliminar a ${account.nombre || account.username}?`)) return;

    setMessage(null);
    try {
      await deleteUser(account.id);
      setMessage({ error: false, text: 'El usuario se eliminó correctamente.' });
      await loadUsers();
    } catch (error) {
      setMessage({ error: true, text: error.message || 'No se pudo eliminar el usuario.' });
    }
  };

  return (
    <>
      <PageHeader>
        <h1>Usuarios del espacio de trabajo</h1>
        <p>
          Administra quién accede a {tenant?.razon_social || 'tu espacio de trabajo'}.
          Cada persona establece su contraseña desde una invitación por correo.
        </p>
      </PageHeader>

      {message && (
        <StatusMessage $error={message.error} role={message.error ? 'alert' : 'status'}>
          {message.text}
        </StatusMessage>
      )}

      <ContentGrid>
        <Panel>
          <h2>Agregar usuario</h2>
          <QuotaText>
            Usuarios: {users.length} de{' '}
            <strong>{userLimit}</strong> cuentas utilizadas. El administrador cuenta dentro del límite.
          </QuotaText>
          <UserForm onSubmit={handleCreateUser}>
            <FormField>
              <label htmlFor="new-user-name">Nombre</label>
              <FormInput
                id="new-user-name"
                value={form.nombre}
                onChange={(event) => setForm({ ...form, nombre: event.target.value })}
                autoComplete="name"
                required
              />
            </FormField>
            <FormField>
              <label htmlFor="new-user-username">Nombre de usuario</label>
              <FormInput
                id="new-user-username"
                value={form.username}
                onChange={(event) => setForm({ ...form, username: event.target.value })}
                autoComplete="username"
                required
              />
            </FormField>
            <FormField>
              <label htmlFor="new-user-email">Correo electrónico</label>
              <FormInput
                id="new-user-email"
                type="email"
                value={form.email}
                onChange={(event) => setForm({ ...form, email: event.target.value })}
                autoComplete="email"
                required
              />
            </FormField>
            <PrimaryButton
              type="submit"
              disabled={atLimit || isSubmitting || isLoading}
            >
              {isSubmitting ? 'Creando usuario...' : atLimit ? 'Límite de usuarios alcanzado' : 'Agregar usuario'}
            </PrimaryButton>
          </UserForm>
        </Panel>

        <Panel>
          <h2>Equipo</h2>
          {isLoading ? (
            <p role="status">Cargando usuarios...</p>
          ) : users.length === 0 ? (
            <p>No hay usuarios para mostrar.</p>
          ) : (
            <UserList>
              {users.map((account) => (
                <UserRow key={account.id}>
                  <UserDetails>
                    <strong>
                      {account.nombre || account.username}
                      {account.is_tenant_admin ? ' · Administrador' : ''}
                      {account.id === currentUser?.id ? ' (vos)' : ''}
                    </strong>
                    <span>Usuario: {account.username}</span>
                    {account.email && <span>Correo: {account.email}</span>}
                    <span>{account.is_active ? 'Activo' : 'Inactivo'}</span>
                    <span>
                      {account.is_email_verified ? 'Correo confirmado' : 'Invitación pendiente'}
                    </span>
                    {!account.is_email_verified && !account.email && (
                      <span>Agrega un correo para enviar la invitación</span>
                    )}
                  </UserDetails>
                  {!account.is_tenant_admin && (
                    <>
                      <UserActions>
                        <SecondaryButton
                          type="button"
                          onClick={() => handleToggleActive(account)}
                        >
                          {account.is_active ? 'Desactivar' : 'Activar'}
                        </SecondaryButton>
                        <SecondaryButton
                          type="button"
                          onClick={() => handleDelete(account)}
                        >
                          Eliminar
                        </SecondaryButton>
                        {!account.is_email_verified && account.email && account.is_active && (
                          <SecondaryButton
                            type="button"
                            onClick={() => handleResendInvitation(account)}
                            disabled={isSubmitting}
                          >
                            Reenviar invitación
                          </SecondaryButton>
                        )}
                      </UserActions>
                    </>
                  )}
                </UserRow>
              ))}
            </UserList>
          )}
        </Panel>
      </ContentGrid>
    </>
  );
};

export default Users;
