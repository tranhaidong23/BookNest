# Day2 — đối chiếu kế hoạch và kiểm mẫu local, 19/11/2026

## Mục tiêu và việc vừa thực hiện

Đọc đủ 8 file được yêu cầu, thêm báo cáo mô tả mới nhất, đối chiếu brief và tạo `docs/PROJECT_PLAN.md` (trước đó chưa tồn tại). Giữ nguyên báo cáo lịch sử. Kiểm lại mẫu XML 20 sách bằng `scripts/check_day02_sample.py`, ghi [sample_check.json](sample_check.json) có thời điểm UTC. Đọc tài liệu nguồn bổ sung, không tải thêm dataset hay gọi API sách/AI. Cập nhật README, HANDOFF và ghi chú hiện hành AGENTS.

| Kiểm tra mới | Kết quả |
|---|---|
| Python .venv | 3.11.9 |
| Hash raw | 7 file khớp manifest trước/sau |
| Hash XML ZIP | Khớp manifest trước/sau |
| Mẫu | Cùng 20 book_id của pilot cũ; seed 20261119, 2 sách/block 1.000 ID |
| XML cùng edition ID và work ID | 20/20 |
| Tựa/tác giả chính nhất quán sau chuẩn hóa | 20/20 |
| Text mô tả không rỗng | 20/20, 100% **trong mẫu** |
| App | app/main.py vẫn chỉ là trang chào |
| Git | Không thấy .git tại project; cả git rev-parse và git -C ... rev-parse lỗi `cannot change to 'C:/Users/Admin'`. Chưa xác minh root/remote bằng Git; không sửa cấu hình Git |
| Full audit / unittest | Không chạy lại ở lượt này |

Kiểm mẫu chứng minh khả năng đọc và liên kết snapshot local, không chứng minh metadata tác giả nguồn nhập luôn đúng, chất lượng ngữ nghĩa hay quyền public. Không suy rộng 100% mẫu thành 100% catalogue. Script đọc 20 XML trong ZIP, dùng index local để định vị rồi kiểm lại ID với CSV gốc; không chỉ tin cờ matching cũ.

## Khác với brief và tài liệu cũ

- Brief và đoạn hiện hành cũ của AGENTS dừng ở audit 4 tests; thực tế đã có scripts/audit_source_descriptions.py, scripts/pilot_descriptions.py, tests/test_descriptions.py và báo cáo mô tả mới hơn.
- **Kết quả lịch sử**, không phải vừa chạy: audit đầy đủ 10.000 XML ghép hai ID, 9.685 có text (96,85%), 315 trống, 358 sách trong hàng đợi. Open Library pilot có 18/20 edition trả về, 15/20 có text, 13/20 có text và tựa/tác giả nhất quán sơ bộ, 7/20 có Goodreads edition ID trùng. Xem [báo cáo trước](../../day01/descriptions_20261119/summary.md).
- 4 tests thuộc audit sâu; 7 tests thuộc lượt mô tả trước. Không đổi nhãn lịch sử thành “vừa passed”.
- Archive XML khoảng 55,8 MB đã tải ở lượt trước; lượt này không tải thêm. Day2 đã có phần kỹ thuật feasibility, **chưa hoàn thành Day2** vì catalogue và quyền còn mở.
- books.csv vẫn không có description; descriptions hiện nằm trong nguồn XML riêng. Chưa có mô hình/metrics, AI, DB hay deploy theo bàn giao; không coi việc chưa thấy cấu hình local là bằng chứng đã kiểm mọi tài khoản cloud.

## Nguồn và điều kiện sử dụng

| Nguồn | Bằng chứng / khả năng lấy | Kết luận phạm vi hiện tại |
|---|---|---|
| Goodbooks XML | Đã có ZIP revision pin, manifest, ID/work và text; kiểm mới mẫu local ở trên. [Nguồn và điều kiện đã ghi lượt trước](../../day01/descriptions_20261119/sources.md) | Ưu tiên nghiên cứu local. Repository công bố CC BY-SA 4.0 không tự xác minh quyền mọi mô tả/bìa bên thứ ba. Chưa duyệt public |
| Open Library | API pilot/cache lịch sử; vừa đọc lại [licensing](https://openlibrary.org/developers/licensing) | Trang nêu không khẳng định quyền mới và có thể có quyền tồn tại trên đóng góp. Chưa xác minh từng text/bìa; không mặc định public domain |
| Google Books | Vừa đọc lại [terms](https://developers.google.com/books/terms), tài liệu API đã đọc ở lượt trước; chưa gọi API | Có điều kiện về phí ứng dụng và gỡ nội dung. Chưa đo độ phủ hoặc duyệt public; chỉ là phương án dự phòng |
| UCSD Book Graph | [Trang Books](https://sites.google.com/eng.ucsd.edu/ucsdbookgraph/books) có schema description/book_id/work_id/ISBN; công bố metadata toàn bộ khoảng 2 GB. [Trang chủ cũ](https://sites.google.com/eng.ucsd.edu/ucsdbookgraph/home/) ghi academic use only, không phân phối lại/không dùng thương mại và thông báo chuyển trang | Chỉ kiểm tài liệu, chưa tải hoặc đo overlap với Goodbooks. Trang mới https://mengtingwan.github.io/data/goodreads.html không trả nội dung đọc được qua công cụ ở lượt này; endpoint tải mới và điều kiện hiện hành chưa xác minh. Không dùng làm nguồn public lúc này |

Nhận định quyền ở đây là trạng thái kiểm nguồn, không phải kết luận pháp lý toàn diện. Không gửi email xin quyền, đăng ký tài khoản hoặc thay đổi dịch vụ bên ngoài. Nguồn mới nhiều dữ liệu hơn không đồng nghĩa giải quyết được quyền public.

## Quyết định và blockers

1. Kế thừa kết quả đã có, chỉ kiểm mới mẫu local; tránh tải/chạy lại toàn bộ không cần thiết.
2. Giữ catalogue nghiên cứu và catalogue sản phẩm là hai khái niệm rõ ràng. Chưa thu hẹp catalogue để làm đẹp metrics; chưa áp dụng bộ lọc dựa trên kết quả test.
3. Chưa chốt quyền mô tả/bìa và chưa rà xong nội dung: blocker cho nghiệm thu catalogue public, không cản tiếp tục nghiên cứu local. Cần review 358 sách, xác minh nguồn hoặc dùng nguồn thay thế có điều kiện phù hợp, log tiêu chí đưa vào catalogue.
4. Cơ chế auth, AI provider, chi phí/tài nguyên Neon/Render và protocol chi tiết chưa chốt. Chúng nằm ở mốc sau; không đổi hosting hay mở rộng triển khai ở lượt feasibility.
5. Git CLI lỗi môi trường ở trên; không cần khởi tạo/sửa Git để hoàn thành mốc tài liệu và kiểm mẫu. Khi có yêu cầu Git, phải xác minh lại trước thao tác.

## Tái lập và file

```text
.venv\Scripts\python.exe -B scripts/check_day02_sample.py
```

Lệnh không gọi mạng, giữ báo cáo Day1; chạy lại cập nhật sample_check.json của mốc Day2. File mới: PROJECT_PLAN.md, script kiểm mẫu, báo cáo này, sample_check.json. Chỉ cập nhật tài liệu hiện hành khác, không sửa raw, manifest, app hoặc tests. Không commit/push/deploy, không thay đổi ScoutIQ, không train/gọi AI.

## Câu hỏi phản biện

- **Vì sao mẫu 100% mà toàn bộ 96,85%?** Mẫu nhỏ có thể không chứa sách trống; số toàn bộ kế thừa audit có mẫu số 10.000, không thay bằng tỷ lệ mẫu.
- **Khớp ID đã bảo đảm nội dung đúng?** Chỉ kiểm liên kết và nhất quán nguồn; text có thể là placeholder/nhầm nội dung dù ID khớp.
- **Vì sao chưa dùng UCSD cho public?** Schema có ích, nhưng điều kiện công bố hạn chế phân phối lại; cần xác minh quyền, không chỉ tải được file.
- **Day2 xong chưa?** Đã kiểm feasibility và có bằng chứng mapping/coverage; quyền và catalogue chưa nghiệm thu nên vẫn đang làm.

Bước kế tiếp đề xuất: hoàn tất review ưu tiên và chính sách catalogue/quyền trong Day2; sau đó mới triển khai cleaning/protocol theo PROJECT_PLAN. Không tự khởi chạy các mốc sau trong lượt này.
