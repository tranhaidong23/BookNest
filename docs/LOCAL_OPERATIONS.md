# Vận hành và hiệu năng local

Mốc23/11/2026: chỉ localhost, chưa Render/Neon, chưa nghiệm thu public. [Bằng chứng đo](../reports/day16_17/local_performance_20261123/benchmark.json).

## Chạy ứng dụng

Tại thư mục BookNest, dùng `.venv\Scripts\python.exe -m streamlit run app/main.py`. `.streamlit/config.toml` bind127.0.0.1:8501, không gửi telemetry. Mặc định BOOKNEST_MODE=local là demo theo phiên và catalogue nghiên cứu; không mở cổng public. Không coi demo này là tài khoản đã đăng nhập.

BOOKNEST_MODE=postgres chọn UI tài khoản, cần OIDC và hai DSN riêng runtime/broker trong secrets phía server. DSN hiện chỉ cho loopback. Thiếu secrets thì dừng trước đọc catalogue. Chưa có cấu hình/provider thực được nghiệm thu; không chuyển host để lách cổng local. Các mode khác dừng kín.

Không ghi secrets vào báo cáo, log hoặc Git. Không dùng role owner/superuser cho ứng dụng. Thông báo lỗi repository là thông báo chung; cần điều tra local bằng loại lỗi/phạm vi thao tác, tránh in DSN hoặc nội dung cá nhân.

## Tải catalogue và quyền

`catalogue_snapshot()` đọc public_catalogue bằng một statement trong transaction của runtime. Với10.000 hàng, giảm101 kết nối xuống1 so cách phân trang cũ. Không cache catalogue dùng chung lâu dài: mỗi rerun đọc lại để phản ánh thay đổi quyền. Quyền được kiểm lại ở DB khi lưu rating/run.

Snapshot là quyền tại thời điểm truy vấn; một tab đang hiển thị không tự biến mất khi quyền bị rút sau đó. Lượt rerun kế tiếp sẽ lấy lại catalogue. Không tuyên bố cơ chế push revoke tức thì tới mọi browser. Khi chưa có metadata approved, UI hiện trạng thái rỗng; không dùng catalogue nghiên cứu làm fallback.

## Phạm vi số đo

`scripts/benchmark_local.py` đo engine trên300 profiles tổng hợp, seed20261123, support3/5/10; không đọc test để tối ưu chất lượng. Đo DB trên10.000 metadata tổng hợp approved trong cluster PostgreSQL18.6 tạm, fresh SCRAM connections. Có kiểm equality dữ liệu trước/sau thay cách đọc, rút quyền và20 lượt lưu qua4 threads/2accounts.

Các lần đo chạy trên máy làm việc Windows/Python3.11.9,12 logical CPUs. Tải nền không được cô lập; unit tests có chạy đồng thời trong một phần cửa sổ đo DB. P95 ở mẫu3/20 chỉ mô tả mẫu, không dùng làm SLA. Array bytes không phải RSS, model-load có hash nhưng có thể hưởng OS cache. Latency gợi ý+persist dùng catalogue đã nạp, không gồm OIDC/UI/networkWAN/AI. Không suy throughput bền vững hoặc cấu hình Render từ phép đo này.

## Khi có lỗi

- Artifact hash sai: dừng nạp model/catalogue, đối chiếu manifest đã khóa; không tự tái huấn luyện hay đổi manifest cho qua.
- DB không truy cập được: hiển thị lỗi chung, không chuyển sang session demo và giả là đã lưu; transaction lỗi phải rollback.
- Profile đổi khi đang tính: yêu cầu tạo gợi ý lại; không lưu run dựa trên snapshot cũ.
- Metadata bị rút: không hiển thị lại title từ explanation cũ; chủ tài khoản vẫn xóa được rating/kệ của sách bị ẩn.
- Phiên claims hết hạn: không bootstrap repository; cần đăng nhập lại. Hành vi provider/cookie thực còn cần kiểm.

## Backup/restore đã diễn tập

`scripts/verify_backup_restore.py` đã qua9 checks trên dữ liệu tổng hợp: pg_dump custom archive, pg_restore vào database trống khác trong cùng cluster tạm; toàn bộ rows/policies/RLS flags/table grants khớp, runtime owner isolation và cascade vẫn đúng. Pending catalogue/text vẫn ẩn. [Bằng chứng](../reports/day16_17/restore_20261123/summary.md). Archive và cluster đã dọn, không có file backup thực đang được giữ từ phép thử này.

Restore này cần các roles đã tồn tại; chưa diễn tập mất cả cluster/máy. Khi chuẩn bị phục hồi thực tế phải có hồ sơ role provisioning/ownership, secrets phía server và checksum backup riêng; không dùng file report JSON như backup. Chưa đặt RPO/RTO hoặc tuyên bố PITR/Neon đã sẵn sàng.

## Các cổng chưa đạt

Hai thiết bị/browser thật, OIDC redirect/logout, TLS/pooling/Neon, backup/restore khác cluster hoặc cloud, mobile/accessibility, sustained load, monitor/quota AI và deployment chưa được kiểm. Không đánh dấu Day16–17 hoàn tất. Mọi cloud/deploy cần phạm vi được người dùng cho phép; không tự tạo tài nguyên hoặc credentials. Các kiểm tra PostgreSQL native hiện tạo cluster tạm riêng rồi dừng/dọn, không sửa dịch vụ/DB hiện có.
