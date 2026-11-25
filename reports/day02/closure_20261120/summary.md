# Chốt phạm vi Day2 — 20/11/2026

Người dùng xác nhận “ok chốt” sau đề xuất giữ 10.000 sách, để thiếu mô tả chưa xác minh và chuyển trọng tâm sang khoa học dữ liệu. **Day2 được đóng theo phạm vi điều chỉnh đã chấp thuận**, không phải vì các quyền/nội dung còn thiếu đã được xác minh. Policy hiện hành: [CATALOGUE_POLICY v0.2](../../../docs/CATALOGUE_POLICY.md).

## Phạm vi đã chốt

1. Benchmark giữ 10.000 sách và ratings; thiếu mô tả không làm mất dữ liệu đánh giá.
2. Catalogue sản phẩm dự kiến giữ sách thiếu mô tả nếu metadata đủ điều kiện public. Văn bản fallback: “Chưa có mô tả được xác minh”. Bìa chưa đủ quyền dùng placeholder tự tạo.
3. Mô tả, intro, bìa và metadata có cổng kiểm riêng. Chưa đủ bằng chứng thì không công khai trường đó; không suy quyền từ khớp ID hoặc độ dài text. Quyết định fallback không miễn kiểm quyền metadata.
4. Không chờ phủ hết 349 hàng để làm Day3. Sáu đoạn Wikipedia ứng viên là backlog ưu tiên, chưa nghiệm thu; 9.651 text ứng viên cũng chưa được duyệt hàng loạt.
5. Catalogue local v1 và overlay giữ nguyên. Nếu thay payload, tạo phiên bản mới.

## Bằng chứng kế thừa, không chạy lại ở mốc này

- [Catalogue v1](../catalogue_v1_20261119/summary.md): 10.000 sách, manifest/hash và cổng intro local.
- [Pilot nhóm thiếu nguồn](../wikipedia_gap_20261119/summary.md): 20 mẫu, 8 work khớp, 6 đoạn ứng viên, 2 mỏng, 12 chờ; snapshot revision/hash. 14 tests đạt ở mốc pilot, không phải vừa chạy lại.
- [Triage và policy trước](../review_20261119/summary.md): 358 hàng đã phân loại; không lọc ratings vì thiếu mô tả.

## Việc còn lại và điều kiện hoàn thành

| Việc | Khi nào | Điều kiện |
|---|---|---|
| Xác minh 6 đoạn Wikipedia | Backlog nội dung ưu tiên | Kiểm sự kiện, phạm vi tác phẩm/edition, quyền đoạn dùng và attribution; không tự nâng trạng thái public |
| Metadata public | Trước phát hành | Ghi nguồn/điều kiện và danh sách trường được hiển thị |
| Intro tiếng Việt | Giai đoạn nội dung/AI | Có nguồn đạt cổng, bản giới thiệu được kiểm, attribution và giấy phép phù hợp |
| Fallback mô tả và placeholder bìa | Giai đoạn giao diện | Triển khai và kiểm không lộ text/ảnh chưa duyệt |
| Nếu thu hẹp catalogue sản phẩm | Trước đánh giá trên tập đó | Đóng băng candidate set, báo ảnh hưởng và so sánh model cùng tập |

**Bước tiếp theo là Day3**: áp dụng cleaning trên lớp derived, EDA và thiết kế protocol/split tái lập; không dùng tín hiệu test để tạo features, không giả lập timestamp. Mốc chốt này chỉ sửa tài liệu, chưa chạy Day3, sinh intro, sửa app, train hoặc deploy.

Đã cập nhật policy, HANDOFF, PROJECT_PLAN, README và AGENTS. Kiểm nhất quán các mốc/trạng thái và liên kết local; không cần chạy tests cho thay đổi tài liệu. Không sửa raw/catalogue/cache, không kiểm lại hashes ở mốc này; không commit/push/deploy hoặc thay đổi ScoutIQ.
