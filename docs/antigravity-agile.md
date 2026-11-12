# Team Antigravity trên Codex

Bản thích nghi từ plugin Antigravity `agile-scrum-team`, đối chiếu ngày
12/11/2026. Giữ 12 persona Agile/phần mềm/AI, bổ sung `agile-codex` tương ứng
reviewer của bản gốc và persona điều phối `agile-scrum-master` theo yêu cầu người dùng.
Tổng cộng 14 vai trò. Main Agent nạp persona Scrum Master để trực tiếp giao việc,
không khởi tạo một tầng coordinator child. Bản gốc không bị sửa.
Các TOML mới ở `.codex/agents/agile-*.toml`;
skill ở `.agents/skills/agile-scrum-orchestrator/`. Bản cài cá nhân tương ứng ở
`$CODEX_HOME/agents` và `$CODEX_HOME/skills/agile-scrum-orchestrator`.

Trong phiên Codex mới, gọi `$agile-scrum-orchestrator` kèm ý tưởng và thư mục dự án.
Các agent cá nhân có thể dùng ở dự án khác. Dự án có persona cùng tên sẽ dùng
cấu hình local của dự án; kiểm tra instructions thực tế trước khi giao việc.
Không khẳng định client đã nạp ngay các role vào phiên đang chạy.

Tech Lead chọn stack/model và chuẩn code; Architect thiết kế hợp đồng. Bốn vai trò
AI theo giới hạn Colab/Kaggle và RTX 2060 6 GB. Các agent native kế thừa model của
phiên; bảng model Claude/Gemini của Antigravity không được áp cho Codex. Reviewer
khác phiên bảo đảm tách tác giả, không chứng minh đa dạng họ model.

`agile-codex` là native reviewer bổ sung chỉ đọc theo instructions, không phải
một Codex CLI lồng bên ngoài hay một sandbox riêng. Coding standards được liên
kết qua AGENTS.md/Context Packet, không dựa vào trigger của Antigravity.

CLI và skill `$agile-delivery` gốc vẫn quản lý chín role/sáu stage. Không dùng
task `agile-*` với CLI đó. Skill mới quản lý trạng thái và ba Gate riêng theo
`references/agile-state-template.md`; không có lệnh tự chứng nhận Gate đạt.

Kiểm chứng bản cài ngày 12/11/2026: 14 TOML native parse hợp lệ, không override
model/provider/quyền; skill vượt `quick_validate.py`, các reference tồn tại;
file cài cá nhân trùng byte với file trong toolkit. Review độc lập của
`/root/review_agile_adaptation` không còn Blocker/High Risk, gồm kiểm tra hành vi
Discovery chưa duyệt, bàn giao thiếu log Colab và bảo trì cấu hình nhỏ. Đã sửa
chỉ dẫn workflow cũ trong AGENTS.md để không trộn ba Gate với sáu stage.
Đây là kiểm chứng cấu hình và hướng dẫn, chưa chứng minh client đã nạp registry
hoặc từng agent đã chạy một nhiệm vụ sản phẩm thật. Mở phiên mới để nạp.

Kiểm tra trước khi xuất bản: cấu hình 14 agent, skill, liên kết tài liệu, Ruff
lint/format và cấu hình workflow gốc đều đạt. Suite unittest gốc trên Windows
chạy 45 test, còn 12 thất bại, 6 lỗi và 3 bỏ qua, cùng kết quả trước thay đổi này.
Các lỗi được quan sát gồm chạy executable/script kiểu Unix (WinError 193) và tạo
symlink thiếu quyền Windows (WinError 1314). Chưa sửa phần tương thích Windows
của suite/adapter trong lần bổ sung persona và skill này.
