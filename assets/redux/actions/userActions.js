import api from "../../api";

export const actionTypes = {
  SET_USER: "SET_USER",
  SET_USER_SETTINGS: "SET_USER_SETTINGS",
};

export const loadUser = () => (dispatch) =>
  api.get("/profile/").then((response) => {
    dispatch({
      type: actionTypes.SET_USER,
      user: response.user,
    });
    return response.user;
  });

export const updateUserSettings = (settingsPatch) => (dispatch) =>
  api.patch("/profile/settings/", settingsPatch).then((settings) => {
    dispatch({
      type: actionTypes.SET_USER_SETTINGS,
      settings,
    });
  });
