# Day2 — đóng băng catalogue local v1

Ngày 19/11/2026. **Đã hoàn tất phần catalogue local và bàn giao kỹ thuật Day2. Chưa nghiệm thu toàn bộ Day2 theo yêu cầu catalogue sản phẩm/quyền public.** Không đổi định nghĩa “hoàn tất” để che phần còn thiếu.

## Kết quả mới chạy

- `scripts/freeze_day02_catalogue.py` tạo `data/processed/catalogue_v1/catalogue.jsonl`: 10.000 book_id duy nhất, ID Goodreads edition/work, nguồn/revision/hash, trạng thái nội dung/quyền/intro, benchmark_include=true. Không chứa toàn văn mô tả, ratings hoặc secrets.
- Catalogue v1 bất biến: chạy lại nếu payload khác sẽ dừng, phải tạo version mới. [manifest.json](manifest.json) chứa hash artifact và input, thống kê và thời điểm.
- 9.642 text chưa được review nghĩa + 9 cờ tựa đã giải thích = 9.651 ứng viên sàng lọc; 315 thiếu + 22 thiếu bằng chứng + 11 cần phân biệt tập + 1 placeholder = 349 giữ chờ. Không gán 9.651 thành “được duyệt”.
- 0 bản giới thiệu đủ gate public hiện tại. Lý do đồng thời: chưa tạo/review intro, chưa kiểm đủ nội dung và quyền; không có nghĩa tất cả nguồn chắc chắn bị cấm.
- Gate kiểm identity + content + intro đã review 60–100 từ + quyền hiển thị/chuyển thể có evidence. Gate là helper/test local, **chưa tích hợp app hay cơ chế bảo mật production**. Quyền bìa độc lập; bản ghi chỉ yêu cầu placeholder, chưa tạo asset bìa.
- Kiểm hash 7 raw và ZIP trước/sau, xác minh review output khớp manifest; không sửa raw. Kết quả tests mới trong validation.json; 9 tests của mốc trước là lịch sử.

## Quyết định đã chốt

Benchmark nghiên cứu: 10.000 sách, không loại vì thiếu mô tả; không sửa ratings. Nguồn metadata local: Goodbooks XML cùng revision. Catalogue sản phẩm: chỉ xét sách qua gate nội dung/quyền, nhưng danh sách cuối chưa đủ bằng chứng để chốt. Không lấy danh sách 9.651 làm bộ lọc train/test.

Đã tìm và thử hướng nguồn bổ sung có điều kiện tái sử dụng rõ hơn: Wikipedia text cộng đồng, scope tác phẩm, attribution/ShareAlike. Đọc 3 trang mẫu và đối chiếu CSV; 3/3 có nội dung/tựa/tác giả phù hợp, mẫu có chủ đích không đại diện. Đã cache HTML cả 3, xác minh revision, SHA-256 và khai báo CC BY-SA 4.0; chưa duyệt quyền từng đoạn bên thứ ba/ảnh. Chi tiết ở [source_decisions.md](source_decisions.md) và [wikipedia_fetch.json](wikipedia_fetch.json). Không tải ảnh, không AI, không bulk download.

## Trạng thái nghiệm thu

| Hạng mục Day2 | Trạng thái |
|---|---|
| Nguồn local, mapping, coverage | Đã có bằng chứng |
| Triage hàng đợi và cleaning policy | Đã có ở mốc trước |
| Catalogue local versioned + manifest | Vừa hoàn thành |
| Chính sách và kiểm gate public | Vừa có helper/test; chưa tích hợp ứng dụng |
| Danh sách catalogue sản phẩm đủ nguồn/quyền | Chưa hoàn tất |
| Quyền bìa/giới thiệu của từng sách | Chưa hoàn tất |

Có thể chuyển công việc local sang Day3 khi được yêu cầu, dùng catalogue v1; không phải chờ public mới nghiên cứu. Nhưng không đánh dấu toàn bộ Day2 “done” hoặc coi app có thể public. Nếu tiếp tục đúng phần Day2 còn thiếu: pilot Wikipedia trên mẫu đa dạng và pin nguồn, rồi chốt danh sách sản phẩm có bằng chứng. Không cần xin lại quyền làm local; chỉ xin phép nếu thực sự cần gửi yêu cầu quyền cho bên ngoài.

## Tái lập / giới hạn

```text
.venv\Scripts\python.exe -B scripts/freeze_day02_catalogue.py
.venv\Scripts\python.exe -B -m unittest discover -s tests -v
```

Lệnh đầu không gọi mạng, không ghi đè catalogue khác nội dung; cập nhật manifest kiểm tra của mốc này. Chưa chạy cleaning/split/model/AI/DB/deploy; không commit/push hoặc thay đổi ScoutIQ. Phần bổ sung nguồn chỉ nghiên cứu feasibility. Không báo coverage mẫu 3 sách là độ phủ nguồn mở toàn catalogue.
