import Link from "next/link";
import Script from "next/script";
import type { PublicStore } from "@/lib/types/store";
import type { LiveCampaignSummary } from "@/lib/types/campaign";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

async function getPublicStore(slug: string): Promise<PublicStore | null> {
  try {
    const res = await fetch(`${API_URL}/api/v1/store/public/${slug}`, { next: { revalidate: 60 } });
    if (!res.ok) return null;
    return res.json();
  } catch {
    return null;
  }
}

async function getLiveCampaigns(storeSlug: string): Promise<LiveCampaignSummary[]> {
  try {
    const res = await fetch(`${API_URL}/api/v1/campaigns/public/store/${storeSlug}/live`, {
      next: { revalidate: 60 },
    });
    if (!res.ok) return [];
    const data = await res.json();
    return data.campaigns || [];
  } catch {
    return [];
  }
}

export default async function PublicStorePage({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = await params;
  const [store, campaigns] = await Promise.all([getPublicStore(slug), getLiveCampaigns(slug)]);

  if (!store) {
    return (
      <div style={{ minHeight: "100vh", display: "flex", alignItems: "center", justifyContent: "center" }}>
        <div style={{ textAlign: "center" }}>
          <h1>Store not found</h1>
          <p>The storefront you are looking for does not exist.</p>
        </div>
      </div>
    );
  }

  return (
    <>
      {store.facebook_pixel_id && (
        <>
          <Script id="fb-pixel" strategy="afterInteractive">
            {`
              !function(f,b,e,v,n,t,s)
              {if(f.fbq)return;n=f.fbq=function(){n.callMethod?
              n.callMethod.apply(n,arguments):n.queue.push(arguments)};
              if(!f._fbq)f._fbq=n;n.push=n;n.loaded=!0;n.version='2.0';
              n.queue=[];t=b.createElement(e);t.async=!0;
              t.src=v;s=b.getElementsByTagName(e)[0];
              s.parentNode.insertBefore(t,s)}(window, document,'script',
              'https://connect.facebook.net/en_US/fbevents.js');
              fbq('init', '${store.facebook_pixel_id}');
              fbq('track', 'PageView');
            `}
          </Script>
        </>
      )}

      {store.google_analytics_id && (
        <>
          <Script
            src={`https://www.googletagmanager.com/gtag/js?id=${store.google_analytics_id}`}
            strategy="afterInteractive"
          />
          <Script id="ga-config" strategy="afterInteractive">
            {`
              window.dataLayer = window.dataLayer || [];
              function gtag(){dataLayer.push(arguments);}
              gtag('js', new Date());
              gtag('config', '${store.google_analytics_id}');
            `}
          </Script>
        </>
      )}

      <div style={{ minHeight: "100vh", background: "#fafafa" }}>
        <header
          style={{
            background: "#fff",
            borderBottom: "1px solid #f0f0f0",
            padding: "16px 24px",
            display: "flex",
            alignItems: "center",
            gap: 16,
          }}
        >
          {store.logo_url ? (
            // eslint-disable-next-line @next/next/no-img-element
            <img src={store.logo_url} alt={store.name} style={{ height: 40, objectFit: "contain" }} />
          ) : (
            <h1 style={{ margin: 0, fontSize: 24, fontWeight: 700 }}>{store.name}</h1>
          )}
        </header>

        <main style={{ maxWidth: 960, margin: "0 auto", padding: "48px 24px" }}>
          <h2 style={{ fontSize: 32, marginBottom: 8, textAlign: "center" }}>{store.name}</h2>
          <p style={{ color: "#666", textAlign: "center", marginBottom: 40 }}>
            Shop our latest campaigns
          </p>

          {campaigns.length === 0 ? (
            <div
              style={{
                background: "#fff",
                border: "1px dashed #d9d9d9",
                borderRadius: 12,
                padding: 48,
                color: "#999",
                textAlign: "center",
              }}
            >
              No live campaigns yet. Check back soon!
            </div>
          ) : (
            <div
              style={{
                display: "grid",
                gridTemplateColumns: "repeat(auto-fill, minmax(280px, 1fr))",
                gap: 24,
              }}
            >
              {campaigns.map((c) => (
                <Link
                  key={c.id}
                  href={`/campaign/${c.slug}`}
                  style={{
                    background: "#fff",
                    borderRadius: 12,
                    overflow: "hidden",
                    border: "1px solid #f0f0f0",
                    textDecoration: "none",
                    color: "inherit",
                  }}
                >
                  {c.design_image_url ? (
                    // eslint-disable-next-line @next/next/no-img-element
                    <img
                      src={c.design_image_url}
                      alt={c.title}
                      style={{ width: "100%", aspectRatio: "1", objectFit: "cover" }}
                    />
                  ) : (
                    <div style={{ aspectRatio: "1", background: "#f0f0f0" }} />
                  )}
                  <div style={{ padding: 16 }}>
                    <h3 style={{ margin: "0 0 4px", fontSize: 18 }}>{c.title}</h3>
                    <p style={{ margin: 0, color: "#888", fontSize: 14 }}>{c.product_name}</p>
                    <p style={{ margin: "8px 0 0", fontWeight: 600, color: "#1677ff" }}>
                      From ${Number(c.retail_price).toFixed(2)}
                    </p>
                  </div>
                </Link>
              ))}
            </div>
          )}
        </main>
      </div>
    </>
  );
}
