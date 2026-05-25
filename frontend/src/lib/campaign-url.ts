const FRONTEND_URL = process.env.NEXT_PUBLIC_FRONTEND_URL || "";

export function buildCampaignShareUrl(
  slug: string,
  options?: { source?: string; medium?: string; baseUrl?: string }
): string {
  const base = (options?.baseUrl || FRONTEND_URL || (typeof window !== "undefined" ? window.location.origin : ""))
    .replace(/\/$/, "");
  const url = new URL(`${base}/campaign/${slug}`);
  url.searchParams.set("utm_source", options?.source || "finpulse");
  url.searchParams.set("utm_medium", options?.medium || "share");
  url.searchParams.set("utm_campaign", slug);
  return url.toString();
}
