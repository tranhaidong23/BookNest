# BookNest — kế hoạch dự án đã đối chiếu

## Hiện hành 25/11/2026 — readiness local

Kiểm tra môi trường và 130 mục hash Day10 đạt; 68 Python tests vừa chạy đạt. Xem reports/day16_17/readiness_20261125/summary.md và docs/REPRODUCIBILITY.md. Chưa dựng môi trường sạch, replay metrics hoặc kiểm DB/browser mới. Tiếp Day18–19 báo cáo/slide; không tuning test/cloud/commit/push/deploy/ScoutIQ. Các mốc dưới là lịch sử.

**Cập nhật restore23/11:** [9 checks backup/restore local đạt](../reports/day16_17/restore_20261123/summary.md), same-cluster/roles sẵn; chưa cloud/cross-cluster. Tiếp Day18–19 báo cáo/slide và tái lập local. Các mốc dưới là lịch sử.

**Cập nhật Day16–17 local23/11:** [Hiệu năng/hồi quy](../reports/day16_17/local_performance_20261123/summary.md) đã đo, sửa catalogue101->1connections;68 Python tests/11 UI regression đạt. Chưa cloud/thiết bị thực/restore; tiếp các phần local vận hành và báo cáo. Các mốc dưới là lịch sử.

**Cập nhật Day15 local23/11:** [Công cụ nguồn/rubric](../reports/day15/content_local_20261123/summary.md) có68 Python tests và8 native content-gate checks; chưa gọi AI/chấm semantic hoặc duyệt quyền thực. Tiếp phần local hiệu năng/operational Day16–17, không deploy/cloud. Các mốc dưới là lịch sử.

**Cập nhật UI tài khoản 23/11:** [UI/database integration](../reports/day12_14/account_ui_20261123/summary.md) đạt63 Python tests và11 native/AppTest checks. Chỉ catalogue được duyệt, kiểm rút quyền và persistence; danh tính UI test được tiêm, chưa OIDC/provider/browser/Neon. Tiếp Day15 local nguồn/quyền; không gọi full Day12–14 hoàn tất. Các mốc dưới là lịch sử.

**Cập nhật auth23/11:** identity gate/broker đã kiểm59Python tests và8native cases, chưa OIDC thật/UI integration. [Phạm vi](AUTHENTICATION.md). Full Day12–14 vẫn chưa hoàn tất.

**Cập nhật backend23/11:** repository PostgreSQL và snapshot migration002 đã kiểm16integrationcases/51Python tests; UI/auth chưa nối. [Bằng chứng](../reports/day12_14/postgres_repository_20261123/summary.md). Không coi full Day12–14 hoàn tất.

**Hiện hành23/11/2026:** [Day12–14 session demo local](../reports/day12_14/local_app_20261123/summary.md) đã có các luồng chính,47 Python tests, serving parity5.342profiles. Chưa backend persistence/auth hoặc visual QA, không đánh dấu full phase xong. [Day11 native PostgreSQL](../reports/day11/native_postgres_20261123/summary.md) SCRAM/RLS/transaction reset đạt; chưa Neon. Các mốc dưới là lịch sử.

**Hiện hành23/11/2026:** [Day10 test hoàn tất](../reports/day10/final_20261123/summary.md),42 Python tests/audit độc lập đạt; [Day11 phần local](../reports/day11/schema_local_20261123/summary.md) có24 PostgreSQL checks và10.000 metadata readback. Chưa Neon/OIDC/cloud. Người dùng đã cho phép tiếp tục qua các mốc local; không xem được hạn mức token tuần. Giới hạn commit/push/deploy/ScoutIQ giữ nguyên. Các mốc dưới là lịch sử.

**Hiện hành Day8–9, 23/11/2026:** [MF và validation hoàn tất](../reports/day08_09/mf_20261123/summary.md); 40 tests và kiểm độc lập selected cold5 đạt. MF16/lambda10 NDCG0,097247 thua popularity và Item-KNN; giữ KNN là ứng viên chính. Bước tiếp Day10 khóa cấu hình trước test và đánh giá cuối, chưa bắt đầu. Các mốc dưới là lịch sử.

**Hiện hành Day6–7, 23/11/2026:** [Item-KNN và đối chứng validation](../reports/day06_07/item_knn_20261123/summary.md) hoàn tất; 35 tests đạt, independent selected cold5 audit khớp. Chọn K200/shrink10; NDCG0,471873 so popularity0,255947. Bước tiếp Day8–9 MF/fold-in, chưa test cuối. Các mốc dưới là lịch sử.

**Hiện hành Day5, 23/11/2026:** [baselines/validation hoàn tất](../reports/day05/baselines_20261123/summary.md); [định nghĩa grid](DAY05_BASELINES.md). 30 tests đạt, kiểm lại artifacts cold k5 khớp. Popularity vẫn là đối chứng ranking mạnh hơn bias; chưa test/KNN/MF. Bước tiếp Day6–7. Các mốc dưới là lịch sử.

**Hiện hành Day4, 20/11/2026:** [split v1 đã khóa](../reports/day04/split_20261120/summary.md) theo protocol v0.1; 24 tests đạt, full-data kiểm assignment và readback đạt. [SPLIT_USAGE](SPLIT_USAGE.md). Day5 sẽ triển khai baselines/validation; chưa fit hoặc đánh giá test. Các mốc dưới là lịch sử.

**Hiện hành Day3, 20/11/2026:** [derived v2 và EDA](../reports/day03/preparation_v2_20261120/summary.md) đã tạo, 19 tests đạt; [protocol v0.1](EVALUATION_PROTOCOL.md) đã viết trước split/train. Day4 còn thực thi/kiểm split và khóa manifest. Các mốc dưới là lịch sử.

**Hiện hành 20/11/2026:** người dùng đã chốt [Day2 theo phạm vi điều chỉnh](../reports/day02/closure_20261120/summary.md), [policy v0.2](CATALOGUE_POLICY.md). Benchmark giữ 10.000 sách; mô tả chưa duyệt để thiếu, bìa placeholder; quyền metadata/text/ảnh vẫn phải đủ trước public. Xác minh sáu đoạn Wikipedia chuyển thành backlog nội dung ưu tiên, không chặn Day3. Mốc này chỉ cập nhật tài liệu, chưa chạy Day3; các cập nhật 19/11 phía dưới là lịch sử.

**Mốc mới nhất:** [pilot Wikipedia nhóm thiếu nguồn](../reports/day02/wikipedia_gap_20261119/summary.md): 20 mẫu, 8 work khớp, 6 đoạn ứng viên, 2 mỏng; 14 tests đạt. Overlay riêng, v1 nguyên; chưa duyệt edition/public, chưa chốt toàn bộ Day2 hoặc chạy Day3. Các mốc dưới giữ lịch sử.

**Mốc mới nhất:** [catalogue local v1](../reports/day02/catalogue_v1_20261119/summary.md) đã khóa 10.000 sách; 11 tests đạt. Wikipedia pilot 3 tác phẩm có cache/hash/revision/license. Chưa nghiệm thu catalogue sản phẩm/quyền; không đánh dấu toàn bộ Day2 done. Các cập nhật và bảng phía dưới giữ lịch sử. Chưa chạy Day3.

**Cập nhật sau mốc đối chiếu:** triage 358 hàng đã hoàn tất, 9 tests mới đạt; [policy local v0.1](CATALOGUE_POLICY.md) giữ benchmark 10.000 sách, chưa chốt catalogue public. [Bằng chứng mới](../reports/day02/review_20261119/summary.md). Các bảng hiện trạng dưới đây ghi nhận thời điểm đối chiếu trước, không thay thế mốc mới này. Chưa chạy Day3.

Cập nhật 19/11/2026. Một người thực hiện, mục tiêu 21 ngày làm việc, trình bày 21/12/2026. Ngày trong roadmap là mốc công việc, không tự đánh dấu hoàn tất theo lịch. Chưa có rubric chính thức; thông tin metrics được coi trọng chưa được xác nhận. File này chưa tồn tại khi kiểm tra; tạo mới, không thay thế nội dung cũ.

## 1. Mục tiêu và câu hỏi nghiên cứu

**BookNest — Hệ thống gợi ý sách cá nhân hóa tích hợp AI.** Câu hỏi chính: “Với 3–5 đánh giá ban đầu, hệ thống có cải thiện chất lượng gợi ý so với cách đề xuất sách phổ biến không?” So sánh thêm 3/5/10 đánh giá nếu đủ thời gian. Kết luận phải dựa trên đối chứng và giới hạn; không đặt mục tiêu accuracy tùy ý.

Sản phẩm cuối: website công khai, database thật, recommender có đánh giá định lượng, AI có ích, báo cáo, slide, video demo dự phòng và tài liệu phản biện. Thanh điều chỉnh mức khám phá là mở rộng; cắt trước nếu chậm. Giữ thời gian cho đối chứng và tập bảo vệ.

## 2. Đối chiếu hiện trạng

| Hạng mục | Trạng thái và nguồn bằng chứng |
|---|---|
| Python | Vừa kiểm tra: 3.11.9 trong .venv |
| Dataset | Báo cáo lịch sử: 10.000 sách, 53.424 users, 5.976.479 ratings, 912.705 to_read; revision/7 file gốc ở DATA_MANIFEST.json |
| Audit ratings/tags | Lịch sử: không trùng/xung đột ratings; 8 dòng dư trùng khóa tags, 6 count âm; 2.200 cặp ratings/to_read giao nhau; chưa chạy lại audit đầy đủ trong mốc đối chiếu |
| Mô tả | Đã tiến xa hơn brief: archive XML đã tải ở lượt trước, 10.000 liên kết edition/work; 9.685 mô tả không rỗng; hàng đợi review 358 sách |
| Pilot nguồn khác | Lịch sử Open Library 20 sách: 18 edition trả về, 15 có text, 13 có text + tựa/tác giả nhất quán sơ bộ; 7 có Goodreads edition ID trùng |
| Kiểm mới trong mốc này | Đọc lại 20 XML local của cùng mẫu: 20/20 khớp edition/work, tựa/tác giả, có text. Xác minh lại hash cả 7 raw và ZIP trước/sau; không gọi lại API sách |
| Tests | 4 tests là audit cũ; 7 tests là kết quả lượt kiểm mô tả trước. Mốc đối chiếu không chạy lại unittest và không gọi đó là kết quả mới |
| App | Vừa đọc app/main.py: trang chào Streamlit; chưa có chức năng sản phẩm |
| Git | Không có .git tại project khi kiểm; lệnh git rev-parse lỗi truy cập C:/Users/Admin nên chưa xác nhận được Git root/remote bằng Git |
| Chưa có bằng chứng triển khai | Model/quality metrics, split, AI, Neon, Render, auth và ownership chưa triển khai theo bàn giao; không dò secrets hoặc tài khoản cloud để suy diễn |

Bằng chứng mới: [Day2 feasibility](../reports/day02/feasibility_20261119/summary.md), [sample_check.json](../reports/day02/feasibility_20261119/sample_check.json). Bằng chứng lịch sử: [audit sâu](../reports/day01/extended_20261119/summary.md), [nguồn mô tả](../reports/day01/descriptions_20261119/summary.md). “96,85%” chỉ là độ phủ text, không phải accuracy hay tỷ lệ được phép public. “100% mẫu” không thay thế kết quả toàn catalogue.

## 3. Phạm vi sản phẩm và nghiệm thu dự kiến

Giao diện tiếng Việt, phong cách thư viện hiện đại, dễ đọc, có bìa khi đủ quyền, bố cục thoáng và dùng được trên mobile.

| Khu vực | Hành vi cần có |
|---|---|
| Khám phá | Tìm theo tên/tác giả, lọc thể loại đã chuẩn hóa |
| Chi tiết sách | Metadata, đúng edition/bìa, giới thiệu có nguồn và trạng thái thiếu rõ ràng |
| Hồ sơ sở thích | Thêm/sửa/xóa rating 1–5 |
| Dành cho bạn | Top 10, loại sách đã đánh giá; lý do gắn với evidence engine |
| Muốn đọc | Thêm/xóa và lưu danh sách của đúng người dùng |
| Lịch sử | Lưu lần gợi ý, model/config version và danh sách kết quả |
| Thí nghiệm | Protocol, biểu đồ đối chứng, metrics và giới hạn |

Khách được khám phá/thử. Lưu hồ sơ lâu dài cần auth và ownership từ server; đánh giá dịch vụ xác thực có sẵn trước khi chọn. Không dùng UUID client gửi làm bằng chứng quyền. Kiểm ít nhất hai tài khoản độc lập, không đọc/sửa dữ liệu nhau; kiểm cả thao tác thêm/sửa/xóa và truy vấn lịch sử.

## 4. Kiến trúc và dữ liệu vận hành

Python 3.11, Streamlit, recommendation engine Python huấn luyện trước, PostgreSQL trên **Neon**, hosting **Render**, một API AI phía server chưa chọn nhà cung cấp. Không tự chuyển hosting; chưa cần FastAPI nếu không có lý do cụ thể. Trước triển khai phải đọc tài liệu/giá/tài nguyên hiện hành, kiểm model RAM/startup, timeout và điều kiện gói dịch vụ; không coi miễn phí là liên tục/vô hạn. Chưa xác nhận chi phí trong mốc này.

Schema dự kiến có migrations: books; book_tags/bảng thể loại; book_descriptions (text nguồn, URL/ID, scope edition/work, quyền, AI text, version/thời điểm); users (định danh auth); user_ratings; reading_list; recommendation_runs; recommendation_items. Chốt schema theo luồng thực tế. Ratings benchmark tách ratings website. Dữ liệu train lớn và model artifacts quản lý riêng, không bắt buộc đưa vào DB vận hành. Credentials chỉ server, không vào Git/client/log; không yêu cầu gửi key/connection string trong chat.

## 5. Nguồn mô tả và catalogue

Ưu tiên XML Goodbooks đã pin để nghiên cứu local, ghép bằng hai ID và kiểm tựa/tác giả. ISBN lấy chuỗi XML hợp checksum sau kiểm edition; không đoán chữ số mất từ CSV. Raw và mọi manifest bất biến; derived có provenance/version/lý do thay đổi, missing là null. Rà 358 trường hợp được gắn cờ; không gộp sách chỉ vì text trùng. Tags cần allowlist thể loại; review count trùng/xung đột, cách ly count âm; không tự biến thành 0.

Mỗi sách trong catalogue sản phẩm được nghiệm thu nên có giới thiệu tiếng Việt khoảng 60–100 từ từ mô tả có nguồn. Chưa cam kết catalogue public đủ 10.000. Nếu thu hẹp: ghi tiêu chí trước đánh giá, giữ danh sách ID, lý do và độ phủ; báo tác động lên user/item/ratings và phạm vi kết luận. Không chọn sách dễ gợi ý theo test metrics. Benchmark và catalogue sản phẩm có thể khác nhưng phải công bố rõ; không so các mô hình trên ứng viên khác nhau.

Nguồn dự phòng: Open Library đã có pilot; Google Books mới kiểm tài liệu/điều khoản, chưa đo độ phủ; UCSD chỉ kiểm trang tài liệu, chưa tải dataset. UCSD có hạn chế academic use/no redistribution trên trang công bố cũ và báo đã chuyển trang; chưa xác minh giấy phép public hay endpoint tải mới. Không suy luận được public vì dùng cho bài học. Chưa nguồn nào được duyệt toàn bộ quyền bìa/mô tả cho website. Xem [báo cáo nguồn](../reports/day02/feasibility_20261119/summary.md).

Phân biệt giới thiệu tóm lược nguồn, review độc giả thật và tổng hợp reviews (phạm vi/protocol riêng). Không gọi AI text là review độc giả, không bịa cốt truyện/trải nghiệm. Không đưa test review/rating vào đặc trưng của cặp test. Tóm lược/dịch AI không tự giải quyết quyền nguồn.

## 6. Mô hình và protocol phải chốt trước train

Đối chứng đã chạy: popularity Top-K; baseline sao có hiệu chỉnh; Item-KNN; Matrix Factorization. KNN K200/shrink10 được chọn validation và giữ nguyên khi mở test Day10; MF d16/lambda10 là cấu hình được chọn trong họ MF. Chi tiết grid/công thức ở báo cáo Day5–10. Mọi popularity/mean/bias tính trên train, không lấy average_rating toàn nguồn. Test đã mở, không được tiếp tục tuning dựa vào kết quả test.

Protocol hiện hành: [EVALUATION_PROTOCOL.md](EVALUATION_PROTOCOL.md), snapshot đã khóa cùng split Day4. User-held-out 80/10/10, warm riêng, support 3/5/10 lồng nhau với target chung, relevance >=4, ranking toàn catalogue và tuning validation. Split artifacts đã tạo; xem [SPLIT_USAGE.md](SPLIT_USAGE.md).

Đánh giá sao: RMSE/MAE. Ranking: NDCG@10 và Recall@10 chính, Precision@10 bổ sung nếu cần; thêm catalogue coverage và latency. Định nghĩa rõ mẫu số coverage, môi trường/tải đo latency. Không có số metrics trước khi chạy. Không diễn giải item chưa chấm là rating 0/không thích; similarity không phải accuracy/xác suất thích. CSV không timestamp, không tuyên bố temporal evaluation từ thứ tự dòng.

Cold-start là thí nghiệm chính: giữ users validation/test ngoài train để mô phỏng người mới; chỉ dùng 3/5/10 support ratings tạo hồ sơ. Support lồng nhau và tập target chung khi so các mức đầu vào; support không lọt target, không dùng target để chọn support/tuning. Chốt eligibility (đủ support/target), báo số người bị loại và thiên lệch. Tuning cold-start trên users validation riêng. MF cần fold-in/tạo vector user từ support với item factors đã học, kiểm riêng khả năng này. Warm-start báo riêng. Khi đủ điều kiện, báo chênh lệch theo user và độ bất định, không chỉ một điểm trung bình. Kết quả offline không tự chứng minh hiệu quả thực tế.

## 7. AI và kiểm chất lượng

AI chỉ tóm lược mô tả thành giới thiệu tiếng Việt và diễn đạt lý do từ evidence engine; không tự ranking hoặc tạo ground truth. Giới thiệu ưu tiên tạo trước và lưu nguồn, prompt/model/version, thời điểm. Giải thích có mẫu dự phòng. Có giới hạn quota/chi phí, timeout, lỗi và fallback phía server.

Kiểm thủ công khoảng 30–50 giới thiệu theo rubric: đúng sách/edition, có căn cứ, dễ đọc, không thêm thông tin sai; ghi người chấm và cách chọn mẫu. Người phát triển tự chấm không gọi là đánh giá độc lập. Chỉ bắt đầu khi nguồn/quyền và catalogue đủ rõ; chưa gọi AI trong mốc feasibility.

## 8. Roadmap 21 ngày làm việc

| Mốc | Công việc và đầu ra | Trạng thái cập nhật23/11 |
|---|---|---|
| Day1 | Project, thu thập, khám phá/audit, manifest | Đã có; không đồng nghĩa đã sạch |
| Day2 | Nguồn mô tả, mapping, coverage; chốt catalogue local và policy fallback | Đã chốt phạm vi điều chỉnh 20/11; quyền/nội dung public còn backlog, không đồng nghĩa đã duyệt |
| Day3 | Cleaning, derived, EDA và thiết kế protocol | Đã thực hiện 20/11: derived v2, 19 tests; chưa split/train |
| Day4 | Thực thi protocol và split tái lập | Đã thực hiện 20/11; split v1, 24 tests, full-data invariants/readback/hashes đạt |
| Day5 | Baselines đã định nghĩa và metrics validation | Hoàn tất 23/11: popularity/mean/bias, 30 tests; không test performance |
| Day6–7 | Item-KNN và kiểm đối chứng | Hoàn tất 23/11: K200/shrink10 chọn validation, 35 tests; không test performance |
| Day8–9 | MF, tuning, đối chứng cùng điều kiện | Hoàn tất 23/11: MF16/lambda10 chọn validation; thua KNN/popularity ranking; 40 tests, chưa test performance |
| Day10 | Thí nghiệm 3/5/10 support, chốt config, đánh giá cuối theo protocol | Hoàn tất23/11; lock trước test, KNN thắng popularity,42 tests và audit toàn Top10; không refit |
| Day11 | Neon schema/migration và quyền | Phần local hoàn tất23/11:24 PostgreSQL checks,10.000 metadata readback; chưa áp dụng hoặc kiểm Neon |
| Day12–14 | Catalogue, hồ sơ, auth/ownership, gợi ý, lịch sử, muốn đọc | Session demo và UI tài khoản nối PostgreSQL đã có;11 UI/DB checks đạt. Broker/claims kiểm local, chưa OIDC provider/Neon/browser; chưa full completion |
| Day15 | AI giới thiệu/giải thích và rubric kiểm | Công cụ packet/prompt/draft và rubric local đã có;68 tests/8 DB checks; chưa AI thật hoặc nghiệm thu nội dung |
| Day16–17 | Render, hiệu năng, hai user/thiết bị, nghiệm thu luồng | Đã đo local engine/DB, tối ưu catalogue101->1connections,20concurrent saves2accounts/11UI regression/9restore checks đạt; chưa cloud/hai thiết bị/cross-cluster restore |
| Day18–19 | Báo cáo, slide và đối chứng có bằng chứng | Chưa bắt đầu |
| Day20 | Diễn tập, phản biện, video dự phòng | Chưa bắt đầu |
| Day21 | Tái lập, đóng gói, bàn giao | Chưa bắt đầu |

Có thể thử deploy trang khung nếu được cho phép riêng. Người dùng hiện đã cho phép tiếp tục nhiều mốc local trong một lượt; không tự deploy/cloud. Nếu chậm, cắt khám phá nâng cao và mở rộng reviews trước; bảo toàn thí nghiệm chính, sản phẩm cốt lõi, tài liệu và thời gian tập trình bày.

## 9. Gate tiếp theo và cách làm việc

Tiếp vận hành/restore và tái lập local, báo cáo/slide theo roadmap. UI tài khoản đã nối repository; Day10 test đã xem, không dùng để tuning. Neon/OIDC thực/pool, quyền public và triển khai cloud vẫn backlog riêng, không tự phê duyệt. Không lấy số đo local hoặc synthetic identities thay bằng chứng cloud/đăng nhập thật.

Sau mỗi mốc: cập nhật HANDOFF/README/inventory khi cần, ghi mục tiêu/file/kết quả/cách kiểm/giới hạn, nhật ký quyết định và câu hỏi phản biện. Tách lịch sử, vừa chạy và dự kiến. Tests phải bảo vệ logic dữ liệu/model/ownership, không tăng số lượng vì trình bày. Giữ raw/SHA-256; không đưa data/.venv/secrets lên Git. Chuẩn bị thay đổi review được trước khi xin phép commit/push/deploy; chưa có quyền thực hiện các hành động đó. Không thay đổi ScoutIQ (dự án riêng dừng Day20).
