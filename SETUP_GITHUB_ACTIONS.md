# Hướng dẫn Setup GitHub Actions - Từng bước chi tiết

## ✅ Kiểm tra dự án hiện tại

### File cần thiết (Đã có đủ):
- ✅ `main.py` - File chính chạy automation
- ✅ `requirements.txt` - Danh sách thư viện cần thiết
- ✅ `.gitignore` - Bỏ qua credentials.json, venv, logs
- ✅ `.github/workflows/automation.yml` - Workflow GitHub Actions
- ✅ `README.md` - Hướng dẫn sử dụng

### File KHÔNG cần (sẽ bị ignore):
- ❌ `run_automation.py` - Không cần, dùng `main.py` trực tiếp
- ❌ `scripts/` - Không cần cho GitHub Actions
- ❌ `credentials.json` - Không commit, dùng GitHub Secrets
- ❌ `venv/` - Không commit
- ❌ `logs/` - Không commit

---

## 📋 CÁC BƯỚC THỰC HIỆN

### BƯỚC 1: Tạo GitHub Repository

1. Đăng nhập [github.com](https://github.com)
2. Click **"+"** → **"New repository"**
3. Điền thông tin:
   - **Repository name**: `cosmetics-automation` (hoặc tên bạn muốn)
   - **Visibility**: Chọn **Public** (quan trọng để dùng free GitHub Actions)
   - **KHÔNG tích** bất kỳ checkbox nào (README, .gitignore, license)
4. Click **"Create repository"**
5. **Lưu URL repository** (ví dụ: `https://github.com/username/cosmetics-automation`)

---

### BƯỚC 2: Khởi tạo Git và commit code

Mở terminal/command prompt trong thư mục project:

```bash
# Khởi tạo Git
git init

# Kiểm tra file sẽ được commit (KHÔNG được thấy credentials.json)
git status

# Thêm tất cả file vào staging
git add .

# Commit
git commit -m "Initial commit: Cosmetics API automation"
```

**⚠️ QUAN TRỌNG:** Kiểm tra `git status` đảm bảo KHÔNG thấy:
- `credentials.json`
- `venv/`
- `logs/`
- `scripts/`
- `run_automation.py`

---

### BƯỚC 3: Push code lên GitHub

```bash
# Thêm remote repository (thay YOUR_USERNAME và YOUR_REPO)
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git

# Đổi tên branch thành main
git branch -M main

# Push lên GitHub
git push -u origin main
```

**Lưu ý:** Lần đầu push sẽ yêu cầu đăng nhập:
- **Username**: Tên GitHub của bạn
- **Password**: Dùng **Personal Access Token** (không phải password GitHub)

**Tạo Personal Access Token:**
1. GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
2. Generate new token (classic)
3. Chọn quyền: `repo` (full control)
4. Generate và copy token
5. Dùng token này làm password khi push

---

### BƯỚC 4: Thêm Google Credentials vào GitHub Secrets

1. Vào repository trên GitHub
2. Click tab **"Settings"** (menu trên cùng)
3. Click **"Secrets and variables"** → **"Actions"** (menu bên trái)
4. Click **"New repository secret"**
5. Điền:
   - **Name**: `GOOGLE_CREDENTIALS` (phải chính xác)
   - **Secret**: Mở file `credentials.json` trên máy → Copy **TOÀN BỘ** nội dung (kể cả `{` và `}`) → Paste vào đây
6. Click **"Add secret"**

**✅ Xác nhận:** Bạn sẽ thấy secret `GOOGLE_CREDENTIALS` trong danh sách (nhưng không thấy giá trị - đó là bình thường)

---

### BƯỚC 5: Test chạy workflow

1. Vào repository trên GitHub
2. Click tab **"Actions"**
3. Bạn sẽ thấy workflow **"Monthly Automation"**
4. Click vào workflow → Click nút **"Run workflow"** (dropdown) → **"Run workflow"**
5. Chờ 2-5 phút để workflow chạy xong

---

### BƯỚC 6: Kiểm tra kết quả

#### 6.1. Xem log trên GitHub:
1. Click vào workflow run vừa chạy
2. Click vào job **"update-sheets"**
3. Xem từng step:
   - ✅ "Checkout code" - Tải code
   - ✅ "Set up Python" - Cài Python 3.12
   - ✅ "Install dependencies" - Cài thư viện
   - ✅ "Setup Google credentials" - Tạo credentials.json
   - ✅ "Run automation" - Chạy `python main.py`
   - ✅ "Upload logs" - Lưu log

#### 6.2. Kết quả thành công:
- Tất cả steps có dấu ✅ xanh
- Ở step "Run automation", bạn sẽ thấy:
  ```
  ============================================================
  UPDATE GOOGLE SHEET
  ============================================================
  ✓ Opened spreadsheet: https://...
  Fetching all data from API (may take time)...
  ✓ Updated Sheet 1: XXX rows
  ✓ Updated Sheet 2: XXX rows
  ✅ Update completed!
  ```

#### 6.3. Kiểm tra Google Sheet:
- Mở Google Sheet
- Kiểm tra Sheet1_Filtered và Sheet2_AllColumns đã được cập nhật
- Kiểm tra timestamp của lần cập nhật cuối

---

## ✅ Hoàn thành!

Sau khi setup xong:

- ✅ Workflow sẽ **tự động chạy** vào **mùng 1 mỗi tháng lúc 2:00 AM UTC**
- ✅ Bạn có thể **chạy thủ công** bất cứ lúc nào từ tab Actions
- ✅ Xem **log chi tiết** trên GitHub
- ✅ **Không cần** máy tính bật 24/7
- ✅ **Hoàn toàn miễn phí** (với public repository)

---

## 🔧 Troubleshooting

### Lỗi: "credentials.json not found"
**Giải pháp:**
- Kiểm tra GitHub Secret `GOOGLE_CREDENTIALS` đã được thêm chưa
- Đảm bảo đã copy toàn bộ nội dung JSON (kể cả dấu ngoặc `{}`)
- Tên secret phải chính xác: `GOOGLE_CREDENTIALS`

### Lỗi: "Cannot open sheet"
**Giải pháp:**
- Mở file `credentials.json` trên máy
- Tìm field `client_email` (ví dụ: `xxx@xxx.iam.gserviceaccount.com`)
- Mở Google Sheet → Share → Thêm email Service Account với quyền **Editor**

### Lỗi: "Permission denied" khi push
**Giải pháp:**
- Dùng Personal Access Token thay vì password
- Hoặc setup SSH key

### Muốn thay đổi lịch chạy
**Giải pháp:**
1. Sửa file `.github/workflows/automation.yml`
2. Thay đổi dòng: `- cron: '0 2 1 * *'`
   - `0 2 1 * *` = 2:00 AM, ngày 1 mỗi tháng
   - `0 10 15 * *` = 10:00 AM, ngày 15 mỗi tháng
3. Commit và push:
   ```bash
   git add .github/workflows/automation.yml
   git commit -m "Update schedule"
   git push
   ```

---

## 📝 Checklist cuối cùng

Trước khi hoàn thành, đảm bảo:

- [ ] Code đã được push lên GitHub
- [ ] File `credentials.json` **KHÔNG** có trên GitHub (kiểm tra trên web)
- [ ] GitHub Secret `GOOGLE_CREDENTIALS` đã được thêm
- [ ] Workflow đã chạy thử thành công (có dấu ✅ xanh)
- [ ] Google Sheet đã được cập nhật
- [ ] Repository là **Public** (để dùng free GitHub Actions)

---

**Chúc bạn setup thành công! 🎉**

