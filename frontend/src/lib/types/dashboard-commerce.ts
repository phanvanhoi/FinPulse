export interface CommerceKPIs {
  revenue: number;
  revenue_change_pct: number | null;
  orders_count: number;
  orders_pending: number;
  units_sold: number;
  live_campaigns: number;
  draft_campaigns: number;
  avg_order_value: number;
}

export interface RevenueByDay {
  date: string;
  revenue: number;
  orders: number;
}

export interface OrdersByStatus {
  status: string;
  count: number;
}

export interface TopCampaignSummary {
  id: string;
  title: string;
  slug: string;
  status: string;
  units_sold: number;
  revenue: number;
}

export interface RecentOrderSummary {
  id: string;
  customer_email: string;
  total: number;
  status: string;
  created_at: string;
  campaign_title: string | null;
}

export interface StoreSummary {
  name: string;
  slug: string;
  has_logo: boolean;
  storefront_url: string;
}

export interface SetupStatus {
  has_logo: boolean;
  has_live_campaign: boolean;
  has_paid_order: boolean;
}

export interface CommerceInsightPreview {
  insight_type: string;
  category: string;
  title: string;
  body_markdown: string;
  severity: string;
}

export interface FinanceSnapshot {
  revenue: number;
  net_income: number | null;
  cash_on_hand: number | null;
  source: string;
  detail: string;
}

export interface MarketingSnapshot {
  live_campaigns: number;
  units_sold: number;
  ad_spend: number | null;
  overall_roas: number | null;
  source: string;
  detail: string;
}

export interface CommerceDashboardOverview {
  period_start: string;
  period_end: string;
  kpis: CommerceKPIs;
  revenue_by_day: RevenueByDay[];
  orders_by_status: OrdersByStatus[];
  top_campaigns: TopCampaignSummary[];
  recent_orders: RecentOrderSummary[];
  store: StoreSummary | null;
  setup: SetupStatus;
  insights: CommerceInsightPreview[];
  finance_snapshot: FinanceSnapshot | null;
  marketing_snapshot: MarketingSnapshot | null;
}
