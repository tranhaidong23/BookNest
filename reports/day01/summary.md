# Day 1 — Thu thập dữ liệu BookNest

## Đã thực hiện
- Giữ cấu trúc và trang khung người dùng đã tạo, thêm cấu hình VS Code và .gitignore.
- Collector standard library Python: scripts/collect_goodbooks.py; pin revision, tải theo luồng, file tạm và SHA-256, không ghi đè raw không khớp.
- Thu thập 5 CSV cùng README/LICENSE. Manifest: ../../docs/DATA_MANIFEST.json.
- Audit ban đầu: data_audit.json.

## Kết quả quan sát
- Sách: 10,000; ratings: 5,976,479; users: 53,424.
- Rating ngoài thang 1–5: 0; rating tham chiếu sách không tồn tại: 0.
- Tag tham chiếu sách không tồn tại: 0; tag ID không tồn tại: 0.
- SHA-256 raw xác minh trước audit. Không làm sạch/đổi raw, chưa mô hình hoặc metrics.

## Chưa xác minh
Duplicate user-book, foreign keys to_read, URL bìa, chất lượng tags, độ phủ/ghép mô tả và quyền hiển thị nội dung public. Không có cột description trong books.csv hoặc timestamp trong ratings.csv. Chưa backup ngoài máy.

## Bước tiếp theo
Audit sâu và kiểm tra nguồn giới thiệu sách. Chốt protocol trước train; chưa xây catalogue production hoặc gọi API AI.

## Câu hỏi phản biện
1. Vì sao dùng dataset này? Có rating thật và ID liên kết metadata để xây đối chứng; tính đại diện bị giới hạn bởi catalogue sách phổ biến.
2. Tái lập dữ liệu thế nào? Pin commit nguồn, ghi URL/size/SHA-256 từng file; chạy lại kiểm hash.
3. Đã chứng minh chất lượng gợi ý chưa? Chưa; audit chỉ chứng minh một số thuộc tính dữ liệu, cần protocol và holdout để đo chất lượng.
