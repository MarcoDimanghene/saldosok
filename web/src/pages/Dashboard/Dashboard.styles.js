import styled from 'styled-components';
import { COLORS, RADIUS } from '../../styles/palette';
import { Card } from '../../component/ui/UIComponents';

export const DashboardContainer = styled.div`
  width: 100%;
  max-width: 1440px;
  margin: 0 auto;
`;

export const DashboardHeader = styled.header`
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 1.5rem;
  margin-bottom: 2rem;

  @media (max-width: 700px) {
    flex-direction: column;
  }
`;

export const DashboardTitle = styled.h1`
  margin-bottom: 0.4rem;
  color: #00e5ff;
  font-size: 2rem;

  @media (max-width: 540px) {
    font-size: 1.6rem;
    overflow-wrap: anywhere;
  }
`;

export const DashboardSubtitle = styled.p`
  color: rgba(255, 255, 255, 0.72);
`;

export const HeaderActions = styled.div`
  display: flex;
  align-items: center;
  justify-content: flex-end;
  flex-wrap: wrap;
  gap: 0.75rem;
`;

export const SummaryGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 1rem;
  margin-bottom: 1.25rem;

  @media (max-width: 1100px) {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  @media (max-width: 480px) {
    grid-template-columns: 1fr;
  }
`;

export const MetricCard = styled(Card)`
  position: relative;
  min-width: 0;
  padding: 1.25rem;
  border: 1px solid rgba(255, 255, 255, 0.1);
  background: ${COLORS.PRIMARY_CONTAINER};
  color: ${COLORS.SURFACE_CARD};

  > span:last-child {
    color: rgba(255, 255, 255, 0.65);
    font-size: 0.82rem;
  }
`;

export const MetricIcon = styled.div`
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 2.35rem;
  height: 2.35rem;
  margin-bottom: 1rem;
  border-radius: ${RADIUS.MD};
  background: ${({ $tone }) => (
    $tone === 'warning' ? 'rgba(255, 180, 76, 0.12)'
      : $tone === 'muted' ? 'rgba(164, 214, 76, 0.12)'
        : 'rgba(0, 229, 255, 0.12)'
  )};
  color: ${({ $tone }) => (
    $tone === 'warning' ? '#ffb44c'
      : $tone === 'muted' ? '#a4d64c'
        : '#00e5ff'
  )};
  font-size: 1.25rem;
`;

export const MetricLabel = styled.span`
  display: block;
  margin-bottom: 0.45rem;
  color: rgba(255, 255, 255, 0.68);
  font-size: 0.82rem;
`;

export const MetricValue = styled.strong`
  display: block;
  margin-bottom: 0.55rem;
  overflow-wrap: anywhere;
  color: #ffffff;
  font-size: clamp(1.25rem, 2vw, 1.75rem);
  font-variant-numeric: tabular-nums;
`;

export const TwoColumnGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 1.25rem;
  margin-bottom: 1.25rem;

  @media (max-width: 900px) {
    grid-template-columns: 1fr;
  }
`;

export const DashboardCard = styled(Card)`
  min-width: 0;
  margin-bottom: 1.25rem;
  padding: 1.5rem;
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: ${RADIUS.LG};
  background: ${COLORS.PRIMARY_CONTAINER};
  color: ${COLORS.SURFACE_CARD};

  ${TwoColumnGrid} & {
    margin-bottom: 0;
  }
`;

export const SectionHeading = styled.div`
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 0.5rem 1rem;
  margin-bottom: 1.25rem;

  > span {
    color: rgba(255, 255, 255, 0.58);
    font-size: 0.8rem;
  }
`;

export const SectionTitle = styled.h2`
  font-size: 1.05rem;
`;

export const PartnerList = styled.ul`
  display: flex;
  flex-direction: column;
  gap: 0.15rem;
  list-style: none;
`;

export const PartnerRow = styled.li`
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  padding: 0.85rem 0;
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);

  &:last-child {
    border-bottom: 0;
  }

  > span:first-child {
    min-width: 0;
    overflow-wrap: anywhere;
    color: rgba(255, 255, 255, 0.75);
    font-size: 0.9rem;
  }
`;

export const PartnerAmount = styled.strong`
  flex-shrink: 0;
  color: #ffffff;
  font-variant-numeric: tabular-nums;
`;

export const ProgressTrack = styled.div`
  height: 5px;
  overflow: hidden;
  margin: 0.15rem 0 0.5rem;
  border-radius: ${RADIUS.FULL};
  background: rgba(255, 255, 255, 0.1);

  span {
    display: block;
    height: 100%;
    border-radius: inherit;
    background: #00e5ff;
    transition: width 0.25s ease;
  }
`;

export const UpcomingGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 0.85rem;

  @media (max-width: 700px) {
    grid-template-columns: 1fr;
  }
`;

export const UpcomingItem = styled.div`
  display: flex;
  flex-direction: column;
  gap: 0.65rem;
  min-width: 0;
  padding: 1rem;
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: ${RADIUS.MD};
  background: rgba(0, 0, 0, 0.12);

  strong {
    color: #00e5ff;
    font-size: 0.9rem;
  }

  span {
    color: rgba(255, 255, 255, 0.72);
    font-size: 0.82rem;
    overflow-wrap: anywhere;
  }
`;

export const EmptyState = styled.p`
  padding: 1rem 0;
  color: rgba(255, 255, 255, 0.65);
  font-size: 0.9rem;
`;

export const LoadingState = styled.p`
  padding: 1.5rem;
  border: 1px solid rgba(0, 229, 255, 0.15);
  border-radius: ${RADIUS.MD};
  background: ${COLORS.PRIMARY_CONTAINER};
  color: rgba(255, 255, 255, 0.78);
`;

export const ErrorMessage = styled.div`
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 0.75rem;
  margin-bottom: 1.25rem;
  padding: 1rem 1.25rem;
  border: 1px solid rgba(248, 113, 113, 0.3);
  border-radius: ${RADIUS.MD};
  background: rgba(127, 29, 29, 0.22);
  color: #fecaca;
`;
