# BookNest

## Hiện hành 25/11/2026 — readiness local

Kiểm tra môi trường và 130 mục hash Day10 đạt; 68 Python tests vừa chạy đạt. Xem reports/day16_17/readiness_20261125/summary.md và docs/REPRODUCIBILITY.md. Chưa dựng môi trường sạch, replay metrics hoặc kiểm DB/browser mới. Tiếp Day18–19 báo cáo/slide; không tuning test/cloud/commit/push/deploy/ScoutIQ. Các mốc dưới là lịch sử.

**Cập nhật restore23/11:** [Backup/restore local](reports/day16_17/restore_20261123/summary.md) qua9 checks, giữ dữ liệu/RLS/grants và cách ly hai identities. Chỉ database khác trong cùng cluster tạm; chưa cross-cluster hoặc Neon. Các mốc dưới là lịch sử.

**Cập nhật hiệu năng23/11:** [Day16–17 local](reports/day16_17/local_performance_20261123/summary.md) đã giảm tải catalogue10.000sách từ101 xuống1connection, median quan sát76,92ms;68 tests và11 UI/DB hồi quy đạt. Không phải số đo Render/Neon. [Vận hành local](docs/LOCAL_OPERATIONS.md). Các mốc dưới là lịch sử.

**Cập nhật Day15 local23/11:** [Công cụ kiểm nguồn/bản nháp](reports/day15/content_local_20261123/summary.md),68 Python tests và8 kiểm tra cổng nội dung PostgreSQL đạt. Chưa gọi AI hoặc duyệt mô tả thực; bản nháp luôn chờ người kiểm. Các mốc dưới là lịch sử.

**Cập nhật UI tài khoản 23/11:** [PostgreSQL UI](reports/day12_14/account_ui_20261123/summary.md) đã nối lưu rating/kệ/history,63 Python tests và11 native/AppTest checks đạt. Chế độ tài khoản chỉ dùng catalogue được duyệt; chưa OIDC thực tế/Neon/browser QA. Demo local vẫn dùng session. Các mốc dưới là lịch sử.

**Cập nhật auth23/11:** [Identity broker/policy](reports/day12_14/identity_20261123/summary.md) có59 Python tests,8native integration checks; chưa OIDC exchange hoặc UI wiring. [Thiết kế](docs/AUTHENTICATION.md). Các mốc dưới là lịch sử.

**Cập nhật backend23/11:** [PostgreSQL repository](reports/day12_14/postgres_repository_20261123/summary.md) đã qua16 integration checks;51 Python tests đạt. UI vẫn session-only, chưa nối auth/database hoặc Neon. Các mốc dưới là lịch sử.

**Hiện hành23/11/2026:** [App local đã có luồng chính](reports/day12_14/local_app_20261123/summary.md),47 Python tests và serving parity5.342profiles đạt; [cách chạy](docs/LOCAL_DEMO.md). [PostgreSQL native local](reports/day11/native_postgres_20261123/summary.md) đã kiểm SCRAM/RLS/transaction reset. Chưa auth/persistence nối app, Neon hoặc visual QA; đây chưa là sản phẩm public. Các mốc dưới là lịch sử.

**Hiện hành 23/11/2026:** [Day10 test hoàn tất](reports/day10/final_20261123/summary.md): KNN cold5 NDCG0,462428 so popularity0,248938;42 Python tests và audit độc lập đạt. [Day11 schema local](reports/day11/schema_local_20261123/summary.md):24 PostgreSQL checks,10.000 metadata readback khớp; chưa Neon/auth/cloud. Tiếp ứng dụng local theo yêu cầu tiếp tục nhiều mốc. Các mốc dưới là lịch sử.

**Hiện hành Day8–9, 23/11/2026:** [MF và validation đã hoàn tất](reports/day08_09/mf_20261123/summary.md), 40 tests đạt và kiểm độc lập selected cold5. MF16/lambda10 NDCG@10 0,097247, thua popularity0,255947 và Item-KNN0,471873. Bước tiếp Day10 khóa cấu hình và đánh giá cuối; chưa đọc/evaluate test. Các mốc dưới là lịch sử.

**Hiện hành Day6–7, 23/11/2026:** [Item-KNN validation đã hoàn tất](reports/day06_07/item_knn_20261123/summary.md), 35 tests đạt và kiểm độc lập selected cold5. K200/shrink10 đạt NDCG@10 0,471873 so popularity 0,255947; coverage 49,79%. Chưa test performance/MF. Bước tiếp Day8–9 MF/fold-in. Các mốc dưới là lịch sử.

**Hiện hành Day5, 23/11/2026:** [baselines/validation đã chạy](reports/day05/baselines_20261123/summary.md), 30 tests đạt và kiểm độc lập cold k5. Popularity NDCG@10 0,255947, bias tốt nhất grid về ranking 0,017337; bias cải thiện RMSE so mean. Chưa đọc/evaluate test hoặc KNN/MF. Bước tiếp Day6–7 Item-KNN. Các mốc dưới là lịch sử.

**Hiện hành Day4, 20/11/2026:** [split đã tạo và khóa](reports/day04/split_20261120/summary.md), [hướng dẫn sử dụng](docs/SPLIT_USAGE.md). Train 3.863.209 ratings; cold users tách biệt; 24 tests đạt và kiểm tái tạo assignment toàn dữ liệu. Bước tiếp Day5 baselines/validation; chưa train hoặc có quality metrics. Các mốc dưới là lịch sử.

**Hiện hành Day3, 20/11/2026:** [cleaning/EDA đã thực hiện](reports/day03/preparation_v2_20261120/summary.md), [protocol v0.1](docs/EVALUATION_PROTOCOL.md) đã viết. Derived day03_v2 giữ 10.000 sách/5.976.479 ratings; 19 tests đạt. Bước tiếp Day4 tạo/kiểm split, chưa train. Raw/catalogue v1 nguyên, quyền public chưa nghiệm thu. Các mốc dưới là lịch sử.

**Hiện hành 20/11/2026:** [Day2 đã chốt phạm vi điều chỉnh](reports/day02/closure_20261120/summary.md): giữ 10.000 sách benchmark, mô tả chưa xác minh để thiếu, bìa placeholder; [policy v0.2](docs/CATALOGUE_POLICY.md). Chưa nghiệm thu public hoặc triển khai fallback. Bước tiếp là Day3 local; các mốc dưới giữ lịch sử.

**Mốc mới nhất 19/11/2026:** [pilot nguồn Wikipedia cho nhóm thiếu mô tả](reports/day02/wikipedia_gap_20261119/summary.md): 20 sách, 8 ghép work, 6 đoạn nội dung ứng viên; 14 tests đạt. Catalogue v1 giữ nguyên, chưa duyệt nội dung public hoặc toàn bộ Day2. Những số liệu dưới thuộc các mốc trước.

**Cập nhật 19/11/2026:** hoàn tất kiểm nguồn mô tả, ghép XML đủ 10.000 sách; 9.685 mô tả không rỗng (96,85%). [Kết quả, đề xuất làm sạch và giới hạn](reports/day01/descriptions_20261119/summary.md). Chưa xác minh quyền public, huấn luyện hoặc deploy.

Hệ thống gợi ý sách cá nhân hóa, giới thiệu ngắn bằng tiếng Việt có nguồn và đối chứng bằng dữ liệu thật.

## Trạng thái
Day1–10 dữ liệu/models/test hoàn tất; KNN là mô hình chính. Schema, repository và UI tài khoản đã kiểm PostgreSQL local;68 Python tests đạt. Day15 có công cụ nguồn/rubric offline; Day16–17 có đo hiệu năng/hồi quy local. Chưa provider OIDC thật, Neon/Render, visual/mobile QA hoặc nghiệm thu quyền nội dung public.

## Công nghệ dự kiến
Python 3.11, Streamlit, PostgreSQL trên Neon, hosting Render, một API AI phía server.

## Dữ liệu
Nguồn: https://github.com/zygmuntz/goodbooks-10k
Giấy phép repository công bố: CC BY-SA 4.0. Giữ attribution; kiểm tra riêng quyền hiển thị mô tả/bìa trước public deployment.
Manifest version/URL/SHA-256: [docs/DATA_MANIFEST.json](docs/DATA_MANIFEST.json).
Raw ở data/raw/goodbooks-10k, nằm trong .gitignore cùng .venv và artifacts.

## Chạy lại từ thư mục dự án (CMD)
```cmd
.venv\Scripts\python.exe scripts\collect_goodbooks.py collect
.venv\Scripts\python.exe scripts\collect_goodbooks.py audit
```
Collector tái dùng revision đã ghi, kiểm hash file cũ và từ chối ghi đè file không khớp. Chưa có backup ngoài máy.

## Tiếp theo
Day12–14 phần ứng dụng local: catalogue, hồ sơ ratings, gợi ý từ KNN đã khóa, lịch sử và muốn đọc. [Database](docs/DATABASE.md) có migration và kiểm local; chưa kết nối Neon. Test đã xem, không tuning bằng test. Quyền public vẫn theo [policy](docs/CATALOGUE_POLICY.md), không tự deploy.

## Khám phá và audit sâu (CMD/PowerShell)
```text
.venv\Scripts\python.exe -B scripts\explore_data.py
.venv\Scripts\python.exe -B scripts\audit_extended.py
.venv\Scripts\python.exe -B -m unittest discover -s tests -v
```
`audit_extended.py` hiện xuất vào mốc báo cáo `extended_20261119`; chạy lại sẽ cập nhật các file của mốc đó. Giữ bản cũ riêng nếu cần lịch sử nhiều lần chạy.
