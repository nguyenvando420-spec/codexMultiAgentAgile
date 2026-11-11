# Backlog và kế hoạch thực hiện

Trạng thái: draft — chưa có task đủ điều kiện triển khai.

## Mục tiêu vòng thực hiện

Chọn một phần giá trị người dùng có thể demo và nghiệm thu. Thứ tự theo nhu cầu và phụ thuộc, không chỉ chia theo chức danh.

| Task ID | Yêu cầu / giá trị | Vai trò | Phụ thuộc | Đường dẫn sở hữu | Tiêu chí nghiệm thu | Trạng thái |
| --- | --- | --- | --- | --- | --- | --- |

## Hợp đồng task

Tạo task cụ thể trong `.team/tasks/` từ mẫu. Mỗi task ghi đầu vào, giới hạn sửa file, phụ thuộc, tiêu chí nghiệm thu, đầu ra và kiểm tra. Lưu ID phiên thực tế khi giao việc.

## Điều kiện bắt đầu và hoàn thành

Task bắt đầu khi đủ đầu vào, phụ thuộc và quyền sửa file. Task hoàn thành khi có đầu ra, kiểm tra có bằng chứng và review độc lập theo rủi ro. Việc được Developer đánh dấu xong chưa thay thế nghiệm thu.

## Phụ thuộc và rủi ro

Ghi task có thể chạy song song, điểm tích hợp, quyết định còn thiếu và câu hỏi có thể chặn tiến độ. Giữ tối đa ba children đang hoạt động hoặc giới hạn thực tế thấp hơn.
