import { actionTypes } from "../actions/customFlagActions";

const customFlagActions = (state, action) => {
  if (state === undefined) {
    return [];
  }

  switch (action.type) {
    case actionTypes.SET_CUSTOM_FLAGS:
      return action.flags;
    case actionTypes.SET_CUSTOM_FlAG:
      return [...state.filter((f) => f.id !== action.flag.id), action.flag];
    case actionTypes.UNSET_CUSTOM_FLAG:
      return state.filter((f) => f.id !== action.flag.id);
    default:
      return state;
  }
};

export default customFlagActions;
