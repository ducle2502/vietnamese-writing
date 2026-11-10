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
  version: "2.0.0"
---

# vietnamese-writing

Viết câu tiếng Việt đứng độc lập, rõ chủ thể, gọn ý và hợp người đọc. Tự nhiên không có nghĩa là xuề xòa hay loại bỏ hết từ Hán - Việt. Một câu phù hợp với báo cáo kiểm toán sẽ khác câu trên mạng xã hội hoặc trong hợp đồng pháp lý.

## Xác định người đọc trước khi đặt bút

Trước khi viết hoặc sửa, tự xác định văn bản thuộc nhóm nào trong 7 nhóm (`general`, `audit_report`, `academic`, `legal`, `marketing`, `social_media`, `translation`), ai là người đọc trực tiếp và họ cần ra quyết định gì. Chỉ hỏi lại người dùng khi thiếu thông tin làm sai lệch nội dung hoặc xưng hô.

| Nhóm văn bản | Yêu cầu trọng tâm |
| :--- | :--- |
| Báo cáo quản trị, kiểm toán (`audit_report`) | Đưa kết luận, hệ quả và con số lên đầu. Diễn đạt lỗi kỹ thuật thành tác động vận hành hoặc tiền bạc cho lãnh đạo bận rộn. Tách rõ phần đã có bằng chứng xác thực với phần chưa đủ căn cứ. |
| Học thuật, nghiên cứu (`academic`) | Giữ chuẩn thuật ngữ ngành, dẫn nguồn cụ thể `(Tác giả, Năm)` hoặc `[Số]` ngay sau nhận định tổng quan, không dùng câu mở bài câu khách. |
| Pháp lý, công vụ (`legal`) | Giữ đúng thuật ngữ luật định, chủ thể quyền và nghĩa vụ, viện dẫn Điều và Khoản chính xác, không tự ý đổi từ chuyên môn sang khẩu ngữ. |
| Mạng xã hội, chia sẻ chuyên môn (`social_media`) | Mở thẳng vào tình huống thực tế. Dẫn dắt từ thao tác đời thường dễ hình dung trước khi nâng dần lên giải pháp tự động, tránh chèn tên hàm lập trình hoặc công thức toán khô cứng. |
| Tiếp thị, giới thiệu (`marketing`) | Nêu rõ lợi ích gắn với đối tượng và con số cụ thể, không hứa hẹn quá mức bằng chứng. |
| Dịch thuật Anh - Việt (`translation`) | Bóc ý gốc rồi sắp lại theo mạch Đề - Thuyết tự nhiên của tiếng Việt, dẹp bỏ câu bị động dịch từng chữ nhưng giữ nguyên toàn bộ điều kiện và sắc thái chắc chắn. |
| Tin bài, trao đổi chung (`general`) | Câu ngắn và vừa (`12` đến `28` chữ), một ý chính mỗi câu, xưng hô nhất quán. |

## Nguyên tắc câu chữ cốt lõi

Mở thẳng vào vấn đề, sự kiện hoặc số liệu. Bỏ các câu rào đón kiểu chatbot (*"Chắc chắn rồi! Dưới đây là..."*, *"Hy vọng thông tin này hữu ích"*), câu mở bài vĩ mô (*"Trong bối cảnh... ngày càng phát triển"*) và câu kết hứa hẹn chung chung (*"hứa hẹn mở ra kỷ nguyên mới"*).

Ưu tiên chủ thể chỉ người hoặc đơn vị cụ thể đi với động từ trực tiếp. Tránh câu bị động dịch sát từ chữ *by* (*"được phê duyệt bởi"*), cụm danh từ hóa nặng nề (*"sự sụt giảm của"*, *"việc triển khai của"*), chủ ngữ giả (*"Nó là cần thiết để"*) và thói quen nhét động từ rỗng (*"tiến hành việc kiểm tra"* thay vì *"kiểm tra"*).

Giữ nhịp trình bày sạch và thoáng. Không rải từ nối sách vở (*"Hơn nữa,"*, *"Thêm vào đó,"*, *"Bên cạnh đó,"*) ở đầu mọi câu, không đóng khuôn danh sách bằng nhãn in đậm kèm dấu hai chấm lặp đi lặp lại ở mọi gạch đầu dòng, không dùng dấu gạch ngang dài (`—`) nối mệnh đề kiểu tiếng Anh.

Chọn đúng từ theo thực tế công việc. Không dùng sai nghĩa từ Hán - Việt (như dùng chữ *"thực chứng"* của triết học để dịch cụm *dựa trên bằng chứng*), không dịch ngược các từ tiếng Anh đã quen dùng hàng ngày (`email` thành *"thư điện tử"*, `web` thành *"mạng toàn cầu"*).

## Bốn cái bẫy cấm mắc khi sửa văn

1. Tránh vặn câu thành lối đếm tuần tự ngô nghê (`Hồ sơ thứ nhất... Sang hồ sơ thứ hai... Ở hồ sơ thứ ba...`) chỉ để né cảnh báo lặp từ của máy quét. Khi có nhiều dòng số liệu cùng cấu trúc, hãy trình bày thành bảng.
2. Tuyệt đối tránh biến văn bản trình lãnh đạo thành giọng sồn sã hoặc giật gân báo chí (`Anh Minh ơi,`, `cố bấm nút`, `rủi ro sát sườn`, `tê liệt`, `tử huyệt`). Văn quản trị cần điềm tĩnh, lễ độ chừng mực, để con số tự nói lên mức độ nghiêm trọng và bỏ các câu khen xã giao hoặc tự khoe xếp loại (`loại giỏi`, `very good`).
3. Cấm tự bịa từ đời thường ngô nghê trái cách gọi nơi làm việc (`in đúp` thay vì *lặp dòng*, `chép thiếu tiền` thay vì *chuyển thiếu số dư*, `cho máy tính ghép` thay vì *chạy đối soát tự động*).
4. Giữ nguyên dữ kiện và mức độ chắc chắn khi rút gọn câu. Không đổi *có thể giảm* thành *giảm*, không đổi *sau khi* thành *nhờ*, không xóa điều kiện *nếu / trừ khi* và không coi việc chưa tìm thấy hồ sơ là bằng chứng đơn vị không thực hiện.

## Quy trình quét và đối soát với `scripts/vi_scanner.py`

Khi biên tập tệp hoặc bài viết dài, chạy công cụ [scripts/vi_scanner.py](scripts/vi_scanner.py) theo trình tự hai bước (đường dẫn tính từ thư mục chứa kỹ năng này):

```bash
python scripts/vi_scanner.py scan TEP_CAN_RA.md --json
python scripts/vi_scanner.py verify BAN_GOC.md BAN_SAU_SUA.md
```

Ở bước quét đầu tiên, lệnh `scan` mặc định chạy ở chế độ `all` và xuất đủ 100% tín hiệu của tất cả 7 nhóm văn bản. Mỗi tín hiệu trả về đều ghi rõ `applicable_profiles` (nhóm văn bản bị ảnh hưởng) và `exempt_profiles` (nhóm được miễn). Agent đọc hai trường này đối chiếu với loại tài liệu thực tế đang làm để quyết định sửa hay giữ nguyên, không xóa máy móc mọi chỗ bị gắn cờ. Chỉ truyền `--profile <tên_nhóm>` khi muốn lọc riêng cho một thể loại cố định. Tra cứu danh mục đủ 30 mã quy tắc tại [references/rule-catalog.md](references/rule-catalog.md) và bảng ngoại lệ tại [references/loanwords-and-exceptions.md](references/loanwords-and-exceptions.md) khi cần xem ví dụ chi tiết.

Ở bước hậu kiểm, luôn lưu bản gốc trước khi sửa để chạy lệnh `verify`. Công cụ này kiểm tra 6 nhóm dữ kiện phải giữ nguyên gồm con số (kể cả ngày tháng, tỷ lệ phần trăm), từ phủ định, từ chỉ điều kiện, từ chỉ mức độ chắc chắn, đường dẫn cùng khối code và nguồn trích dẫn. Nếu bản sửa làm lệch bất kỳ nhóm nào ngoài chủ đích (trừ trường hợp cố ý gọt bớt cụm rào đón chồng chéo như `dường như có vẻ như`), phải khôi phục lại chính xác nghĩa gốc trước khi trả kết quả.

Khi trả kết quả cho người dùng, đưa thẳng sản phẩm đã hoàn thiện. Không đính kèm bảng điểm máy quét hay kể lại quy trình biên tập trừ khi người dùng yêu cầu nhận xét văn bản.

## Bảo trì định kỳ danh sách từ mượn

Mã nguồn [scripts/vi_scanner.py](scripts/vi_scanner.py) không gắn cứng tên dự án hay thuật ngữ riêng lẻ mà chỉ duy trì danh sách từ tiếng Anh đã quen dùng trong tiếng Việt (`UNIVERSAL_NATURALIZED_LOANWORDS` và `WORKPLACE_TECH_LOANWORDS`). Do từ vựng giao tiếp thay đổi theo thời gian, định kỳ hàng quý hoặc hàng năm cần chạy lệnh `python scripts/vi_scanner.py check-maintenance` và rà soát theo hướng dẫn tại [references/loanwords-and-exceptions.md](references/loanwords-and-exceptions.md).
