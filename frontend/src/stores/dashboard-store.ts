import { create } from "zustand";
import api from "@/lib/api";
import type { DashboardOverview, CampaignPerformance, InsightListResponse } from "@/lib/types";

interface DashboardState {
  overview: DashboardOverview | null;
  campaigns: CampaignPerformance[];
  insights: InsightListResponse | null;
  isLoading: boolean;
  error: string | null;
  fetchOverview: (periodStart?: string, periodEnd?: string) => Promise<void>;
  fetchCampaigns: () => Promise<void>;
  fetchInsights: (page?: number) => Promise<void>;
}

export const useDashboardStore = create<DashboardState>((set) => ({
  overview: null,
  campaigns: [],
  insights: null,
  isLoading: false,
  error: null,

  fetchOverview: async (periodStart, periodEnd) => {
    set({ isLoading: true, error: null });
    try {
      const params: Record<string, string> = {};
      if (periodStart) params.period_start = periodStart;
      if (periodEnd) params.period_end = periodEnd;
      const { data } = await api.get<DashboardOverview>("/dashboard/overview", { params });
      set({ overview: data, isLoading: false });
    } catch (err) {
      set({ error: "Failed to load dashboard", isLoading: false });
    }
  },

  fetchCampaigns: async () => {
    try {
      const { data } = await api.get<CampaignPerformance[]>("/dashboard/campaigns");
      set({ campaigns: data });
    } catch (err) {
      set({ error: "Failed to load campaigns" });
    }
  },

  fetchInsights: async (page = 1) => {
    try {
      const { data } = await api.get<InsightListResponse>("/insights", {
        params: { page, page_size: 10 },
      });
      set({ insights: data });
    } catch (err) {
      set({ error: "Failed to load insights" });
    }
  },
}));
