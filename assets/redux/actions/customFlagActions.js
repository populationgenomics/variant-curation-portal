import api from "../../api";

export const actionTypes = {
  SET_CUSTOM_FLAGS: "SET_CUSTOM_FLAGS",
  SET_CUSTOM_FlAG: "SET_CUSTOM_FlAG",
  UNSET_CUSTOM_FLAG: "UNSET_CUSTOM_FLAG",
  SET_CUSTOM_FLAG_ERRORS: "SET_CUSTOM_FLAG_ERRORS",
};

export const loadCustomFLags = () => (dispatch) =>
  api.get("/custom_flag/").then((response) => {
    dispatch({
      type: actionTypes.SET_CUSTOM_FLAGS,
      flags: response,
    });
    return response;
  });

export const createCustomFlag = (flagData) => (dispatch) =>
  api.post("/custom_flag/create", flagData).then((response) => {
    dispatch({
      type: actionTypes.SET_CUSTOM_FlAG,
      flag: response,
    });
    return response;
  });

export const updateCustomFlag = (flag) => (dispatch) => {
  const patchData = { key: flag.key, label: flag.label, shortcut: flag.shortcut };
  return api.patch(`/custom_flag/${flag.id}/update`, patchData).then((response) => {
    dispatch({
      type: actionTypes.SET_CUSTOM_FlAG,
      flag: response,
    });
    return response;
  });
};

export const deleteCustomFlag = (flag) => (dispatch) =>
  api.delete(`/custom_flag/${flag.id}/delete`).then(() => {
    dispatch({
      type: actionTypes.UNSET_CUSTOM_FLAG,
      flag,
    });
    return flag;
  });
