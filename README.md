# BookNest

Đồ án Khoa học dữ liệu về gợi ý sách cá nhân hóa, dùng Goodbooks-10k và ứng dụng Streamlit tiếng Việt.

## Trạng thái ngày25 tháng11 năm2026

Dữ liệu và thí nghiệm đã hoàn tất đến Day10. Item-KNN K200/shrink10 được chọn bằng validation trước khi mở test. Có demo local và UI tài khoản nối PostgreSQL; quyền dữ liệu được kiểm với identities tổng hợp. Chưa nghiệm thu đăng nhập OIDC thật, Neon/Render, browser/mobile hoặc nội dung public. Công cụ chuẩn bị bản nháp AI chỉ chạy offline, chưa gọi provider.

Lần kiểm25/11:68 Python tests đạt,130 mục hash Day10 khớp (có thể trùng file). Chưa dựng lại toàn bộ từ máy sạch. Day11–17 mới hoàn thành từng phần local.

Bổ sung chuẩn bị GitHub25/11: full suite70tests đạt sau khi thêm2tests cho inventory; chạy ngoài sandbox do asyncio socketpair bị kẹt trong sandbox. Model và130mục hash không đổi. [Bằng chứng](reports/github_preparation/verification.json).

[Bàn giao](docs/HANDOFF.md) · [Kế hoạch](docs/PROJECT_PLAN.md) · [Lịch sử README](docs/README_HISTORY_20261125.md)

## Nghiên cứu và kết quả

10.000 sách,53.424 người dùng,5.976.479 ratings. Chỉ train được fit; validation chọn cấu hình; test mở sau khi khóa. Missing không mặc định0. Không có timestamp nên không tuyên bố đánh giá theo thời gian.

| Cold test với5 đánh giá hỗ trợ | Item-KNN | Popularity |
|---|---:|---:|
| NDCG@10 | 0,462428 | 0,248938 |
| Recall@10 | 0,065387 | 0,033484 |
| Coverage | 50,24% | 0,14% |

Đây là metrics benchmark, không phải accuracy hay chất lượng catalogue sản phẩm đã lọc quyền. Test đã xem, không tuning tiếp bằng test. [Protocol](docs/EVALUATION_PROTOCOL.md), [kết quả và giới hạn](reports/day10/final_20261123/summary.md).

## Cài môi trường

Trong thư mục dự án, Windows với Python3.11:

```powershell
py -3.11 -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Đây là hướng dẫn cài cho máy mới, chưa phải bằng chứng clean-install đạt. Requirements pin gói trực tiếp, chưa khóa toàn bộ dependency bắc cầu. Native DB integration fixtures hiện tìm PostgreSQL tại `C:/Program Files/PostgreSQL/18/bin`.

## Dữ liệu và model không đi kèm Git

`data/`, `artifacts/`, `.venv/`, `node_modules/`, `.env`, `.streamlit/secrets.toml` được loại khỏi Git. Clone mã nguồn chưa đủ để chạy app hoặc toàn bộ tests.

Bảng đối chiếu metadata nguồn `reports/day01/descriptions_20261119/matches.json` cũng giữ local, chưa đưa vào commit đầu. Báo cáo lịch sử có thể tham chiếu file này; kết quả tổng hợp vẫn được lưu, nhưng clone không có toàn bộ bằng chứng chi tiết của pilot nguồn.

Demo cần artifacts đã xác minh:

- `data/processed/day06_item_knn_v1/`: catalogue_ids.npy, popularity.npy, neighbors_s10.npy, weights_s10.npy và manifest Day6 tương ứng trong reports.
- `data/processed/day11_operational_v1/books.json` và catalogue_manifest Day11 trong reports.
- Full tests/readiness còn cần dữ liệu/artifacts các giai đoạn trước.

Nguồn benchmark: [Goodbooks-10k](https://github.com/zygmuntz/goodbooks-10k). [Manifest revision và hashes](docs/DATA_MANIFEST.json), [chính sách nguồn/quyền](docs/CATALOGUE_POLICY.md), [quy trình tái lập](docs/REPRODUCIBILITY.md). Không suy quyền mô tả/bìa từ quyền mã nguồn; không sửa manifest để chấp nhận artifacts chưa xác minh.

## Chạy workspace đã có artifacts

```powershell
.venv\Scripts\python.exe -B scripts/check_local_readiness.py
.venv\Scripts\python.exe -B -m unittest discover -s tests
.venv\Scripts\python.exe -m streamlit run app/main.py
```

Demo mặc định chỉ localhost, hồ sơ lưu theo phiên và có thể mất khi phiên kết thúc. `BOOKNEST_MODE=postgres` chọn UI tài khoản, cần cấu hình OIDC và database phía server; thiếu cấu hình thì dừng. Không có credentials mặc định. [Demo](docs/LOCAL_DEMO.md), [authentication](docs/AUTHENTICATION.md), [database](docs/DATABASE.md), [vận hành](docs/LOCAL_OPERATIONS.md).

Một số script nghiên cứu có output cố định theo ngày và có thể ghi đè báo cáo cũ; không chạy hàng loạt để tái lập. Giữ raw/model/manifest đã khóa và chọn workspace/output riêng cho replay.

## Cấu trúc

| Thư mục | Nội dung |
|---|---|
| app/ | Streamlit demo và UI tài khoản |
| booknest/ | Engine, repository, identity, kiểm bản nháp |
| scripts/ | Pipeline dữ liệu, mô hình, audit và kiểm tích hợp |
| tests/ | Kiểm logic dữ liệu, model, nội dung và UI |
| db/ | SQL migrations và import |
| docs/ | Protocol, quyết định và bàn giao |
| reports/ | Kết quả, manifests và bằng chứng theo mốc |

Không tự commit/push/deploy. Rà danh sách file và quyền nội dung trước phát hành; không đưa secrets/datasets/môi trường Python lên Git.
