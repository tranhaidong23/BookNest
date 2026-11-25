# Day 1 tiếp tục — audit dữ liệu, 19/11/2026

## Mục tiêu và phạm vi
Hoàn tất script khám phá và audit sâu snapshot Goodbooks-10k trước làm sạch/huấn luyện. Người dùng đã chuyển sang cho phép thực hiện trực tiếp và báo cáo. Giữ nguyên raw; chưa giao diện mới, mô hình, AI, Neon hoặc Render.

## Công việc và file
- `scripts/explore_data.py`: đọc metadata, kiểm mã sách không trùng rồi ghép 5 ratings đầu; thống kê thiếu trường.
- `scripts/audit_extended.py`: 5 CSV + manifest → audit.json và 3 CSV tổng hợp trong thư mục báo cáo này; chạy từ bất kỳ cwd.
- `tests/test_audit_extended.py`: 4 tests bằng unittest; phân biệt cặp lặp với nhãn xung đột và kiểm checksum ISBN.
- `requirements.txt`: khai báo đúng hai dependency trực tiếp đang dùng (Streamlit và pandas); môi trường quan sát ở environment.json/environment-freeze.txt. Không cài package mới; chưa fresh-install/Render verification.
- Version nguồn giữ nguyên theo ../../../docs/DATA_MANIFEST.json. Nguồn: https://github.com/zygmuntz/goodbooks-10k . Không tải dữ liệu mới ở lượt này.

## Kết quả thực
| Kiểm tra | Kết quả |
|---|---:|
| Sách | 10,000 |
| Người dùng | 53,424 |
| Ratings | 5,976,479 |
| Rating trùng cặp / nhãn xung đột | 0 / 0 |
| Rating ngoài 1–5 / ID sách không tồn tại | 0 / 0 |
| Danh sách muốn đọc | 912,705 |
| Muốn đọc trùng cặp / ID người dùng hoặc sách không tồn tại | 0 / 0 |
| Cặp vừa có rating vừa muốn đọc | 2,200 |
| Tag trùng khóa (dòng dư) | 8 |
| Tag có count âm | 6 |
| Thiếu ISBN / ISBN13 / ngôn ngữ | 700 / 585 / 1.084 |

Mật độ cặp quan sát: 1.1187%. 1% sách được đánh giá nhiều nhất chiếm 17.09% ratings. Đây là mô tả dataset, không phải metric chất lượng gợi ý. `average_rating` và số lượng rating trong metadata toàn nguồn không được dùng như thống kê train khi kiểm thử holdout.

## Phát hiện và hướng xử lý dự kiến
- Không cần deduplicate ratings trong snapshot hiện tại; không áp dụng lọc hoặc sửa nhãn.
- ISBN13 raw dùng biểu diễn số khoa học; ISBN10 có chuỗi ngắn. Kiểm checksum raw thất bại không đủ kết luận ISBN gốc sai. Không tự khôi phục độ chính xác đã mất hoặc ghép mô tả dựa trên chuỗi chưa xác minh. Ưu tiên mapping ID tác phẩm/edition, sau đó tác giả/tựa để đối chiếu.
- Tags gồm `to-read`, `currently-reading`, `favorites`, `owned` cùng tên thể loại. Cần taxonomy allowlist có review; không coi toàn bộ shelves là genre. Các dòng trùng/âm phải có chính sách xử lý trước khi dùng content features.
- `to_read` là tín hiệu riêng; 2.200 cặp chồng không mặc nhiên là lỗi vì không có timestamp đối chiếu. Không dùng làm nhãn tiêu cực.
- Năm không dương có thể là năm trước Công nguyên; chỉ gắn cờ, không tự sửa. Mô tả chưa có trong books.csv. Không gọi AI để bịa giới thiệu.

## Kiểm chứng và giới hạn
4/4 tests đạt, script khám phá chạy được, audit toàn bộ 5 CSV hoàn tất. Hash raw khớp manifest trước và sau. Chưa có quality metrics: giữ null. Chưa xác minh URL bìa, độ phủ mô tả, quyền hiển thị nội dung bên thứ ba, backup ngoài máy hoặc cài mới. Chưa tạo Git repo/remote, chưa commit/push/deploy. Data/.venv/artifacts đã có quy tắc ignore; cần kiểm bằng Git khi khởi tạo repo.

## Bước tiếp theo
Thu thập thử mô tả từ nguồn có ID, kiểm mapping và tỷ lệ phủ; chốt catalogue và chính sách làm sạch tags/ISBN. Sau đó EDA sâu và protocol train/validation/test; chưa chạy training trong mốc này.

## Phản biện
1. **Vì sao audit trước train?** Cặp trùng có thể xuất hiện cả train/test, tags nhiễu và metadata tổng hợp có thể gây leakage hoặc làm sai giải thích.
2. **Độ thưa 98,88% có nghĩa người dùng không thích phần còn lại?** Không. Cặp chưa quan sát là unknown, không tự chuyển thành rating 0.
3. **Có thể dùng ISBN để lấy mô tả ngay không?** Cần xác minh biểu diễn nguồn và edition; hiện chưa đủ để tin mọi chuỗi ISBN.
4. **4 tests chứng minh mô hình tốt chưa?** Chưa. Chúng kiểm helper audit; chất lượng recommender cần đối chứng trên dữ liệu giữ lại.
