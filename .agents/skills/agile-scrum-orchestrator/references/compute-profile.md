# Giới hạn compute cho nhóm AI

Kế thừa yêu cầu của người dùng từ team Antigravity ngày 12/11/2026:
huấn luyện/fine-tune chỉ trên Google Colab hoặc Kaggle; inference/evaluation phải
chạy được trên RTX 2060 6 GB. Ngoại lệ cần đề xuất rõ để người dùng quyết định.
Các giới hạn bên dưới là ngân sách thiết kế, không phải cam kết quota của cloud.

- Mục tiêu peak VRAM inference ≤ 5 GB, chừa khoảng 1 GB cho driver/desktop.
  Cộng weights, KV cache theo context length, activations và embedding/reranker
  chạy đồng thời. Không suy ra vừa VRAM chỉ từ kích thước file model.
- Ưu tiên thử model nhỏ (khoảng 0.5B–4B) và lượng tử hóa phù hợp. Model 7B–8B
  rất sát ngân sách; phải đo với context/concurrency thật và ghi CPU offload nếu có.
  Không áp ngưỡng số tham số như bằng chứng rằng một model chắc chắn vừa VRAM.
- RTX 2060/T4 thuộc Turing: chọn dtype/kernel thực sự hỗ trợ GPU đó; không mặc
  định native bf16 hoặc FlashAttention-2. Kiểm tra GPU thực tế của phiên cloud,
  phiên bản framework và compatibility trước khi chốt kernel/quantization.
- Training tiết kiệm tài nguyên: cân nhắc QLoRA/LoRA, batch/gradient accumulation,
  gradient checkpointing, seed và dependency pin; không ép một kỹ thuật cho mọi
  loại model. Ghi ngân sách GPU-hours, checkpoint định kỳ và resume sau ngắt phiên.
- Quota, thời lượng, GPU và lưu trữ Colab/Kaggle thay đổi: xác minh trong tài khoản
  và phiên hiện tại; không hardcode số quota cũ như dữ kiện chắc chắn.
- Agent tạo notebook và hướng dẫn. Người dùng chạy Colab và cung cấp log/artifact;
  chỉ dùng Kaggle CLI nếu người dùng đã cấu hình và cho phép chạy job đó. Không
  tự lấy token hoặc dùng thao tác giả lập để né giới hạn dịch vụ.
- Ghi dataset/version/hash, split train/val/golden chống leakage, model/tokenizer,
  seed, hyperparameters, dependency versions, checkpoint, logs và artifact hashes.
- MLOps-Eval dùng Golden Test độc lập với dữ liệu tune, đo chất lượng/safety,
  latency P50/P95, throughput, peak VRAM trên đúng RTX 2060 6 GB. Phân biệt thời
  gian cold/warm, context length, batch/concurrency và GPU/CPU offload.
- DevOps dựng inference/version/rollback; MLOps-Eval kiểm chứng độc lập bằng log
  và lệnh thật. Chưa có máy hoặc log thì báo blocked/chưa kiểm chứng, không pass.
- Dùng Python/venv/container phù hợp và giữ nguyên Python hệ thống. Toolkit này
  đã có Python 3.11 trong `.venv`; môi trường của ứng dụng AI được Tech Lead chốt.
