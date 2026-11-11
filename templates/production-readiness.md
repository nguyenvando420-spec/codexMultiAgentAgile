# Sẵn sàng production

Trạng thái: pending — chưa đủ bằng chứng phát hành.

Trạng thái triển khai: blocked — chưa xác định đích hoặc chưa kiểm chứng. Chỉ cập nhật `prepared`/`deployed` khi có bằng chứng tương ứng.

## Mục tiêu và bản phát hành

Ghi môi trường đích, revision/source digest, artifact, cấu hình, người chịu trách nhiệm và phạm vi hành động đã được giao. Không đưa secret vào tài liệu.

## Điều kiện vận hành

| Check của gate | Phép kiểm chứng | Kết quả thực tế | Bằng chứng | Lý do nếu không áp dụng |
| --- | --- | --- | --- | --- |
| `ci` | Pipeline trên đúng revision | Chưa chạy | Chưa có | Chưa xác định |
| `security` | Các kiểm soát phù hợp và findings | Chưa chạy | Chưa có | Chưa xác định |
| `migration` | Migration và tương thích dữ liệu | Chưa chạy | Chưa có | Chưa xác định |
| `backup_restore` | Backup và thử khôi phục | Chưa chạy | Chưa có | Chưa xác định |
| `rollback` | Rollback hoặc roll-forward an toàn | Chưa chạy | Chưa có | Chưa xác định |
| `observability` | Health, log, metrics và cảnh báo | Chưa chạy | Chưa có | Chưa xác định |
| `performance` | Tải/độ trễ phù hợp mục tiêu | Chưa chạy | Chưa có | Chưa xác định |

Phân biệt kiểm tra không áp dụng với kiểm tra chưa thể chạy. Ghi thêm chi phí dự kiến/quan sát, vận hành và ứng cứu theo nhu cầu dự án.

## Kế hoạch và bằng chứng phát hành

Chuẩn bị bước triển khai, smoke test, tiêu chí dừng, giám sát và phục hồi. Ghi biên nhận từ môi trường đích, thời điểm, phiên bản và kết quả sau deploy nếu thực sự đã phát hành. Gate đạt hoặc trạng thái workflow `complete` không phải biên nhận deploy.

## Rủi ro và phản biện

Ghi reviewer độc lập, findings, hành động khắc phục và phần còn chờ đầu vào/quyền thiết yếu.
