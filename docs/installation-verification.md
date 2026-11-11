# Kiểm chứng cài đặt — 2026-11-11

Đã cài toolkit vào một thư mục riêng trong workspace cài đặt ban đầu.
`AGENTS.md` ở workspace cha dẫn các yêu cầu phát triển dự án tới skill của toolkit.
Không thay đổi cấu hình Codex toàn cục hoặc tạo dự án ứng dụng chưa được mô tả.

## Kết quả thực tế

| Kiểm tra | Kết quả |
| --- | --- |
| Native subagent | Đã dùng để xây vai trò/quy trình, adapter và phản biện độc lập |
| 9 role TOML + cấu hình concurrency | Parse/kiểm tra cấu trúc đạt |
| Skill Creator `quick_validate.py` | `Skill is valid!` |
| Ruff lint | Đạt |
| Ruff format | Đạt |
| Bộ kiểm thử Python | 45 tests đạt |
| Launcher shell | `sh -n` đạt |
| Khởi tạo dự án thử | Thành công trong thư mục tạm; giữ `discovery`, `not_deployed` |
| Chuyển bước thiếu review | Bị chặn đúng; trạng thái không bị thay đổi |
| `agy --help` | Hoạt động |
| Probe worker agy thật | `blocked`, exit 1; `live_worker_verified=false` |
| Workflow GitHub CI | Đã tạo file, chưa chạy trên GitHub |
| Nạp custom agent trong phiên Codex mới | Chưa quan sát; phiên hiện tại dùng native delegation và hướng dẫn vai trò trực tiếp |

Agent phản biện độc lập không còn phát hiện blocking/major trong phạm vi được
kiểm tra. Các regression đã sửa gồm xác nhận probe nhầm khi exit 0, source symlink
làm lọt thay đổi, và tiến trình con còn sống sau timeout. Review bổ sung xác nhận
digest hợp đồng task, task theo giai đoạn và init không thay thế thư mục có sẵn.

## Giới hạn còn lại

Worker agy bị sandbox chặn ghi log/crash report trong `~/.gemini/antigravity-cli`
và mở cổng localhost. Chưa kiểm chứng tác vụ thật qua dịch vụ/model agy. Native
subagent là đường thực thi hiện dùng được; adapter được kiểm thử bằng executable
giả lập và có báo cáo lỗi cho probe thật.

Các gate kiểm tra bản ghi/bằng chứng được cung cấp, không tự chứng minh chất lượng
sản phẩm hay deployment thật. Chưa có ứng dụng, stack hoặc môi trường production
được người dùng chỉ định để triển khai. Xem [hướng dẫn](../README.md) để bắt đầu
với ý tưởng thực tế.
