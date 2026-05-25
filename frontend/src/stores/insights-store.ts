import { create } from "zustand";
import api from "@/lib/api";
import type { Insight, InsightListResponse } from "@/lib/types";

interface InsightsState {
  items: Insight[];
  total: number;
  isLoading: boolean;
  isRefreshing: boolean;
  error: string | null;
  fetchInsights: (page?: number, category?: string) => Promise<void>;
  refreshInsights: () => Promise<void>;
  dismissInsight: (id: string) => Promise<void>;
}

export const useInsightsStore = create<InsightsState>((set, get) => ({
  items: [],
  total: 0,
  isLoading: false,
  isRefreshing: false,
  error: null,

  fetchInsights: async (page = 1, category?: string) => {
    set({ isLoading: true, error: null });
    try {
      const params: Record<string, string | number> = { page, page_size: 20 };
      if (category && category !== "all") params.category = category;
      const { data } = await api.get<InsightListResponse>("/insights", { params });
      set({ items: data.items, total: data.total, isLoading: false });
    } catch {
      set({ error: "Failed to load insights", isLoading: false });
    }
  },

  refreshInsights: async () => {
    set({ isRefreshing: true, error: null });
    try {
      await api.post("/insights/refresh");
      await get().fetchInsights();
      set({ isRefreshing: false });
    } catch {
      set({ error: "Failed to refresh insights", isRefreshing: false });
    }
  },

  dismissInsight: async (id: string) => {
    await api.post(`/insights/${id}/dismiss`);
    set((state) => ({
      items: state.items.filter((i) => i.id !== id),
      total: Math.max(0, state.total - 1),
    }));
  },
}));
