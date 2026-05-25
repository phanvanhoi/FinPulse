import { create } from "zustand";
import api from "@/lib/api";
import type { DomainVerification, Store, StoreUpdatePayload } from "@/lib/types/store";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

interface StoreSettingsState {
  store: Store | null;
  domainVerification: DomainVerification | null;
  isLoading: boolean;
  isSaving: boolean;
  error: string | null;
  fetchStore: () => Promise<void>;
  updateStore: (payload: StoreUpdatePayload) => Promise<void>;
  uploadLogo: (file: File) => Promise<void>;
  setDomain: (customDomain: string) => Promise<void>;
  verifyDomain: () => Promise<void>;
  fetchDomainVerification: () => Promise<void>;
}

export const useStoreSettingsStore = create<StoreSettingsState>((set, get) => ({
  store: null,
  domainVerification: null,
  isLoading: false,
  isSaving: false,
  error: null,

  fetchStore: async () => {
    set({ isLoading: true, error: null });
    try {
      const { data } = await api.get<Store>("/store");
      set({ store: data, isLoading: false });
    } catch {
      set({ error: "Failed to load store settings", isLoading: false });
    }
  },

  updateStore: async (payload) => {
    set({ isSaving: true, error: null });
    try {
      const { data } = await api.patch<Store>("/store", payload);
      set({ store: data, isSaving: false });
    } catch {
      set({ error: "Failed to save store settings", isSaving: false });
      throw new Error("Failed to save");
    }
  },

  uploadLogo: async (file) => {
    set({ isSaving: true, error: null });
    try {
      const formData = new FormData();
      formData.append("file", file);
      const token = localStorage.getItem("access_token");
      const { data } = await fetch(`${API_URL}/api/v1/store/logo`, {
        method: "POST",
        headers: token ? { Authorization: `Bearer ${token}` } : {},
        body: formData,
      }).then(async (res) => {
        if (!res.ok) throw new Error("Upload failed");
        return res.json();
      });
      set({ store: data as Store, isSaving: false });
    } catch {
      set({ error: "Failed to upload logo", isSaving: false });
      throw new Error("Failed to upload");
    }
  },

  setDomain: async (customDomain) => {
    set({ isSaving: true, error: null });
    try {
      const { data: verification } = await api.post<DomainVerification>("/store/domain", {
        custom_domain: customDomain,
      });
      await get().fetchStore();
      set({ domainVerification: verification, isSaving: false });
    } catch {
      set({ error: "Failed to set custom domain", isSaving: false });
      throw new Error("Failed to set domain");
    }
  },

  verifyDomain: async () => {
    set({ isSaving: true, error: null });
    try {
      const { data: verification } = await api.post<DomainVerification>("/store/domain/verify");
      await get().fetchStore();
      set({ domainVerification: verification, isSaving: false });
    } catch (err: unknown) {
      const message =
        err && typeof err === "object" && "response" in err
          ? (err as { response?: { data?: { detail?: string } } }).response?.data?.detail
          : "Failed to verify domain";
      set({ error: message || "Failed to verify domain", isSaving: false });
      throw new Error(message || "Failed to verify domain");
    }
  },

  fetchDomainVerification: async () => {
    try {
      const { data } = await api.get<DomainVerification>("/store/domain/verification");
      set({ domainVerification: data });
    } catch {
      set({ error: "Failed to load domain verification info" });
    }
  },
}));
