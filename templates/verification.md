# Kiểm chứng và nghiệm thu kỹ thuật

Trạng thái: pending — chưa được QA kiểm chứng.

## Phiên bản và môi trường

Ghi source digest/revision, môi trường, cấu hình không chứa secret và ID phiên QA/Security thực tế.

## Tiêu chí nghiệm thu

| Yêu cầu | Trường hợp kiểm chứng | Lệnh / bước thực hiện | Kết quả | Bằng chứng |
| --- | --- | --- | --- | --- |

## Kiểm tra bắt buộc của gate

Các tên check: `format`, `lint`, `test`, `build`, `security`. Format/lint/test cần `passed` với bằng chứng; các mục được phép không áp dụng cần lý do cụ thể được reviewer kiểm tra. Thiếu môi trường hoặc chưa thực hiện không phải là không áp dụng.

## Lỗi và kiểm tra lại

Mỗi lỗi có mức độ, cách tái hiện, ảnh hưởng, bản sửa và bằng chứng xác minh lại. Không để QA tự sửa rồi tự công nhận độc lập cho phần mình sửa.

## Giới hạn và kết luận

Ghi phần chưa test, rủi ro còn lại và verdict theo bằng chứng. Kiểm chứng phải được làm lại nếu source liên quan thay đổi.
