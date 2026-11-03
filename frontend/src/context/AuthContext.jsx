import { createContext, useContext, useEffect, useState } from "react";
import api from "../api/client";

const AuthContext = createContext(null);
export const useAuth = () => useContext(AuthContext);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  async function loadUser() {
    const token = localStorage.getItem("cartpilot_access");
    if (!token) { setLoading(false); return; }
    try {
      const response = await api.get("/auth/me/");
      setUser(response.data);
    } catch {
      setUser(null);
      localStorage.removeItem("cartpilot_access");
      localStorage.removeItem("cartpilot_refresh");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => { loadUser(); }, []);

  async function login(username, password) {
    const response = await api.post("/auth/token/", { username, password });
    localStorage.setItem("cartpilot_access", response.data.access);
    localStorage.setItem("cartpilot_refresh", response.data.refresh);
    const profile = await api.get("/auth/me/");
    setUser(profile.data);
    return profile.data;
  }

  async function register(data) {
    await api.post("/auth/register/", data);
    return login(data.username, data.password);
  }

  function logout() {
    localStorage.removeItem("cartpilot_access");
    localStorage.removeItem("cartpilot_refresh");
    setUser(null);
  }

  return <AuthContext.Provider value={{ user, loading, login, register, logout, refreshUser: loadUser }}>{children}</AuthContext.Provider>;
}
