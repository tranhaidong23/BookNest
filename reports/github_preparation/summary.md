# Chuẩn bị GitHub ngày25 tháng11 năm2026

## Kết quả kiểm trước commit

Đã stage tập mã nguồn/tài liệu; giữ bảng metadata matches.json ngoài Git. .gitattributes * -text ngăn Git tự đổi LF/CRLF làm sai SHA-256 evaluator.70tests đạt ngoài sandbox (3,585giây); chạy trong sandbox trước đó kẹt ở socketpair khi Streamlit tạo asyncio loop, đã ngắt; lần chẩn đoán có timer45giây xác nhận stack và thoát. Không sửa model để khắc phục.130mục hash Day10 vẫn khớp. Staged blobs được đối chiếu byte với worktree và quét patterns, không có forbidden paths; scope không phải legal approval hoặc full secret audit. Chưa commit/push.

## Bổ sung sau kiểm Git thực tế

Đã khởi tạo Git local trên main và cấu hình origin đúng repo người dùng; chưa stage/commit/push. git_validation.json ghi danh sách ứng viên và kiểm7ignored paths bằng Git thật, không phải suy từ script inventory. Các dòng “chưa init” phía dưới là kết quả lượt trước. Báo cáo có metadata nghiên cứu, chưa duyệt toàn bộ để public. docs/GITHUB_PREPARATION.md ghi trình tự và giới hạn tiếp theo.

Repo được người dùng cung cấp: https://github.com/tranhaidong23/BookNest. Lượt kiểm connector xác nhận public. Workspace chưa có .git; chưa init, stage, commit hoặc push. Mục tiêu tự động được người dùng bật lại sau khi đã tạm dừng, nhưng giới hạn commit/push/deploy vẫn giữ nguyên.

Đã viết lại README: trạng thái hiện hành, kết quả, cài Python, prerequisites artifacts, cách chạy và giới hạn tái lập. Bản cũ giữ trong docs/README_HISTORY_20261125.md. Thêm .vscode/ vào .gitignore để loại cấu hình editor local.

scripts/review_public_files.py lập danh sách paths/bytes/hashes và quét một số dạng token/key/DSN, binary/file lớn và notebook outputs; không in giá trị nghi là secret. Loại data/artifacts/.venv/node_modules/secrets/editor settings. Không dùng Git ignore engine và chưa đọc Git index, vì vậy inventory không phải danh sách staged thực tế. Không coi không có pattern match là chứng minh không có secrets hoặc đã đủ quyền public.

inventory.json ghi kết quả cuối của lượt chuẩn bị. Trước commit/push vẫn cần kiểm Git index thực tế và duyệt nội dung báo cáo, metadata, quyền nguồn. Chưa có license mã nguồn được người dùng chọn; không tự gán license của dataset cho project. Không đưa datasets/model artifacts vào commit để làm app chạy ngay khi clone; README nói rõ các file còn cần.

Không đổi model, raw, catalogue hoặc test metrics. Không gọi cloud AI, không deploy hoặc sửa ScoutIQ.

Kết quả lượt cuối:189file ứng viên,807.306bytes, không match các pattern đã định nghĩa. Hai tests mới của inventory đạt: loại vùng nhạy cảm/không in token và phát hiện notebook có output. Không chạy lại full suite ở mốc này;68tests toàn dự án là kết quả readiness trước, không báo thành70tests vừa chạy. Chưa kiểm quyền nội dung của189file hoặc Git index thực tế.
