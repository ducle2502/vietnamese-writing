---
name: vietnamese-writing
description: >-
  Viết, biên tập và kiểm tra tiếng Việt tự nhiên theo người đọc và mục đích sử dụng.
  Dùng khi soạn thảo hoặc rà soát câu trả lời, email, báo cáo quản trị, bài báo
  học thuật, văn bản pháp lý, bài đăng mạng xã hội và bản dịch Anh - Việt. Đi kèm
  công cụ scripts/vi_scanner.py rà câu chữ máy móc, dịch thô, sáo rỗng và đối soát
  bảo toàn dữ kiện.
license: MIT
compatibility: Python 3.11+ (chỉ cần khi chạy công cụ scripts/vi_scanner.py)
metadata:
  author: ducle2502
  version: "2.2.0"
---

# vietnamese-writing

Viết câu tiếng Việt đứng độc lập, rõ chủ thể, gọn ý và hợp người đọc. Viết tự nhiên là đặt đúng từ vào đúng ngữ cảnh công việc, không phải xuề xòa hay cực đoan xóa sạch từ Hán - Việt. Câu văn trong báo cáo kiểm toán tất nhiên phải khác câu trên mạng xã hội hoặc trong hợp đồng pháp lý.

## Xác định người đọc trước khi đặt bút

Trước khi viết hoặc sửa, hãy xác định văn bản thuộc nhóm nào trong 7 nhóm (`general`, `audit_report`, `academic`, `legal`, `marketing`, `social_media`, `translation`) và ai sẽ đọc trực tiếp. Làm rõ luôn quy mô của chủ thể viết (cá nhân, nhóm sinh viên, dự án mã nguồn mở hay doanh nghiệp) cùng quyết định mà người đọc cần đưa ra. Chỉ hỏi lại khi thiếu thông tin có nguy cơ làm sai nội dung hoặc xưng hô.

| Nhóm văn bản | Yêu cầu trọng tâm |
| :--- | :--- |
| Báo cáo quản trị, kiểm toán (`audit_report`) | Đưa kết luận, hệ quả và con số lên đầu. Diễn đạt lỗi kỹ thuật thành tác động vận hành hoặc tiền bạc cho lãnh đạo bận rộn. Tách rõ phần đã có bằng chứng xác thực với phần chưa đủ căn cứ. |
| Học thuật, nghiên cứu (`academic`) | Giữ chuẩn thuật ngữ ngành, dẫn nguồn cụ thể `(Tác giả, Năm)` hoặc `[Số]` ngay sau nhận định tổng quan, không dùng câu mở bài câu khách. |
| Pháp lý, công vụ (`legal`) | Giữ đúng thuật ngữ luật định, chủ thể quyền và nghĩa vụ, viện dẫn Điều và Khoản chính xác, không tự ý đổi từ chuyên môn sang khẩu ngữ. |
| Mạng xã hội, chia sẻ chuyên môn (`social_media`) | Mở thẳng vào tình huống thực tế. Dẫn dắt từ thao tác đời thường dễ hình dung trước khi nâng dần lên giải pháp tự động, tránh chèn tên hàm lập trình hoặc công thức toán khô cứng. |
| Tiếp thị, giới thiệu (`marketing`) | Nêu rõ lợi ích gắn với đối tượng và con số cụ thể, không hứa hẹn quá mức bằng chứng. |
| Dịch thuật Anh - Việt (`translation`) | Bóc ý gốc rồi sắp lại theo mạch Đề - Thuyết tự nhiên của tiếng Việt, dẹp bỏ câu bị động dịch từng chữ nhưng giữ nguyên toàn bộ điều kiện và sắc thái chắc chắn. |
| Tin bài, tài liệu kỹ thuật, trao đổi chung (`general`) | Câu ngắn và vừa (`12` đến `28` chữ), một ý chính mỗi câu, xưng hô và chức danh khớp đúng quy mô thực tế. |

## Nguyên tắc câu chữ, nhịp đoạn và kỷ luật bằng chứng

Mở thẳng vào vấn đề, sự kiện hoặc số liệu. Bỏ các câu rào đón kiểu chatbot (*"Chắc chắn rồi! Dưới đây là..."*, *"Hy vọng thông tin này hữu ích"*), câu mở bài vĩ mô (*"Trong bối cảnh... ngày càng phát triển"*), câu kết hứa hẹn chung chung (*"hứa hẹn mở ra kỷ nguyên mới"*) và hộp cảnh báo đạo đức hoặc pháp lý tự phát khi người dùng không yêu cầu. Ở câu mở đầu tài liệu kỹ thuật, cắt bỏ các định ngữ độn câu, đuôi phủ định kể công (*"và không cần cài thêm..."*) cùng vế giải thích lại hệ quả hiển nhiên (*"nên không phải..."*).

Ưu tiên chủ thể chỉ người hoặc đơn vị cụ thể đi với động từ trực tiếp. Giữ mỗi câu văn xuôi hoặc câu trong ô bảng tối đa `35` chữ (`45` chữ với điều khoản pháp lý). Mọi câu vượt ngưỡng này đều bị chặn cứng ở cả `scan` lẫn `profile`. Tránh câu bị động dịch sát từ chữ *by* (*"được phê duyệt bởi"*, *"được CMake tự động tải"*), cụm danh từ hóa (*"sự sụt giảm của"*, *"việc triển khai của"*) và chủ ngữ giả (*"Nó là cần thiết để"*). Cắt bỏ cụm mở câu vòng vo (*"Thông qua việc..."*, *"Liên quan đến vấn đề..."*), động từ rỗng (*"tiến hành việc kiểm tra"* thay vì *"kiểm tra"*) và tính từ quảng cáo rỗng (*"cảnh báo thông minh"*, *"giao diện mượt"*, *"bảng trực quan"*, *"đóng ứng dụng an toàn"*).

Giữ nhịp đoạn cô đọng và áp dụng kỷ luật bằng chứng theo chuẩn [references/voice-and-argument-patterns.md](references/voice-and-argument-patterns.md). Trong văn bản kiểm toán, giám sát và quản trị rủi ro, giữ độ dài câu trung bình từ `15` đến `24` chữ (`CV >= 0,40`), mỗi đoạn dưới `2` câu. Mở đầu mục bằng kết luận trực diện hoặc đặt tiêu đề hai vế đối lập (*Chủ đề: Điểm tiến bộ, nhưng điểm nghẽn cốt lõi vẫn hạn chế kết quả*). Dùng nhãn phân đoạn ngắn kết thúc bằng dấu chấm (*Thực trạng và bằng chứng.*, *Nguyên nhân kiểm soát.*, *Rủi ro và ảnh hưởng.*, *Kiến nghị.*) thay cho danh sách hai chấm. Luôn ghép cặp `Tử số/Mẫu số (Tỷ lệ %)` khi chốt kết luận và tách bạch hoạt động trung gian (*đang trình, đã họp, đã hướng dẫn lại*) khỏi đầu ra kiểm chứng được. Không cộng gộp hạng mục còn lỗi vào tỷ lệ hoàn thành và không dùng tổng bù trừ ròng bằng `0` để kết luận khớp đúng từng dòng. Chỉ dùng đúng một từ tình thái *có thể* khi nêu hệ quả rủi ro tương lai.

Giữ nhịp trình bày sạch, không lặp hai tầng. Không vẽ hộp tóm tắt 4 ô (`01` đến `04`) ngay trước bảng chức năng chi tiết và không mở thẻ `<details>` lặp lại bảng phân công đã có. Trong tài liệu đồ án nhỏ, không tự bịa bảng so sánh với công cụ lớn hay phương án bù nhìn. Giữ văn bản thay thế ảnh (`alt="..."`) ngắn gọn từ `2` đến `6` chữ nêu đúng tên hình mà không kèm khẩu hiệu quảng cáo. Chú thích sau dấu `#` trong cây thư mục không vượt quá `10` chữ, và chỉ bọc dấu nháy ngược quanh tên tệp, lệnh hoặc mã nguồn.

Chọn đúng từ theo thực tế công việc và khớp vai người viết. Tránh dùng sai nghĩa từ Hán - Việt (như lấy chữ *"thực chứng"* để dịch *evidence-based*, hoặc viết *"khắc phục yếu điểm"* thay cho *điểm yếu*). Rà kỹ các lỗi sai chính tả vỏ ngữ âm công sở (`chỉnh chu`, `chuẩn đoán`, `chắp bút`, `cập nhập`, `sát nhập`, `dậm chân`, `xoay sở`, `xuất sứ`). Không dịch từng chữ thuật ngữ phần mềm sang các cụm xa lạ (*"khung hợp đồng"*, *"khung vận hành"*, *"khóa hợp đồng"*, *"giao kèo dữ liệu"*, *"khung chạy sẵn"*, *"hiện thực lớp"*, *"túi chứa dữ liệu"*). Không tự phong chức danh tập đoàn (*"Kỹ sư giao thức mạng"*, *"20 tác vụ vòng đời phần mềm"*, *"tác vụ/thành viên"*) cho bài tập nhóm sinh viên. Không dịch ngược từ tiếng Anh đã quen dùng (`email` thành *"thư điện tử"*, `pull request` thành *"yêu cầu kéo"*) và không chêm từ ngoại lai lửng lơ (`booking lịch`).

## Năm lỗi sửa quá tay cần tránh

1. Tránh vặn câu thành lối đếm tuần tự ngô nghê (`Hồ sơ thứ nhất... Sang hồ sơ thứ hai... Ở hồ sơ thứ ba...`) chỉ để né cảnh báo lặp từ của máy quét. Khi có nhiều dòng số liệu cùng cấu trúc, hãy chuyển sang bảng.
2. Tuyệt đối tránh biến văn bản trình lãnh đạo thành giọng sồn sã hoặc kịch tính hóa hiện trường (`Anh Minh ơi,`, `cố bấm nút`, `rủi ro sát sườn`, `trực chiến 24/7`, `tử huyệt`). Đồng thời không bê động từ điều tra hình sự, cổ văn hoặc báo chí giật gân (`phát lộ`, `phát giác`, `vạch trần`, `sập API`, `vỏn vẹn`, `giậm chân tại chỗ`) vào báo cáo kỹ thuật. Văn quản trị cần điềm tĩnh, để con số tự nói lên mức độ nghiêm trọng và bỏ hẳn câu tự khoe xếp loại (`loại giỏi`, `very good`).
3. Cấm tự bịa từ đời thường ngô nghê trái cách gọi nơi làm việc (`in đúp` thay vì *lặp dòng*, `chép thiếu tiền` thay vì *chuyển thiếu số dư*, `cho máy tính ghép` thay vì *chạy đối soát tự động*).
4. Giữ nguyên dữ kiện và mức độ chắc chắn khi rút gọn câu. Không đổi *có thể giảm* thành *giảm*, không đổi *sau khi* thành *nhờ* và không xóa điều kiện *nếu / trừ khi*. Tuyệt đối không coi việc chưa tìm thấy hồ sơ là bằng chứng đơn vị không thực hiện.
5. Cấm xoay vòng động từ đồng nghĩa gượng gạo (`Khóa hợp đồng / Thiết kế / Xây dựng / Hiện thực / Lập trình / Phát triển / Tính toán / Lập bộ / Soạn / Thiết lập`) ở đầu các ô bảng hoặc danh sách chỉ để lách cờ lặp từ `VIS-FMT-005`. Trong bảng phân công hoặc bảng liệt kê thành phần kỹ thuật, bỏ hẳn động từ dẫn đầu và ghi thẳng tên tệp, lớp hoặc đầu việc.

## Tự quét bài viết, lập hồ sơ giọng văn và đối soát bằng `scripts/vi_scanner.py`

Sau khi viết mới hoặc biên tập xong tệp `.md`, `.txt`, `.docx` hay bài viết bất kỳ, bắt buộc tự quét lại đầu ra bằng [scripts/vi_scanner.py](scripts/vi_scanner.py) trước khi bàn giao. Chỉ miễn bước này với câu trả lời hội thoại ngắn 1 đến 2 câu:

```bash
# Quét tệp vừa viết hoặc vừa sửa (.md, .txt, .docx; mặc định xuất đủ 100% tín hiệu mọi nhóm)
python scripts/vi_scanner.py scan TEP_VUA_VIET.md --json

# Quét tệp báo cáo .docx và bỏ qua các cột bảng chứa văn bản trích lục của bên thứ ba
python scripts/vi_scanner.py scan BAO_CAO.docx --profile audit_report --ignore-table-cols 2,3

# Lập hồ sơ 18 chỉ số nhịp câu (stylometry) và 12 chỉ số kỷ luật lập luận DHDNA
python scripts/vi_scanner.py profile BAO_CAO.docx --ignore-table-cols 2,3 --json

# Nếu sửa trên văn bản có sẵn của người dùng, chạy thêm bước đối soát dữ kiện
python scripts/vi_scanner.py verify BAN_GOC.md BAN_SAU_SUA.md
```

Ở bước quét đầu tiên, lệnh `scan` mặc định chạy ở chế độ `all` và xuất đủ 100% tín hiệu của cả 7 nhóm văn bản. Mỗi kết quả đều ghi rõ `applicable_profiles` (nhóm áp dụng), `exempt_profiles` (nhóm miễn trừ) và gợi ý `suggestion_vi` khớp trực tiếp với cụm từ bị đánh dấu. Riêng lỗi câu quá dài (`VIS-LEN-001`, vượt `35` từ hoặc `45` từ với văn bản pháp lý, kể cả trong ô bảng) làm cả `scan` lẫn `profile` trả mã lỗi `1` ngay lập tức. Khi gặp lỗi độ dài câu, Agent bắt buộc tách câu hoặc rút gọn cho đến khi đạt `0` lỗi, tuyệt đối không miễn trừ giữ nguyên. Với các tín hiệu khác, hãy đối chiếu `applicable_profiles` cùng loại tài liệu thực tế để quyết định sửa hay giữ nguyên. Chỉ truyền `--profile <tên_nhóm>` khi cần lọc riêng cho một thể loại cố định. Tra cứu đủ 42 mã quy tắc tại [references/rule-catalog.md](references/rule-catalog.md), mẫu giọng văn chức năng tại [references/voice-and-argument-patterns.md](references/voice-and-argument-patterns.md) và bảng ngoại lệ tại [references/loanwords-and-exceptions.md](references/loanwords-and-exceptions.md).

Ở bước hậu kiểm, luôn lưu bản gốc trước khi sửa để chạy lệnh `verify`. Lệnh này đối soát 6 nhóm dữ kiện gốc: con số (kể cả ngày tháng, phần trăm), phủ định, điều kiện, mức chắc chắn, đường dẫn/code và nguồn trích dẫn. Nếu bản sửa làm lệch nhóm nào ngoài chủ đích (trừ trường hợp gọt cụm rào đón chồng chéo như `dường như có vẻ như`), phải khôi phục đúng nghĩa gốc trước khi bàn giao.

Khi trả kết quả cho người dùng, gửi thẳng văn bản đã hoàn thiện. Không đính kèm bảng điểm máy quét hay kể lại quy trình biên tập trừ khi người dùng yêu cầu nhận xét câu chữ.

## Bảo trì bảng quy tắc và từ vựng trên CSV

Toàn bộ quy tắc và từ vựng nằm tại hai tệp CSV chuẩn `UTF-8 BOM` mở trực tiếp bằng Excel. Tệp [data/vocab.csv](data/vocab.csv) quản lý từ mượn quen dùng, cụm dịch ngược, lối chêm từ ngoại lai và các cụm văn mẫu cần tránh, còn [data/grammar.csv](data/grammar.csv) khai báo 42 quy tắc cấu trúc cùng trọng số. Định kỳ hàng quý hoặc hàng năm, chạy lệnh `python scripts/vi_scanner.py check-maintenance` và rà soát theo hướng dẫn tại [references/loanwords-and-exceptions.md](references/loanwords-and-exceptions.md).
