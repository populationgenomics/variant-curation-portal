import { applyMiddleware, combineReducers, createStore } from "redux";
import thunk from "redux-thunk";

import appSettingsReducer from "./reducers/appSettingsReducer";
import curationResultReducer from "./reducers/curationResultReducer";
import userReducer from "./reducers/userReducer";
import customFlagReducer from "./reducers/customFlagReducer";

const rootReducer = combineReducers({
  appSettings: appSettingsReducer,
  curationResult: curationResultReducer,
  user: userReducer,
  customFlags: customFlagReducer,
});

const store = createStore(rootReducer, undefined, applyMiddleware(thunk));

export default store;
