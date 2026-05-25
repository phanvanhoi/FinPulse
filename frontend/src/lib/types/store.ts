export interface Store {
  id: string;
  organization_id: string;
  name: string;
  slug: string;
  logo_url: string | null;
  favicon_url: string | null;
  custom_domain: string | null;
  domain_verification_status: "unverified" | "pending" | "verified";
  domain_verification_token: string | null;
  tips_enabled: boolean;
  tip_options: number[];
  facebook_pixel_id: string | null;
  google_analytics_id: string | null;
  abandoned_checkout_enabled: boolean;
  abandoned_checkout_delay_minutes: number;
  abandoned_checkout_email_subject: string | null;
  abandoned_checkout_email_body: string | null;
  created_at: string;
  updated_at: string;
}

export interface StoreUpdatePayload {
  name?: string;
  tips_enabled?: boolean;
  tip_options?: number[];
  facebook_pixel_id?: string | null;
  google_analytics_id?: string | null;
  abandoned_checkout_enabled?: boolean;
  abandoned_checkout_delay_minutes?: number;
  abandoned_checkout_email_subject?: string | null;
  abandoned_checkout_email_body?: string | null;
}

export interface DomainVerification {
  custom_domain: string | null;
  verification_status: string;
  verification_token: string | null;
  dns_record_name: string | null;
  dns_record_value: string | null;
  instructions: string | null;
}

export interface PublicStore {
  name: string;
  slug: string;
  logo_url: string | null;
  facebook_pixel_id: string | null;
  google_analytics_id: string | null;
}
