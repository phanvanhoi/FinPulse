# FinPulse — Hướng dẫn sử dụng

FinPulse là nền tảng bán hàng in ấn / print-on-demand (POD) kiểu SocPrints: tạo cửa hàng, chạy sales campaign, nhận đơn và theo dõi doanh thu.

---

## 1. Truy cập hệ thống


| Trang                   | URL (thay bằng domain/IP của bạn)             |
| ----------------------- | --------------------------------------------- |
| Trang chủ / Dashboard   | `http://YOUR_DOMAIN/`                         |
| Đăng nhập               | `http://YOUR_DOMAIN/login`                    |
| Đăng ký                 | `http://YOUR_DOMAIN/signup`                   |
| Storefront (công khai)  | `http://YOUR_DOMAIN/store/{slug-cua-hang}`    |
| Trang campaign bán hàng | `http://YOUR_DOMAIN/campaign/{slug-campaign}` |
| Kiểm tra API            | `http://YOUR_DOMAIN/health`                   |


**Lưu ý:** Vào `/` khi **chưa đăng nhập** sẽ tự chuyển sang `/login`. Sau khi đăng nhập sẽ vào **Dashboard**.

---

## 2. Bắt đầu — Tài khoản Seller

### 2.1 Đăng ký

1. Mở `/signup`
2. Nhập:
  - **Email** — email đăng nhập
  - **Password** — tối thiểu 8 ký tự
  - **Tên** — tên hiển thị
  - **Tên cửa hàng / tổ chức** — tên thương hiệu
3. Bấm **Create Account**

Hệ thống tự tạo **Organization** và **Store** (cửa hàng) cho bạn.

### 2.2 Đăng nhập

1. Mở `/login`
2. Nhập email và mật khẩu
3. Bấm **Sign In**

Nếu đã đăng nhập rồi, mở `/login` hoặc `/signup` sẽ tự chuyển về Dashboard.

---

## 3. Dashboard — Tổng quan cửa hàng

Sau khi đăng nhập, bạn vào **Dashboard** (`/`).

### 3.1 Các chỉ số chính (KPI)


| Chỉ số             | Ý nghĩa                               |
| ------------------ | ------------------------------------- |
| **Revenue**        | Doanh thu từ đơn đã thanh toán (paid) |
| **Orders**         | Tổng số đơn trong kỳ                  |
| **Units Sold**     | Số sản phẩm đã bán                    |
| **Live Campaigns** | Campaign đang chạy                    |
| **Pending Orders** | Đơn chờ thanh toán                    |
| **Avg Order**      | Giá trị đơn hàng trung bình           |


Chọn kỳ xem: **7 ngày / 30 ngày / 90 ngày**.

### 3.2 Biểu đồ

- **Revenue Trend** — doanh thu theo ngày
- **Orders by Status** — phân bố đơn: paid / pending / failed / refunded

### 3.3 Checklist (user mới)

Dashboard hiển thị checklist khi bạn chưa hoàn thành:

1. Upload logo cửa hàng
2. Publish campaign đầu tiên
3. Nhận đơn thanh toán đầu tiên

### 3.4 AI Insights

Gợi ý tự động từ dữ liệu cửa hàng (campaign draft, đơn pending, doanh thu tăng/giảm…).

- Xem nhanh trên Dashboard
- Xem đầy đủ tại **AI Insights** (`/insights`)
- Bấm **Refresh insights** để tạo gợi ý mới

### 3.5 Finance & Marketing widgets

- **Finance** — doanh thu (từ đơn hàng hoặc kế toán nếu đã kết nối) → link `/finance`
- **Marketing** — campaign đang live / dữ liệu quảng cáo (nếu có) → link `/campaigns` hoặc `/marketing`

### 3.6 Bảng dữ liệu

- **Top Campaigns** — campaign bán chạy nhất
- **Recent Orders** — đơn mới nhất, có nút **Export CSV**

### 3.7 Thao tác nhanh

- **New Campaign** — tạo campaign mới
- **View Storefront** — mở trang cửa hàng công khai

---

## 4. Thiết lập Storefront

Vào **Storefront** trong menu (`/settings/store`).

### Tab Branding

- Đặt **tên cửa hàng**
- **Upload logo**
- Copy **link storefront** dạng: `http://YOUR_DOMAIN/store/ten-cua-hang`

### Tab Domain

- Gắn **domain riêng** (vd. `shop.brand.com`)
- Làm theo hướng dẫn **DNS TXT** để verify

### Tab Tips

- Bật/tắt **tip** khi khách checkout
- Cấu hình các mức tip (%)

### Tab Tracking

- **Meta Pixel ID** — theo dõi quảng cáo Facebook/Instagram
- **Google Analytics ID** — theo dõi traffic

Hệ thống tự bắn sự kiện: AddToCart, InitiateCheckout, Purchase.

### Tab Abandoned Checkout

- Bật email nhắc **giỏ hàng bỏ quên**
- Tùy chỉnh subject/body email
- Cần cấu hình **SendGrid** trên server (xem mục 8)

---

## 5. Tạo Sales Campaign

### 5.1 Luồng tạo (3 bước)

**Campaigns** → **New Campaign** (`/campaigns/new`)


| Bước | Việc cần làm                                                                                 |
| ---- | -------------------------------------------------------------------------------------------- |
| 1    | Chọn **sản phẩm** (T-shirt, Hoodie, Mug…), đặt **giá bán**, mô tả, thời gian chạy (tuỳ chọn) |
| 2    | **Upload design** — ảnh thiết kế in lên sản phẩm                                             |
| 3    | **Publish** — campaign chuyển sang trạng thái **LIVE**                                       |


### 5.2 Quản lý campaign

Tại **Campaigns** (`/campaigns`):


| Trạng thái | Hành động                                            |
| ---------- | ---------------------------------------------------- |
| **Draft**  | Bấm **Publish** để lên sóng                          |
| **Live**   | **View** — mở trang bán; **End** — kết thúc campaign |
| Theo dõi   | Cột **Sold** — số đơn đã bán                         |


### 5.3 Link chia sẻ

```
http://YOUR_DOMAIN/campaign/{slug-campaign}
```

Slug tạo tự động từ tiêu đề (vd. `summer-tee-sale`).

Khách cũng có thể vào qua **storefront** (`/store/{slug}`) — danh sách campaign đang LIVE.

---

## 6. Luồng khách mua hàng

```
Storefront (/store/{slug})
    ↓
Chọn campaign LIVE
    ↓
Trang campaign (/campaign/{slug})
    ↓
Chọn size/variant, số lượng → Buy Now
    ↓
Nhập email, tên, địa chỉ giao hàng
    ↓
Thanh toán (Stripe hoặc mock nếu chưa cấu hình)
    ↓
Trang thành công (/checkout/success)
```

- Khi khách nhập email rồi bỏ checkout → hệ thống có thể gửi email nhắc (nếu bật Abandoned Checkout + SendGrid)
- Khi thanh toán thành công → email xác nhận đơn (nếu có SendGrid)

---

## 7. Quản lý đơn hàng

Vào **Orders** (`/orders`).


| Cột      | Mô tả                              |
| -------- | ---------------------------------- |
| Order    | Mã đơn                             |
| Campaign | Campaign nguồn                     |
| Customer | Email khách                        |
| Total    | Tổng tiền                          |
| Status   | pending / paid / failed / refunded |
| Date     | Ngày tạo                           |


**Export:**

- **Export page** — xuất đơn trên trang hiện tại
- **Export all (CSV)** — xuất toàn bộ đơn

Dashboard cũng có **Export CSV** ở bảng Recent Orders.

---

## 8. Cấu hình hệ thống (Admin / DevOps)

File cấu hình trên server: `.env` (thư mục gốc project).

### 8.1 URL bắt buộc

```env
FRONTEND_URL=http://YOUR_DOMAIN_OR_IP
BACKEND_URL=http://YOUR_DOMAIN_OR_IP
NEXT_PUBLIC_API_URL=http://YOUR_DOMAIN_OR_IP
```

Sau khi đổi `NEXT_PUBLIC_API_URL` cần **rebuild frontend**.

### 8.2 Database

```env
POSTGRES_PASSWORD=mat_khau_manh
DATABASE_URL=postgresql+asyncpg://finpulse:mat_khau@db:5432/finpulse
DATABASE_URL_SYNC=postgresql://finpulse:mat_khau@db:5432/finpulse
```

**Quan trọng:** Nếu mật khẩu có ký tự đặc biệt, phải **URL-encode** trong `DATABASE_URL`:


| Ký tự | Encode |
| ----- | ------ |
| `!`   | `%21`  |
| `@`   | `%40`  |
| `#`   | `%23`  |


### 8.3 Thanh toán — Thẻ (Visa / Mastercard / Amex) qua Stripe

**Visa không phải cổng riêng** — thẻ Visa, Mastercard, Amex được xử lý qua **Stripe Checkout**.

#### Bước 1: Tạo tài khoản Stripe

1. Đăng ký tại [https://dashboard.stripe.com](https://dashboard.stripe.com)
2. Bật **Payments** → **Checkout**
3. Lấy API keys: **Developers → API keys**

#### Bước 2: Cấu hình `.env` trên VPS

```env
STRIPE_SECRET_KEY=sk_live_...
STRIPE_WEBHOOK_SECRET=whsec_...
```

- `sk_test_...` — môi trường test (thẻ test Stripe)
- `sk_live_...` — production (thu tiền thật)

#### Bước 3: Webhook Stripe (bắt buộc cho production)

1. Stripe Dashboard → **Developers → Webhooks → Add endpoint**
2. URL: `https://YOUR_DOMAIN/api/v1/orders/webhooks/stripe`
3. Event: `checkout.session.completed`
4. Copy **Signing secret** → `STRIPE_WEBHOOK_SECRET` trong `.env`

#### Bước 4: Rebuild backend

```bash
docker compose -f docker-compose.prod.yml up -d --build backend
```

Khách checkout sẽ thấy tuỳ chọn **Credit / Debit Card (Visa, Mastercard, Amex)**.

---

### 8.4 Thanh toán PayPal

#### Bước 1: Tạo app PayPal Developer

1. Đăng ký [https://developer.paypal.com](https://developer.paypal.com)
2. **Dashboard → Apps & Credentials → Create App**
3. Copy **Client ID** và **Secret**

#### Bước 2: Cấu hình `.env`

```env
# Sandbox (test)
PAYPAL_CLIENT_ID=your_sandbox_client_id
PAYPAL_CLIENT_SECRET=your_sandbox_secret
PAYPAL_MODE=sandbox

# Production (khi go-live)
PAYPAL_MODE=live
```

#### Bước 3: Rebuild backend + migration

```bash
git pull origin master
docker compose -f docker-compose.prod.yml exec backend alembic upgrade head
docker compose -f docker-compose.prod.yml up -d --build backend
```

Khách checkout sẽ thấy tuỳ chọn **PayPal** — sau khi approve trên PayPal, đơn tự capture và chuyển sang **paid**.

#### Lưu ý PayPal

- Sandbox: dùng tài khoản test PayPal Developer để thử
- Live: app phải được PayPal duyệt trên business account
- Có thể bật **cả Stripe và PayPal** cùng lúc — khách chọn khi checkout

---

### 8.5 Không cấu hình cổng nào

Nếu thiếu cả `STRIPE_SECRET_KEY` và `PAYPAL_CLIENT_ID` → checkout chạy **mock** (chỉ dev/test, **không thu tiền thật**). Production phải cấu hình ít nhất một cổng.

### 8.6 Email SendGrid (tuỳ chọn)

```env
SENDGRID_API_KEY=SG....
FROM_EMAIL=noreply@yourdomain.com
```

Dùng cho: xác nhận đơn, abandoned cart email.

### 8.7 Performance VPS nhỏ (2GB RAM)

```env
UVICORN_WORKERS=1
```

Thêm **swap 2GB** trên VPS trước khi build frontend.

---

## 9. Lệnh vận hành thường dùng (VPS)

```bash
cd /root/FinPulse/FinPulse

# Cập nhật code
git pull

# Xem trạng thái
sudo docker compose -f docker-compose.prod.yml --env-file .env ps -a

# Deploy / khởi động
sudo docker compose -f docker-compose.prod.yml --env-file .env up -d --build

# Chỉ rebuild backend (nhanh)
sudo docker compose -f docker-compose.prod.yml --env-file .env build backend
sudo docker compose -f docker-compose.prod.yml --env-file .env up -d backend

# Logs
sudo docker compose -f docker-compose.prod.yml --env-file .env logs backend --tail=50
sudo docker compose -f docker-compose.prod.yml --env-file .env logs frontend --tail=50

# Health check
curl -s http://127.0.0.1/health
```

---

## 10. Quy trình bán hàng đầy đủ

```
1. Signup → Login
2. Storefront: logo, Pixel/GA, tips (tuỳ chọn)
3. Campaigns → New → chọn sản phẩm → upload design → Publish
4. Chia sẻ link /campaign/{slug} hoặc /store/{slug}
5. Orders: theo dõi đơn, export CSV
6. Dashboard: xem KPI, insights, biểu đồ
7. (Tuỳ chọn) Stripe + SendGrid + domain + SSL
```

---

## 11. Xử lý lỗi thường gặp


| Triệu chứng                    | Nguyên nhân                   | Cách xử lý                                           |
| ------------------------------ | ----------------------------- | ---------------------------------------------------- |
| Signup failed                  | Backend lỗi hoặc email trùng  | Xem `logs backend`; thử email khác hoặc Login        |
| 502 Bad Gateway                | Backend/frontend chưa healthy | `docker compose ps`; đợi backend healthy rồi `up -d` |
| Port 80 không vào được         | Nginx chưa chạy               | Kiểm tra `nginx` container; mở firewall port 80      |
| Campaign không hiện trên store | Chưa Publish                  | Campaign phải status **LIVE**                        |
| Không nhận email               | Chưa cấu hình SendGrid        | Thêm `SENDGRID_API_KEY` trong `.env`                 |
| Build frontend treo lâu        | VPS thiếu RAM                 | Thêm swap 2GB; chỉ rebuild backend khi không cần FE  |
| Backend unhealthy              | Lỗi code / DB / deps          | `logs backend --tail=50`; `git pull` + rebuild       |


---

## 12. Menu hệ thống


| Menu            | Chức năng                        |
| --------------- | -------------------------------- |
| **Dashboard**   | Tổng quan KPI, biểu đồ, insights |
| **Finance**     | Báo cáo tài chính (mở rộng)      |
| **Marketing**   | Hiệu suất quảng cáo (mở rộng)    |
| **AI Insights** | Gợi ý từ dữ liệu cửa hàng        |
| **Campaigns**   | Tạo / quản lý campaign           |
| **Orders**      | Danh sách đơn hàng               |
| **Storefront**  | Cấu hình cửa hàng                |
| **Connections** | Kết nối dịch vụ bên thứ 3        |


---

## 13. Liên hệ & hỗ trợ

- Repository: `https://github.com/phanvanhoi/FinPulse`
- Khi báo lỗi, gửi kèm:
  - Output `docker compose ps -a`
  - `logs backend --tail=50`
  - Mô tả bước tái hiện lỗi

---

*Cập nhật: FinPulse Commerce Dashboard — Phase 1–4*