import axios from "axios";
import store from "@/store";
import router from "@/router";

const options = {
  baseURL: process.env.VUE_APP_API_URL || "http://localhost:8000/api",
  timeout: 10000,
};

const instance = axios.create(options);

let isRefreshing = false;
let failedQueue = [];

const processQueue = (error, token = null) => {
  failedQueue.forEach(prom => {
    if (error) {
      prom.reject(error);
    } else {
      prom.resolve(token);
    }
  });
  failedQueue = [];
};

instance.interceptors.request.use(
  function (config) {
    const token = localStorage.getItem("LLMAccess");

    if (token && config.isPublic !== true) {
      config.headers.Authorization = `Bearer ${token}`;
    }

    return config;
  },
  function (error) {
    return Promise.reject(error);
  }
);

instance.interceptors.response.use(
  function (response) {
    return response;
  },
  async function (error) {
    const originalRequest = error.config;

    const isAuthEndpoint = originalRequest.url?.includes('/auth/token/') || 
                          originalRequest.url?.includes('/auth/sign-up/');

    if (error?.response?.status !== 401 || originalRequest.isPublic) {
      if (!isAuthEndpoint) {
        store.dispatch("addMessageWithTimeout", {
          type: "error",
          text: "Đã xảy ra lỗi khi thực hiện yêu cầu",
          error,
          timeout: 5000,
        });
      }
      return Promise.reject(error);
    }

    if (originalRequest._retry) {
      store.dispatch("logout");
      router.push("/login");
      return Promise.reject(error);
    }

    if (isRefreshing) {
      return new Promise(function (resolve, reject) {
        failedQueue.push({ resolve, reject });
      })
        .then(token => {
          originalRequest.headers.Authorization = 'Bearer ' + token;
          return instance(originalRequest);
        })
        .catch(err => {
          return Promise.reject(err);
        });
    }

    originalRequest._retry = true;
    isRefreshing = true;

    const refreshToken = localStorage.getItem("LLMRefresh");

    if (!refreshToken) {
      store.dispatch("logout");
      router.push("/login");
      return Promise.reject(error);
    }

    try {
      console.log("Refreshing token...");
      
      const response = await axios.post(
        `${options.baseURL}/auth/token/refresh/`,
        { refresh: refreshToken }
      );

      const newAccessToken = response.data.access;
      localStorage.setItem("LLMAccess", newAccessToken);

      if (response.data.refresh) {
        localStorage.setItem("LLMRefresh", response.data.refresh);
      }

      console.log("Token refreshed successfully");

      originalRequest.headers.Authorization = 'Bearer ' + newAccessToken;

      processQueue(null, newAccessToken);

      return instance(originalRequest);

    } catch (refreshError) {
      console.error("Failed to refresh token:", refreshError);
      
      processQueue(refreshError, null);
      store.dispatch("logout");
      router.push("/login");
      
      return Promise.reject(refreshError);
    } finally {
      isRefreshing = false;
    }
  }
);

export default instance;