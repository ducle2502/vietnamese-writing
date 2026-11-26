---
name: vietnamese-writing
description: >-
  Viết, biên tập và kiểm tra tiếng Việt tự nhiên theo người đọc và mục đích sử dụng.
  Áp dụng cho email, báo cáo quản trị, bài nghiên cứu, văn bản pháp lý, mạng xã hội và
  bản dịch Anh - Việt. Đi kèm công cụ scripts/vi_scanner.py rà câu chữ máy móc, dịch thô,
  sáo rỗng và đối chiếu giữ nguyên dữ kiện gốc.
license: MIT
compatibility: Python 3.11+ (chỉ cần khi chạy công cụ scripts/vi_scanner.py)
metadata:
  author: ducle2502
  version: "2.5.0"
---

# vietnamese-writing

Viết câu tiếng Việt gọn ý, rõ chủ thể thực hiện và đúng người đọc. Viết tự nhiên nghĩa là dùng đúng từ cho đúng ngữ cảnh công việc, không suồng sã và không cực đoan xóa sạch từ Hán - Việt. Văn phong báo cáo kiểm toán phải khác văn phong mạng xã hội hoặc hợp đồng pháp lý.

## Xác định người đọc trước khi đặt bút

Trước khi viết hoặc sửa, xác định rõ người đọc trực tiếp, quy mô tổ chức (cá nhân, nhóm sinh viên hay doanh nghiệp) và quyết định họ cần đưa ra. Mặc định máy quét luôn chạy chế độ `all` để giữ chuẩn nền tối thiểu trên mọi văn bản. Dùng 7 nhóm thể loại (`general`, `audit_report`, `academic`, `legal`, `marketing`, `social_media`, `translation`) làm gợi ý cân chỉnh và chỉ truyền `--profile` khi người dùng chỉ định riêng. Chỉ hỏi lại khi thiếu thông tin dễ làm sai nội dung hoặc xưng hô.

| Nhóm văn bản | Trọng tâm biên tập |
| :--- | :--- |
| Báo cáo quản trị, kiểm toán (`audit_report`) | Đưa kết luận, hệ quả và con số lên đầu. Quy đổi lỗi kỹ thuật thành tác động tiền bạc, vận hành hoặc tuân thủ. Tách rõ phần đã kiểm chứng với phần chưa đủ căn cứ. |
| Học thuật, nghiên cứu (`academic`) | Giữ chuẩn thuật ngữ ngành. Dẫn nguồn `(Tác giả, Năm)` hoặc `[Số]` ngay sau nhận định tổng quan, không mở bài câu khách. |
| Pháp lý, công vụ (`legal`) | Giữ nguyên thuật ngữ luật định, chủ thể quyền nghĩa vụ và viện dẫn Điều, Khoản chính xác. Không đổi từ chuyên môn sang khẩu ngữ. |
| Mạng xã hội, chia sẻ chuyên môn (`social_media`) | Mở thẳng vào tình huống đời thường dễ hình dung trước khi nói tới giải pháp. Tránh nhét tên hàm lập trình hay công thức khô cứng. |
| Tiếp thị, giới thiệu (`marketing`) | Nêu lợi ích gắn với đối tượng và số liệu cụ thể, không hứa hẹn quá bằng chứng. |
| Dịch thuật Anh - Việt (`translation`) | Bóc tách ý gốc rồi sắp lại theo mạch Đề - Thuyết tiếng Việt. Bỏ câu bị động dịch từng chữ nhưng giữ nguyên điều kiện và mức độ chắc chắn. |
| Tin bài, tài liệu kỹ thuật, trao đổi chung (`general`) | Câu ngắn vừa (`12` đến `28` chữ), mỗi câu một ý chính, chức danh khớp đúng quy mô thật. |

## Nguyên tắc câu chữ, nhịp đoạn và bằng chứng

**Mở thẳng vào sự kiện hoặc số liệu.** Cắt bỏ câu xã giao kiểu chatbot (*"Chắc chắn rồi! Dưới đây là..."*, *"Hy vọng thông tin này hữu ích"*), câu mở bài sáo (*"Trong bối cảnh... ngày càng phát triển"*), câu kết hứa hẹn chung chung và hộp răn đe pháp lý tự phát. Với tài liệu kỹ thuật, bỏ định ngữ độn câu, đuôi kể công phủ định (*"và không cần cài thêm..."*) và vế giải thích lại điều hiển nhiên.

**Câu ngắn, chủ động và rõ người làm.** Ưu tiên chủ thể cụ thể đi cùng động từ trực tiếp. Giữ mỗi câu văn xuôi và ô bảng tối đa `35` từ (`45` từ với điều khoản pháp lý), vì vượt ngưỡng này cả `scan` lẫn `profile` đều trả lỗi ngay. Tránh câu bị động dịch từng chữ từ *by* (*"được phê duyệt bởi"*, *"được CMake tự động tải"*), cụm danh từ hóa (*"sự sụt giảm của"*), chủ ngữ giả (*"Nó là cần thiết để"*), cụm mở câu vòng vo (*"Thông qua việc..."*), động từ rỗng (*"tiến hành việc kiểm tra"*) và tính từ quảng cáo sáo (*"cảnh báo thông minh"*, *"giao diện mượt"*).

**Nhịp đoạn và nguyên tắc bằng chứng cho báo cáo quản trị.** Xem chuẩn đầy đủ tại [references/voice-and-argument-patterns.md](references/voice-and-argument-patterns.md). Giữ câu trung bình `15` đến `24` từ (`CV >= 0,40`), mỗi đoạn dưới `2` câu. Để giữ `CV >= 0,40`, hãy xen câu `7–10` từ đủ chủ ngữ và vị ngữ với câu dữ kiện `22–31` từ. Tuyệt đối không cắt thành câu cụt `4–6` từ thiếu chủ ngữ. Chia báo cáo kiểm toán thành 3 lớp (Trang đầu, Thân bài, Phụ lục), trình bày phát hiện theo khung `5C` và giữ mã theo dõi nội bộ (`EV-xx`, `WP-xx`, `CL-xx`, `GAP-xx`) ở giấy tờ làm việc. Dùng nhãn đoạn ngắn kết thúc bằng dấu chấm (*Thực trạng và bằng chứng.*, *Nguyên nhân kiểm soát.*, *Rủi ro và ảnh hưởng.*, *Kiến nghị.*) thay cho danh sách hai chấm.

**Khóa số liệu và ranh giới khẳng định.** Luôn ghép đủ `Tử số/Mẫu số (Tỷ lệ %)` khi chốt kết luận. Tách hoạt động trung gian (*đang trình, đã họp, hướng dẫn lại*) khỏi đầu ra kiểm chứng và không gộp mục còn lỗi vào tỷ lệ hoàn thành. Không lấy tổng bù trừ ròng bằng `0` để kết luận khớp đúng từng dòng. Chỉ dùng đúng một từ *có thể* khi nêu rủi ro tương lai và tránh khẳng định tuyệt đối vượt quá mẫu kiểm tra.

**Viết ghi chú bảng kiểm đánh giá (`Có / Một phần / Chưa có`).** Mỗi ô ghi chú chỉ viết `1` câu tối đa `35` từ nêu thẳng lý do chấm. Không mở đầu bằng *"Có vì"*, *"Một phần vì"* hay *"Chưa có vì"*, và không đưa mã bằng chứng hay tên trường kỹ thuật vào cột ghi chú. Dùng *"chưa tìm thấy"* thay cho *"thiếu"* hay *"không có"* khi chưa đọc hết hồ sơ.

**Trình bày sạch và tránh lặp hai tầng.** Không vẽ hộp tóm tắt 4 ô (`01` đến `04`) lặp lại bảng chi tiết ngay bên dưới, không tự bịa bảng so sánh với công cụ lớn hay bảng tiến độ `G1` đến `G4` thiếu mốc thật. Bỏ bảng giải thích lại điều đã rõ và bỏ câu hù dọa rủi ro chung chung. Không nhồi số đếm tùy ý vào tiêu đề kiểu listicle và không thay máy móc bằng `"một số"`, `"những"`, `"các"`. Chỉ giữ con số khi gắn với giới hạn thật của công cụ hoặc khung cấu trúc cố định. Khi tài liệu có biểu đồ PNG vẽ bằng `matplotlib` hoặc `Pillow`, phải kiểm tra trực tiếp chữ tiếng Việt trong mã sinh ảnh. Giữ `alt` ảnh và nhãn cạnh Mermaid gọn trong `2` đến `8` chữ, chú thích `#` cây thư mục tối đa `10` chữ, chỉ bọc dấu nháy ngược quanh tên tệp, lệnh hoặc mã nguồn.

**Dùng đúng từ theo ngữ cảnh công việc.** Tránh dùng sai nghĩa Hán - Việt (*"thực chứng"* thay cho *dựa trên bằng chứng*, *"khắc phục yếu điểm"* thay cho *điểm yếu*). Rà các lỗi chính tả hay gặp (`sồn sã`, `chỉnh chu`, `chuẩn đoán`, `chắp bút`, `cập nhập`, `sát nhập`, `dậm chân`, `xoay sở`, `xuất sứ`). Không dịch từng chữ thuật ngữ phần mềm (*"khung hợp đồng"*, *"hiện thực lớp"*, *"túi chứa dữ liệu"*), không tự phong chức danh tập đoàn cho đồ án nhỏ. Không dịch sát *gap* thành *"khoảng trống"* trừu tượng khi đã có *thiếu sót* hay *lỗ hổng kiểm soát*. Giữ nguyên từ quen dùng như `email`, `pull request` và không chêm tiếng Anh tùy tiện (`booking lịch`). Tránh ghép *"cảnh báo + lĩnh vực"* (*"cảnh báo pháp lý"*, *"cảnh báo tuân thủ"*). Hãy đổi sang *lưu ý pháp lý* hoặc nêu thẳng rủi ro cần xử lý.

**Phân loại giọng văn qua `profile`.** Lệnh trả 4 kiểu giọng chính cùng nhãn mặc định `CLEAN_GENERAL_VIETNAMESE`. Nhãn `MULTI_READER_ASSURANCE` chỉ bật khi có từ `2` nhãn bằng chứng hoặc cấu trúc phân luồng người đọc. Đoạn quá dài hoặc nhịp câu quá đều trả kèm cảnh báo `BUREAUCRATIC_OR_MONOTONE_DRAFT`.

## Năm lỗi sửa quá tay cần tránh

1. Đừng vặn câu thành lối đếm tuần tự ngô nghê (`Hồ sơ thứ nhất... Sang hồ sơ thứ hai...`) chỉ để né cờ lặp từ. Khi nhiều dòng cùng cấu trúc, chuyển sang bảng.
2. Tránh hạ giọng xuống suồng sã hoặc kịch tính hóa hiện trường (`Anh Minh ơi,`, `rủi ro sát sườn`, `trực chiến 24/7`, `tử huyệt`, `phát lộ`, `vạch trần`, `sập API`, `vỏn vẹn`, `giậm chân tại chỗ`). Để số liệu tự nói mức độ, bỏ câu tự khen xếp loại (`loại giỏi`).
3. Không tự bịa từ đời thường ngô nghê trái cách gọi công việc (`in đúp` thay vì *lặp dòng*, `chép thiếu tiền` thay vì *chuyển thiếu số dư*).
4. Giữ nguyên dữ kiện gốc, ngày tháng, điều kiện và mức độ chắc chắn. Không đổi *có thể giảm* thành *giảm*, *sau khi* thành *nhờ* hay xóa *nếu / trừ khi*. Không suy diễn việc chưa tìm thấy hồ sơ thành đơn vị không làm. Nếu đổi chữ có nguy cơ làm lệch mức chắc chắn pháp lý hoặc gặp chữ viết tắt nội bộ chưa rõ tên đầy đủ, hãy giữ nguyên và gắn cờ `NEEDS_AUTHOR_DECISION`. Đồng thời, kiểm tra giải nghĩa chữ viết tắt ngay ở lần xuất hiện đầu tiên trên bản ghép hoàn chỉnh.
5. Không xoay vòng động từ đồng nghĩa gượng gạo (*Khóa / Thiết kế / Xây dựng / Hiện thực / Lập trình...*) ở đầu các ô bảng chỉ để né `VIS-FMT-005`. Với bảng phân công kỹ thuật, bỏ động từ dẫn đầu và ghi thẳng tên tệp, lớp hoặc đầu việc.

## Chuyển tệp nguồn sang Markdown thô

Khi người dùng gửi tệp, Agent chuyển sang `TEN_GOC.raw.md` rồi mới quét. Thứ tự ưu tiên như sau, dừng ngay ở bước chạy được:

1. Chạy công cụ chuyển đổi trực tiếp: thư viện đọc `.docx` tích hợp sẵn (`extract_docx_text_and_meta`), hoặc `markitdown`, `liteparse`, `docling`, `pandoc` cho `.pdf`, `.xlsx`, `.pptx`, `.html`.
2. Nếu bước 1 lỗi hoặc làm mất bảng: dùng `vision` đọc bản render trang và chép lại thành Markdown có cấu trúc.
3. Nếu `vision` vẫn không đọc được: dừng và báo rõ tên tệp cùng lý do, tuyệt đối không tự bịa nội dung.

Luôn ưu tiên bước 1 trước khi gọi mô hình ngôn ngữ. Chuyển một lần, lưu vết theo `sha256` của tệp gốc và giữ nguyên thứ tự đoạn, bảng, tiêu đề, số liệu cùng đường dẫn trong bản `.raw.md`.

Mỗi bản chuyển đi kèm `TEN_GOC.raw.meta.json`:

```json
{"source": "BAO_CAO.pdf", "sha256": "...", "converter": "docling",
 "deterministic": true, "needs_review": false}
```

Khi phải dùng nhánh `vision`, ghi `converter=vision`, `deterministic=false`, `needs_review=true` và báo người dùng kiểm tra lại số liệu trước khi kết luận. Lệnh `verify` chỉ dùng đáng tin cậy khi tệp gốc đã chuyển trực tiếp ở bước 1. Riêng `.docx`, hai lệnh `scan` và `profile` tự đọc trực tiếp từ tệp Word.

## Tự quét, lập hồ sơ và đối soát dữ kiện

Sau khi viết mới hoặc nhận `TEN_GOC.raw.md`, luôn chạy [scripts/vi_scanner.py](scripts/vi_scanner.py) trước khi bàn giao (trừ câu trả lời hội thoại ngắn 1 đến 2 câu):

```bash
# Quét chuẩn nền chung trên toàn bộ 7 nhóm (mặc định)
python scripts/vi_scanner.py scan TEN_GOC.raw.md --json

# Quét báo cáo và bỏ qua cột bảng trích lục của bên thứ ba
python scripts/vi_scanner.py scan TEN_GOC.raw.md --profile audit_report --ignore-table-cols 2,3

# Lập hồ sơ 18 chỉ số nhịp câu (stylometry) và 14 chỉ số lập luận DHDNA
python scripts/vi_scanner.py profile TEN_GOC.raw.md --ignore-table-cols 2,3 --json

# Đối chiếu 6 nhóm dữ kiện gốc trước và sau khi sửa
python scripts/vi_scanner.py verify TEN_GOC.raw.md BAN_SUA.md
```

Ở lượt quét đầu tiên, `scan` mặc định rà ở chế độ `all` để bảo đảm chuẩn tối thiểu chung, kèm sẵn `applicable_profiles`, `exempt_profiles` và gợi ý `suggestion_vi`. Lỗi vượt ngưỡng độ dài câu (`VIS-LEN-001`) bắt buộc tách câu về `0` lỗi trên mọi loại tài liệu. Với các tín hiệu khác, dựa vào ngữ cảnh thực tế của người đọc để quyết định sửa hay giữ, chỉ thêm `--profile` khi người dùng chỉ định riêng.

Tra cứu thêm tại bốn tệp tham chiếu: [references/rule-catalog.md](references/rule-catalog.md), [references/voice-and-argument-patterns.md](references/voice-and-argument-patterns.md), [references/loanwords-and-exceptions.md](references/loanwords-and-exceptions.md) và [references/pattern-bank.md](references/pattern-bank.md). Khi sửa trên văn bản có sẵn, luôn giữ lại `TEN_GOC.raw.md` để chạy `verify` đối chiếu dữ kiện. Lệnh này kiểm tra con số, từ phủ định, điều kiện, mức chắc chắn, đường dẫn và nguồn trích dẫn. Khi bàn giao, trả thẳng bản hoàn thiện và không kèm bảng điểm hay lời kể quy trình trừ khi người dùng hỏi.

## Bảo trì bảng quy tắc và từ vựng

Toàn bộ `2.197` mục từ và `55` quy tắc nằm trong hai tệp CSV chuẩn `UTF-8 BOM` ([data/vocab.csv](data/vocab.csv) và [data/grammar.csv](data/grammar.csv)) để mở chỉnh trực tiếp bằng Excel. Định kỳ hàng quý hoặc hàng năm, chạy `python scripts/vi_scanner.py check-maintenance` và rà soát danh sách từ mượn theo [references/loanwords-and-exceptions.md](references/loanwords-and-exceptions.md).
