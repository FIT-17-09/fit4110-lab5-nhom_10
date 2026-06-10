# Service Boundary - AI Vision Service (A4)

## 1. Thong tin chung

| Thuoc tinh | Mo ta |
|------------|-------|
| **Service Name** | AI Vision Service |
| **Product** | Product A |
| **Nhom** | A4 |
| **Version** | 1.0.0 |
| **Technology** | Python + FastAPI + YOLOv8/Ultralytics |

---

## 2. Vai tro trong he thong

AI Vision Service chiu tra nhiem phan tich hinh anh bang AI, phat hien doi tuong nhu nguoi, xe, vat the trong hinh anh tu Camera Stream gui sang.

```
┌─────────────────────────────────────────────────────────────────────┐
│                    Smart Campus Operations Platform                    │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│   ┌──────────────┐      ┌──────────────────────┐                    │
│   │ Camera IP    │─────▶│ Camera Stream (A2)   │                    │
│   └──────────────┘      └──────────┬───────────┘                    │
│                                     │                                │
│                                     ▼                                │
│                           ┌──────────────────────┐                   │
│                           │  AI Vision (A4)      │◀── Nhom 10       │
│                           │  - YOLO/Ultralytics  │                   │
│                           │  - Object detection  │                   │
│                           └──────────┬───────────┘                   │
│                                      │                               │
│           ┌──────────────────────────┼────────────────────────────┐  │
│           │                          │                            │  │
│           ▼                          ▼                            ▼  │
│   ┌──────────────┐          ┌──────────────┐           ┌─────────┐ │
│   │ Core Business│          │ Analytics    │           │ Notifi- │ │
│   │ (A6)         │          │ (A5)         │           │ cation  │ │
│   └──────────────┘          └──────────────┘           │ (A7)    │ │
│                                                          └─────────┘ │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 3. Service Boundary

### 3.1 Input (Nhan tu)

| Nguon | Loai du lieu | Mo ta |
|-------|-------------|-------|
| **Camera Stream (A2)** | `ImageAnalysisRequest` | Anh/frame tu camera can phan tich |
| **Internal API** | HTTP POST | Goi trực tiếp /vision/analyze endpoint |

### 3.2 Output (Tra ve)

| Dong ho | Loai du lieu | Mo ta |
|---------|-------------|-------|
| **Camera Stream (A2)** | `ImageAnalysisResponse` | Ket qua phat hien doi tuong |
| **Core Business (A6)** | `ImageAnalysisResponse` | Chuyen ket qua de ra quyet dinh |
| **Analytics (A5)** | `VisionStats` | Thong ke phan tich |

### 3.3 Upstream (Goi den)

| Service | Protocol | Muc dich |
|---------|----------|----------|
| Khong co upstream | - | AI Vision la service chi nhan, khong goi service khac |

### 3.4 Downstream (Goi toi)

| Service | Protocol | Muc dich |
|---------|----------|----------|
| **Core Business (A6)** | HTTP (qua event/message) | Gui ket qua phan tich de ra quyet dinh |

---

## 4. Du lieu dau vao

### 4.1 ImageAnalysisRequest

```json
{
  "camera_id": "cam-gate-01",
  "image_url": "http://example.com/frame.jpg",
  "timestamp": "2026-05-02T09:10:00+07:00"
}
```

### 4.2 Dac diem

- **camera_id**: ID cua camera gui anh (bat buoc)
- **image_url**: URL cua anh can phan tich (hoac image_data base64)
- **timestamp**: Thoi diem chup anh (bat buoc)

---

## 5. Du lieu dau ra

### 5.1 ImageAnalysisResponse

```json
{
  "detected": true,
  "objects": [
    {
      "object": "person",
      "confidence": 0.91,
      "bbox": [100, 50, 200, 300]
    }
  ],
  "risk_level": "medium",
  "alert_triggered": false,
  "processing_time_ms": 150,
  "model_version": "yolov8n",
  "timestamp": "2026-05-02T09:10:01+07:00"
}
```

### 5.2 Dac diem

- **detected**: Co phat hien doi tuong khong
- **objects**: Danh sach doi tuong phat hien
- **risk_level**: Muc do rui ro (low/medium/high/critical)
- **alert_triggered**: Co can tao canh bao khong
- **processing_time_ms**: Thoi gian xu ly

---

## 6. Risk Level Logic

| So luong doi tuong | Loai doi tuong | Risk Level |
|-------------------|---------------|------------|
| 0 | - | low |
| 1-3 | person, bicycle, car | low |
| 4+ | person | medium |
| 1+ | unknown/not_in_list | high |
| 10+ | - | critical |

---

## 7. Endpoint Catalog

| Method | Endpoint | Mo ta | Auth |
|--------|----------|-------|------|
| GET | `/health` | Kiem tra trang thai | Khong |
| POST | `/vision/analyze` | Phan tich mot anh | Bearer Token |
| POST | `/vision/batch` | Phan tich nhieu anh | Bearer Token |
| GET | `/vision/objects` | Lay danh sach doi tuong ho tro | Khong |
| GET | `/vision/stats` | Lay thong ke phan tich | Bearer Token |

---

## 8. Du lieu quan ly (Data Owner)

| Du lieu | Loai | Muc dich |
|---------|------|---------|
| Analysis history | In-memory/Redis | Luu lich su phan tich |
| Vision stats | In-memory | Thong ke tong hop |
| Supported objects | Config | Danh sach doi tuong ho tro |

---

## 9. Loi va Xu ly

| Loi | HTTP Status | Xu ly |
|-----|-------------|-------|
| Invalid request | 400 | Tra ve ProblemDetails |
| Missing auth | 401 | Tra ve Unauthorized |
| Image fetch failed | 500 | Tra ve error + fallback response |
| Model load failed | 500 | Tra ve error + restart hint |

---

## 10. Ghi chu trien khai

- AI Vision chay port 8000
- Su dung YOLOv8n (nhanh, nhe) cho mock hoac production
- Neu khong co GPU, su dung mock AI response
- Luu y khi ket noi voi Camera Stream - can cung ten truong

---

## 11. Revision History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2026-06-10 | Initial version |
