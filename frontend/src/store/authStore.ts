import { create } from "zustand";
import { User } from "@/types";
import { getToken, setToken, removeToken, getStoredUser, setStoredUser } from "@/lib/auth";
import { loginApi } from "@/lib/api";

interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
  login: (username: string, password: string) => Promise<boolean>;
  logout: () => void;
  initialize: () => void;
}

export const useAuthStore = create<AuthState>((set) => ({
  user: getStoredUser(),
  token: getToken(),
  isAuthenticated: !!getToken(),
  isLoading: false,
  error: null,

  initialize: () => {
    const token = getToken();
    const user = getStoredUser();
    set({ token, user, isAuthenticated: !!token });
  },

  login: async (username: string, password: string) => {
    set({ isLoading: true, error: null });
    try {
      const data = await loginApi(username, password);
      setToken(data.access_token);
      setStoredUser(data.user);
      set({
        user: data.user,
        token: data.access_token,
        isAuthenticated: true,
        isLoading: false,
      });
      return true;
    } catch (err: any) {
      set({
        error: err.response?.data?.detail || "Invalid credentials",
        isLoading: false,
      });
      return false;
    }
  },

  logout: () => {
    removeToken();
    set({ user: null, token: null, isAuthenticated: false });
  },
}));
