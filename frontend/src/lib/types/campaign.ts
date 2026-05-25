export interface ProductVariant {
  id: string;
  name: string;
  sku: string | null;
  base_price: number;
}

export interface Product {
  id: string;
  name: string;
  description: string | null;
  category: string;
  image_url: string | null;
  variants: ProductVariant[];
}

export interface CampaignVariant {
  variant_id: string;
  variant_name: string;
  price: number;
}

export interface Campaign {
  id: string;
  store_id: string;
  product_id: string;
  product_name: string | null;
  title: string;
  slug: string;
  description: string | null;
  design_image_url: string | null;
  design_back_url: string | null;
  print_location: "front" | "back" | "both";
  retail_price: number;
  status: "draft" | "live" | "ended";
  starts_at: string | null;
  ends_at: string | null;
  units_sold: number;
  variants: CampaignVariant[];
  created_at: string;
  updated_at: string;
}

export interface PublicCampaign {
  id: string;
  title: string;
  slug: string;
  description: string | null;
  design_image_url: string | null;
  retail_price: number;
  status: string;
  product_name: string;
  product_image_url: string | null;
  variants: CampaignVariant[];
  store_name: string;
  store_slug: string;
  store_logo_url: string | null;
  tips_enabled: boolean;
  tip_options: number[];
  facebook_pixel_id?: string | null;
  google_analytics_id?: string | null;
}

export interface CampaignCreatePayload {
  title: string;
  product_id: string;
  description?: string;
  retail_price: number;
  print_location?: "front" | "back" | "both";
  variant_prices: { variant_id: string; price: number }[];
  starts_at?: string;
  ends_at?: string;
}

export interface CampaignUpdatePayload {
  title?: string;
  description?: string;
  retail_price?: number;
  print_location?: "front" | "back" | "both";
  variant_prices?: { variant_id: string; price: number }[];
  starts_at?: string;
  ends_at?: string;
}

export interface LiveCampaignSummary {
  id: string;
  title: string;
  slug: string;
  description: string | null;
  design_image_url: string | null;
  retail_price: number;
  product_name: string;
}
