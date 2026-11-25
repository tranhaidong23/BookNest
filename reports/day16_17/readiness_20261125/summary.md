# Kiểm tra sẵn sàng local — 25/11/2026

Thêm `scripts/check_local_readiness.py` và `docs/REPRODUCIBILITY.md`. Công cụ chỉ đọc, xuất JSON ra stdout, không ghi model/manifest hoặc gọi DB/network.

## Vừa thực hiện

- Python 3.11.9; Streamlit 1.67.0, pandas 3.1.1, NumPy 2.4.6, SciPy 1.17.0, psycopg và psycopg-binary 3.3.9 khớp requirements.
- 88 mục hash khóa + 5 inputs + 32 outputs + 5 liên kết bằng chứng Day10 khớp; exit 0. Đây là số mục kiểm theo nhóm, có thể trùng file.
- `python -B -m unittest discover -s tests`: 68 tests đạt, runner báo 2,593 giây. Có cảnh báo Streamlit thiếu ScriptRunContext ở bare mode; không có test failure. Bộ tests có tính toán trên fixture nhỏ, không tái huấn luyện benchmark.
- Hướng dẫn phân biệt integrity, replay và dựng từ máy sạch; chỉ rõ các script cũ có thể ghi đè output lịch sử.

## Giới hạn

Chưa dựng environment mới, chưa khóa dependency bắc cầu, chưa kiểm toàn raw/catalogue lần này. Không tính lại metrics/Top10, không chạy lại native DB/browser/OIDC, không đổi mô hình. Các số 11 UI/native và 9 restore checks là lịch sử ngày 23/11, không phải kết quả mới.

Tiếp Day18–19: soạn báo cáo và slide từ bằng chứng đã khóa. Cloud, provider, quyền nội dung, browser/mobile và cross-cluster restore vẫn chưa nghiệm thu. Không commit/push/deploy hoặc thao tác ScoutIQ.
