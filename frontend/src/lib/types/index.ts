export interface User {
  id: string;
  email: string;
  name: string;
  organization_id: string;
  is_active: boolean;
}

export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

export interface FinancialSummary {
  revenue: number;
  expenses: number;
  net_income: number;
  gross_margin_pct: number;
  cash_on_hand: number;
  accounts_receivable: number;
  accounts_payable: number;
  cash_runway_days: number | null;
  revenue_change_pct: number | null;
}

export interface MarketingSummary {
  total_spend: number;
  total_impressions: number;
  total_clicks: number;
  total_conversions: number;
  avg_cpc: number;
  avg_ctr: number;
  overall_roas: number;
  active_campaigns: number;
  spend_change_pct: number | null;
}

export interface DashboardOverview {
  period_start: string;
  period_end: string;
  financial: FinancialSummary;
  marketing: MarketingSummary;
  marketing_spend_pct_of_revenue: number | null;
  estimated_cac: number | null;
}

export interface CampaignPerformance {
  campaign_id: string;
  campaign_name: string;
  platform: string;
  spend: number;
  impressions: number;
  clicks: number;
  conversions: number;
  roas: number;
  status: string;
}

export interface Insight {
  id: string;
  insight_type: string;
  category: string;
  title: string;
  body_markdown: string;
  severity: string;
  data_context: Record<string, unknown> | null;
  is_read: boolean;
  generated_at: string;
}

export interface InsightListResponse {
  items: Insight[];
  total: number;
  page: number;
  page_size: number;
}

export interface Connection {
  id: string;
  provider: string;
  status: string;
  last_synced_at: string | null;
  error_message: string | null;
}
