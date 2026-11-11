# Chuẩn code dùng chung

Trạng thái: draft — cấu hình công cụ chờ quyết định stack.

Người chịu trách nhiệm: Tech Lead.

## Cấu trúc và convention

Ghi cấu trúc module, naming, API, xử lý lỗi, logging, dependency, test và quy tắc tương thích. Theo convention có sẵn nếu dự án đã tồn tại. Developer không tạo chuẩn riêng cho từng agent.

## Công cụ thực thi

| Kiểm tra | Công cụ và phiên bản | File cấu hình chuẩn | Lệnh local | Job CI | Loại trừ có lý do |
| --- | --- | --- | --- | --- | --- |
| Format | Chưa chọn | Chưa cấu hình | Chưa có | Chưa có | Chưa có |
| Lint | Chưa chọn | Chưa cấu hình | Chưa có | Chưa có | Chưa có |
| Type check nếu áp dụng | Chưa chọn | Chưa cấu hình | Chưa có | Chưa có | Chưa có |
| Test | Chưa chọn | Chưa cấu hình | Chưa có | Chưa có | Chưa có |
| Build nếu áp dụng | Chưa chọn | Chưa cấu hình | Chưa có | Chưa có | Chưa có |

Sau khi chốt stack, cấu hình công cụ thực tế và chạy các lệnh. Không ghi format/lint đã đạt chỉ vì có EditorConfig hoặc tài liệu này. Lưu bằng chứng kết quả và xác minh CI chặn vi phạm chuẩn.

## Làm việc song song và review

Phân quyền sở hữu file trong task. Một người tích hợp thay đổi cấu hình chung và lockfile. Reviewer độc lập kiểm chứng thay đổi; major dependency hoặc stack cần ADR.
