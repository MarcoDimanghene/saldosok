import { useEffect, useState } from 'react';
import { PLANES } from '../../config/appConfig';
import { useAuth } from '../../hook/useAuth';
import { getUsers } from '../../services/userService';
import {
  PlanCard,
  PlanGrid,
  PlanHeader,
  PlanMessage,
  PlanSelectButton,
  PlansContainer,
} from './Plans.styles';

const Plans = () => {
  const { tenant, updateTenant } = useAuth();
  const [userCount, setUserCount] = useState(0);
  const [isLoading, setIsLoading] = useState(true);
  const [isUpdating, setIsUpdating] = useState(false);
  const [message, setMessage] = useState(null);

  useEffect(() => {
    let isMounted = true;
    getUsers()
      .then((users) => {
        if (isMounted) setUserCount(users.length);
      })
      .catch((error) => {
        if (isMounted) setMessage({
          error: true,
          text: error.message || 'No se pudo consultar la cantidad de cuentas.',
        });
      })
      .finally(() => {
        if (isMounted) setIsLoading(false);
      });
    return () => {
      isMounted = false;
    };
  }, []);

  const handleSelectPlan = async (plan) => {
    setMessage(null);
    setIsUpdating(true);
    try {
      await updateTenant({ plan: plan.id });
      setMessage({ error: false, text: `Tu plan ahora es ${plan.nombre}.` });
    } catch (error) {
      setMessage({ error: true, text: error.message || 'No se pudo cambiar el plan.' });
    } finally {
      setIsUpdating(false);
    }
  };

  return (
    <PlansContainer>
      <PlanHeader>
        <h1>Planes</h1>
        <p>
          El titular puede cambiar el plan del espacio de trabajo. Las cuentas actuales deben caber
          dentro del límite del nuevo plan.
        </p>
        <p>
          Plan actual: <strong>{PLANES.find(({ id }) => id === tenant?.plan)?.nombre || tenant?.plan}</strong>
          {' · '}
          {isLoading ? 'Consultando cuentas…' : `${userCount} cuenta${userCount === 1 ? '' : 's'} en uso`}
        </p>
      </PlanHeader>

      {message && (
        <PlanMessage $error={message.error} role={message.error ? 'alert' : 'status'}>
          {message.text}
        </PlanMessage>
      )}

      <PlanGrid>
        {PLANES.map((plan) => {
          const isCurrent = tenant?.plan === plan.id;
          const belowCurrentCount = plan.usuarios < userCount;
          return (
            <PlanCard key={plan.id} $selected={isCurrent}>
              <h2>{plan.nombre}</h2>
              <p>{plan.descripcion}</p>
              <strong>Hasta {plan.usuarios} {plan.usuarios === 1 ? 'usuario' : 'usuarios'}</strong>
              <PlanSelectButton
                type="button"
                onClick={() => handleSelectPlan(plan)}
                disabled={isCurrent || belowCurrentCount || isLoading || isUpdating}
                title={belowCurrentCount ? `Reduce las cuentas a ${plan.usuarios} para seleccionar este plan.` : undefined}
              >
                {isCurrent ? 'Plan actual' : belowCurrentCount ? 'Supera el límite actual' : 'Elegir plan'}
              </PlanSelectButton>
            </PlanCard>
          );
        })}
      </PlanGrid>
    </PlansContainer>
  );
};

export default Plans;
