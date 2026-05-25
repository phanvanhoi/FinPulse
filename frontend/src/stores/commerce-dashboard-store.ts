import { create } from "zustand";
import api from "@/lib/api";
import type { CommerceDashboardOverview } from "@/lib/types";

interface CommerceDashboardState {
  overview: CommerceDashboardOverview | null;
  isLoading: boolean;
  error: string | null;
  periodDays: number;
  setPeriodDays: (days: number) => void;
  fetchCommerceOverview: () => Promise<void>;
}

export const useCommerceDashboardStore = create<CommerceDashboardState>((set, get) => ({
  overview: null,
  isLoading: false,
  error: null,
  periodDays: 30,

  setPeriodDays: (days) => {
    set({ periodDays: days });
    get().fetchCommerceOverview();
  },

  fetchCommerceOverview: async () => {
    const { periodDays } = get();
    set({ isLoading: true, error: null });
    try {
      const { data } = await api.get<CommerceDashboardOverview>("/dashboard/commerce-overview", {
        params: { period_days: periodDays },
      });
      set({ overview: data, isLoading: false });
    } catch {
      set({ error: "Failed to load dashboard", isLoading: false });
    }
  },
}));
