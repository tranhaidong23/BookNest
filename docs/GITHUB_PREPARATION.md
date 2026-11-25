# Chuẩn bị repository GitHub

Ngày25/11/2026, Git local đã khởi tạo nhánh main, origin=https://github.com/tranhaidong23/BookNest.git. Chưa có commit, chưa stage file và chưa push. Repo GitHub được kiểm trước đó là public. Đây là chuẩn bị quản lý mã nguồn, không deploy ứng dụng.

## Các bước đã kiểm

Git check-ignore xác nhận data/, artifacts/, .venv/, .env, .streamlit/secrets.toml, .vscode/ và node_modules/ bị loại. Danh sách `git ls-files --others --exclude-standard` được đối chiếu với inventory sơ bộ; phần khác biệt ban đầu chỉ là hai file báo cáo inventory tự loại để tránh hash đệ quy.

README mới phân biệt clone mã nguồn với workspace đã có dữ liệu/model. Bản cũ giữ trong README_HISTORY_20261125.md; các đường dẫn tương đối trong bản lịch sử được viết theo vị trí README gốc ở root, nên dùng README hiện hành để điều hướng.

## Phạm vi đề xuất trước commit đầu

Mã nguồn app/booknest/scripts/tests, migrations SQL, requirements, cấu hình Streamlit local, README và tài liệu kỹ thuật là nhóm cần rà trước. Reports chứa cả metrics tổng hợp, manifest/hash và các bảng metadata sách dùng nghiên cứu. Không coi toàn bộ reports đã đủ quyền public chỉ vì file nhỏ hoặc không chứa secrets.

Cần kiểm từng báo cáo/source fixture sẽ stage, giữ attribution phù hợp và loại payload nguồn chưa được duyệt. Không thay dữ liệu/artifacts lịch sử để né kiểm quyền: có thể giữ file local và loại khỏi commit, nhưng phải kiểm mọi tham chiếu và hướng dẫn để repo không tuyên bố chạy đủ khi thiếu prerequisites.

Chưa chọn license cho mã nguồn. Không tự áp giấy phép dataset lên toàn dự án. Các terms/rights ghi ở báo cáo lịch sử phản ánh lần nghiên cứu đó; không phải phê duyệt công khai mới cho repository.

## Trình tự tiếp theo

1. Chốt danh sách file đầu tiên, kiểm nội dung và dependencies/đường dẫn của tập file đó.
2. Stage đúng danh sách, đọc diff staged, kiểm lại secrets/file lớn/ignored paths; báo số file và phạm vi cụ thể.
3. Xin phép commit/push trên phạm vi đã review, vì người dùng vẫn giữ chỉ dẫn không tự commit/push/deploy.
4. Sau khi có phép, commit rồi push và xác minh SHA local/remote; không force push hoặc tự deploy.

Không đưa password/token trong remote URL. Địa chỉ origin hiện dùng HTTPS không có credential. Không cần tạo lại repo hoặc sao chép dataset vào Git.

## Giữ nguyên byte khi clone

.gitattributes đặt `* -text` để Git không tự chuyển LF/CRLF. Các evaluator và bằng chứng đã khóa SHA-256 cần giữ nguyên byte, kể cả dấu xuống dòng. Thiết lập này không tắt textual diff. Sau staging cần so blob trong Git index với file local; chỉ kiểm nội dung nhìn giống nhau là chưa đủ. Không sửa các evaluator hoặc manifest đã khóa để đồng nhất line endings.
