import queryString from "query-string";

import getCookie from "./utilities/getCookie";

class ApiClient {
  // eslint-disable-next-line class-methods-use-this
  request(path, options) {
    return fetch(`/api${path}`, options).then((response) => {
      const isOk = response.ok;
      if (response.status === 204) return {};
      return response.json().then(
        (data) => {
          if (isOk) {
            return data;
          }

          const error = new Error(data.detail || "Unknown error");
          error.data = data;
          throw error;
        },
        () => {
          throw new Error("Unable to parse response");
        }
      );
    });
  }

  get(path, params = {}) {
    const query = queryString.stringify(params);
    const requestPath = query ? `${path}?${query}` : path;
    return this.request(requestPath, {});
  }

  patch(path, data) {
    return this.request(path, {
      body: JSON.stringify(data),
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": getCookie("csrftoken"),
      },
      method: "PATCH",
    });
  }

  post(path, data) {
    return this.request(path, {
      body: JSON.stringify(data),
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": getCookie("csrftoken"),
      },
      method: "POST",
    });
  }

  delete(path) {
    return this.request(path, {
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": getCookie("csrftoken"),
      },
      method: "DELETE",
    });
  }
}

export default new ApiClient();
