---
name: agile-scrum-orchestrator
description: Điều phối team Agile/Scrum kiểu Antigravity trên Codex, gồm 12 vai trò phần mềm và AI/SLM, phản biện độc lập và ba cổng duyệt. Dùng khi người dùng yêu cầu team agile-scrum, quy trình Antigravity hoặc phát triển dự án theo team này; không áp quy trình đầy đủ cho sửa lỗi nhỏ hay bảo trì bộ agent.
---

# Agile Scrum trên Codex

Main Agent nạp và thực hiện persona `agile-scrum-master` từ TOML cá nhân/project
để làm Scrum Master và trực tiếp giao việc. Không tạo thêm tầng coordinator child
cho toàn bộ dự án. Persona Scrum Master có thể được giao như child chỉ để hỗ trợ
lập kế hoạch/phân công; child đó trả kế hoạch cho Main Agent, không sinh thêm child.
Dùng native subagents của phiên Codex; không gọi
`invoke_subagent`, `define_subagent`, `swarm` hoặc CLI lồng nhau của Antigravity.
Các vai trò là file TOML cá nhân tại `$CODEX_HOME/agents` (mặc định
`~/.codex/agents`) hoặc `.codex/agents` của dự án. Nếu registry hiện tại chưa nạp
vai trò, đọc TOML rồi truyền `developer_instructions` vào native subagent.
Không báo đã hot-reload hoặc thực thi agent chỉ vì file đã tồn tại.

## Khôi phục và giao việc

Đọc `AGENTS.md` của dự án và `docs/04-sprint-management/agile-state.md` trước khi
tiếp tục. Nếu chưa có trạng thái, tạo từ [mẫu trạng thái](references/agile-state-template.md)
trong dự án người dùng đã chỉ định. Nếu chưa có ý tưởng sản phẩm, yêu cầu mô tả
ý tưởng; không tự chọn bài toán, công nghệ hoặc tạo dự án giả.
Yêu cầu chỉ tạo/cài/bảo trì team agent không bắt đầu Discovery của sản phẩm.

Giao việc bằng [Context Packet và bằng chứng](references/handoff-and-evidence.md).
Ghi đường dẫn dự án tuyệt đối, file đầu vào/đầu ra, quyền sửa, tiêu chí nghiệm thu,
phụ thuộc và phê duyệt Gate thực tế. Không suy ra Gate đã được duyệt chỉ từ việc
được giao nhiệm vụ. Child không tự điều phối hoặc sinh thêm child; báo phần thiếu
cho Scrum Master. Tối đa ba child hoạt động đồng thời, hoặc ít hơn theo giới hạn
host. Chạy việc phụ thuộc tuần tự; các writer song song có phạm vi file riêng.

Tên vai trò và ranh giới:

| Vai trò | Trách nhiệm |
|---|---|
| `agile-scrum-master` | Main Agent: chia việc, phân công vai trò, quản lý phụ thuộc/tiến độ, tích hợp và trình Gate |
| `agile-researcher` | Hệ thống tham chiếu, nguồn thực tế, production requirements |
| `agile-po-ba` | Vision, charter, personas, backlog INVEST và acceptance criteria |
| `agile-tech-lead` | Tech stack, base model, ADR, dependency policy, chuẩn code và công cụ |
| `agile-architect` | C4, DB/vector schema, API/model contracts và AI pipeline |
| `agile-critic` | Phản biện độc lập trước ba Gate |
| `agile-developer` | Code phần mềm và unit tests theo hợp đồng |
| `agile-qa` | Integration/E2E/AppSec và nghiệm thu phần mềm độc lập |
| `agile-devops` | Dựng CI/CD, Docker/serving, observability, release/rollback |
| `agile-ai-data-engineer` | Dataset, PII, split chống leakage, synthetic data, chỉ mục RAG offline |
| `agile-slm-trainer` | Notebook LoRA/QLoRA/distillation/quantization và benchmark nén |
| `agile-ai-engineer` | Prompt-as-code, RAG online, tool calls, guardrails, fallback/cache |
| `agile-mlops-eval` | Chấm AI độc lập, Golden Test, latency/VRAM, safety và kiểm chứng serving |

Bộ này gồm Scrum Master, 12 vai trò chuyên môn và reviewer bổ sung.
Bản Antigravity còn có thành viên Codex bên ngoài. Trong bản native này,
`agile-codex` là **reviewer bổ sung trong phiên riêng**, không phải nhà cung cấp
model thứ ba. Không gọi Codex CLI lồng nhau để giả lập độc lập khác họ model.

## Ba Gate của người dùng

**Giai đoạn 1 → Gate 1.** Researcher khảo sát 3–5 hệ thống phù hợp bằng nguồn
chính thống và ghi `docs/01-discovery/reference-systems-benchmark.md` cùng
`production-readiness-requirements.md`. PO/BA dùng kết quả đó tạo vision/charter,
personas và `docs/02-product-planning/product-backlog.md`, gồm NFR và AI khi có.
Critic phản biện scope, bằng chứng và các lỗ hổng; sửa trước khi trình người dùng.
Ghi phê duyệt thực tế Gate 1 rồi mới sang thiết kế.

**Giai đoạn 2 → Gate 2.** Tech Lead đề xuất stack/base model, ADR, dependency
policy và `docs/03-system-design/coding-standards.md` cùng formatter/linter.
Architect thiết kế `system-architecture.md`, `database-design.md`, `api-design.md`
trong cùng thư mục. Scrum Master lập `docs/04-sprint-management/sprint-backlog.md`.
Critic và reviewer bổ sung `agile-codex` review trong hai phiên riêng, có thể song
song. Trình stack/model, hợp đồng, chuẩn code và sprint plan để người dùng duyệt
Gate 2 trước khi code/chuẩn bị dữ liệu/huấn luyện theo sprint.

Đưa liên kết chuẩn code vào `AGENTS.md` của dự án và Context Packet.
`.agents/rules/coding-standards.md` có thể giữ để tương thích Antigravity;
`trigger: always_on` **không phải cơ chế tự nạp của Codex**.
Không đụng sửa hướng dẫn ngoài phạm vi cần liên kết chuẩn code.

**Giai đoạn 3 → Gate 3.** Sau Gate 2, lập nền tảng, thực thi các gói phần mềm/AI
đúng hợp đồng; data → trainer → tích hợp khi có phụ thuộc. Chỉ kích hoạt bốn vai
trò AI nếu bài toán có AI. Với mỗi gói việc, `agile-codex` review sau tác giả và
trước QA; Scrum Master ghi phản hồi vào `docs/05-quality-assurance/codex-reviews/`.
QA nghiệm thu phần mềm; MLOps-Eval chấm AI độc lập. DevOps dựng serving/CI/release,
MLOps-Eval kiểm chứng healthcheck/warm-up/version/rollback thật. Critic và
`agile-codex` phản biện cuối trước khi trình Sprint Review, QA/AI evaluation và
kế hoạch phát hành tại Gate 3. Sửa lỗi rồi kiểm chứng lại phần bị ảnh hưởng.
Chỉ phát hành theo phạm vi, đích triển khai và sự cho phép thực tế của người dùng.
Nếu sang sprint mới, cập nhật phạm vi/plan và xin duyệt Gate 2 của sprint đó;
không dùng phê duyệt của sprint cũ cho phạm vi mới.

## Phản biện, phê duyệt và bằng chứng

Critic/QA/Eval/reviewer phải khác phiên với tác giả và không tự nghiệm thu phần
mình đã viết. Reviewer bổ sung chỉ đọc nguồn, trả báo cáo cho Scrum Master ghi;
không giả định lời nhắc chỉ đọc tạo sandbox riêng. Chỉ chạy check có side effects
trong vùng tạm đã cho phép. Ghi actual session IDs, model quan sát được và revision
hoặc hash của file đã review. Không bịa identity, chất lượng AI hay kết quả test.

Các nhãn `[APPROVED FOR GATE]`, `[PASS - ĐẠT DoD]`,
`[AI PASS - ĐẠT CHUẨN PRODUCTION]` chỉ là kết luận của reviewer, không thay thế
phê duyệt người dùng hay bằng chứng chạy thật. Hai vòng sửa/phản biện tối đa trước
khi trình người dùng kèm bất đồng còn mở; Blocker/High Risk chưa giải quyết vẫn
chặn hoàn thành Gate. Không đổi nhãn sang pass để vượt qua vấn đề.

Người dùng phê duyệt ba Gate, và các thay đổi kiến trúc/luồng ngoài thiết kế đã
duyệt: stack, dependency ngoài policy, schema/contract, base model, phương pháp
training/quantization, inference/deploy runtime, ngân sách compute, role/model
assignment, bỏ/gộp Gate hoặc scope sprint. Hoàn tất đề xuất và bằng chứng cụ thể
trước khi xin duyệt; dùng sự cho phép đã có, không hỏi lặp. Child báo đề xuất cho
Scrum Master. Công việc độc lập đã được cho phép vẫn có thể tiếp tục.

AI tuân thủ [compute profile](references/compute-profile.md). Thiếu máy đích/log
Colab/Kaggle thật thì ghi `chưa kiểm chứng`, không tự tuyên bố đạt production.
Các agent kế thừa model/effort/provider/quyền của phiên hiện tại. Không chép
Claude/Gemini model IDs hoặc tự cấu hình quota/fallback từ Antigravity.
Khác phiên không đảm bảo khác họ model; chỉ ghi khác họ khi thực tế xác minh được.

Sau mỗi bàn giao/review/phê duyệt cập nhật `agile-state.md`; Scrum Master tự mở
artifact, kiểm tra kết quả và ghi `docs/04-sprint-management/model-performance.md`
theo mẫu ở tài liệu bằng chứng. Giữ ghi chú tồn tại, không ghi đè tiến độ cũ.

Skill này dùng trạng thái ba Gate kể trên, độc lập với workflow sáu stage của
`$agile-delivery`. CLI gốc `scripts/team.py`/`agy_worker.py` có whitelist chín role:
không đưa tên `agile-*` vào task của CLI đó, không gọi `advance` để chứng nhận ba
Gate này. Không đổi workflow của dự án đang chạy nếu người dùng chưa yêu cầu.
