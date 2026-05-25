export interface OrderItem {
  variant_name: string;
  product_name: string;
  quantity: number;
  unit_price: number;
  line_total: number;
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
