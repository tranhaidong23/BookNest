# BookNest — hướng dẫn dự án

## Hiện hành25/11/2026 — đã stage để review commit đầu

Mã nguồn/tài liệu đã stage local, chưa commit/push. .gitattributes * -text giữ nguyên byte cho hashes đã khóa; staged blobs đã đối chiếu local. matches.json pilot metadata giữ ngoài Git bằng ignore.70tests vừa đạt ngoài sandbox; lượt sandbox trước kẹt asyncio socketpair và đã kết thúc, không lỗi model.130mục hash Day10 đạt. reports/github_preparation ghi scope/bằng chứng; cần người dùng cho phép commit/push cụ thể. Không tự deploy/ScoutIQ.

## Hiện hành25/11/2026 — Git local đã khởi tạo

Đã git init main, origin=https://github.com/tranhaidong23/BookNest.git; chưa stage/commit/push. Git check-ignore đạt cho data/artifacts/.venv/secrets/.vscode/node_modules. docs/GITHUB_PREPARATION.md và reports/github_preparation/git_validation.json ghi phạm vi. Repo remote public; metadata trong báo cáo vẫn cần duyệt trước đưa lên, không coi scan token sạch là rights approval. Tiếp rà tập file và chuẩn bị diff review được; không commit/push/deploy/ScoutIQ khi chưa có phép.

## Chỉ đạo mới nhất 25/11/2026 — đã bật lại mục tiêu

Người dùng bật goal active sau khi cung cấp repo GitHub tranhaidong23/BookNest. Tiếp phần local, ưu tiên chuẩn bị repo và rà file theo trao đổi gần nhất; không tự commit/push/deploy hoặc sửa ScoutIQ. README đã chuẩn hóa; reports/github_preparation là inventory sơ bộ, chưa index Git/rights approval. Chỉ đạo paused bên dưới là lịch sử; không coi resume là quyền công khai dữ liệu hoặc dùng cloud.

## Chỉ đạo hiện hành 25/11/2026 — dừng tự động tiếp tục

Người dùng đã hủy lệnh “tiếp tục cho đến khi hết token tuần này”. Goal đã paused theo yêu cầu. Không tự tiếp tục roadmap hoặc chuyển giai đoạn; chờ yêu cầu cụ thể mới. Yêu cầu hiện tại chỉ báo cáo tiến độ, pipeline hiện tại và dự kiến. Chỉ đạo này thay mọi ghi chú goal active/tiếp tục nhiều mốc bên dưới; các kết quả đã làm giữ nguyên. Không commit/push/deploy hoặc sửa ScoutIQ.

## Hiện hành 25/11/2026 — readiness local

Kiểm tra môi trường và 130 mục hash Day10 đạt; 68 Python tests vừa chạy đạt. Xem reports/day16_17/readiness_20261125/summary.md và docs/REPRODUCIBILITY.md. Chưa dựng môi trường sạch, replay metrics hoặc kiểm DB/browser mới. Tiếp Day18–19 báo cáo/slide; không tuning test/cloud/commit/push/deploy/ScoutIQ. Các mốc dưới là lịch sử.

## Hiện hành 23/11/2026 — restore local

scripts/verify_backup_restore.py qua9 checks pg_dump/custom->pg_restore database trống cùng cluster tạm, toàn rows/policies/RLS flags/table grants khớp, owner isolation/pending gate/cascade đạt. reports/day16_17/restore_20261123/summary.md. Archive/cluster đã dọn; roles đã tồn tại, chưa cross-cluster/Neon/PITR. Không schema/model change;68tests là mốc trước. Tiếp báo cáo/slide và tái lập local; không cloud/commit/push/deploy/ScoutIQ. Các mốc dưới là lịch sử.

## Hiện hành 23/11/2026 — Day16–17 hiệu năng local

catalogue_snapshot() đọc public view một statement, thay101connections/10krows; parity/revocation/concurrent20runs2accounts đạt. reports/day16_17/local_performance_20261123/summary.md và docs/LOCAL_OPERATIONS.md.68 Python tests và11 UI/native regression đạt. Median catalogue76,92ms vs6445,90ms cũ, máy/tải không cô lập nên không SLA/cloud claim. Engine/hash nguyên. Chưa Render/Neon/OIDC/browser/restore; tiếp local operational restore/reproducibility và báo cáo. Không commit/push/deploy/ScoutIQ. Các mốc dưới là lịch sử.

## Hiện hành 23/11/2026 — Day15 local

content_review.py + prepare_content_review.py và docs/CONTENT_REVIEW.md có packet/hash/spans, prompt và rubric;68 Python tests,8 native content lifecycle checks đạt. reports/day15/content_local_20261123/summary.md. Chưa provider/AI quality/rights approval thực; structural pass không là semantic accuracy, output luôn pending. Day12–14 UI account đã có nhưng OIDC/Neon/browser còn thiếu. Tiếp Day16–17 phần local hiệu năng/operational checks, không deploy/cloud hoặc tuning test. Các mốc dưới là lịch sử.

## Hiện hành 23/11/2026 — UI tài khoản PostgreSQL

app/account.py đã nối repository qua BOOKNEST_MODE=postgres;63 Python tests và11 AppTest/native PostgreSQL checks đạt. reports/day12_14/account_ui_20261123/summary.md. Candidate chỉ public_catalogue; metadata bị rút không lộ qua history/explanation, vẫn xóa được personal data. Thiếu secrets dừng kín. Identity injection trong UI test, chưa OIDC thật/browser/Neon. Không áp metrics benchmark cho candidate catalogue đã lọc. Tiếp Day15 nguồn/quyền local; không tự duyệt metadata hoặc cloud. Các mốc dưới là lịch sử; giới hạn commit/push/deploy/ScoutIQ giữ nguyên.

## Hiện hành 23/11/2026 — identity policy/broker

booknest/identity.py + auth_backend.py và migration003 đã có;59 Python tests và8native broker integration checks đạt. docs/AUTHENTICATION.md, reports/day12_14/identity_20261123/summary.md. Claims chỉ từ st.user đã được framework xác minh, issuer/sub làm khóa; broker role riêng, contextlocal, duplicate/concurrency-safe; DB bootstrap chỉloopback. Chưa provider login/cookie/logout/Neon hoặc UI wiring. Tiếp UI/accountintegration với publicmetadata gate, không gọi synthetic claims là OIDC verified. Các mốc trước là lịch sử; giới hạn cloud/commit/push/deploy/ScoutIQ giữ nguyên.

## Hiện hành 23/11/2026 — PostgreSQL repository

booknest/repository.py đã có persistence profile/ratings/shelf/search/run-history với connection runtime fresh, context local, advisory lock theo user, stale-profile check và atomic run/support/items. Migration002 thêm recommendation_support, không sửa001. 51 Python tests +16 native PostgreSQL18.6/Psycopg3.3.9 integration checks đạt, gồm8 concurrent writes; fixture cluster đã dừng/dọn. Xem reports/day12_14/postgres_repository_20261123/summary.md. UI vẫn session-only, chưa auth provisioning/UI adapter/Neon/pool; tiếp phần tích hợp, không gọi full Day12–14 xong. Model/test bất biến và giới hạn cloud/commit/push/deploy/ScoutIQ giữ nguyên.

## Hiện hành 23/11/2026 — app local và PostgreSQL native

Day12–14 có demo local app/main.py: catalogue/rating/KNN/kệ/history theo session, chưa auth/persistence/Neon. Xem docs/LOCAL_DEMO.md và reports/day12_14/local_app_20261123/summary.md. 47 Python tests đạt; adapter Top10/fallback khớp đủ5.342 validation profiles. Chưa visual/mobile QA: browser host thiếu, CUA Windows dừng do không xác định chắc URL; không tự tuyên bố đã kiểm giao diện. Không tiếp tục CUA khi tool yêu cầu dừng trong turn đó.

Native PostgreSQL18.6 đã kiểm trong cluster tạm riêng localhost/SCRAM: hai identities RLS, transaction context reset,5 hành động cấm và sai password đều đạt; cluster dừng/dọn sạch. Xem reports/day11/native_postgres_20261123/summary.md. Không sửa services/DB hiện có. PGlite24checks và10.000 metadata readback vẫn là bằng chứng riêng. Tiếp backend persistence/auth integration local và các phần roadmap được phép; không đổi model/test sau kết quả, không tự cloud/public/commit/push/deploy/ScoutIQ. Các mốc dưới là lịch sử.

## Hiện hành 23/11/2026 — Day10 test và Day11 local

Người dùng đã yêu cầu tiếp tục qua các mốc local, “đến khi hết token tuần này”; không xem được hạn mức tuần, không tự đặt budget. Chỉ dẫn cũ dừng sau từng ngày đã được yêu cầu mới thay thế; vẫn không commit/push/deploy, sửa ScoutIQ hoặc tự thực hiện cloud. Goal đang tiếp tục các phần local của roadmap.

Day10 hoàn tất: reports/day10/final_20261123/summary.md. Lock trước test08:10:33 UTC, mở08:10:45; test đã được xem, không còn holdout chưa mở cho tuning tương lai. Item-KNN K200/shrink10 giữ nguyên: cold5 test NDCG0,462428/Recall0,065387 so popularity0,248938/0,033484; delta NDCG0,213490 CI95%[0,205643;0,221704]. 42 Python tests; verifier toàn235.072 Top10 và independent cold5 KNN/MF5.343 users khớp. Không refit; raw/split/models nguyên.

Day11 phần local đã làm: db/migrations/001_initial.sql, docs/DATABASE.md, reports/day11/schema_local_20261123/summary.md. PGlite0.5.17 PostgreSQL nhúng:24 DB checks, đọc lại10.000 metadata fields khớp; metadata pending/public view0, không nhập benchmark users/ratings/descriptions. Chưa Neon/OIDC/pooling/cloud. Bước tiếp Day12–14 app local với engine đã khóa, fallback nội dung và ownership; không gọi demo local là nghiệm thu public/auth/cloud. Các mốc dưới là lịch sử.

## Hiện hành 23/11/2026 — Day8–9

MF/validation hoàn tất: reports/day08_09/mf_20261123/summary.md và docs/DAY08_MATRIX_FACTORIZATION.md. Grid 16/32 chiều × lambda10/50, 8 vòng ALS, biases train Day5 cố định; chọn d16_l10 theo cold5 NDCG0,097247/Recall0,012989/RMSE0,922190, thua popularity và KNN về ranking. Item-KNN K200/shrink10 vẫn dẫn đầu NDCG0,471873. 40 tests đạt; verifier độc lập selected cold5 toàn 5.342 Top10/545.103 rating predictions và 20 item equations khớp, hashes nguyên. Artifacts data/processed/day08_mf_v1; không đọc/evaluate test. Bước tiếp Day10 khóa cấu hình trước test và đánh giá cuối theo protocol, chưa bắt đầu; không tự chạy giai đoạn sau. Các mốc dưới là lịch sử.

## Hiện hành 23/11/2026 — Day6–7

Item-KNN ranking đã hoàn tất validation: reports/day06_07/item_knn_20261123/summary.md và docs/DAY06_ITEM_KNN.md. Chọn K200/shrink10 bằng cold-validation k5: NDCG 0,471873, Recall 0,066420, coverage49,79%, so popularity0,255947/0,034853/0,13%. 35 tests đạt; verifier toàn Top10 cold5 và 10 source rows/two shrinks khớp. Positive-only train graph, không đọc/evaluate test, không predict stars từ affinity. Artifacts data/processed/day06_item_knn_v1; SciPy1.17.0 thêm .venv/requirements. Bước tiếp Day8–9 MF/fold-in và validation; chưa bắt đầu, không tự chạy test hoặc giai đoạn khác. Các mốc dưới là lịch sử.

## Hiện hành 23/11/2026 — Day5

Day5 baselines/validation hoàn tất: reports/day05/baselines_20261123/summary.md, docs/DAY05_BASELINES.md. 30 tests đạt, verifier độc lập cold k5 khớp. Popularity NDCG@10 0,255947; bias lambda50 0,017337; bias10 RMSE 0,904851 vs mean 0,987718. Bias50 được chọn trong họ bias theo ranking, vẫn thua popularity. Artifacts data/processed/day05_baselines_v1; chỉ fit train, không đọc/evaluate test. Chưa KNN/MF; bước tiếp Day6–7 Item-KNN/validation, không tự chạy test hoặc giai đoạn khác. Các mốc dưới là lịch sử.

## Hiện hành 20/11/2026 — Day4

Split day04_split_v1 đã khóa theo protocol v0.1: 3.863.209 train ratings, 42.739 development / 5.342 cold-validation / 5.343 cold-test users. Xem reports/day04/split_20261120/summary.md và docs/SPLIT_USAGE.md. 24 tests đạt; full-data đảo input/đổi nhãn không đổi assignment; export readback đạt. Raw/Day3/catalogue nguyên. Chỉ train.csv được fit; không dùng counts toàn nguồn. Chưa models/test performance. Bước tiếp Day5 baselines và metrics validation; không tự đánh giá test hoặc chạy giai đoạn sau. Các mốc dưới là lịch sử.

## Hiện hành 20/11/2026 — Day3

Đã tạo data/processed/day03_v2: cleaning/EDA và docs/EVALUATION_PROTOCOL.md v0.1. Xem reports/day03/preparation_v2_20261120/summary.md. Giữ 10.000 sách/5.976.479 ratings; bỏ 6 tag duplicate extras, cách ly 10 dòng negative/conflict. 19 tests đạt. Derived v1 là lịch sử (5 tựa whitespace), dùng v2; catalogue_v1 Day2 vẫn bất biến. Chưa split/train: bước tiếp Day4 triển khai/kiểm split, không tự chạy models Day5. Các trạng thái dưới là lịch sử.

## Hiện hành 20/11/2026 — Day2 đã chốt phạm vi điều chỉnh

Người dùng đã xác nhận “ok chốt”: giữ 10.000 sách benchmark, cho phép sách thiếu mô tả với fallback, bìa placeholder; metadata vẫn cần đủ quyền trước public. Day2 đóng theo policy v0.2, không đồng nghĩa nghiệm thu public hoặc đã xác minh 6 đoạn Wikipedia. Xem docs/CATALOGUE_POLICY.md và reports/day02/closure_20261120/summary.md. Bước tiếp là Day3 local; tại mốc chốt chỉ cập nhật tài liệu, chưa chạy Day3. Giữ v1 nguyên, thay payload phải version mới. 14 tests là kết quả lịch sử pilot, không chạy lại tại mốc chốt. Các chỉ dẫn cũ chưa hoàn tất Day2 bên dưới là lịch sử đã được quyết định này thay thế về phạm vi, không thay thế cổng quyền public.

Mốc mới nhất: reports/day02/wikipedia_gap_20261119/summary.md. Pilot phân tầng 20 sách từ nhóm 349: 8 khớp work, 6 có đoạn nội dung ứng viên, 2 mỏng, 12 giữ chờ. Snapshot 8 revision/hash, overlay riêng; 14 tests vừa đạt. Chưa edition/public-ready; giữ v1 nguyên, chưa toàn bộ Day2 hoặc Day3. Các mốc dưới là lịch sử.

## Hiện hành 19/11/2026
Mốc mới nhất: reports/day02/catalogue_v1_20261119/summary.md. Catalogue local v1 đã khóa 10.000 sách, 11 tests mới đạt; pilot Wikipedia 3 tác phẩm có HTML/hash/revision/license. Chưa final catalogue sản phẩm/quyền; không gọi toàn bộ Day2 hoàn tất. Không sửa catalogue v1 khác payload; tạo version mới nếu thay đổi. Các ghi nhận sau là lịch sử.

Mốc mới nhất: reports/day02/review_20261119/summary.md và docs/CATALOGUE_POLICY.md. Đã triage 358 hàng, 9 tests mới đạt; benchmark giữ 10.000 sách, 349 mô tả còn cần nguồn/xác minh. 9.651 ứng viên text chưa được duyệt nội dung/quyền. Chưa catalogue public, chưa Day3/training. Các trạng thái sau giữ làm lịch sử.

Ưu tiên trạng thái mới trong docs/HANDOFF.md và docs/PROJECT_PLAN.md. Day2 feasibility: đã kiểm XML/mô tả ở lượt trước (96,85% có text toàn catalogue, 7 tests lịch sử); lượt đối chiếu mới chỉ kiểm lại 20 XML local và hashes, không chạy lại tests/full audit. Catalogue và quyền public chưa chốt. Xem reports/day02/feasibility_20261119/summary.md. Đoạn dưới giữ làm lịch sử audit.

Người dùng đã yêu cầu tự thực hiện và báo cáo như trước; cho phép công việc local cần thiết. Tiếp tục theo HANDOFF và reports/day01/extended_20261119/summary.md. Audit sâu đã xong: 4 tests đạt, raw nguyên; chưa mô hình/quality metrics. Không tự commit/push/deploy. Những ghi nhận trước giữ làm lịch sử.

Đọc README.md, docs/HANDOFF.md, reports/day01/summary.md trước khi tiếp tục.
Ưu tiên dữ liệu, protocol và mô hình trước giao diện. Người dùng muốn học và được giải thích; các tác vụ tạo project/thu thập dữ liệu hiện được phép thực hiện trực tiếp.
Scope: recommender sách, giới thiệu tiếng Việt có nguồn, Neon PostgreSQL, Render public app, báo cáo và slide; deadline trình bày 21/12/2026, kế hoạch 21 ngày làm việc. Tiêu chí chấm chính thức chưa có.
Không dùng similarity làm accuracy, không tạo metrics hoặc review giả. Missing không mặc định là 0. Train/validation/test độc lập; tuning chỉ validation. Đánh giá người mới cần user-held-out protocol riêng.
Giữ raw và manifest SHA-256; không đưa datasets/secrets/.venv lên Git. Không dùng test ratings/reviews làm đặc trưng cho chính cặp kiểm thử. Goodbooks ratings CSV không có timestamp; không tuyên bố temporal evaluation hợp lệ từ thứ tự dòng.
Thông tin bìa/mô tả phải ghép đúng tác phẩm/edition và có nguồn; AI chỉ tóm lược thông tin có căn cứ. Kiểm điều kiện nguồn trước hiển thị công khai.
Không tự commit/push/deploy hoặc thay đổi ScoutIQ. ScoutIQ đã dừng tại Day20, sẽ tiếp tục bằng hướng dẫn trong phiên riêng.
Sau mỗi mốc cập nhật HANDOFF và báo cáo thực tế, phân biệt dự kiến/đã thực hiện/chưa xác minh. Không khởi chạy nhiều giai đoạn không được yêu cầu.
