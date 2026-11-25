# Kiểm tra tái lập local

Mốc 25/11/2026 kiểm tra môi trường hiện có; chưa dựng lại trên máy trống.

## Trước demo

Chạy tại thư mục BookNest:

```powershell
.venv\Scripts\python.exe -B scripts/check_local_readiness.py
.venv\Scripts\python.exe -B -m unittest discover -s tests
.venv\Scripts\python.exe -m streamlit run app/main.py
```

Lệnh đầu chỉ đọc file và in JSON, exit code 0 khi đạt, 1 khi phiên bản hoặc hash không khớp. Lỗi đọc manifest cũng làm lệnh thất bại. Kiểm Python 3.11, các phiên bản pin trong requirements (gồm psycopg-binary), 88 mục khóa Day10, 5 inputs, 32 outputs và 5 liên kết bằng chứng. Các nhóm có thể cùng tham chiếu một file; 130 là số mục kiểm, không phải cam kết 130 file riêng biệt. Hash input có đọc bytes của file test đã mở trước đây, không phân tích ratings hoặc tính lại metrics.

Nếu sai hash, giữ file và báo cáo lỗi để điều tra; không sửa manifest hoặc chạy lại training để che khác biệt. Công cụ này không kiểm toàn bộ raw/catalogue, không xác nhận semantic correctness, không kiểm provider/DB hoặc mọi dependency bắc cầu. Mốc kiểm toàn dữ liệu trước đây vẫn là bằng chứng riêng.

Demo mặc định dùng session local; đóng phiên có thể mất dữ liệu. Chế độ postgres cần cấu hình server và provider thực chưa nghiệm thu. Xem [vận hành](LOCAL_OPERATIONS.md) và [demo](LOCAL_DEMO.md).

## Phân biệt ba mức tái lập

1. **Integrity hiện có:** các file đang giữ khớp manifest. Đã kiểm 25/11.
2. **Replay tính toán:** chạy lại evaluator và verifier để tính kết quả. Đợt này không chạy; Day10 cũng chưa replay toàn CLI lần hai. Test đã xem, không dùng để tuning.
3. **Dựng từ môi trường sạch:** tạo Python environment mới, cài dependencies, khôi phục dữ liệu/artifacts từ bản có provenance và kiểm đầy đủ. Chưa thực hiện. requirements chỉ pin gói trực tiếp; chưa có lock đầy đủ dependencies/wheels hoặc backup ngoài máy được xác minh.

Không coi việc sao chép .venv là quy trình portable. Trước diễn tập máy mới cần xác định Python/OS, nguồn cài offline hoặc network được phép, native PostgreSQL và dung lượng; các fixture hiện mặc định PostgreSQL tại `C:/Program Files/PostgreSQL/18/bin`.

## Những lệnh cần lưu ý khi tái lập

Một số scripts lịch sử có đường dẫn output cố định theo ngày, có thể ghi đè báo cáo cũ. Không chạy hàng loạt theo tên file. Đọc từng script, chọn output mới hoặc làm trong bản workspace riêng đã kiểm đường dẫn trước khi replay. Không sửa source evaluator đã khóa chỉ để đổi đường dẫn rồi gọi đó là cùng một lần chạy.

Restore hiện chỉ được diễn tập giữa hai database trong cùng cluster tổng hợp; không có archive backup thực được giữ lại. Không suy ra khả năng phục hồi mất máy, cross-cluster hay Neon/PITR. Không đưa secrets/datasets/.venv lên Git.
