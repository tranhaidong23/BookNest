# Day2 — pilot Wikipedia cho nhóm thiếu nguồn, 19/11/2026

Đã hoàn tất pilot cố định 20 sách và lưu lớp nguồn bổ sung riêng. **8/20 ghép được cấp tác phẩm; 6 có đoạn nội dung ứng viên, 2 còn mỏng; 12 chưa ghép được phù hợp trong kết quả đã xét.** Chưa duyệt edition hoặc public cho bất kỳ hàng nào. Không sửa catalogue v1; chưa kết luận toàn bộ Day2 hoàn tất.

## Cách đo và bằng chứng

Lấy mẫu ngẫu nhiên trong từng nhóm, seed 20261120 (seed cố định, không phải ngày chạy): 12/315 thiếu mô tả, 4/22 cần thêm bằng chứng, 4/11 nghi trùng nội dung giữa các tập. Hàng placeholder duy nhất không nằm trong mẫu. Tìm tựa cơ sở + tác giả đầu, tối đa 3 kết quả tiếng Anh mỗi sách. Agent đọc kết quả và đối chiếu tựa, tác giả, loại tác phẩm, phạm vi tập/chuyển thể; đây không phải kiểm định độc lập của người chấm.

| Nhóm | Mẫu | Khớp work | Có đoạn nội dung ứng viên |
|---|---:|---:|---:|
| Thiếu mô tả | 12 | 4 | 3 |
| Cần thêm bằng chứng | 4 | 1 | 1 |
| Nghi trùng/phạm vi tập | 4 | 3 | 2 |
| Tổng | 20 | 8 | 6 |

40% khớp work và 30% có đoạn ứng viên **chỉ mô tả mẫu này**. Không suy rộng thành độ phủ 349 hoặc 10.000 sách: mẫu phân tầng không theo tỷ trọng, chỉ tìm top 3 tiếng Anh, chưa truy vấn thay thế. Tìm không ra chưa chứng minh nguồn không tồn tại. 20/20 có kết quả tìm kiếm không có nghĩa 20/20 có nguồn phù hợp.

## Các tác phẩm đã ghép

| book_id | Tựa | Kết quả đọc snapshot revision |
|---|---|---|
| 8947 | Once a Runner | Có premise/plot; giữ cờ thiếu dẫn nguồn, loại đoạn mở đầu có trích dẫn, kết thúc và lời đánh giá |
| 6317 | The Looming Tower | Có Overview; còn cờ nofootnotes, cần đối chiếu thêm trước duyệt nội dung |
| 7878 | Joseph Had a Little Overcoat | Có premise; bỏ câu đạo lý trích nguyên văn/review; chưa ghép bản minh họa 1977/1999 |
| 7917 | Krakatoa: The Day the World Exploded | Đúng tác phẩm nhưng summary ít thông tin; không kéo dài bằng suy diễn |
| 6390 | The Te of Piglet | Có Synopsis riêng, không lấy nội dung The Tao of Pooh thay thế |
| 6716 | Double Fudge | Có plot riêng tập 5 |
| 2215 | Superfudge | Có plot riêng tập 3; đọc toàn bài giải quyết hạn chế lead quá ngắn |
| 7696 | Now We Are Six | Lead mô tả tập thơ đúng tên; còn mỏng, loại thơ trích nguyên văn và ảnh |

12 hàng giữ chờ có lý do riêng trong source_overlay.json. Ví dụ: Nana/Preacher/1Q84 là trang cả bộ, không đủ cho tập 1/9/3; The Castle tiểu thuyết không thay cho bản kịch Fishelson; Eragon đơn lẻ không thay cho omnibus ba cuốn. Cape Fear trả phim/TV; tên The Executioners là đầu mối truy vấn tiếp, chưa xử lý trong pilot này. Betty Crocker Cookbook là họ sách nhiều edition, chưa xác minh nội dung bản đích.

## Nguồn, quyền và làm sạch

Đã tải một batch **8 revision cố định**, đối chiếu revision ID với kết quả tìm kiếm; cache giữ wikitext và siteinfo khai báo CC BY-SA 4.0. Lưu URL bài/revision/history, SHA-256 response/toàn wikitext/đoạn chọn và reviewer cho từng work. Không lấy ảnh. Snapshot có thể chứa trích dẫn/ảnh tham chiếu, nhưng đoạn chọn chỉ phục vụ rà soát và vẫn chưa được đưa vào app.

Giấy phép site là bằng chứng khai báo, chưa phải nghiệm thu mọi đoạn. Lịch sử/thảo luận và khả năng nội dung nhập từ nguồn khác chưa rà đầy đủ. Giữ `rights_status=pending_segment_review`, `edition_verified=false`, `public_ready=false`; chưa tạo intro tiếng Việt. Điều kiện khi tái sử dụng: ghi công bài/các tác giả qua history, dẫn giấy phép, ghi thay đổi và ShareAlike cho bản tóm lược/chuyển ngữ. Xem [quyết định nguồn trước](../catalogue_v1_20261119/source_decisions.md) và [Wikimedia Terms mục 7](https://foundation.wikimedia.org/wiki/Policy:Terms_of_Use#7._Licensing_of_Content).

Quyết định làm sạch: giữ benchmark 10.000; dùng lớp overlay để bổ sung bằng chứng thay vì ghi đè mô tả raw hoặc v1. Tách work/edition/volume/adaptation; không tự duyệt theo độ dài hoặc tên gần giống. Chọn đoạn premise/synopsis có ranh giới, loại reviews quảng bá, câu trích, kết thúc nếu không cần và media; chưa biến wikitext thành văn bản sản phẩm. Hai đoạn mỏng giữ chờ, không nhờ AI bịa để đủ 60–100 từ. Sáu đoạn ứng viên vẫn cần kiểm sự kiện và quyền, không đồng nghĩa sáu intro đã đạt.

## Kiểm tra đã chạy ở mốc này

- 14 unittest đạt (11 tests cũ chạy lại + 3 mới: cache bị sửa, ranh giới đoạn, lỗi API).
- Replay tìm kiếm từ cache không gọi mạng; nội dung candidates giữ cùng hash.
- Review replay kiểm hash response, revision, ranh giới từng đoạn và 20 quyết định.
- SHA-256 7 file raw khớp trước/sau; catalogue v1 vẫn `869aa530a03b016a0795cfc1f752a927f59dc5df5f49d4054e6a4e9806c1de55`. Không chạy lại audit ratings hoặc hash ZIP ở mốc này.
- Lượt tìm đầu có 9 HTTP 429. Giữ nguyên file lỗi, thử lại một lần chậm với file `_retry1`; cả 9 đã thành công, lỗi cuối 0. Script hiện dừng mạng ngay nếu gặp 429, không coi lỗi mạng là thiếu nguồn.

Bằng chứng: [search_audit.json](search_audit.json), [response_manifest.json](response_manifest.json), [review_audit.json](review_audit.json). Dữ liệu local không đưa Git: `data/processed/wikipedia_gap_20261119/{candidates,source_overlay}.json`; cache `data/external/wikipedia/gap_20261119/`. Scripts `pilot_wikipedia_gap.py`, `review_wikipedia_gap.py` mặc định replay local; snapshot 8 revision được lấy bằng một lệnh batch trong phiên, URL tham số được lưu đủ trong cache (chưa có CLI tải lại batch).

```powershell
.venv\Scripts\python.exe -B scripts/pilot_wikipedia_gap.py
.venv\Scripts\python.exe -B scripts/review_wikipedia_gap.py
.venv\Scripts\python.exe -B -m unittest discover -s tests -v
```

## Trạng thái tiếp theo

Wikipedia có ích như nguồn bổ sung nhưng chưa đủ bằng chứng để dùng làm nguồn duy nhất cho nhóm 349. Ưu tiên xác minh 6 đoạn ứng viên, tra tên thay thế cho những trường hợp có đầu mối và tìm nguồn riêng cho volume/adaptation. 349 hàng vẫn giữ trạng thái chờ trong v1; overlay mới không tự trừ số hàng chờ. Còn phải chốt catalogue sản phẩm và quyền nội dung trước public. Chưa Day3, training, AI API, database hoặc deploy; không commit/push hay sửa ScoutIQ.
