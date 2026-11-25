# Day15 — giới thiệu có nguồn và kiểm nội dung

Phần local đã có `booknest/content_review.py` và CLI `scripts/prepare_content_review.py`. Không gọi API AI, không ghi database, không tự duyệt mô tả. Giải thích gợi ý hiện dùng cạnh Item-KNN thật và mẫu câu; không cần LLM để nói vì sao một sách được gợi ý.

## Gói bằng chứng

Mỗi JSON packet gồm `book_id`, `title`, `authors`, `source_scope` (work/edition), `source_entity_id`, `target_entity_id`, `source_url` HTTPS, `source_revision`, `source_text`, `source_text_sha256`, `evidence`.

Mỗi evidence có `id`, `start`, `end`, `quote`. Offset đếm ký tự Python Unicode, end không bao gồm ký tự cuối; quote phải bằng chính xác `source_text[start:end]`. Hash SHA-256 tính trên UTF-8 của source_text, không phải hash file JSON hoặc HTML gốc. Giữ cả hash HTML/snapshot gốc trong hồ sơ nguồn riêng; không thay thế manifest raw.

Hai entity ID là chứng cứ để người kiểm đối chiếu, **không được coi khớp chỉ vì chuỗi giống nhau**. Tựa/tác giả/edition phải được người kiểm đối chiếu với nguồn đã lưu. Không gửi packet có nguồn chưa được phép truyền tới một provider bên ngoài. CLI hiện chỉ tạo prompt local, không quyết định quyền sử dụng.

```powershell
.venv\Scripts\python.exe -B scripts/prepare_content_review.py data/dev/review/packet.json --output data/dev/review/prompt-v1.json
.venv\Scripts\python.exe -B scripts/prepare_content_review.py data/dev/review/packet.json --draft data/dev/review/draft.json --model-version human-draft --output data/dev/review/review-v1.json
```

CLI chỉ tạo file mới trong data/dev, không ghi đè. Draft có dạng `{"claims":[{"text":"Một câu có căn cứ.","evidence_ids":["e1"]}]}`. Claims rỗng là thiếu bằng chứng. Tối đa8 câu và120 từ phân tách bằng whitespace; đây là giới hạn kỹ thuật, không phải bộ đếm từ tiếng Việt theo ngôn ngữ học.

## Rubric người kiểm — mỗi mục Pass/Fail/Chưa xác minh

| Mục | Điều cần kiểm | Nếu không Pass |
|---|---|---|
| Identity | Đúng tác phẩm/tác giả; phân biệt bản dịch, tuyển tập, edition | Không duyệt identity |
| Phạm vi | Nguồn work không bị dùng khẳng định chi tiết edition | Sửa hoặc bỏ câu |
| Căn cứ từng câu | Evidence thực sự hỗ trợ ý nghĩa, không chỉ trùng từ | Sửa hoặc bỏ câu |
| Không thêm dữ kiện | Không bịa cốt truyện, giải thưởng, review, đánh giá chất lượng | Bác bản nháp |
| Tiếng Việt | Dễ hiểu, đúng tên riêng, không đổi nghĩa/phóng đại | Sửa và kiểm lại |
| Quyền | Có bằng chứng phù hợp cho hiển thị và biến đổi; đủ attribution theo hồ sơ đã duyệt | Giữ pending; không tự suy quyền |
| Truy vết | URL/revision/hash và model/prompt version khớp bản được kiểm | Tạo phiên bản mới |

Reviewer ghi người kiểm, thời điểm, quyết định từng mục và ghi chú vào hồ sơ riêng. Công cụ không tự tạo chữ ký duyệt. Nội dung cần cả identity_verified, content_reviewed và rights_status=approved trong schema; metadata của sách cũng phải approved. Bìa có cổng riêng. Thay payload nguồn hoặc bản giới thiệu phải version mới, không sửa catalogue_v1.

## Ranh giới kiểm tự động

Kiểm hash/offset/schema/reference chỉ chứng minh cấu trúc và liên kết đoạn trích. Một câu bịa nhưng dẫn ID hợp lệ vẫn có thể qua kiểm này; tests ghi rõ trường hợp ấy. Output luôn public_ready=false, content_reviewed=false, identity_verified=false và rights_status=pending. Không dùng tỷ lệ pass cấu trúc làm factual accuracy.

Prompt tách chỉ dẫn system khỏi JSON nguồn không tin cậy, yêu cầu bỏ qua chỉ dẫn trong nguồn. Đây không phải bằng chứng chống prompt injection của một model/provider chưa chạy. Chưa có mẫu AI thật được chấm, chưa có tỷ lệ hallucination hoặc nghiệm thu chất lượng ngôn ngữ.

Khi chưa có nguồn được duyệt, giao diện giữ “Chưa có mô tả được xác minh”. Không tự biến6 đoạn Wikipedia ứng viên hoặc9.651 ứng viên text lịch sử thành nội dung public.
