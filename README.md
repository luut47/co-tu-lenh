

Game Cờ Tư Lệnh được viết bằng Python và Pygame.


## 1. Yêu cầu

- Python 3.10 trở lên
- Có `pip`
- Máy tính hỗ trợ giao diện để chạy `pygame`

Khuyến nghị:

- Windows 10/11
- Nếu dùng macOS hoặc Linux, cần cài Python 3 và cho phép chạy ứng dụng có cửa sổ đồ hoạ

## 2. Cần copy những gì sang máy khác

Chỉ cần copy source code của thư mục `co-tu-lenh2`.

Nên giữ các thư mục và file sau:

- `assets/`
- `config/`
- `core/`
- `services/`
- `ui/`
- `main.py`
- `requirements.txt`
- `achievements.json`

Không nên copy:

- `.venv/`
- `__pycache__/`
- `.idea/`

Nếu copy cả project bằng USB, Drive hoặc Git, sau khi sang máy mới hãy tạo lại môi trường ảo và cài lại thư viện.

## 3. Cài đặt trên máy mới

Mở terminal tại thư mục `co-tu-lenh2`, sau đó làm theo các bước bên dưới.

### Windows PowerShell

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python main.py
```

Nếu PowerShell báo lỗi không cho phép chạy script, dùng tạm:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

Sau đó kích hoạt lại:

```powershell
.venv\Scripts\Activate.ps1
```

### Windows CMD

```cmd
python -m venv .venv
.venv\Scripts\activate.bat
pip install -r requirements.txt
python main.py
```

### macOS / Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python main.py
```

## 4. Thư viện cần cài

Project hiện tại dùng:

```txt
pygame
```

Lệnh:

```bash
pip install -r requirements.txt
```

## 5. Cách chạy game

Sau khi cài đặt xong, từ thư mục gốc project chạy:

```bash
python main.py
```

Game sẽ mở cửa sổ Pygame và vào màn hình chính.

## 6. Nếu máy khác không chạy được

Kiểm tra lần lượt:

1. Đã cài Python chưa:

```bash
python --version
```

2. Đã kích hoạt môi trường ảo chưa.

3. Đã cài thư viện chưa:

```bash
pip show pygame
```

4. Đang chạy lệnh trong đúng thư mục `co-tu-lenh2` chưa.

5. Thư mục `assets/` còn đầy đủ hình ảnh và âm thanh không.

## 7. Lưu ý dữ liệu

- Thành tích người chơi được lưu trong `achievements.json`
- Nếu muốn giữ lại dữ liệu thành tích khi chuyển sang máy khác, hãy copy file này cùng với source code
- Nếu xoá file này, game có thể tạo lại file mới

## 8. Cấu trúc ngắn gọn

```text
co-tu-lenh2/
|-- assets/
|-- config/
|-- core/
|-- services/
|-- ui/
|-- achievements.json
|-- main.py
|-- requirements.txt
`-- README.md
```

## 9. Lệnh nhanh để gửi cho người khác

Nếu máy khác đã cài sẵn Python, chỉ cần:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python main.py
```

Hoặc trên macOS / Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python main.py
```