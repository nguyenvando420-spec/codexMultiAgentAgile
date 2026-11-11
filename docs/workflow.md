# Quy trình từ ý tưởng đến triển khai

Hệ thống này cung cấp quy trình điều phối bằng subagent trong Codex, các vai trò có cấu hình riêng và công cụ theo dõi dự án. Agent chính sử dụng công cụ spawn/message/wait có sẵn của phiên; các file cấu hình không tự tạo một dịch vụ agent chạy nền. Agent `agy` là worker CLI bên ngoài và cần khởi động thành công trong môi trường được phép.

## Bắt đầu và tiếp tục

Các script yêu cầu Python từ 3.11. Khởi tạo dự án bằng `./agile-team init PATH --name NAME --idea TEXT`; launcher tự chọn interpreter phù hợp. Nếu chạy trực tiếp `python3 scripts/team.py`, kiểm tra phiên bản Python trước. Mở phiên Codex mới tại thư mục dự án để client nạp cấu hình và skill theo dự án. Có thể yêu cầu: “Dùng team Agile và subagent để phát triển ý tưởng này; bắt đầu bằng discovery, ghi rõ giả định và phản biện từng giai đoạn.”

Khi tiếp tục, đọc `.team/project.json`, task đang mở, gate hiện tại và ADR thay vì tạo lại kế hoạch. Chạy `python3 scripts/team.py status PATH` và `python3 scripts/team.py check PATH`. Việc đọc `AGENTS.md` trong phiên hiện tại có thể giúp bắt đầu ngay; không khẳng định client đã tự nạp custom agents trước khi quan sát được.

## Các giai đoạn

| Giai đoạn | Công việc | Bằng chứng tối thiểu |
| --- | --- | --- |
| `discovery` | BA làm rõ vấn đề/MVP; Research tìm hệ thống tương tự và khả năng áp dụng; phản biện phạm vi/nguồn | `docs/product-brief.md`, `docs/research.md` |
| `architecture` | Architect chọn công nghệ/thiết kế, SRE kiểm tra vận hành; Tech Lead chốt chuẩn và công cụ; phản biện đánh đổi | `docs/architecture.md`, `docs/adr/0001-stack.md`, `docs/coding-standards.md` |
| `planning` | Chia backlog theo giá trị, phụ thuộc, quyền sửa file và tiêu chí nghiệm thu; phản biện độ đầy đủ | `docs/backlog.md`, task cụ thể trong `.team/tasks/` |
| `implementation` | Developer triển khai các task đủ điều kiện; Tech Lead tích hợp; phản biện code | `docs/implementation.md`, code và kết quả kiểm tra gắn với source snapshot |
| `verification` | QA kiểm thử độc lập, Security kiểm tra theo rủi ro, Developer sửa lỗi; phản biện bằng chứng | `docs/verification.md`, logs/kết quả gắn với source snapshot |
| `release` | SRE kiểm chứng điều kiện production, chuẩn bị/phát hành trong phạm vi được giao; phản biện khả năng vận hành | `docs/production-readiness.md`, `docs/runbook.md`, kết quả kiểm tra và source snapshot |

`complete` nghĩa là quy trình đã đi hết các giai đoạn theo các bản ghi gate được kiểm tra. Nó không tự chứng minh ứng dụng đã lên production. Ghi rõ `prepared`, `deployed` hoặc `blocked` trong tài liệu release; chỉ ghi `deployed` khi có biên nhận từ môi trường đích và kiểm tra sau triển khai.

## Cách điều phối

1. Giao task theo mẫu `templates/task.json`, đầy đủ `objective`, đầu vào, giới hạn sửa file, `dependencies` và tiêu chí nghiệm thu. Kiểm tra phụ thuộc trước khi chạy. Agent chưa có file định nghĩa được client nạp có thể nhận trực tiếp instructions của vai trò trong một native subagent.
2. Chỉ chạy song song các task độc lập, tối đa ba children hoặc giới hạn thấp hơn của phiên. Tách quyền sở hữu file; dùng worktree riêng nếu dễ xung đột. Không để nhiều agent đồng thời sửa lockfile hoặc cấu hình formatter.
3. Ghi kết quả thực tế và bằng chứng; điều phối viên tích hợp rồi giao một phiên khác phản biện. Reviewer kiểm tra cả yêu cầu và artifacts thô, không chỉ bản tóm tắt của tác giả.
4. Ghi gate `.team/gates/<stage>.json` theo mẫu `templates/gate.json`. Các bản ghi ban đầu ở trạng thái `pending`; reviewer chỉ đổi sang `pass` sau khi kiểm tra.
5. Dùng `python3 scripts/team.py gate PATH STAGE` kiểm tra rồi `python3 scripts/team.py advance PATH` chuyển bước. Advance kiểm tra lại các gate từ đầu đến giai đoạn hiện tại. Nếu tài liệu hoặc code liên quan thay đổi, tạo lại bằng chứng và phản biện lại phần bị ảnh hưởng. Không sửa hash chỉ để làm một review cũ trông như còn hiệu lực.

## Bằng chứng và phản biện

Mỗi gate ghi `author_session` và `reviewer_session` là hai ID thực tế khác nhau, `reviewer_role` là `critical_reviewer`, cùng verdict. Evidence gồm đường dẫn tương đối trong dự án và SHA-256 của nội dung. Các giai đoạn implementation, verification và release sử dụng `source_digest` để phát hiện code thay đổi sau kiểm chứng. Các gate planning, implementation, verification và release còn dùng `task_contract_digest` để gắn review với tập task và phạm vi đã giao. Thêm/bớt task hoặc đổi objective, allowed_paths, acceptance_criteria hay dependencies cần phản biện lại; cập nhật trạng thái/kết quả/owner không tự làm cũ hợp đồng task.

Dùng `python3 scripts/team.py evidence PATH FILE...` và `python3 scripts/team.py snapshot PATH` để lấy JSON tương ứng; không tự điền hash tưởng tượng. Snapshot in các mục loại trừ và từ chối symlink trong source để tránh bằng chứng phụ thuộc nội dung bên ngoài khó kiểm soát.

Findings ghi `id`, `severity` (`blocking`, `major`, `minor`), `status` (`open`, `resolved`), `reason`, `evidence`, `resolution`. Lỗi blocking/major đang mở chặn gate. Một đề xuất minor chưa áp dụng phải có lý do và owner theo dõi. Checks ghi tên, trạng thái (`passed`, `failed`, `not_applicable`), bằng chứng và lý do khi không áp dụng. `checks[].evidence` là mảng các đường dẫn đã có trong danh sách evidence được hash của gate. Mục not_applicable có thể có mảng rỗng nếu có lý do cụ thể. Một kiểm tra chưa chạy không được khai là passed hoặc not_applicable.

Gate verification yêu cầu các check `format`, `lint`, `test`, `build`, `security`; format/lint/test bắt buộc passed. Gate release yêu cầu `ci`, `security`, `migration`, `backup_restore`, `rollback`, `observability`, `performance`. Các mục được phép không áp dụng cần lý do thực chất và phản biện độc lập.

Các script xác minh cấu trúc, trạng thái, hash và sự nhất quán của bản ghi; chúng không thể tự xác nhận người nhập đã trung thực hoặc chất lượng sản phẩm. Điều phối viên phải đối chiếu identity thực của subagent, nguồn và log. File chuẩn bị theo mẫu, dấu check thủ công hoặc báo cáo đẹp không thay thế bằng chứng thực thi.

## Công nghệ và chuẩn code

Không chọn sẵn stack cho một ý tưởng chưa được mô tả. Architect ghi các lựa chọn trong ADR và nêu đánh đổi theo nhu cầu, ngân sách, khả năng vận hành. Tech Lead cấu hình công cụ formatter/linter/kiểm tra kiểu phù hợp, lệnh test và CI sau khi stack được chọn. EditorConfig chỉ là thiết lập trình soạn thảo, không thay thế formatter hoặc CI. Developer không tự đổi stack hoặc thêm dependency chính mà không cập nhật quyết định chung.

## Điều kiện production

Theo rủi ro thực tế, SRE và Security xác định kiểm tra cần thiết: cấu hình môi trường, secret, phân quyền, migration, backup/restore, rollback hoặc roll-forward, health check, logging/metrics/cảnh báo, hiệu năng, chi phí và người chịu trách nhiệm vận hành. Nội dung không áp dụng cần lý do cụ thể và phản biện; môi trường chưa có nghĩa là chưa kiểm chứng.

Chuẩn bị code, cấu hình, pipeline và runbook trong phạm vi đã được giao. Chỉ hỏi khi thiếu đầu vào thiết yếu hoặc quyền cho một hành động bên ngoài cụ thể; không tạo thêm bước xin phép cho công việc đảo ngược đã được giao. Không tự tạo tài khoản, phát sinh chi phí hoặc suy diễn quyền publish production. Nếu chưa có đích triển khai, hoàn thiện phần chuẩn bị và ghi rõ phần còn chờ.

## Tích hợp agy

Xem `python3 scripts/agy_worker.py --help`. Adapter truyền task rõ ràng và lưu kết quả/log theo từng lần chạy. `--help` chạy được chưa chứng minh agent đã chạy, đăng nhập hoặc có quyền cần thiết. Không dùng cờ bỏ qua quyền. Nếu sandbox chặn ghi log, bind localhost, mạng hoặc xác thực, ghi lỗi và tiếp tục phần độc lập bằng native subagent. Không đổi môi trường để lách chính sách của phiên.

## Nguồn cấu hình

Cấu trúc custom agents và giới hạn concurrency dựa trên [OpenAI — Subagents](https://learn.chatgpt.com/docs/agent-configuration/subagents). Quyền truy cập của subagent kế thừa phiên chính; file vai trò chỉ là hướng dẫn, không tạo sandbox riêng. Các phiên bản client có thể khác nhau: dùng `doctor` và trợ giúp CLI tại máy để xác minh; mở phiên mới để nạp thay đổi.
