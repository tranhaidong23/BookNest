# Bàn giao BookNest

## Hiện hành25/11/2026 — chuẩn bị commit đầu đã stage

Đã stage mã nguồn/tài liệu, chưa commit/push. .gitattributes * -text bảo toàn bytes, khắc phục nguy cơ autocrlf phá evaluator hashes khi clone; staged blobs khớp worktree ở lần kiểm. reports/day01/descriptions_20261119/matches.json giữ local theo ignore, README nêu file bằng chứng chi tiết không có trong clone.70unit tests vừa đạt ngoài sandbox sau chẩn đoán lần sandbox kẹt socketpair/asyncio;130hash checks Day10 đạt. Xem reports/github_preparation/publication_scope.md và verification.json. Cần xin phép commit/push trên danh sách staged cụ thể; không coi goal resume là cho phép public hoặc deploy.

## Hiện hành25/11/2026 — Git local và origin

Git local init nhánh main thành công, origin trỏ repo người dùng https://github.com/tranhaidong23/BookNest.git. Chưa stage/commit/push. Git check-ignore loại đúng7nhóm đường dẫn kiểm; inventory sơ bộ khớp Git candidates ngoài báo cáo tự loại. Xem docs/GITHUB_PREPARATION.md và reports/github_preparation/git_validation.json. Báo cáo nghiên cứu chứa metadata nên còn phải chốt phạm vi công khai; không tự coi toàn reports đã approved. Tiếp rà danh sách và diff trước xin phép commit/push, không deploy/ScoutIQ.

## Hiện hành25/11/2026 — chuẩn bị GitHub sau resume

Người dùng bật lại goal sau khi cung cấp repo public tranhaidong23/BookNest. Đã chuẩn hóa README và lưu bản cũ docs/README_HISTORY_20261125.md; loại .vscode khỏi Git; scripts/review_public_files.py tạo inventory sơ bộ, không phải Git index. Xem reports/github_preparation/summary.md. Chưa init/stage/commit/push hoặc deploy; không phê duyệt quyền metadata/nguồn. Tiếp hoàn thiện việc chuẩn bị local và rà danh sách thực trước xin phép commit/push. Các chỉ đạo paused bên dưới là lịch sử, giới hạn công khai/cloud/ScoutIQ giữ nguyên.

## Chỉ đạo hiện hành 25/11/2026 — dừng mục tiêu tự động

Người dùng đã yêu cầu dừng lệnh tiếp tục đến hết token tuần; goal chuyển paused. Không tự làm Day18–19 hoặc giai đoạn khác cho tới yêu cầu mới. Hiện chỉ báo cáo tiến độ và phân biệt pipeline đã có/dự kiến. Các câu “tiếp Day18–19” hoặc “goal active” bên dưới là lịch sử, không còn là lệnh thực thi. Kết quả mới nhất: readiness local25/11,68tests/130mục hash đạt với giới hạn đã nêu; Day10 hoàn tất, Day11–17 chỉ hoàn thành từng phần local.

## Hiện hành 25/11/2026 — readiness local

Kiểm tra môi trường và 130 mục hash Day10 đạt; 68 Python tests vừa chạy đạt. Xem reports/day16_17/readiness_20261125/summary.md và docs/REPRODUCIBILITY.md. Chưa dựng môi trường sạch, replay metrics hoặc kiểm DB/browser mới. Tiếp Day18–19 báo cáo/slide; không tuning test/cloud/commit/push/deploy/ScoutIQ. Các mốc dưới là lịch sử.

## Rà soát theo yêu cầu — Day10 đã chốt ngày23/11/2026

Người dùng yêu cầu quay lại làm nốt Day10. [Closure](../reports/day10/closure_20261123/summary.md) và integrity.json xác nhận88locked hashes,5inputs,32outputs,metrics/evaluator/audit evidence đều khớp;lock trước test. Day10 hoàn tất theo protocol, không phát hiện phần thiếu cần fit/tuning/chạy lại test. Lượt này chỉ kiểm integrity, không gọi là rerun235.072Top10 hoặc chạy lại42tests lịch sử. Không khởi chạy giai đoạn mới trong lượt rà soát; các phần ứng dụng/local đã làm bên dưới vẫn giữ nguyên.

## Hiện hành — 23/11/2026, restore local

[Báo cáo restore](../reports/day16_17/restore_20261123/summary.md): verify_backup_restore.py qua9checks, PostgreSQL18.6 custom pg_dump/pg_restore vào database mới cùng cluster tạm; exactrows/policies/RLS flags/table grants, runtime2owners/pendinggate/no-context/forbiddenrole/cascade đều đạt. Archive và cluster đã dọn. Role definitions tồn tại sẵn nên chưa cross-cluster provisioning/restore, không Neon/PITR/RPO/RTO. Không thay schema/model,68unit tests là mốc trước không chạy lại riêng cho script.

Tiếp Day18–19 báo cáo/slide có bằng chứng và các phần tái lập local. Không bỏ qua backlog thật: OIDC/provider, browser/mobile, quyền nội dung/AI semantic, Neon/Render vẫn chưa nghiệm thu và không tự làm cloud. Goal active, không commit/push/deploy/ScoutIQ. Các mốc dưới là lịch sử.

## Hiện hành — 23/11/2026, Day16–17 hiệu năng local

[Báo cáo](../reports/day16_17/local_performance_20261123/summary.md), [runbook](LOCAL_OPERATIONS.md). Thêm repository.catalogue_snapshot() và account_service gọi một truy vấn public view;10krow equality với cách cũ đạt,101->1connection. Median76,92ms vs6445,90ms, số đo local không cô lập (unit tests chạy đồng thời một phần), không SLA. Product engine support5 median1,87ms;20concurrent saves4threads2accounts đúng20unique runs vàowner counts. Modelhash nguyên, không test-data tuning.

68 Python tests đạt,11 UI/native regression chạy lại đạt ở report/ui_regression, cluster dừng/dọn. Historical reports không ghi đè. Một statement snapshot tránh pagination drift nhưng không push-revoke tới tab đã render; rerun mới đọc quyền lại. Chưa OIDC/Neon/Render/mobile/browser/backuprestore. Tiếp operational restore/reproducibility local rồi báo cáo/slide; không commit/push/deploy/ScoutIQ. Các mốc dưới là lịch sử.

## Hiện hành — 23/11/2026, Day15 công cụ nội dung local

[Báo cáo](../reports/day15/content_local_20261123/summary.md), [quy trình](CONTENT_REVIEW.md). booknest/content_review.py kiểm packet hash/offset/reference, build prompt riêng system/data và kiểm draft schema; mọi output pending, không semantic/rights approval. CLI prepare_content_review.py chỉ tạo file mới data/dev, không API/DB write. 68 Python tests đạt;8 PostgreSQL content lifecycle checks đạt, cluster dọn. Tests có trường hợp câu bịa dẫn ID hợp lệ để chứng minh giới hạn structural checks. Chưa chạy AI thật/chấm nội dung/quyền thực, không coi full Day15 xong.

Tiếp Day16–17 local hiệu năng và operational checks; cloud/deploy/provider auth/browser QA vẫn chưa thực hiện. UI account integration mốc trước đạt11 checks, chưa OIDC. Giữ model/test/raw/catalogue bất biến; không tự commit/push/deploy/ScoutIQ. Goal vẫn tiếp tục, hạn mức token tuần không quan sát được. Các mốc dưới là lịch sử.

## Hiện hành — 23/11/2026, UI tài khoản nối database

[Báo cáo](../reports/day12_14/account_ui_20261123/summary.md): app/account.py + account_service.py nối runtime repository; entrypoint BOOKNEST_MODE=postgres, thiếu cấu hình dừng kín. 63 Python tests và11 UI/native PostgreSQL checks đạt, cluster tạm dọn sạch. Kiểm persistence qua phiên mới, hai identities cách ly, snapshot/CRUD, rút metadata không phát lại title/explanation và vẫn xóa được personal data. UI test tiêm identities, chưa chứng minh OIDC/provider/browser/Neon. Public catalogue thực vẫn chưa có metadata được duyệt; không tự cấp quyền từ fixture.

Candidate chỉ catalogue được duyệt; không gọi metrics Day10 là chất lượng của tập ứng viên mới. Model/benchmark vẫn nguyên. Session demo local giữ nguyên. Tiếp Day15 quy trình nội dung, nguồn/quyền và báo cáo local; chưa full Day12–14 production. Người dùng cho tiếp nhiều mốc local, không commit/push/deploy/cloud/ScoutIQ. Các mốc dưới là lịch sử.

## Hiện hành — 23/11/2026, identity broker chuẩn bị

[Auth design](AUTHENTICATION.md), [báo cáo](../reports/day12_14/identity_20261123/summary.md). booknest/identity.py kiểm st.user đã được framework xác minh: loggedin/issuer/sub/aud/azp/exp/iat/nbf và maxage8h; không decode JWT tự tin, không email-as-ID. Migration003 role identity_broker riêng SELECTlimited/INSERT app_users, RLS transaction issuer/sub; không personal data hoặc UPDATE/DELETE. resolve_identity concurrent insert-or-read UUID, không ghi đè app displayname.

booknest/auth_backend.py bootstrap claims rồi broker->runtime repository, AccountConfig repr ẩn DSNs, DB factory chỉ explicit loopback, pinhostaddr/rejectremote/service. Chưa UI wiring/OIDC provider/auth cookie/Neon. 59 Python tests đạt; scripts/verify_identity.py qua8nativechecks gồm8concurrent first-login calls,3 synthetic accounts, crossissuer separate/contextreset/6forbiddenactions. Fixture cluster dừng/dọn. Bằng chứng validation.json, không gọi claims fixtures là OIDC thực tế.

Tiếp nối UI/account backend; cần candidate gate metadata approved (hiện publicview0) và giải thích không lộ tựa sách đã bị rút quyền. Giữ sessiondemo local nguyên và rõ nhãn cho tới khi UI backend path được kiểm. Không tự cloud/keys/commit/push/deploy/ScoutIQ hoặc tuningtest. Các mốc dưới là lịch sử.

## Hiện hành — 23/11/2026, PostgreSQL repository

[Báo cáo backend](../reports/day12_14/postgres_repository_20261123/summary.md). booknest/repository.py dùng Psycopg[binary]3.3.9 mới pin requirements. Repository bind UUID đã được backend xác minh; chưa tự auth/provision identity. Mỗi method connection runtime mới, transaction context local, kiểm rejectowner/super/bypass/elevated role, advisory lock theo user; parameterized SQL và generic DB errors. CRUD ratings/shelf/display name, public search, atomic save run/support/items, history/delete. Reject stale profile nếu ratings đổi trong lúc tính gợi ý.

db/migrations/002_recommendation_support.sql thêm snapshot với RLS/compositeFK, noUPDATEgrant;001 nguyên. scripts/local_postgres_fixture.py dùngcluster tạm/SCRAM/localhost/fresh runtime connection; scripts/verify_repository.py đã qua16integrationchecks (persistence/isolation/atomicrollback/8 concurrent writes/cascade/context). Cluster dừng/dọn, không DB/service khác. 51 Python tests đạt. validation.json ghi sourcehash/scope. Chưa pool/OIDC/Neon/UI wiring; app/main.py vẫn sessiondemo47-test milestone lịch sử, không lưu PostgreSQL.

Tiếp auth identity provisioning và UI/repository adapter theo phạm vi local, public metadata còn0 nên không tự xuất catalogue nghiên cứu ra public. Chưa bật remote DB hoặc yêu cầu gửi secrets qua chat. Giữ model/test bất biến; không commit/push/deploy/ScoutIQ. Các mốc dưới là lịch sử.

## Hiện hành — 23/11/2026, app local / native PostgreSQL

[Local app report](../reports/day12_14/local_app_20261123/summary.md), [hướng dẫn](LOCAL_DEMO.md). app/main.py đã thay khung: catalogue search/paging8, rating chỉ lưu khi bấm, KNN Top10/evidence thật, kệ3trạng thái, history20snapshot. State theo session, chưa auth/login/persistence/Neon. Public mode dừng trước catalogue; launch127.0.0.1, telemetry off. Metadata chưa quyền public, toàn descriptions fallback, SVG cover do dự án tạo.

47 Python tests đạt gồm5 serving/AppTest checks; tests/test_app_local.py kiểm searchempty, save3ratings/shelf/recs/history, hai sessions, publicguard. scripts/verify_serving.py đã đối chiếu đủ5.342 cold-validation5 Top10/fallback với artifact Day6, không test-data read. Model arrays/catalogue hash kiểm khi load; không fit/tuning. reports/day12_14/local_app_20261123/implementation.json ghi source hashes và phạm vi kiểm.

Lượt trước Streamlit session85808 chạy127.0.0.1:8501 và HTTP200; phải kiểm lại handle/process trước khi suy còn chạy. Chưa visual/mobile QA: IAB browser host không khả dụng; CUA getApp Chrome bị dừng vì không xác định URL chắc để enforce policy. Đã báo người dùng và kết thúc CUA theo tool; không có screenshot. Không gọi AppTest là browser QA hoặc session isolation là account auth.

[Native PostgreSQL bổ sung](../reports/day11/native_postgres_20261123/summary.md): binaries ở C:/Program Files/PostgreSQL/18/bin, version18.6. scripts/verify_native_postgres.py tạo cluster tạm trong data/dev, localhost/randomport/SCRAM, runtime login thật và bad password, hai UUID RLS, context reset sau COMMIT,5 hành động cấm đạt. Lượt cuối thoát0 và dừng/dọn cluster; không services/DB khác. Đã sửa pg_ctl inherited-PIPE hang bằng outputfile và finally cleanup; sandbox cần quyền chạy restricted token. Chưa Neon/TLS/pool/OIDC/concurrency. SQL migration001 nguyên.

Tiếp phần local còn thiếu: app persistence và auth integration đáng kiểm, Day15 nguồn/quyền/evidence guard, báo cáo/slide theo roadmap. Chưa gọi toàn Day12–14 production hoàn tất. Người dùng cho phép tiếp tục nhiều mốc local, goal active; không commit/push/deploy/cloud chưa phép hoặc ScoutIQ. Các mốc dưới là lịch sử.

## Hiện hành — 23/11/2026, Day10 hoàn tất / Day11 local

Người dùng cho phép tiếp tục qua các mốc local cho tới giới hạn token tuần; không quan sát được hạn mức đó. Goal active tiếp tục roadmap local, không tự dừng sau từng ngày như chỉ dẫn lịch sử; không commit/push/deploy hoặc sửa ScoutIQ, không cloud chưa được phép.

[Day10 report](../reports/day10/final_20261123/summary.md): lock08:10:33 UTC trước test access08:10:45. Item-KNN K200/shrink10 vẫn chính; cold5 test NDCG0,462428/Recall0,065387/coverage50,24%, popularity0,248938/0,033484/0,14%. NDCG delta0,213490 CI95%[0,205643;0,221704]. Cold3/10 KNN NDCG0,400849/0,542567; warm0,152072. Không refit/tuning test. Test đã mở, không được gọi là holdout chưa xem nữa. Artifacts data/processed/day10_final_v1, hashes/metrics/lock/journal/validation trong report directory.

42 Python tests đạt trước mở test. scripts/verify_day10.py đã kiểm toàn235.072 saved Top10/per-user metrics/coverage, independent cold5 KNN cộng cạnh và MF augmented least-squares cho5.343 users, MF cold5 rating aggregates; không full CLI replay hoặc independent mọi rating model/scenario. Không thay raw/catalogue/split/models.

[Day11 local report](../reports/day11/schema_local_20261123/summary.md), [database design](DATABASE.md): PostgreSQL migration với runtime/reviewer roles,5 bảng ownership RLS, public view metadata/intro/cover gates, composite FK run/user. PGlite0.5.17 dev dependency pin trong tools/db-test;24 DB checks đạt. Export metadata Day3 vào data/processed/day11_operational_v1/books.json; importer đọc lại10.000 rows mọi field khớp. Tất cả metadata pending, public view0, không copy source descriptions hoặc benchmark users/ratings. SQL/fixtures test không phải thay đổi Neon. Docker daemon không chạy; npm tải có quyền mạng sau sandbox chặn, không thay services.

Chưa Neon/OIDC/connection-pool/concurrency/backup/auth thực tế. Tiếp Day12–14 app local, giữ engine KNN đã khóa và fallback nội dung; catalogue local phải ghi rõ quyền chưa public, không dùng credentials/client UUID như danh tính tin cậy. Đã đọc Sites skill theo nhánh local-only (không registration/sync/publish) và local preview reference; giữ Streamlit hiện có app/main.py. Chưa sửa app ở mốc này. Các mốc dưới là lịch sử.

## Hiện hành — 23/11/2026, Day8–9 MF/validation

[Báo cáo](../reports/day08_09/mf_20261123/summary.md), [định nghĩa trước chạy](DAY08_MATRIX_FACTORIZATION.md). scripts/day08_mf.py fit observed-only residual MF từ train, giữ biases lambda50 Day5 cố định; 4 cấu hình dimensions16/32 × lambda10/50, 8 vòng ALS, seed20261123. Cold fold-in chỉ support, không cập nhật items. Chọn d16_l10 theo NDCG cold5; artifacts data/processed/day08_mf_v1, manifest/metrics/objective/validation/timing ở báo cáo. Không thêm dependencies.

Cold5 MF NDCG0,097247/Recall0,012989/coverage4,32%/RMSE0,922190, thua popularity NDCG0,255947 và KNN0,471873. RMSE tốt hơn bias50 nhưng kém bias10; không đổi tiêu chí chọn. Selected cold3/10 NDCG0,071277/0,128648, warm0,017805. CI validation hậu chọn, không test evidence. 40 tests đạt; verifier augmented least-squares độc lập kiểm 20 item equations và toàn 5.342 cold5 Top10/545.103 rating predictions, hashes/traces/finite factors; catalogue_v1 hash nguyên. Chưa full training CLI replay hoặc verifier độc lập mọi scenario. Không sửa raw/split/Day5/Day6.

Bước tiếp Day10: khóa danh sách/cấu hình trước khi mở test; đề xuất Item-KNN K200/shrink10 chính, popularity và MF d16/l10 đối chứng. Đánh giá 3/5/10 và warm theo protocol, không tuning trên test hoặc refit train+validation. Chưa bắt đầu Day10, chưa đọc/evaluate test; không tự chạy giai đoạn sau. Chưa AI/DB/UI/cloud, không commit/push/deploy hoặc sửa ScoutIQ; quyền public vẫn backlog. Các mốc dưới là lịch sử.

## Hiện hành — 23/11/2026, Day6–7 Item-KNN

[Báo cáo](../reports/day06_07/item_knn_20261123/summary.md), [định nghĩa trước chạy](DAY06_ITEM_KNN.md). scripts/day06_item_knn.py học graph từ 2.663.008 positive train pairs (rating>=4), cosine/shrink, min co-positive2, source neighbors K50/200, shrink10/100. Chọn s10_k200 theo cold-validation k5; score không phải số sao, chưa dùng low ratings như negative weight. Artifacts data/processed/day06_item_knn_v1; manifest/metrics/validation/timing ở báo cáo. SciPy1.17.0 cài trong .venv và pin requirements.

Cold k5 NDCG0,471873/Recall0,066420/coverage49,79% vs popularity0,255947/0,034853/0,13%; 97/5.342 fallback vẫn tính. Selected cold3/10 NDCG0,401397/0,546965; warm0,152098. Paired CI validation hậu chọn config, chưa test evidence. 35 tests đạt, verifier kiểm hashes, toàn graph structure, 10 source rows từ sets train cả hai shrink, toàn selected cold5 Top10/metrics khớp; chưa full CLI replay. Raw/catalogue/split/Day5 không sửa.

Bước tiếp Day8–9 MF có fold-in từ đúng support và validation so popularity/KNN. Không tự mở test, không tính RMSE trên affinity KNN. Chưa MF/AI/DB/UI/cloud; không commit/push/deploy hoặc sửa ScoutIQ, backlog quyền public giữ nguyên. Các mốc dưới là lịch sử.

## Hiện hành — 23/11/2026, Day5 baselines/validation

[Báo cáo Day5](../reports/day05/baselines_20261123/summary.md), [định nghĩa trước chạy](DAY05_BASELINES.md). scripts/day05_baselines.py có allowlist train/warm-validation/cold-validation support+target/catalogue; test không đọc. Models từ 3.863.209 train ratings, outputs data/processed/day05_baselines_v1; manifest/metrics/validation/timing trong reports/day05/baselines_20261123. 30 tests đạt; scripts/verify_day05.py tính lại toàn cold k5 Top10/ranking/rating từ artifacts và hashes, khớp. Chưa full CLI replay/fresh-install. NumPy 2.4.6 thêm requirements.

Cold k5: popularity NDCG 0,255947/Recall 0,034853; bias50 NDCG 0,017337; mean RMSE 0,987718; bias10/50 RMSE 0,904851/0,935507. Lambda50 thắng trong grid bias theo NDCG nhưng thua popularity; không đổi tiêu chí sang RMSE. Bias offset user không cá nhân hóa thứ tự; coverage popularity chỉ 13/10.000. Cold 3/10 và warm đã đo, bootstrap validation hậu chọn lambda có giới hạn; không test evidence.

Bước tiếp Day6–7 Item-KNN, giữ cùng split/candidates, tuning validation support5. Không dùng counts toàn Day3 hoặc test; không tự chạy test cuối. Raw/catalogue/split không sửa; chưa AI/DB/UI/cloud, không commit/push/deploy hay sửa ScoutIQ. Backlog quyền public giữ nguyên. Các mốc dưới là lịch sử.

## Hiện hành — 20/11/2026, Day4 split đã khóa

[Báo cáo Day4](../reports/day04/split_20261120/summary.md), [cách dùng split](SPLIT_USAGE.md). Dữ liệu `data/processed/day04_split_v1/`; manifest/audit/protocol snapshot ở reports/day04/split_20261120. Train 3.863.209; warm-validation/test mỗi tập 458.825; cold-validation support/target 53.420/545.103; cold-test support/target 53.430/543.667. Users 42.739 development, 5.342 cold-validation, 5.343 cold-test. Không ineligible; train có đủ 10.000 item. Mỗi cold target có 1 user không positive; giữ theo protocol, không đổi seed.

24 tests đạt; phân hoạch đủ/rời nhau, ID/nhãn nguyên, cold rời train, support lồng nhau/target chung. Full-data reverse+label perturbation cho assignment giống nhau; readback exports đạt. Chưa chạy toàn CLI replay thứ hai; validation.json ghi kiểm hashes cuối. Không sửa protocol Day3: snapshot giữ đúng hash.

Bước tiếp Day5: định nghĩa baseline/metrics, fit chỉ train.csv; tuning cold-validation support=5, giữ test cho cấu hình cuối. Không dùng book_counts/ratings toàn Day3 làm feature. Chưa fit/model metrics/AI/DB/deploy; backlog quyền public giữ nguyên, không commit/push/deploy hay sửa ScoutIQ. Các mốc dưới là lịch sử.

## Hiện hành — 20/11/2026, Day3

[Báo cáo Day3](../reports/day03/preparation_v2_20261120/summary.md), [protocol v0.1](EVALUATION_PROTOCOL.md). Dùng data/processed/day03_v2: ratings/to_read byte-identical, metadata 10.000 sách có ISBN XML/identity/hash, text chuẩn hóa chưa feature/public approval. Tags còn 999.896; bỏ 6 bản sao thừa, cách ly 4 dòng xung đột + 6 âm có source_row/reason. 316 descriptions null; 590 original_title null. Derived v1 giữ lịch sử do 5 tựa whitespace; catalogue_v1 Day2 không đổi.

19 tests vừa đạt; raw/ZIP/catalogue kiểm hash trước/sau; replay xem validation.json cùng báo cáo. EDA density 1,1187%, top100 chiếm 17,0871%. Protocol user-held-out 80/10/10, support lồng nhau 3/5/10, target chung; warm riêng, tuning validation, không temporal.

Bước tiếp Day4: tạo split, kiểm rời nhau/replay/eligibility/unseen items và khóa manifest trước baseline Day5. Chưa split/train/AI/DB/UI/deploy. Backlog quyền public và 6 đoạn Wikipedia giữ nguyên; không commit/push/deploy hoặc sửa ScoutIQ. Các mốc dưới là lịch sử.

## Hiện hành — 20/11/2026, Day2 đã chốt phạm vi điều chỉnh

Người dùng xác nhận “ok chốt” phương án [policy v0.2](CATALOGUE_POLICY.md). Giữ 10.000 sách/ratings benchmark; catalogue sản phẩm dự kiến cho phép sách thiếu mô tả nếu metadata đủ điều kiện public. Hiển thị “Chưa có mô tả được xác minh”, bìa dùng placeholder khi chưa đủ quyền. Fallback/asset chưa triển khai. Không đợi lấp 349 hàng để làm khoa học dữ liệu.

[Biên bản Day2 và backlog](../reports/day02/closure_20261120/summary.md): Day2 đóng theo phạm vi mới, chưa nghiệm thu public. Sáu đoạn Wikipedia vẫn là ứng viên cần xác minh nội dung/quyền; 9.651 text chưa duyệt. Giữ v1 và overlay nguyên; chưa cần tạo v2. Mốc này chỉ sửa tài liệu, không chạy lại tests/hash; 14 tests thuộc pilot trước.

Bước tiếp: Day3 local — cleaning/derived, EDA, protocol/split tái lập. Chưa chạy Day3 hoặc training tại mốc chốt. Quyền metadata/text/ảnh và attribution là điều kiện trước public; không commit/push/deploy, không sửa ScoutIQ. Các mốc bên dưới giữ lịch sử, yêu cầu cũ phải chốt toàn bộ nội dung trước đóng Day2 đã được phạm vi mới thay thế.

## Hiện hành — 19/11/2026, pilot Wikipedia nhóm thiếu nguồn

[Báo cáo mới](../reports/day02/wikipedia_gap_20261119/summary.md): mẫu phân tầng 20/349, 8 khớp work, 6 đoạn nội dung ứng viên, 2 mỏng, 12 chờ. Đã cache 8 revision cố định và khai báo license, lưu source_overlay.json riêng với ranh giới đoạn/hash/provenance. Chưa duyệt edition/quyền/public; không đổi v1 hoặc giảm 349 trạng thái chờ. 14 tests vừa chạy đạt, replay cache/review đạt; 7 raw và v1 hashes khớp, không chạy lại audit ratings/ZIP. 9 lỗi 429 ban đầu đã retry chậm thành công, giữ cả attempt lỗi.

Bước tiếp Day2: xác minh nội dung/quyền 6 đoạn ứng viên, truy vấn tên thay thế và nguồn đúng tập/chuyển thể; chốt catalogue sản phẩm. Không suy 40% mẫu thành toàn catalogue, không gọi toàn bộ Day2 hoàn tất. Chưa Day3/training/AI API/cloud; không commit/push/deploy hay sửa ScoutIQ. Các mốc dưới là lịch sử.

## Hiện hành — 19/11/2026, catalogue local v1 đã khóa

Người dùng yêu cầu làm nốt Day2. Đã hoàn tất phần local: `data/processed/catalogue_v1/catalogue.jsonl` có 10.000 sách, ID/provenance/trạng thái; script freeze_day02_catalogue.py từ chối ghi đè nếu payload đổi. [Manifest và báo cáo](../reports/day02/catalogue_v1_20261119/summary.md). 9.651 ứng viên text chưa duyệt nghĩa/quyền; 349 giữ chờ. Gate public intro có helper/tests nhưng chưa tích hợp app. 0 intro public-ready vì chưa sinh/review/quyền; bìa yêu cầu placeholder, chưa tạo asset. Vừa chạy 11 tests đạt; raw/ZIP hashes khớp trước/sau.

Đã nghiên cứu hướng Wikipedia text CC BY-SA: 3 tác phẩm mẫu khớp tựa/tác giả cấp work (113/400/413), cache 3 HTML với hash/revision và khai báo license trong wikipedia_fetch.json. Mẫu có chủ đích, chưa coverage đại diện; không dùng bìa hoặc tự áp giấy phép trang cho mọi trích dẫn. Đây là hướng cụ thể để bổ sung nguồn, chưa catalogue public được duyệt.

**Không tuyên bố toàn bộ Day2 hoàn tất:** phần local đã khóa, còn danh sách catalogue sản phẩm đủ nội dung/quyền. Nếu tiếp tục phần còn lại Day2: mở pilot Wikipedia sang mẫu đa dạng/349 sách và kiểm scope/quyền từng đoạn. Có thể làm Day3 local với v1 khi được yêu cầu; chưa tự bắt đầu. Không train/AI/DB/deploy/commit/push, không sửa ScoutIQ. Các mốc dưới là lịch sử.

## Hiện hành — 19/11/2026, triage Day2 và policy local

Đã phân loại đủ 358 hàng đợi: 315 text rỗng kiểm tự động; 43 text có nội dung được Codex agent đọc (không phải người chấm độc lập). 9 cờ tựa được giải thích; 22 đoạn ngắn cần thêm nguồn; 1 placeholder không dùng; 11 text trùng cần xác minh đúng tập. [Báo cáo](../reports/day02/review_20261119/summary.md), [policy v0.1](CATALOGUE_POLICY.md), review_audit.json và validation.json cùng mốc.

Chốt benchmark local giữ 10.000 book_id/ratings. 9.651 ứng viên sàng lọc text không phải catalogue đã duyệt; 349 mô tả còn chờ. Lọc giả định ứng viên sẽ bỏ 91.141 ratings, giữ 98,475%; chưa áp dụng. Chi tiết quyết định/ID trong data/processed/review_20261119, không đưa dataset lên Git. Script review_description_queue.py tái lập local, kiểm hash XML từng hàng; raw/ZIP khớp trước/sau. **Vừa chạy 9 tests đạt** ở mốc này; lịch sử trước giữ nguyên.

Đã đọc Google Books branding có yêu cầu không sửa nội dung API; chưa duyệt nguồn này cho dịch/tóm lược AI. Quyền text/bìa public vẫn unresolved; chưa final catalogue sản phẩm. Triage/policy local hoàn tất, có thể chuẩn bị Day3 derived/EDA/protocol trong mốc tiếp theo song song giải quyết nguồn/quyền; chưa chạy Day3, train, AI, DB hay deploy. Không commit/push/deploy hoặc thay đổi ScoutIQ.

## Hiện hành — 19/11/2026, đối chiếu kế hoạch và Day2 feasibility

Đã đọc brief đầy đủ, tạo [PROJECT_PLAN.md](PROJECT_PLAN.md) mới (file chưa tồn tại). Lưu mục tiêu cold-start 3/5/10 ratings, phạm vi sản phẩm, Neon/Render, AI, protocol dự kiến và roadmap 21 ngày đến hạn 21/12/2026. Day2 đang thực hiện, chưa chốt catalogue/quyền; không tự đánh dấu hoàn tất theo ngày.

Xem [báo cáo Day2](../reports/day02/feasibility_20261119/summary.md) và sample_check.json. **Vừa chạy** script `scripts/check_day02_sample.py`: cùng mẫu 20 sách, XML local khớp edition/work và tựa/tác giả 20/20, có mô tả 20/20; hash 7 raw + ZIP khớp trước/sau. Không tải dataset mới, không gọi lại API sách, không chạy full audit/unittest. Kết quả 96,85% toàn catalogue và 7 tests là **lịch sử lượt trước**, không phải vừa chạy. Báo cáo Day1 giữ nguyên.

Đã kiểm tài liệu UCSD: schema có mô tả/IDs nhưng trang công bố cũ hạn chế academic use/no redistribution và báo đã chuyển trang. Chưa xác minh endpoint tải mới, chưa tải/đo overlap hay duyệt public. Google Books chưa đo. `.git` không có tại project; Git CLI lỗi truy cập C:/Users/Admin nên root/remote chưa xác minh bằng lệnh Git. Không sửa Git hoặc truy cập secrets/cloud.

Bước tiếp vẫn trong Day2: review nội dung/nguồn/quyền, chốt tiêu chí catalogue trước derived/protocol. Chưa model/metrics, AI, auth/DB/deploy. Không commit/push/deploy hoặc thay đổi ScoutIQ. Các mục dưới là lịch sử.

## Hiện hành — 19/11/2026, kiểm nguồn mô tả hoàn tất

Đã làm theo yêu cầu local: kiểm nguồn, ghép tác phẩm/edition, đo độ phủ và đề xuất làm sạch. Xem [báo cáo mô tả](../reports/day01/descriptions_20261119/summary.md), [độ phủ XML](../reports/day01/descriptions_20261119/xml_coverage.json), [điều kiện nguồn](../reports/day01/descriptions_20261119/sources.md). Các mục bên dưới là lịch sử.

Phát hiện archive XML gốc trong cùng revision Goodbooks. Tải ZIP riêng tại `data/raw/goodbooks-10k-xml/books_xml.zip`, manifest bổ sung tại reports/day01/descriptions_20261119/xml_manifest.json; giữ nguyên raw CSV và manifest cũ. 10.000/10.000 sách ghép đúng hai ID edition/work và bản ghi duy nhất; 9.685 mô tả không rỗng (96,85%). Đây là độ phủ văn bản, chưa phải chất lượng nội dung/quyền public. 315 trống; 23 ngắn; 11 sách thuộc 5 nhóm text trùng; 9 tựa khác cách ghi; 1 placeholder. Hợp hàng đợi 358 sách trong `data/processed/descriptions_20261119/xml_review_queue.json`. Chi tiết 10.000 dòng ở cùng thư mục data, không đưa dataset lên Git.

ISBN10: 2.690 raw hợp checksum + 6.587 ứng viên thêm số 0 đầu đều khớp XML cùng edition; tổng 9.277. XML có 9.402 ISBN13 hợp checksum. Đề xuất lấy từ XML ở lớp derived, không khôi phục chữ số mất từ CSV khoa học, chưa sửa catalogue. Open Library pilot 20 sách: 18 edition trả về, 15 có mô tả trước matching, 13 vừa có mô tả vừa nhất quán tựa/tác giả theo quy tắc, 7 có Goodreads edition ID trùng. Không suy rộng pilot thành tỷ lệ toàn catalogue. Google Books mới đọc tài liệu, chưa gọi API.

Scripts: `scripts/audit_source_descriptions.py`, `scripts/pilot_descriptions.py`; mặc định replay local, `--fetch` chỉ khi thiếu nguồn. 7 tests đạt; raw/ZIP hashes khớp trước/sau, cache replay đạt. Bản raw XML chứa dữ liệu khác nhưng không dùng reviews hoặc rating aggregates làm features. Quyền public mô tả/bìa vẫn unresolved, chưa AI/tóm lược tiếng Việt, chưa model/quality metrics, chưa protocol mới, Neon/Render hay giao diện.

Bước đề xuất tiếp theo: review 358 sách, xác minh quyền nguồn và chốt cleaning policy rồi mới tạo catalogue derived/protocol. Chưa tự chạy giai đoạn này. Không commit/push/deploy, không thay đổi ScoutIQ.

## Hiện hành — 19/11/2026, Day 1 tiếp tục

Người dùng yêu cầu thực hiện trực tiếp và báo cáo trở lại. Hoàn tất khám phá + audit sâu; xem [báo cáo](../reports/day01/extended_20261119/summary.md), audit.json, validation.json và 3 CSV tổng hợp. 4 unittest passed, 0 failed; hash raw khớp trước/sau. Không sửa raw, chưa model/metrics, AI/Neon/Render. Đã thêm requirements trực tiếp theo môi trường hiện tại; chưa fresh-install/cloud.
Rating: 5.976.479, 53.424 người dùng, 10.000 sách, 0 trùng hoặc xung đột. To-read: 912.705 cặp, 2.200 chồng với ratings; chưa suy lỗi. Tags: 8 dòng dư trùng khóa, 6 count âm; chưa sửa. ISBN nguồn có serialization issue; không ghép mô tả bằng ISBN chưa xác minh. Mô tả và quyền public vẫn chờ kiểm tra.
Bước tiếp theo: pilot lấy/ghép mô tả + chính sách làm sạch trước EDA/protocol. Chưa Git repo/remote, chưa commit/push/deploy; giữ ScoutIQ nguyên trạng. Lịch sử phía dưới giữ nguyên.

## Hiện hành — 17/11/2026, Day 1
Project: C:/Users/Admin/Documents/BookNest. Python .venv: 3.11.9. Đã gọi mở project bằng VS Code, cấu hình interpreter .vscode/settings.json; chưa xác minh giao diện editor bằng Computer Use.
Giữ app/main.py người dùng đã tạo. Chưa thay đổi giao diện hoặc cài thêm thư viện trong lượt thu thập.
Đã tải 5 CSV, README và LICENSE từ Goodbooks-10k revision cố định; xem DATA_MANIFEST.json và ../reports/day01/data_audit.json.
Chưa tạo repo Git/remote, chưa commit/push/deploy. Có .gitignore cho raw, processed, mô hình, môi trường và secrets; cần xác minh bằng git check-ignore sau khi khởi tạo Git.
Chưa có Neon/Render/AI cấu hình riêng của BookNest. Chưa huấn luyện, chưa có quality metrics.
Việc tiếp: duplicate ratings; kiểm metadata/tags, nguồn và độ phủ descriptions; chốt catalogue và protocol. Chưa bảo đảm mỗi cuốn có mô tả; file books.csv không có cột description. Không dùng review giả để bù.
Người dùng làm một mình, mục tiêu 21 ngày làm việc; trình bày 21/12/2026; cần sản phẩm công khai, báo cáo, slide và đối chứng định lượng.
