# Catalogue và làm sạch — v0.2, 20/11/2026

## Quyết định hiện hành — người dùng đã chốt phạm vi

Ngày 20/11/2026, người dùng xác nhận “ok chốt” phương án giữ benchmark, cho phép thiếu mô tả và tách việc nghiệm thu public khỏi tiến độ khoa học dữ liệu. Quyết định này thay thế yêu cầu cũ phải có mô tả/intro đủ quyền cho toàn bộ catalogue mới kết thúc Day2.

- Giữ 10.000 book_id cùng ratings cho nghiên cứu; không lọc candidate set chỉ vì thiếu mô tả. Các quy tắc loại sách đã đọc hoặc điều kiện đánh giá được định nghĩa riêng trong protocol.
- Phạm vi sản phẩm dự kiến giữ các sách đó; quyền metadata công khai vẫn phải kiểm trước phát hành. Sách không có mô tả được duyệt hiển thị đúng câu “Chưa có mô tả được xác minh”. Không hiển thị raw description, bản dịch hoặc đoạn AI chưa được duyệt.
- Bìa dùng placeholder do dự án tự tạo nếu chưa có bằng chứng quyền và mapping ảnh. Đây là yêu cầu triển khai; asset và UI fallback chưa được tạo ở mốc chốt.
- Tách ba cổng: metadata đủ điều kiện hiển thị sách; mô tả/intro đủ điều kiện hiển thị văn bản; ảnh đủ điều kiện hiển thị bìa. Thiếu mô tả/ảnh không tự loại sách khi metadata đã đủ điều kiện. Helper public_ready hiện có chỉ phục vụ cổng intro, chưa phải cổng xuất bản toàn bộ sách.
- Sáu đoạn Wikipedia ứng viên được ưu tiên xác minh tiếp trong backlog nội dung; chưa được duyệt nội dung/quyền. Hai đoạn mỏng và các hàng còn thiếu tiếp tục để thiếu. Không cần lấp hết 349 hàng để bắt đầu Day3; 9.651 ứng viên text cũng không mặc định được phép public.
- Đóng Day2 theo phạm vi đã điều chỉnh: khảo sát nguồn/mapping/coverage, catalogue local v1 và policy fallback đã chốt. Không coi đây là nghiệm thu public hoặc hoàn tất xác minh sáu đoạn. Day3 là bước tiếp theo: derived/cleaning, EDA và protocol; chưa thực hiện tại mốc chốt.

Giữ payload catalogue v1 và source overlay nguyên. Nếu thay dữ liệu, tạo version mới với manifest và log; không cần tạo catalogue v2 chỉ để đổi quyết định tài liệu. [Biên bản chốt và backlog](../reports/day02/closure_20261120/summary.md). Các phần v0.1 dưới đây là lịch sử; quy tắc bảo toàn raw, identity, provenance và không bịa nội dung vẫn áp dụng.

## Bổ sung: catalogue local v1 đã đóng băng

Artifact `data/processed/catalogue_v1/catalogue.jsonl`; [manifest](../reports/day02/catalogue_v1_20261119/manifest.json) có SHA-256 và input. 10.000 sách benchmark, 9.651 ứng viên text, 0 intro hiện đủ gate public. Script freeze_day02_catalogue.py từ chối ghi đè payload khác; thay đổi sau cần version mới. Không phải catalogue sản phẩm đã nghiệm thu.

Nguồn mở bổ sung được nghiên cứu: [Wikipedia text cộng đồng và mẫu 3 tác phẩm](../reports/day02/catalogue_v1_20261119/source_decisions.md); chưa có phép suy rộng quyền hoặc coverage cho toàn catalogue. Các quyết định v0.1 bên dưới vẫn áp dụng.

## Quyết định cho bước local tiếp theo

Giữ **10.000 book_id trong benchmark**; thiếu mô tả không phải lý do xóa rating hoặc loại sách khỏi đánh giá collaborative filtering. Chưa chốt catalogue public. Danh sách 9.651 ứng viên sàng lọc text chỉ phục vụ review, không phải danh sách đã duyệt nội dung/quyền/giới thiệu 60–100 từ. Không dùng nó làm bộ lọc train/test mặc định.

Trạng thái mỗi sách cần tách: identity (edition/work), content (missing/reviewed/needs evidence), rights (unresolved/verified với bằng chứng), scope (work/edition/series), intro (not generated/reviewed). Không suy ra quyền từ text dài hay khớp ID. Review do Codex agent không phải review độc lập của người chấm.

## Kết quả triage hàng đợi

315 mô tả rỗng: giữ null, cần nguồn. 9 cờ tựa: giải thích được bằng alias/series/phụ đề/tựa lặp; giữ tựa CSV và lưu alias XML, chỉ đóng cờ tựa. 22 đoạn ngắn: cần thêm bằng chứng trước giới thiệu 60–100 từ, không khẳng định chúng sai. 1 placeholder nhập liệu (4280): không dùng làm nguồn giới thiệu. 11 sách có text trùng giữa các tập: giữ book_id riêng, cần mô tả đúng tập.

Các chi tiết quan trọng: 4622 là bản kịch, không thay bằng tiểu thuyết cùng tên; 8027 có text companion journal, chưa kết luận edition sai nhưng cần đối chiếu; 7408 là bản chuyển thể có nhân vật hổ, không thay bằng cốt truyện quen thuộc. 9134/706 chứa chi tiết edition/bản dịch, không gán những chi tiết đó cho mọi edition cùng work. Không xóa số tập/bản dịch để tăng tỷ lệ ghép.

## Quy tắc derived dự kiến áp dụng ở Day3

1. Raw/ZIP/cache và manifest giữ nguyên. Mọi giá trị mới có source ID/URL/revision/hash, rule version và lý do. Invalid/missing là null với flag, không là số 0.
2. ISBN lấy từ XML cùng edition/work, kiểm checksum và kiểm trường hợp ISBN dùng chung trước join. Không khôi phục độ chính xác ISBN13 CSV bằng phép đoán. ISBN không thay book_id làm khóa chính.
3. Text gốc tách text chuẩn hóa; bỏ markup/script/style và chuẩn hóa whitespace, giữ ngôn ngữ/dấu. Chưa có text thì không sinh AI. Ngưỡng 80 ký tự chỉ là cờ rà soát, không đủ duyệt chất lượng. Text không được tự kéo dài để đạt 60–100 từ.
4. Tags: chỉ loại bản sao giống hệt sau kiểm; khóa trùng count khác cần quyết định riêng, không cộng mù. Count âm cách ly khỏi features, ghi log; genre dùng allowlist có căn cứ. `to_read` là tín hiệu riêng, giao ratings không tự là lỗi và không là negative.
5. Không đổi nhãn ratings. Không dùng average_rating, popular_shelves, similar_books hoặc reviews toàn nguồn để lén đưa tín hiệu test vào engine. Content từ mô tả phải đánh giá provenance và leakage trước dùng.
6. Nếu catalogue sản phẩm về sau thu hẹp, đóng băng tiêu chí trước đánh giá và báo lượng sách/users/ratings bị tác động. So sánh model cùng candidate set; cold-start vẫn cần protocol user-held-out riêng.

## Quyền nguồn và hướng public

Quyền mô tả, quyền bìa và quyền tạo bản dịch/tóm lược là các mục riêng. Một URL truy cập được không là bằng chứng đủ quyền. Chưa tải bìa hoặc xác minh quyền từng ảnh. Có thể dùng bìa placeholder do dự án tự tạo khi triển khai, nhưng không coi đó là đã hoàn thành yêu cầu giới thiệu.

- Goodbooks công bố CC BY-SA 4.0 ở repository; chưa xác minh quyền bên thứ ba đối với từng mô tả/bìa. Giữ attribution và chuỗi nguồn; chưa duyệt toàn bộ public.
- [Open Library licensing](https://openlibrary.org/developers/licensing) còn nêu quyền có thể tồn tại trên đóng góp. Không coi mọi text/bìa là public domain.
- [Google Books branding](https://developers.google.com/books/branding) yêu cầu attribution, liên kết và không sửa nội dung API; [terms](https://developers.google.com/books/terms) có điều kiện phí/gỡ nội dung. Vì kế hoạch cần dịch/tóm lược, **không tự coi API là nguồn đã cho phép biến đổi**; cần làm rõ điều kiện trước chọn. Đây là quyết định thận trọng của dự án, không phải kết luận pháp lý rằng mọi tóm lược đều bị cấm.
- UCSD: ghi nhận hạn chế academic/no redistribution ở báo cáo feasibility; chưa được duyệt cho public, chưa tải thêm.

Phương án tiếp: tìm nguồn có điều khoản cho phép sử dụng phù hợp hoặc xin quyền chủ thể; nếu cần liên hệ, chuẩn bị yêu cầu cụ thể nhưng không tự gửi. Với nguồn public-domain/giấy phép mở vẫn phải kiểm đúng phiên bản, phạm vi lãnh thổ và quyền riêng của bìa/bản dịch. Chưa cam kết số sách đạt cổng quyền. Nghiên cứu local và chuẩn bị protocol vẫn tiếp tục được; nghiệm thu public chưa hoàn tất.

## Cổng nghiệm thu v0.1 — lịch sử, thay bằng v0.2 phía trên

Benchmark local: 10.000 ID giữ nguyên, raw verified, cleaning policy có version. Catalogue sản phẩm: đúng identity + đủ nội dung + quyền có bằng chứng + intro đã kiểm; hiện chưa nghiệm thu. Không đánh dấu Day2 hoàn tất quyền/public chỉ vì triage đã xong.
