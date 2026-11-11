# Team Agile bằng subagent

Bộ điều phối theo dự án cho Codex: từ phân tích ý tưởng, nghiên cứu hệ thống tham
khảo, quyết định công nghệ, thống nhất chuẩn code đến triển khai và kiểm chứng
khả năng vận hành. Agent chính dùng subagent thật của phiên Codex để giao việc,
thu kết quả và tích hợp. Đây không phải dịch vụ chạy nền tự gọi model.

## Clone và cài đặt

Yêu cầu Python 3.11+ và một phiên Codex có công cụ subagent. `agy` là tùy chọn.

```sh
git clone git@github.com:nguyenvando420-spec/codexMultiAgentAgile.git
cd codexMultiAgentAgile
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements-dev.txt
./agile-team check .
```

Nếu máy dùng alias SSH riêng, thay `github.com` bằng alias đã cấu hình, ví dụ
`github.personal`. Dùng Python 3.11+ cho lệnh tạo môi trường ảo ở trên.
Các dependencies trong `requirements-dev.txt` chỉ phục vụ phát triển toolkit;
runtime không cần cài thư viện bên ngoài.

## Dùng ngay trong Codex

Mở thư mục vừa clone trong Codex; `AGENTS.md` tại repo dẫn tới quy trình này.
Gửi một yêu cầu có ý tưởng cụ thể, ví dụ:

> Dùng team Agile và subagent để phát triển dự án quản lý kho cho cửa hàng của
> tôi. Bắt đầu phân tích và nghiên cứu tham khảo, phản biện độc lập từng giai đoạn,
> sau đó chốt công nghệ, chuẩn code và triển khai đến mức sẵn sàng production.

Ở phiên mới trong thư mục toolkit/dự án đã khởi tạo, có thể gọi `$agile-delivery`.
Custom agents/skill có thể cần mở phiên mới để client nạp. Trong phiên hiện tại,
điều phối viên có thể đọc TOML của vai trò rồi giao instructions cho native
subagent; không coi việc có file cấu hình là bằng chứng client đã hot-reload.

## Khởi tạo dự án mới bằng CLI

```sh
cd codexMultiAgentAgile
./agile-team init ../du-an-moi --name 'Dự án của tôi' --idea 'Mô tả ý tưởng thực tế'
./agile-team status ../du-an-moi
./agile-team check ../du-an-moi
```

`init` chỉ tạo thư mục mới, không ghi đè repo có sẵn. Nó cài role configs, skill,
scripts, mẫu tài liệu và trạng thái `discovery`; chưa tạo code ứng dụng, chọn stack
hoặc đánh dấu gate đạt. Sau đó mở thư mục dự án trong Codex để bắt đầu làm việc.
Repo có sẵn cần tích hợp có chủ đích để giữ nguyên instructions và CI đang dùng;
không chạy `init` lên repo đó.

Launcher tự tìm Python 3.11+ trên PATH và có fallback cho Homebrew trên macOS.
Có thể đặt `AGILE_PYTHON` để chọn đường dẫn interpreter phù hợp.
Runtime của toolkit chỉ dùng thư viện chuẩn; không cần API key riêng khi làm việc
bằng phiên Codex/subagent hiện tại.

## Vai trò và quyết định

9 vai trò: Product Analyst, Research Engineer, Solution Architect, Tech Lead,
Developer, QA Engineer, Critical Reviewer, SRE Engineer và Security Reviewer.
Bạn là Product Owner; agent chính điều phối. Tối đa 3 subagent hoạt động đồng
thời, hoặc giới hạn thấp hơn của host; luân chuyển vai trò theo giai đoạn.

Architect chốt công nghệ và ADR; Tech Lead chốt cấu trúc code, formatter, lint,
test và CI. Research phải cung cấp nguồn và đánh giá mức phù hợp với dự án.
Reviewer dùng phiên độc lập với tác giả. Chi tiết tại [vai trò](docs/roles.md)
và [quy trình](docs/workflow.md).

## Gate có bằng chứng

```sh
./agile-team evidence ../du-an-moi docs/product-brief.md docs/research.md
./agile-team snapshot ../du-an-moi
./agile-team gate ../du-an-moi discovery
./agile-team advance ../du-an-moi
```

Đặt review thật tại `.team/gates/<stage>.json`, dựa trên `templates/gate.json`.
`gate` kiểm tra bản ghi, hash, phiên review khác tác giả và lỗi còn mở; nó không
thực thi các lệnh test được khai báo. `advance` kiểm tra cả các gate trước đó rồi
mới ghi bước kế tiếp. Code hoặc hợp đồng task thay đổi sẽ yêu cầu review lại;
thay đổi status/result của task không làm đổi hợp đồng. Symlink trong source bị
từ chối vì có thể làm snapshot bỏ sót nội dung thực thi. Danh sách loại trừ của
source snapshot được in trong kết quả `snapshot`; reviewer cần đối chiếu phạm vi
và khóa phiên bản image/dependency ở release.

Các gate là bản xác nhận có kiểm tra tính nhất quán, không phải sandbox hoặc chứng
nhận production. Điều phối viên phải xem bằng chứng gốc, session thật và kết quả
ở môi trường đích. `complete` không tự có nghĩa đã deploy. Nếu thiếu môi trường
đích, ghi rõ phần chuẩn bị đã xong và phần kiểm chứng còn bị chặn.

## Worker agy

```sh
.venv/bin/python scripts/agy_worker.py doctor
.venv/bin/python scripts/agy_worker.py doctor --probe
.venv/bin/python scripts/agy_worker.py run \
  --project-root ../du-an-moi --task .team/tasks/TASK-001.json --dry-run
```

Điền task thực tế theo `templates/task.json` trước khi gọi worker. Bỏ `--dry-run`
để thực thi, mặc định `plan`; chỉ vai trò được phép sửa mới dùng `--mode
accept-edits`. Adapter không tự đánh dấu task/gate đạt. Lưu log riêng trong
`.team/runs/`, có timeout và dọn process group. Allowed paths là hợp đồng công
việc; quyền thực tế do host/sandbox kiểm soát. Task/context có thể được gửi tới
dịch vụ model theo cấu hình tài khoản agy hiện tại.

**Kiểm tra live ở môi trường cài đặt ban đầu: blocked.** `agy --help` hoạt động nhưng worker
bị sandbox chặn ghi log/crash report dưới `~/.gemini/antigravity-cli` và bind
localhost. Chưa xác minh vòng chạy task thật. Không dùng cờ bỏ qua quyền để xử lý
lỗi đó. Các phần độc lập tiếp tục bằng native subagent; kiểm tra lại adapter trong
môi trường hợp lệ có thể khởi động agy.

## Kiểm tra và chuẩn code của toolkit

```sh
python3 -m venv .venv  # dùng Python 3.11+
.venv/bin/python -m pip install -r requirements-dev.txt
.venv/bin/ruff check .
.venv/bin/ruff format --check .
.venv/bin/python -m unittest discover -s tests -v
./agile-team check .
```

Toolkit đã cấu hình Ruff cố định phiên bản, EditorConfig và workflow CI ở
`.github/workflows/toolkit.yml`. Đây là chuẩn cho mã Python của toolkit; Tech Lead
sẽ chọn chuẩn và công cụ phù hợp cho ứng dụng sau khi Architect chốt stack.
Workflow CI đã được tạo; chỉ chạy trên GitHub sau khi repo được đưa lên đó.

Cấu hình dựa trên tài liệu [OpenAI — Subagents](https://learn.chatgpt.com/docs/agent-configuration/subagents)
và [Ruff — Installation](https://docs.astral.sh/ruff/installation/).
