# Context Packet và bằng chứng

Mỗi nhiệm vụ gồm:

1. Vai trò, mục tiêu, thư mục dự án tuyệt đối, yêu cầu gốc người dùng.
2. Gate/phiên bản sprint đã được phê duyệt: ngày, lời duyệt hoặc tham chiếu tin
   nhắn thật; chỉ ghi những Gate đã thực sự được duyệt, nêu Gate chưa duyệt.
3. Đầu vào: paths, revisions/hashes, backlog/contract/chuẩn code và compute profile
   liên quan. Với reviewer: giao yêu cầu và artifact gốc trước tự đánh giá tác giả.
4. Phạm vi file được sửa/được đọc, files do writer khác sở hữu; đầu ra bắt buộc.
5. Dependencies, tiêu chí nghiệm thu, checks phải chạy và vùng tạm được phép dùng.
6. Yêu cầu trả về: actual session ID, model nếu quan sát được, file thay đổi,
   kết quả check có command/exit code/log path, findings/blockers, việc chưa làm.

Nhiệm vụ không cho phép child thay đổi contract/stack/luồng. Child báo đề xuất
cho Scrum Master cùng ảnh hưởng; không gọi thêm agent. Không dựng chứng cứ giả
để hoàn thiện bảng biểu. Nếu runtime không cung cấp identity/model, ghi unknown.

Review report ghi: phạm vi và revision/hash; tác giả/reviewer với actual session
IDs; từng phát hiện có ID, severity Blocker/High Risk/Improvement, file:dòng,
hệ quả, cách sửa và cách kiểm chứng; checks đã chạy; phần chưa kiểm chứng và
kết luận. Critic có thể ghi report được giao; `agile-codex` trả report để coordinator
ghi, không sửa nguồn đang review. Mọi thay đổi material cần review lại đúng revision.

Paths theo vai trò:

- Critic: `docs/05-quality-assurance/critique-reviews/gate-1-critique.md`,
  `gate-2-critique.md`, `sprint-N-critique.md`.
- Reviewer bổ sung: `gate-2-codex.md`, `sprint-N-codex.md` cùng thư mục trên;
  từng gói việc: `docs/05-quality-assurance/codex-reviews/WP-id.md`.
- QA: test plan, bug reports và QA report trong `docs/05-quality-assurance/`.
- MLOps-Eval: `docs/05-quality-assurance/ai-evaluation-report.md` và log metrics
  thật; DevOps: release/runbook/rollback trong `docs/06-release-deployment/`.

Trong `docs/04-sprint-management/model-performance.md`, thêm mỗi bàn giao một dòng:

| Ngày | Vai trò | Model thực tế | Session | Task/revision | Kết quả tự báo | Scrum Master kiểm chứng | Sửa lại/chi phí quan sát được | Blockers |
|---|---|---|---|---|---|---|---|---|

Không biến nhãn review hoặc cột tự báo thành nghiệm thu. Gate cần tham chiếu
review artifacts, checks và lời duyệt người dùng gắn đúng scope/revision. Ghi
thời lượng/tokens/cost chỉ khi công cụ có số thật; dùng unknown khi thiếu.
