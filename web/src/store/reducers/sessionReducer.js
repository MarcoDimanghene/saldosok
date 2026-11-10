import { CLEAR_FINANCE } from '../actionTypes.js';

const initialState = { generation: 0 };

export default function sessionReducer(state = initialState, action) {
  if (action.type === CLEAR_FINANCE) {
    return { generation: state.generation + 1 };
  }
  return state;
}
