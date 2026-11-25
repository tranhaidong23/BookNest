# Day12–14 — UI tài khoản nối PostgreSQL local

Ngày 23/11/2026. Đã thêm `BOOKNEST_MODE=postgres` vào entrypoint, UI tài khoản trong `app/account.py` và dịch vụ gợi ý có lọc quyền trong `booknest/account_service.py`. Chế độ local cũ vẫn là demo theo phiên; chế độ tài khoản thiếu secrets thì dừng trước khi đọc catalogue.

## Kết quả đã kiểm

- `python -B -m unittest discover -s tests`: **63 tests đạt**.
- `scripts/verify_account_ui.py`: **11 kiểm tra UI/database đạt**, dùng Streamlit AppTest với repository thật và PostgreSQL 18.6, cluster tạm SCRAM đã dừng/dọn. [Chi tiết và SHA-256](validation.json).
- Các luồng: ghi rating/kệ, tạo và lưu nguyên tử 10 gợi ý cùng snapshot, tải lại từ phiên UI mới, cách ly hai tài khoản, sửa tên riêng, xóa lịch sử/cascade.
- Khi rút quyền metadata, UI không phát lại tựa sách từ explanation cũ; người dùng vẫn xóa được dữ liệu cá nhân gắn với sách bị ẩn. Catalogue rỗng không chuyển sang metadata nghiên cứu.

## Quyết định và ý nghĩa

Danh sách ứng viên của chế độ tài khoản chỉ lấy từ `public_catalogue`. Engine KNN và dữ liệu train giữ nguyên; tập ứng viên sản phẩm có thể nhỏ hơn benchmark, vì vậy **không gán NDCG/Recall Day10 cho catalogue đã lọc**. Khi không có ứng viên được duyệt, trả danh sách rỗng và không lưu một run giả.

Lịch sử giữ snapshot rating nhưng giải thích được dựng lại từ cạnh mô hình và các tựa hiện còn được phép hiển thị. Không dùng chuỗi explanation đã lưu để vượt cổng quyền sau khi metadata bị rút. Kiểm tra dùng một chuỗi bí mật giả lập trong database để xác nhận UI không phát lại nó.

## Giới hạn

Danh tính được tiêm qua dependency injection trong kiểm tra UI; đây không phải đăng nhập OIDC thật. Broker/claims đã có kiểm tra riêng ở mốc trước. Chưa kiểm redirect, cookie, logout qua provider, browser/mobile, Neon hoặc pooling. Không có metadata thực nào được tự duyệt; dữ liệu approved trong kiểm tra là fixture tổng hợp, tự dọn cùng cluster. Chưa gọi toàn Day12–14 hoặc sản phẩm public hoàn tất.

Không fit/tuning hoặc đọc lại test để chọn cấu hình; không thay raw/catalogue/split/model. Không commit, push, deploy hoặc sửa ScoutIQ. Tiếp các phần local của Day15: quy trình nội dung có nguồn, trạng thái duyệt và bằng chứng quyền.
