# RUN_LOCAL.md - Huong dan chay AI Vision Service local

Huong dan nay giup ban clone repo sach va chay AI Vision Service tren may cua minh.

---

## Muc luc

1. [Yeu cau he thong](#1-yeu-cau-he-thong)
2. [Cach 1: Chay khong dung Docker](#2-cach-1-chay-khong-dung-docker)
3. [Cach 2: Chay voi Docker](#3-cach-2-chay-voi-docker)
4. [Cach 3: Chay voi Docker Compose](#4-cach-3-chay-voi-docker-compose)
5. [Kiem tra service](#5-kiem-tra-service)
6. [Kiem thu](#6-kiem-thu)
7. [Xoa bo cai dat](#7-xoa-bo-cai-dat)

---

## 1. Yeu cau he thong

- Python 3.11+
- Docker Desktop (neu dung Docker)
- Git
- npm (neu muon chay Newman tests)

Kiem tra phien ban:

```bash
python --version
docker --version
docker compose version
git --version
```

---

## 2. Cach 1: Chay khong dung Docker

### Buoc 1: Clone repo

```bash
git clone <repo-url>
cd fit4110-lab5-nhom_10
```

### Buoc 2: Tao moi truong ao Python

```bash
# Tao moi truong ao
python -m venv .venv

# Kich hoat moi truong
# Windows PowerShell:
.venv\Scripts\activate
# hoac
.\.venv\Scripts\activate

# Windows CMD:
.venv\Scripts\activate.bat

# Linux/Mac:
source .venv/bin/activate
```

### Buoc 3: Cai dat dependencies

```bash
pip install -r requirements.txt
```

### Buoc 4: Chay service

```bash
uvicorn ai_vision.main:app --app-dir src --host 0.0.0.0 --port 8000
```

Hoac chay voi Python:

```bash
python -m uvicorn ai_vision.main:app --app-dir src --host 0.0.0.0 --port 8000
```

### Buoc 5: Kiem tra

```bash
curl http://localhost:8000/health
```

Ket qua mong muon:

```json
{"status": "ok", "service": "ai-vision", "version": "1.0.0"}
```

---

## 3. Cach 2: Chay voi Docker

### Buoc 1: Build image

```bash
docker build -t ai-vision-a4:v1.0.0 .
```

### Buoc 2: Chay container

```bash
docker run --rm -p 8000:8000 --env-file .env ai-vision-a4:v1.0.0
```

### Buoc 3: Kiem tra

```bash
curl http://localhost:8000/health
```

---

## 4. Cach 3: Chay voi Docker Compose

### Buoc 1: Chay stack

```bash
docker compose up -d --build
```

### Buoc 2: Xem logs

```bash
docker compose logs -f
```

### Buoc 3: Dung stack

```bash
docker compose down
```

Neu muon xoa volume:

```bash
docker compose down -v
```

---

## 5. Kiem tra service

### 5.1 Health check

```bash
curl http://localhost:8000/health
```

### 5.2 Lay danh sach doi tuong ho tro

```bash
curl http://localhost:8000/vision/objects
```

### 5.3 Phan tich anh

```bash
curl -X POST http://localhost:8000/vision/analyze \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer a4-dev-token" \
  -d '{
    "camera_id": "cam-gate-01",
    "image_url": "http://example.com/frame.jpg",
    "timestamp": "2026-05-02T09:10:00+07:00"
  }'
```

### 5.4 Lay thong ke

```bash
curl http://localhost:8000/vision/stats \
  -H "Authorization: Bearer a4-dev-token"
```

---

## 6. Kiem thu

### 6.1 Cai dat Newman

```bash
npm install
```

### 6.2 Chay Newman tests

```bash
# Test local (service chay tren localhost:8000)
npm run test:local

# Test compose (service chay trong Docker Compose)
npm run test:compose
```

### 6.3 Xem bao cao

Sau khi chay Newman, bao cao se duoc tao tai:

- `reports/ai-vision-test.html` - Bao cao HTML
- `reports/ai-vision-test.xml` - Bao cao JUnit XML

---

## 7. Xoa bo cai dat

### Xoa moi truong ao Python

```bash
# Linux/Mac:
rm -rf .venv

# Windows:
rmdir /s /q .venv
```

### Xoa Docker image

```bash
docker rmi ai-vision-a4:v1.0.0
```

### Xoa node_modules

```bash
rm -rf node_modules
```

---

## Loi thuong gap

### Loi: Port 8000 da duoc su dung

Kiem tra va tat ung dung khac su dung port 8000, hoac doi port:

```bash
# Thay doi port trong .env
APP_PORT=8001
```

### Loi: Cannot connect to Docker daemon

Dam bao Docker Desktop dang chay:

```bash
# Windows:
docker info

# Neu loi, khoi dong lai Docker Desktop
```

### Loi: ImportError: No module named 'fastapi'

Kich hoat lai moi truong ao va cai dat lai dependencies:

```bash
deactivate
.venv\Scripts\activate  # hoac source .venv/bin/activate
pip install -r requirements.txt
```

---

## Minh chung

Sau khi chay thanh cong, ban se thay:

1. Service tra ve `/health` voi status "ok"
2. `/vision/objects` tra ve danh sach doi tuong
3. `/vision/analyze` tra ve ket qua phan tich
4. Newman tests pass voi tat ca cac test cases
