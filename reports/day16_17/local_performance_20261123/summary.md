# Day16–17 — hiệu năng và hồi quy local

23/11/2026. Đã đo engine/DB bằng workload tổng hợp, sửa tải catalogue từ101 connections xuống1statement và kiểm dữ liệu bằng nhau. Không thay model/weights/split hoặc tuning sau test. [Số đo đầy đủ, môi trường và hashes](benchmark.json), [hướng dẫn vận hành](../../../docs/LOCAL_OPERATIONS.md).

| Thao tác | Số mẫu | Median | P95 mẫu |
|---|---:|---:|---:|
| Engine đã khóa, support5 | 100 | 1,34 ms | 2,57 ms |
| Engine sản phẩm, support5 | 100 | 1,87 ms | 2,89 ms |
| Catalogue10.000 hàng, cách cũ101connections | 3 | 6.445,90 ms | 7.019,26 ms |
| Catalogue10.000 hàng, snapshot1connection | 20 | 76,92 ms | 181,85 ms |
| Rating upsert, fresh connection | 20 | 51,16 ms | 74,57 ms |
| Gợi ý+lưu, catalogue đã nạp | 20 | 113,66 ms | 168,07 ms |

Model load gồm kiểm hash57,60ms; arrays24.160.000bytes, không phải tổng RSS. Profiles tổng hợp seed20261123, không phải đánh giá quality. 20 lượt lưu qua4workers/2accounts hết1.187,95ms, tạo20run IDs riêng; lịch sử đúng owner30/10 (account đầu có20runs tuần tự trước). Rút quyền được phản ánh ở snapshot kế tiếp. Fixture cluster đã dừng/dọn.

Đã chạy lại68 Python tests đạt. Kiểm hồi quy UI/native database được lưu riêng dưới ui_regression, giữ báo cáo Day12–14 cũ bất biến.

Máy làm việc không cô lập tải nền; unit tests chạy đồng thời một phần thời gian đo DB. Không suy mức cải thiện ổn định bằng tỷ số hai median, không gọi P95 ở3mẫu là SLA. Phát hiện chắc chắn là101->1connections và kết quả catalogue bằng nhau; số đo cho biết chi phí quan sát tại máy này. Không gồm OIDC, browser rendering, WAN, Neon, Render, AI hoặc tải bền vững. Chưa hai thiết bị thực/public/deploy; Day16–17 mới phần local.
