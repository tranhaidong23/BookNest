# BookNest — ứng dụng local, Day12–14

Đã có luồng tìm sách, đánh giá1–5, gợi ý Top10, kệ muốn đọc/đang đọc/đã đọc và lịch sử20 lần trong phiên. Đây là demo local dùng session_state, **không phải tài khoản có xác thực hoặc lưu bền trong Neon**. Reload/kết thúc phiên có thể mất dữ liệu; không cam kết đồng bộ thiết bị.

## Chạy

Tại thư mục BookNest:

```powershell
.venv\Scripts\python.exe -B -m streamlit run app/main.py --server.address 127.0.0.1 --server.port 8501 --server.headless true
```

Mở http://127.0.0.1:8501. `.streamlit/config.toml` mặc định bind localhost và tắt usage telemetry. Không đổi bind sang mạng công khai. `BOOKNEST_MODE=public` cố ý dừng trước hiển thị catalogue; đây chỉ là guard triển khai, không thay auth/network isolation. Chưa deploy hoặc cấp quyền public.

App cần model Day6 đã khóa và operational metadata Day11. Không tải lại dữ liệu, không fit, không đọc test ratings khi phục vụ. `booknest/recommender.py` kiểm SHA-256 bốn arrays theo manifest Day6; catalogue kiểm manifest Day11. Artifacts thiếu/hỏng thì báo lỗi và dừng, không sinh dữ liệu giả.

## Hành vi đã có

- Catalogue có10.000 metadata cho nghiên cứu local; tìm tựa/tác giả,8 sách/trang, thứ tự popularity từ train. Chưa tìm không dấu/fuzzy, chưa phân loại genre.
- Điểm mặc định trên slider chỉ là giá trị chọn trước, **chưa phải rating**. Chỉ lưu khi bấm Lưu đánh giá. Xóa rating trả về missing, không biến thành0.
- Ít nhất3 rating để tạo gợi ý. Item-KNN K200/shrink10 giữ nguyên; loại sách đã rating kể cả rating thấp. Kệ đọc không tự biến thành rating hoặc thêm feature. Vì vậy sách chỉ lưu trên kệ vẫn có thể được gợi ý.
- Giải thích bằng mẫu từ tối đa2 support books có đóng góp dương thật. Không gọi score là xác suất/accuracy, không bịa cốt truyện hay review. Nếu không có bằng chứng dương cho candidate, fallback popularity và ghi rõ.
- Lịch sử lưu snapshot profile và kết quả; sửa rating làm vô hiệu kết quả hiện tại nhưng không viết lại lịch sử. Tối đa20 runs trong phiên.
- Bìa SVG tự tạo, không tải cover ngoài. Toàn bộ mô tả dùng “Chưa có mô tả được xác minh”; không đưa raw descriptions hoặc6 đoạn Wikipedia chưa duyệt ra giao diện. Metadata local vẫn chưa được duyệt public.

## Bằng chứng kiểm

47 Python tests đạt tại mốc triển khai, gồm5 tests mới cho profile hợp lệ/evidence, AppTest luồng rating/kệ/recommendation/history, empty search, hai session riêng và public mode dừng trước catalogue. [AppTest](https://docs.streamlit.io/develop/api-reference/app-testing/st.testing.v1.apptest) mô phỏng Streamlit, không thay kiểm trình duyệt hay chứng minh auth.

`scripts/verify_serving.py` đối chiếu đủ5.342 hồ sơ cold-validation5: Top10 và quyết định fallback khớp toàn bộ output Day6 đã khóa hash. Chỉ xác minh chuyển engine sang serving, không tuning hoặc mở test thêm. [Bằng chứng](../reports/day12_14/local_app_20261123/serving_validation.json).

HTTP local đã trả200 trong lượt trước. Browser host tích hợp không khả dụng; Computer Use Windows dừng vì không xác định chắc URL Chrome để áp dụng policy. Không có screenshot hoặc bằng chứng visual/responsive QA. Không thay thế bằng tuyên bố giao diện đã đẹp/đã kiểm mobile.

## Còn phải làm

Đã có chế độ tài khoản riêng `BOOKNEST_MODE=postgres`, gọi `app/account.py`, repository và bootstrap identity. 63 Python tests và11 UI/native database checks đạt: [báo cáo](../reports/day12_14/account_ui_20261123/summary.md). Chế độ này chỉ hiển thị public_catalogue, không dùng fallback metadata nghiên cứu. Cần secrets phía server đầy đủ; thiếu cấu hình sẽ dừng trước catalogue. Không có thông tin đăng nhập mặc định. Chế độ `local` mô tả ở trên vẫn session-only.

Còn OIDC provider thực tế, Neon/pool/hai tài khoản thật, duyệt quyền catalogue và visual/mobile QA. Kiểm UI local dùng identity fixtures và database thật, không chứng minh luồng đăng nhập bên ngoài. Không đánh dấu toàn bộ Day12–14 production hoàn tất chỉ vì kiểm tra local đạt.
