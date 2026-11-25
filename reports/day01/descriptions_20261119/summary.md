# BookNest — nguồn mô tả, ghép sách và độ phủ, 19/11/2026

## Kết luận thực tế

**Nguồn ưu tiên cho xử lý local là archive XML gốc Goodbooks tại cùng revision với CSV.** Ghép được 10.000/10.000 sách bằng đồng thời ID edition (`goodreads_book_id`) và ID tác phẩm (`work_id`), không có bản ghi edition trùng hoặc XML lỗi parse. Có **9.685/10.000 mô tả không rỗng = 96,85%** sau chuyển HTML sang text để đo. Đây là độ phủ văn bản, không phải accuracy, chất lượng giới thiệu hoặc tỷ lệ nội dung được phép public.

Đã thử thêm Open Library trên mẫu 20 sách. Nguồn này hữu ích làm dự phòng nhưng cần kiểm mapping; không cần dùng tìm kiếm mờ làm nguồn chính khi đã có XML gốc. **Chưa chạy AI, tạo giới thiệu tiếng Việt, huấn luyện, commit/push/deploy hoặc sửa ScoutIQ.**

## Phạm vi và bằng chứng

- Đọc AGENTS, README, HANDOFF, hai báo cáo Day1 và audit sâu trước khi làm.
- Giữ nguyên 7 file raw và manifest cũ; SHA-256 khớp trước/sau. Tải thêm ZIP 55.777.086 bytes vào `data/raw/goodbooks-10k-xml/`, revision `6dd165b555a7b47b2dd36743a425776e641ff50c`. Nguồn, thời điểm, SHA-256: [xml_manifest.json](xml_manifest.json).
- Đọc trực tiếp XML trong ZIP, không extract nội dung lên filesystem; không dùng reviews/số rating trong XML làm features. Chi tiết từng book và hash từng XML nằm trong `data/processed/descriptions_20261119/xml_matches.csv`, thuộc vùng `data/` đã ignore.
- [xml_coverage.json](xml_coverage.json): kết quả toàn catalogue. [coverage.json](coverage.json), [matches.json](matches.json): chỉ pilot Open Library. [response_manifest.json](response_manifest.json): URL, thời điểm, SHA-256 từng cache; body gốc nằm trong `data/external/openlibrary/pilot_20261119/`.
- [sources.md](sources.md): tài liệu API và điều kiện nguồn đã kiểm. Chưa xác nhận quyền công khai mô tả/bìa từng sách; `public_display_allowed=false`. Không có nghĩa đã xác định nội dung bị cấm, mà là chưa hoàn tất kiểm quyền.

## Độ phủ toàn catalogue từ XML

| Kiểm tra | Kết quả |
|---|---:|
| Catalogue / XML parse được | 10.000 / 10.000 |
| Cặp edition ID + work ID khớp, bản ghi duy nhất | 10.000 |
| Tựa khác sau chuẩn hóa chữ/số | 9 |
| Tác giả chính không khớp sau chuẩn hóa | 0 |
| Mô tả không rỗng | 9.685 (96,85%) |
| Mô tả rỗng | 315 (3,15%) |
| Mô tả không rỗng nhưng dưới 80 ký tự | 23 |
| Mô tả có HTML | 7.603 |
| Nhóm mô tả trùng hoàn toàn sau chuẩn hóa whitespace | 5 nhóm, 11 sách |
| Ghi chú nhập dữ liệu nhận diện bằng `for ingest only` | 1 |
| Hàng đợi rà soát hợp các cờ trên | 358 sách |
| ISBN10 XML hợp checksum | 9.277 |
| ISBN13 XML hợp checksum | 9.402 |

Ngưỡng 80 ký tự chỉ giúp ưu tiên review, không phải ngưỡng chất lượng; mô tả ngắn có thể đúng, mô tả dài vẫn có thể sai. 9.642 sách chưa vướng các cờ sơ bộ này **không** đồng nghĩa đã được kiểm nội dung. Chưa nhận diện ngôn ngữ tự động, chưa chấm tính đúng/đủ nghĩa, chưa đo chất lượng recommender.

## Ghép đúng tác phẩm và edition

`book_id` là khóa nội bộ Goodbooks; ratings gộp các edition theo work. Không được dùng giá trị số của ID này làm ID Goodreads/Open Library. XML chỉ được chấp nhận liên kết khi cùng edition ID, cùng work ID và edition record duy nhất. Tựa/tác giả là kiểm tra bổ trợ. Cùng ID giữa CSV và XML là kiểm tra tính nhất quán trong nguồn, chưa phải xác minh độc lập rằng tác giả nguồn nhập đúng mọi metadata.

9 khác biệt tựa đã xem: 6 trường hợp hậu tố/tên series (book_id 1000, 113, 400, 3950, 706, 413), một `&` so với `and` (1375), một phụ đề (9134), một tựa bị lặp (4010). ID edition/work vẫn khớp. Đề xuất giữ tựa CSV để hiển thị và lưu tựa XML như alias; không xóa số tập trên diện rộng. Không đổi bìa/edition theo tựa tương tự.

ISBN: 2.690 mã CSV hợp checksum ngay; 6.587 mã chỉ hợp sau giả thuyết thêm số 0 đầu. Cả 9.277 mã này trùng ISBN trong XML đã ghép đúng edition. Có thể lấy ISBN XML làm giá trị canonical ở lớp derived, giữ raw và lý do chuyển đổi. Không suy ra các chữ số ISBN13 đã mất từ dạng khoa học CSV: lấy chuỗi XML và kiểm checksum. Mã thiếu/sai còn lại phải null hoặc review, không tự đoán.

## Pilot Open Library: cùng mẫu số 20 sách

Chọn bằng `random.Random(20261119)`, 2 sách ngẫu nhiên trong mỗi block 1.000 book_id, sau sắp xếp số. Đây là mẫu thăm dò nhỏ trải catalogue, không đại diện riêng sách tiếng Việt, sách mới hay nhóm sách thiếu mô tả. Không suy rộng tỷ lệ này thành độ phủ 10.000 sách.

| Bước | Số sách / 20 |
|---|---:|
| ISBN raw hợp checksum / thêm số 0 / không có ứng viên | 5 / 13 / 2 |
| API trả bản ghi edition qua ISBN | 18 |
| Có mô tả tại edition hoặc work trước kiểm ghép | 15 (75%) |
| Tựa và tác giả chính nhất quán theo quy tắc bảo thủ | 14 |
| Vừa nhất quán theo quy tắc, vừa có mô tả | 13 (65%) |
| Có liên kết Goodreads edition ID trùng nguồn | 7 (35%) |
| Lỗi truy vấn trong pilot | 0 |

7 liên kết ID trùng đều có mô tả; 13 trường hợp còn lại thiếu trường liên kết Goodreads, không phải ID xung đột. Chưa chứng minh mọi ứng viên đúng edition. Các trường hợp không qua tự động có thể chỉ thiếu tác giả hoặc thiếu phụ đề: ví dụ 3625 có cùng Sam Harris và phần tựa chính nhưng API bỏ phụ đề; cần review, không tự nhận là sai sách. Hai sách không có ISBN không cho ứng viên title/author duy nhất theo quy tắc của pilot; không kết luận Open Library không có chúng.

Mô tả work và edition được đếm riêng bằng độ dài trong matches.json. Mô tả cấp work không đủ xác nhận ngôn ngữ, nhà xuất bản hay bìa cấp edition. Chưa kiểm bìa. Cache cho phép replay offline; không thực hiện thu thập API hàng loạt.

## Đề xuất làm sạch — chưa áp dụng vào catalogue production

1. **Bảo toàn và provenance:** giữ nguyên CSV/ZIP/cache. Lớp derived ghi book_id, Goodreads edition/work ID, source URL/revision/hash, XML member, phạm vi work/edition, trạng thái matching và quyền sử dụng. Khóa nội bộ không đổi; metadata thiếu là null.
2. **ISBN:** lấy ISBN XML hợp checksum sau khi ghép đủ hai ID. Lưu `raw_value`, `canonical_value`, `source`, `reason`; không ghi đè raw. Kiểm các mã dùng chung cho nhiều edition trước khi dùng làm khóa join; ISBN không là khóa chính catalogue.
3. **Text:** decode entity một lần, bỏ HTML/script/style, chuẩn hóa khoảng trắng nhưng giữ dấu và ngôn ngữ. Parser hiện mới tạo text để audit, chưa phải sanitizer HTML production. Lưu bản gốc và text riêng; không nối đoạn quảng cáo/review vào tóm tắt. Giữ null cho 315 sách thiếu mô tả.
4. **Review 358 sách:** hàng đợi ở `data/processed/descriptions_20261119/xml_review_queue.json`. Cách ly placeholder book_id 4280; xem 23 đoạn ngắn theo nghĩa thay vì xóa hết. Book 4622 nêu rõ là bản kịch, không được thay bằng nội dung tiểu thuyết Kafka. Book 8027 nói tới companion journal, cần đối chiếu edition. Không dùng các đoạn này để sinh giới thiệu tự động trước review.
5. **Trùng nội dung:** 5 nhóm nằm ở Hellboy, Ouran, ba tập 1Q84, hai sách Fudge và hai tập Winnie-the-Pooh. Có thể là mô tả series hoặc sao chép metadata; không gộp/xóa book_id hoặc ratings. Cần kiểm nội dung riêng từng tập.
6. **Nguồn dự phòng:** ưu tiên kiểm 315 sách trống và các trường hợp bị loại sau review; yêu cầu bằng chứng title/author + edition/ISBN, phân biệt bản dịch, bản kịch, sách tập hợp. Open Library chỉ là ứng viên; Google Books chưa đo. Không lấp chỗ trống bằng review hay nội dung AI tự nghĩ.
7. **Giới thiệu tiếng Việt và public:** chỉ triển khai sau kiểm nội dung và quyền nguồn. Bản dịch/tóm lược phải có nguồn, liên kết và phạm vi rõ ràng; AI không tự cấp quyền đối với văn bản nguồn. Chưa tạo giới thiệu ở mốc này.
8. **Tags/rating:** giữ quyết định audit trước: không sửa ratings; duplicate tags giống hệt có thể loại dòng dư ở derived, count xung đột cần review thay vì cộng mù; 6 count âm cách ly, không biến thành 0. Genre dùng allowlist đã review. Đây mới là đề xuất, chưa làm sạch tags hay chạy protocol/training.

## Tái lập và kiểm chứng

Chạy từ project, không cần network sau lần thu thập này:

```text
.venv\Scripts\python.exe -B scripts/audit_source_descriptions.py
.venv\Scripts\python.exe -B scripts/pilot_descriptions.py
.venv\Scripts\python.exe -B -m unittest discover -s tests -v
```

`--fetch` chỉ dùng khi thiếu archive/cache; cache đã có được đọc lại, không tự refresh. Chạy lại ghi đè báo cáo derived của mốc này. Không sửa hoặc tải lại raw CSV. XML archive lỗi hash sẽ dừng; cache kiểm hash body. 7 tests đạt (4 audit cũ + 3 kiểm ID/ISBN/text mới). Đã chạy lại từ cache và archive local; SHA-256 raw/ZIP khớp trước/sau. Chưa kiểm cài mới, deploy, backup ngoài máy, độ đúng ngữ nghĩa toàn bộ mô tả hoặc quyền public.

Mốc tiếp theo được đề xuất: rà nội dung và chốt chính sách derived dựa trên hàng đợi này, rồi mới lập catalogue sạch và protocol. Chưa tự khởi chạy các giai đoạn đó.
