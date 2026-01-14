import Vuex from "vuex";
import axios from "@/plugins/axios";

let messageCounter = 0;

const store = new Vuex.Store({
  state: {
    language: "cpp",
    footerActions: null,
    user: null,
    messages: [],
    maxMessages: 3,
    messageTimers: {},
    closingMessages: {},
  },
  mutations: {
    setUser(state, user) {
      state.user = user;
    },
    addMessage(state, message) {
      if (state.messages.length >= state.maxMessages) {
        const removedMsg = state.messages.shift();
        if (state.messageTimers[removedMsg.id]) {
          clearTimeout(state.messageTimers[removedMsg.id]);
          delete state.messageTimers[removedMsg.id];
        }
      }
      state.messages.push(message);
    },
    removeMessage(state, messageId) {
      if (!messageId) {
        console.warn("removeMessage called without messageId");
        return;
      }
      
      const index = state.messages.findIndex(msg => msg.id === messageId);
      if (index !== -1) {
        state.messages.splice(index, 1);
      }
      
      if (state.messageTimers[messageId]) {
        clearTimeout(state.messageTimers[messageId]);
        delete state.messageTimers[messageId];
      }
      
      delete state.closingMessages[messageId];
    },
    setClosingMessage(state, messageId) {
      state.closingMessages[messageId] = true;
    },
    setMessageTimer(state, { messageId, timerId }) {
      state.messageTimers[messageId] = timerId;
    },
    clearMessageTimer(state, messageId) {
      if (state.messageTimers[messageId]) {
        clearTimeout(state.messageTimers[messageId]);
        delete state.messageTimers[messageId];
      }
    },
    setObject(state, object) {
      state.object = object || {};
    }
  },
  actions: {
    addMessageWithTimeout({ commit, dispatch }, message) {
      const messageId = `${Date.now()}-${messageCounter++}`;
      const messageWithId = { ...message, id: messageId };
      
      commit("addMessage", messageWithId);
      
      const timeout = message.timeout || 5000;
      dispatch("startMessageTimer", { messageId, timeout });
      
      return messageId;
    },
    
    startMessageTimer({ commit }, { messageId, timeout }) {
      const timerId = setTimeout(() => {
        commit("setClosingMessage", messageId);
        setTimeout(() => {
          commit("removeMessage", messageId);
        }, 300);
      }, timeout);
      
      commit("setMessageTimer", { messageId, timerId });
    },
    
    pauseMessageTimer({ commit }, messageId) {
      commit("clearMessageTimer", messageId);
    },
    
    resumeMessageTimer({ commit, dispatch, state }, { messageId, timeout }) {
      const messageExists = state.messages.some(msg => msg.id === messageId);
      if (messageExists) {
        dispatch("startMessageTimer", { messageId, timeout });
      }
    },
    
    async getUser({ commit }) {
      const token = window.localStorage.getItem("LLMAccess");
      if (!token) {
        commit("setUser", null);
        return;
      }

      try {
        const { data } = await axios.get("/auth/users/me/");
        commit("setUser", data);
      } catch (error) {
        console.error("Failed to get user:", error);
        throw error;
      }
    },
    
    logout({ commit }) {
      window.localStorage.removeItem("LLMAccess");
      window.localStorage.removeItem("LLMRefresh");
      commit("setUser", null);
      router.push("/login");
    }
  },
  getters: {},
});

export default store;