export interface OrderItem {
  variant_name: string;
  product_name: string;
  quantity: number;
  unit_price: number;
  line_total: number;
  provider_sku?: string | null;
}

export interface Order {
  id: string;
  campaign_id: string | null;
  campaign_title: string | null;
  campaign_slug?: string | null;
  customer_email: string;
  customer_name: string | null;
  subtotal: number;
  tip_amount: number;
  total: number;
  status: string;
  fulfillment_provider?: string | null;
  external_order_id?: string | null;
  fulfillment_status?: string | null;
  fulfillment_error?: string | null;
  tracking_number?: string | null;
  fulfillment_submitted_at?: string | null;
  items: OrderItem[];
  created_at: string;
  facebook_pixel_id?: string | null;
  google_analytics_id?: string | null;
}

export interface CartItem {
  variant_id: string;
  variant_name: string;
  quantity: number;
  unit_price: number;
  line_total: number;
}

export interface Cart {
  id: string;
  campaign_id: string;
  campaign_slug: string;
  campaign_title: string;
  items: CartItem[];
  subtotal: number;
}
