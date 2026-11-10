import {
  CLEAR_FINANCE,
  DASHBOARD_LOADED,
  LOAD_FAILED,
  LOAD_STARTED,
} from '../actionTypes.js';

const initialState = { summary: null, status: 'idle', error: null };

export default function dashboardReducer(state = initialState, action) {
  switch (action.type) {
    case LOAD_STARTED:
      return action.key === 'dashboard'
        ? { ...state, status: 'loading', error: null }
        : state;
    case DASHBOARD_LOADED:
      return { summary: action.payload, status: 'succeeded', error: null };
    case LOAD_FAILED:
      return action.key === 'dashboard'
        ? { ...state, status: 'failed', error: action.error }
        : state;
    case CLEAR_FINANCE:
      return initialState;
    default:
      return state;
  }
}
