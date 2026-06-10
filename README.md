# FIT4110 A4 - AI Vision Service

**Hoc phan:** FIT4110 - Dich vu ket noi va Cong nghe nen tang
**San pham:** Product A - Smart Campus Operations Platform
**Nhom:** A4
**Service:** AI Vision Service
**Version:** 1.0.0

---

## 1. Gioi thieu

AI Vision Service chiu tra nhiem phan tich hinh anh bang AI, phat hien doi tuong nhu nguoi, xe, vat the trong hinh anh tu Camera Stream gui sang.

### Vai tro trong he thong

```
Camera Stream (A2)  -->  AI Vision (A4)  -->  Core Business (A6)
                                    |
                                    v
                              Analytics (A5)
```

---

## 2. Thanh vien nhom

| STT | Ho ten | Ma so | Vai tro |
|-----|--------|-------|---------|
| 1 | (Ten thanh vien 1) | (MSV1) | Service Lead |
| 2 | (Ten thanh vien 2) | (MSV2) | API/Contract Owner |
| 3 | (Ten thanh vien 3) | (MSV3) | Backend Developer |
| 4 | (Ten thanh vien 4) | (MSV4) | Test & DevOps |

---

## 3. Cong nghe su dung

| Cong nghe | Mo ta |
|-----------|-------|
| Python 3.11 | Ngon ngu lap trinh chinh |
| FastAPI | Web framework |
| Uvicorn | ASGI server |
| YOLOv8/Ultralytics | AI model (mock neu khong co GPU) |
| Docker | Dong goi container |
| Postman/Newman | Kiem thu tich hop |

---

## 4. Cau truc repository

```
fit4110-lab5-nhom_10/
├── README.md                      # File nay
├── service_boundary.md            # Mo ta ranh gioi service
├── Dockerfile                    # Docker image cho AI Vision
├── docker-compose.yml            # Docker Compose stack
├── .env.example                  # Vi du cau hinh moi truong
├── requirements.txt              # Python dependencies
├── src/
│   └── ai_vision/
│       ├── __init__.py
│       └── main.py              # FastAPI application
├── contracts/
│   └── ai-vision.openapi.yaml   # OpenAPI contract
├── postman/
│   ├── collections/
│   │   └── ai-vision.postman_collection.json
│   └── environments/
│       └── ai-vision-local.postman_environment.json
├── evidence/                     # Minh chung kiem thu
│   └── ai_vision_test_report.md
└── RUN_LOCAL.md                  # Huong dan chay local
```

---

## 5. Danh sach endpoint chinh

| Method | Endpoint | Mo ta | Auth |
|--------|----------|-------|------|
| GET | `/health` | Kiem tra trang thai service | Khong |
| POST | `/vision/analyze` | Phan tich mot anh | Bearer Token |
| POST | `/vision/batch` | Phan tich nhieu anh | Bearer Token |
| GET | `/vision/objects` | Lay danh sach doi tuong ho tro | Khong |
| GET | `/vision/stats` | Lay thong ke phan tich | Bearer Token |

---

## 6. Service Upstream/Downstream

### Upstream (goi den AI Vision)
- **Camera Stream (A2)**: Gui anh/frame de phan tich

### Downstream (AI Vision goi toi)
- **Core Business (A6)**: Chuyen ket qua phan tich de ra quyet dinh

### Data Owner
- AI Vision luu tru: Analysis history, Vision stats, Supported objects

---

## 7. Cach chay local

### 7.1 Khong dung Docker

```bash
# Tao moi truong ao
python -m venv .venv

# Kich hoat moi truong
# Windows:
.venv\Scripts\activate
# Linux/Mac:
source .venv/bin/activate

# Cai dat dependencies
pip install -r requirements.txt

# Chay service
uvicorn ai_vision.main:app --app-dir src --host 0.0.0.0 --port 8000
```

### 7.2 Su dung Docker

```bash
# Build image
docker build -t ai-vision-a4:v1.0.0 .

# Chay container
docker run --rm -p 8000:8000 --env-file .env ai-vision-a4:v1.0.0
```

### 7.3 Su dung Docker Compose

```bash
# Chay stack
docker compose up -d --build

# Xem logs
docker compose logs -f ai-vision

# Dung stack
docker compose down
```

---

## 8. Kiem thu voi Postman

### 8.1 Chay Newman

```bash
# Cai dat dependencies
npm install

# Chay tests
npm run test:local
```

### 8.2 Import Postman Collection

1. Mo Postman
2. Import file `postman/collections/ai-vision.postman_collection.json`
3. Import environment `postman/environments/ai-vision-local.postman_environment.json`
4. Chon environment "AI Vision Local Environment"
5. Chay collection

---

## 9. Minh chung

- [Postman Collection](./postman/collections/ai-vision.postman_collection.json)
- [OpenAPI Contract](./contracts/ai-vision.openapi.yaml)
- [Test Report](./evidence/ai_vision_test_report.md)
- [Docker Container Log](./evidence/container_log.txt)

---

## 10. Lien he

- **Nhom:** A4
- **Service:** AI Vision
- **Product:** A
- **Hoc phan:** FIT4110 - Dich vu ket noi va Cong nghe nen tang

---

## 11. Revision History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2026-06-10 | Initial version |
