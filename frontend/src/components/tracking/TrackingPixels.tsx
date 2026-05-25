"use client";

import Script from "next/script";

interface TrackingPixelsProps {
  facebookPixelId?: string | null;
  googleAnalyticsId?: string | null;
}

export function TrackingPageView({ facebookPixelId, googleAnalyticsId }: TrackingPixelsProps) {
  return (
    <>
      {facebookPixelId && (
        <>
          <Script id="fb-pixel-base" strategy="afterInteractive">
            {`
              !function(f,b,e,v,n,t,s)
              {if(f.fbq)return;n=f.fbq=function(){n.callMethod?
              n.callMethod.apply(n,arguments):n.queue.push(arguments)};
              if(!f._fbq)f._fbq=n;n.push=n;n.loaded=!0;n.version='2.0';
              n.queue=[];t=b.createElement(e);t.async=!0;
              t.src=v;s=b.getElementsByTagName(e)[0];
              s.parentNode.insertBefore(t,s)}(window, document,'script',
              'https://connect.facebook.net/en_US/fbevents.js');
              fbq('init', '${facebookPixelId}');
              fbq('track', 'PageView');
            `}
          </Script>
        </>
      )}
      {googleAnalyticsId && (
        <>
          <Script
            src={`https://www.googletagmanager.com/gtag/js?id=${googleAnalyticsId}`}
            strategy="afterInteractive"
          />
          <Script id="ga-base" strategy="afterInteractive">
            {`
              window.dataLayer = window.dataLayer || [];
              function gtag(){dataLayer.push(arguments);}
              gtag('js', new Date());
              gtag('config', '${googleAnalyticsId}');
            `}
          </Script>
        </>
      )}
    </>
  );
}

declare global {
  interface Window {
    fbq?: (...args: unknown[]) => void;
    gtag?: (...args: unknown[]) => void;
  }
}

export function trackAddToCart(value: number, currency = "USD") {
  window.fbq?.("track", "AddToCart", { value, currency });
  window.gtag?.("event", "add_to_cart", { value, currency });
}

export function trackInitiateCheckout(value: number, currency = "USD") {
  window.fbq?.("track", "InitiateCheckout", { value, currency });
  window.gtag?.("event", "begin_checkout", { value, currency });
}

export function trackPurchase(value: number, orderId: string, currency = "USD") {
  window.fbq?.("track", "Purchase", { value, currency, content_ids: [orderId] });
  window.gtag?.("event", "purchase", {
    transaction_id: orderId,
    value,
    currency,
  });
}
