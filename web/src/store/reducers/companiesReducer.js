import {
  CLEAR_FINANCE,
  COMPANIES_LOADED,
  LOAD_FAILED,
  LOAD_STARTED,
} from '../actionTypes.js';

const initialState = { items: [], status: 'idle', error: null };

export default function companiesReducer(state = initialState, action) {
  switch (action.type) {
    case LOAD_STARTED:
      return action.key === 'companies'
        ? { ...state, status: 'loading', error: null }
        : state;
    case COMPANIES_LOADED:
      return { items: action.payload, status: 'succeeded', error: null };
    case LOAD_FAILED:
      return action.key === 'companies'
        ? { ...state, status: 'failed', error: action.error }
        : state;
    case CLEAR_FINANCE:
      return initialState;
    default:
      return state;
  }
}
