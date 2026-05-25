import { create } from "zustand";
import api from "@/lib/api";
import type { Campaign, CampaignCreatePayload, CampaignUpdatePayload, Product } from "@/lib/types/campaign";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

interface CampaignState {
  campaigns: Campaign[];
  products: Product[];
  currentCampaign: Campaign | null;
  isLoading: boolean;
  isSaving: boolean;
  error: string | null;
  fetchCampaigns: () => Promise<void>;
  fetchCampaign: (id: string) => Promise<Campaign>;
  fetchProducts: () => Promise<void>;
  createCampaign: (payload: CampaignCreatePayload) => Promise<Campaign>;
  updateCampaign: (id: string, payload: CampaignUpdatePayload) => Promise<Campaign>;
  duplicateCampaign: (id: string) => Promise<Campaign>;
  publishCampaign: (id: string) => Promise<void>;
  endCampaign: (id: string) => Promise<void>;
  uploadDesign: (id: string, file: File, side?: "front" | "back") => Promise<void>;
}

export const useCampaignStore = create<CampaignState>((set) => ({
  campaigns: [],
  products: [],
  currentCampaign: null,
  isLoading: false,
  isSaving: false,
  error: null,

  fetchCampaigns: async () => {
    set({ isLoading: true, error: null });
    try {
      const { data } = await api.get<{ campaigns: Campaign[]; total: number }>("/campaigns");
      set({ campaigns: data.campaigns, isLoading: false });
    } catch {
      set({ error: "Failed to load campaigns", isLoading: false });
    }
  },

  fetchCampaign: async (id) => {
    set({ isLoading: true, error: null });
    try {
      const { data } = await api.get<Campaign>(`/campaigns/${id}`);
      set({ currentCampaign: data, isLoading: false });
      return data;
    } catch {
      set({ error: "Failed to load campaign", isLoading: false });
      throw new Error("Failed to load campaign");
    }
  },

  fetchProducts: async () => {
    try {
      const { data: bpData } = await api.get<{ products: Product[] }>(
        "/products",
        { params: { fulfillment_provider: "burger_prints" } }
      );
      if (bpData.products.length > 0) {
        set({ products: bpData.products });
        return;
      }
      const { data } = await api.get<{ products: Product[] }>("/products");
      set({ products: data.products });
    } catch {
      set({ error: "Failed to load product catalog" });
    }
  },

  createCampaign: async (payload) => {
    set({ isSaving: true, error: null });
    try {
      const { data } = await api.post<Campaign>("/campaigns", payload);
      set((s) => ({ campaigns: [data, ...s.campaigns], isSaving: false }));
      return data;
    } catch {
      set({ error: "Failed to create campaign", isSaving: false });
      throw new Error("Failed to create campaign");
    }
  },

  updateCampaign: async (id, payload) => {
    set({ isSaving: true, error: null });
    try {
      const { data } = await api.patch<Campaign>(`/campaigns/${id}`, payload);
      set((s) => ({
        campaigns: s.campaigns.map((c) => (c.id === id ? data : c)),
        currentCampaign: s.currentCampaign?.id === id ? data : s.currentCampaign,
        isSaving: false,
      }));
      return data;
    } catch {
      set({ error: "Failed to update campaign", isSaving: false });
      throw new Error("Failed to update campaign");
    }
  },

  duplicateCampaign: async (id) => {
    set({ isSaving: true, error: null });
    try {
      const { data } = await api.post<Campaign>(`/campaigns/${id}/duplicate`);
      set((s) => ({ campaigns: [data, ...s.campaigns], isSaving: false }));
      return data;
    } catch {
      set({ error: "Failed to duplicate campaign", isSaving: false });
      throw new Error("Failed to duplicate campaign");
    }
  },

  publishCampaign: async (id) => {
    set({ isSaving: true });
    try {
      const { data } = await api.post<Campaign>(`/campaigns/${id}/publish`);
      set((s) => ({
        campaigns: s.campaigns.map((c) => (c.id === id ? data : c)),
        currentCampaign: s.currentCampaign?.id === id ? data : s.currentCampaign,
        isSaving: false,
      }));
    } catch {
      set({ error: "Failed to publish campaign", isSaving: false });
      throw new Error("Failed to publish");
    }
  },

  endCampaign: async (id) => {
    const { data } = await api.post<Campaign>(`/campaigns/${id}/end`);
    set((s) => ({
      campaigns: s.campaigns.map((c) => (c.id === id ? data : c)),
    }));
  },

  uploadDesign: async (id, file, side = "front") => {
    set({ isSaving: true });
    try {
      const formData = new FormData();
      formData.append("file", file);
      const token = localStorage.getItem("access_token");
      const data = await fetch(`${API_URL}/api/v1/campaigns/${id}/design?side=${side}`, {
        method: "POST",
        headers: token ? { Authorization: `Bearer ${token}` } : {},
        body: formData,
      }).then(async (res) => {
        if (!res.ok) throw new Error("Upload failed");
        return res.json();
      });
      set((s) => ({
        campaigns: s.campaigns.map((c) => (c.id === id ? (data as Campaign) : c)),
        currentCampaign: s.currentCampaign?.id === id ? (data as Campaign) : s.currentCampaign,
        isSaving: false,
      }));
    } catch {
      set({ error: "Failed to upload design", isSaving: false });
      throw new Error("Upload failed");
    }
  },
}));
