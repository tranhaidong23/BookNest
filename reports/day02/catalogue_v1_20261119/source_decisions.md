# Quyết định nguồn bổ sung — 19/11/2026

## Kết luận khả thi

Catalogue local v1 đã đóng băng; chưa có catalogue sản phẩm đủ điều kiện nghiệm thu. Không tiếp tục coi việc đọc lại cùng điều khoản là tiến bộ về quyền. Hướng mới: **ưu tiên thử văn bản cộng đồng Wikipedia có giấy phép rõ ràng cho giới thiệu cấp tác phẩm**, thay vì mặc định dịch mô tả nhà xuất bản từ Goodreads/Google Books. Đây là hướng nguồn, chưa phải pipeline đã triển khai hoặc lời hứa độ phủ.

## Quyền và điều kiện đã đọc

[CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/) cho phép chia sẻ và tạo bản sửa đổi với attribution, chỉ rõ sửa đổi và ShareAlike; giấy phép không bảo đảm mọi quyền cần thiết. Không thể dùng nhãn giấy phép repository để tự chứng minh người cấp có quyền trên từng ảnh/đoạn trích của bên khác.

[Wikimedia Terms of Use, mục 7](https://foundation.wikimedia.org/wiki/Policy:Terms_of_Use#7._Licensing_of_Content) nêu cách tái sử dụng văn bản cộng đồng, ghi công bằng liên kết về bài/lịch sử, đánh dấu sửa đổi và giấy phép cho bản sửa đổi. Nội dung fair-use, phần nhập từ nguồn khác và media có điều kiện riêng. Trước dùng phải kiểm footer/lịch sử/thảo luận và ghi chú của phần lấy. Hướng chọn: chỉ đoạn mô tả bằng lời của cộng đồng; loại ảnh và trích dẫn của bên thứ ba khỏi nguồn tóm lược.

Attribution dự kiến khi đủ điều kiện: “Giới thiệu tiếng Việt được tóm lược/chuyển ngữ từ [tên bài, revision] của các tác giả Wikipedia; nội dung đã được sửa đổi; CC BY-SA 4.0.” Liên kết bài/revision, history và giấy phép; ghi model/prompt/reviewer nội bộ. Bản giới thiệu theo ShareAlike, không suy diễn rằng toàn bộ code ứng dụng phải đổi giấy phép. Chưa tạo bản giới thiệu ở lượt này.

[Google Books branding](https://developers.google.com/books/branding) yêu cầu attribution/liên kết và không sửa nội dung API: giữ làm nguồn tra cứu, chưa duyệt cho dịch/tóm lược. [Open Library licensing](https://openlibrary.org/developers/licensing) không bảo đảm mọi đóng góp hết quyền bên khác. UCSD giữ trạng thái như feasibility trước, không tải thêm.

## Thử đối chiếu mới: 3 tác phẩm có chủ đích

| Goodbooks book_id / work_id | Tựa/tác giả CSV | Trang đã đọc | Kết quả |
|---|---|---|---|
| 113 / 814330 | Catch-22 — Joseph Heller | https://en.wikipedia.org/wiki/Catch-22 | Tựa/tác giả và loại tác phẩm phù hợp; có intro/synopsis. Phần synopsis có cờ văn phong quảng bá, cần loại lời đánh giá chủ quan |
| 400 / 909457 | Neuromancer — William Gibson | https://en.wikipedia.org/wiki/Neuromancer | Tựa/tác giả phù hợp; có intro/plot |
| 413 / 1263212 | The Three Musketeers — Alexandre Dumas | https://en.wikipedia.org/wiki/The_Three_Musketeers | Tựa/tác giả phù hợp; có intro/plot; bài có nhắc cộng tác giả, cần giữ căn cứ nếu đưa chi tiết này vào giới thiệu |

**3/3 trang truy cập được và có nội dung cấp tác phẩm.** Đây là mẫu chọn có chủ đích từ sách nổi tiếng đã biết, không phải tỷ lệ phủ 10.000 hoặc 349 sách đang thiếu nguồn. Không có mapping ID trực tiếp Wikipedia–Goodreads ở thử này; chỉ đối chiếu tựa/tác giả/loại tác phẩm. Không kết luận đúng edition, bản dịch, ISBN hay bìa. Không tự sửa bảng catalogue v1 bằng kết quả thăm dò.

Ban đầu web tool gặp cache miss ở permanent link Catch-22. Sau đó đã tải trực tiếp thành công đúng 3 trang HTML, lưu cache và SHA-256 trong `data/external/wikipedia/day02_pilot/`; [wikipedia_fetch.json](wikipedia_fetch.json) ghi thời điểm, revision đọc từ `wgRevisionId` và khai báo license của trang. Revisions: Catch-22 1384221665; Neuromancer 1384220887; The Three Musketeers 1386075581. Cả 3 có khai báo CC BY-SA 4.0. Đây là snapshot HTML có hash tái lập, chưa phải đã rà mọi nội dung bên thứ ba trong bài. Không tải file ảnh hoặc dataset hàng loạt.

## Việc còn phải hoàn tất cho public

1. Mở rộng pilot nguồn mở trên mẫu bao gồm cả sách ít phổ biến và nhóm 349, tiếp tục lưu revision/hash như 3 mẫu vừa kiểm và kiểm nội dung/giấy phép phần thực dùng. Tránh chỉ lấy sách nổi tiếng để tuyên bố độ phủ.
2. Đóng băng danh sách sản phẩm theo tiêu chí nguồn/mapping/quyền, báo ảnh hưởng đến recommendation candidate set. Chưa có con số minimum catalogue được thống nhất; không tự coi 3 sách là catalogue đủ dùng cho Top 10.
3. Giới thiệu 60–100 từ, rubric 30–50 mẫu và AI API thuộc mốc sau; không tạo sớm chỉ để đánh dấu Day2 đã hoàn tất. Bìa dùng placeholder tự tạo cho tới khi có bằng chứng từng ảnh; không lấy cover Wikipedia mặc định.

Nguồn mở là phương án cụ thể tiếp theo; chưa phải giấy phép cho toàn bộ dữ liệu Goodbooks hoặc nghiệm thu toàn bộ Day2.
