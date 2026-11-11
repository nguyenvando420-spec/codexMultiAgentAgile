# Kiến trúc hệ thống

Trạng thái: proposed — chưa được phản biện độc lập.

## Yêu cầu chi phối thiết kế

Liên kết yêu cầu trong product brief, kết quả nghiên cứu và các ràng buộc vận hành đã xác nhận.

## Thành phần và luồng dữ liệu

Mô tả ranh giới module/dịch vụ, trách nhiệm, luồng chính và tương tác bên ngoài. Sơ đồ chỉ cần khi giúp hiểu thiết kế.

## Dữ liệu và giao diện

Mô hình dữ liệu, API/event contracts, quyền sở hữu dữ liệu, tính nhất quán, migration và tương thích phiên bản.

## Công nghệ và đánh đổi

Tham chiếu ADR; ghi phương án thay thế và lý do chọn theo nhu cầu thực tế. Stack chưa được chọn nếu chưa có quyết định có bằng chứng.

## Bảo mật và lỗi

Trust boundaries, phân quyền, dữ liệu nhạy cảm, cơ chế lỗi/timeout/retry phù hợp và ảnh hưởng khi phụ thuộc hỏng.

## Triển khai và vận hành

Môi trường đích, cấu hình, quan sát hệ thống, chi phí, khả năng phục hồi và giới hạn quy mô. Phối hợp SRE từ đầu.

## Điểm cần kiểm chứng

Ghi prototype/benchmark cần thiết, rủi ro còn lại và tiêu chí thay đổi thiết kế. Lưu phản hồi phản biện và quyết định xử lý.
