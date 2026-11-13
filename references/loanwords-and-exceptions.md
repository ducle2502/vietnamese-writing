# Bảo trì từ mượn tiếng Anh và lưu ý ngoại lệ theo nhóm văn bản

## 1. Quy trình rà soát hàng quý hoặc hàng năm cho danh sách từ mượn

Công cụ `scripts/vi_scanner.py` nhận diện từ tiếng Anh chêm giữa câu qua chữ cái `f, j, w, z`, cụm phụ âm `bl-, cr-, st-, -ck, -tion, -ment` hoặc `SNAKE_CASE`. Sau đó, máy quét đối chiếu trực tiếp với bảng [../data/vocab.csv](../data/vocab.csv) chuẩn `UTF-8 BOM` mở bằng Excel:
1. Nhóm `loanword_universal` (`UNIVERSAL_NATURALIZED_LOANWORDS`) gồm `63` từ đã đi hẳn vào tiếng Việt hàng ngày (`email`, `web`, `website`, `internet`, `wifi`, `video`, `logic`, `logistics`, `container`, `pdf`, `qr`, `otp`...), dùng tự nhiên trong cả báo cáo kiểm toán, văn bản pháp lý lẫn bài báo khoa học.
2. Nhóm `loanword_workplace` (`WORKPLACE_TECH_LOANWORDS`) gồm `115` từ quen thuộc trong giao tiếp công sở, truyền thông và kỹ thuật (`app`, `file`, `link`, `code`, `team`, `slide`, `deadline`, `feedback`, `placeholder`, `api`, `sql`, `cloud`...). Các từ này hợp lệ ở bài viết chung hoặc mạng xã hội, nhưng máy quét vẫn nhắc cân nhắc Việt hóa khi trình báo cáo quản trị cấp cao (`audit_report`).
3. Nhóm `reverse_calque` (`VIS-LEX-002`) bắt các cụm dịch ngược ngô nghê (`thư điện tử`, `yêu cầu kéo`, `kho mã nguồn`) cùng các từ tiếng Anh chêm tùy tiện (`booking lịch`, `check cái file`). Nhóm `banned_phrase` gắn các cụm văn mẫu, khẩu hiệu, lỗi chính tả/dùng từ hoặc từ lậm truyện dịch thô vào mã `rule_id` tương ứng bên [../data/grammar.csv](../data/grammar.csv), kèm gợi ý sửa cụ thể tại cột `replacement_hint`.

Mỗi quý (90 ngày) hoặc ít nhất mỗi năm một lần, chạy lệnh sau để kiểm tra hạn rà soát:

```bash
python scripts/vi_scanner.py check-maintenance
```

Khi cập nhật hai danh sách trên, áp dụng ba tiêu chí chọn từ:
1. Chỉ đưa vào `UNIVERSAL_NATURALIZED_LOANWORDS` khi người đọc ngoài ngành kỹ thuật đều hiểu ngay không cần giải thích. Đồng thời, dịch từ đó sang tiếng Việt lại sinh ra cụm xa lạ như dịch `email` thành *"thư điện tử"* hay `pull request` thành *"yêu cầu kéo"*.
2. Không đưa tên sản phẩm nội bộ, tên dự án riêng hoặc từ lóng chỉ dùng trong một nhóm hẹp vào danh sách chung. Nếu một dự án cần kiểm tra bảng thuật ngữ riêng, hãy truyền qua tham số `--custom-rules <tep.json>`.
3. Sau khi sửa danh sách và cập nhật ngày `last_reviewed` trong `LOANWORDS_REVIEW_META`, bắt buộc chạy lại `python -B -m pytest -v` để đảm bảo không ảnh hưởng tới bộ 100 mẫu chuẩn.

## 2. Các trường hợp hợp lệ không được sửa máy móc

Lệnh `scripts/vi_scanner.py scan` mặc định xuất đủ tín hiệu của cả 7 nhóm văn bản. Lỗi câu dài `VIS-LEN-001` không có ngoại lệ. Với các tín hiệu còn lại, hãy đối chiếu kỹ từng ngữ cảnh trong bảng dưới đây trước khi quyết định sửa hay giữ nguyên câu gốc:

| Tín hiệu máy quét báo | Khi nào cần sửa | Khi nào phải giữ nguyên |
| :--- | :--- | :--- |
| Cụm `được thực hiện`, `được áp dụng`, `được sử dụng` (`VIS-TRANS-002`) | Bài viết phổ thông, bản dịch hoặc mạng xã hội lặp lại dày đặc chữ `được` làm câu trì trệ, thiếu chủ thể. | Báo cáo kiểm toán (`audit_report`), bài báo khoa học (`academic`) và văn bản pháp quy (`legal`) dùng câu khuyết chủ thể theo chuẩn nghề nghiệp (*"Cuộc kiểm toán được thực hiện theo..."*). |
| Cụm danh từ `việc thực hiện của`, `sự thay đổi của` (`VIS-TRANS-003`) | Câu văn thường có thể viết thẳng bằng động từ (*"vì thị trường giảm"* thay cho *"do sự sụt giảm của thị trường"*). | Điều khoản hợp đồng hoặc luật định (`legal`) cần gọi tên hành vi pháp lý làm chủ ngữ (*"Việc thực hiện của các bên theo Điều 288..."*). |
| Danh sách `- **Nhãn:** Nội dung` (`VIS-FMT-001`) | Mọi gạch đầu dòng trong bài đăng hoặc cột phải của bảng đều gắn nhãn in đậm rập khuôn. | Điều khoản *"Giải thích từ ngữ"* trong hợp đồng (`legal`) hoặc bảng chú giải thuật ngữ. |
| Mẫu câu `không đơn thuần là X, mà còn là Y` (`VIS-RHET-001`) | Dùng để khen ngợi phóng đại sáo rỗng (*"không đơn thuần là phần mềm, mà còn là cuộc cách mạng"*). | Phân định hai nghĩa vụ tài chính hoặc pháp lý có thật kèm viện dẫn Điều, Khoản cụ thể (*"không đơn thuần là tiền đặt cọc, mà còn là khoản thanh toán đợt 1 theo Điều 4.2"*). |
| Đoạn văn có độ dài đồng đều (`VIS-FMT-005`) | Bài luận hoặc bài chia sẻ chia thành 4 đến 5 đoạn có số câu và số chữ y hệt nhau như đúc khuôn. | Văn bản pháp luật chia theo từng Điều hoặc thuyết minh báo cáo kiểm toán trình bày song song từng khoản mục. |
| Câu mời gọi `Hãy cùng khám phá`, `Bí quyết không thể bỏ qua` (`VIS-AI-004`, `VIS-CLICHE-004`) | Lọt vào báo cáo quản trị, tài liệu học thuật, pháp lý hoặc bản dịch kỹ thuật. | Bài quảng cáo thương mại (`marketing`) hoặc bài đăng tương tác ngắn trên mạng xã hội (`social_media`) khi đúng giọng thương hiệu. |
| Động từ gợi sự `hé lộ`, `lộ diện` (`VIS-TONE-002`) | Gắn với báo cáo, kiểm thử, dữ liệu hoặc lỗi kỹ thuật trong văn bản quản trị, học thuật, pháp lý (`"diễn tập hé lộ lỗ hổng"`). | Bài giới thiệu sản phẩm (`marketing`), bài đăng mạng xã hội (`social_media`) hoặc miêu tả vật lý ngoài ngữ cảnh phân tích. |

## 3. Ma trận bảy hồ sơ thể loại

| Hồ sơ | Quy tắc siết chặt | Quy tắc bỏ qua hoặc nâng ngưỡng |
| :--- | :--- | :--- |
| `general` | Kích hoạt toàn bộ nhóm AI, tu từ và dịch thô. | Cho phép một cụm `một cách` và 1 đến 2 từ nối đầu câu mỗi đoạn. |
| `audit_report` | Siết nhóm phóng đại, dẫn nguồn không tên, khẩu hiệu rỗng và rào đón chồng lớp. | Bỏ qua bị động quy ước và độ đều đoạn trong thuyết minh báo cáo. |
| `academic` | Siết nhóm AI, tu từ và mở bài kiểu SEO. | Bỏ qua danh từ hóa thuật ngữ và bị động khách quan. |
| `legal` | Siết lỗi chatbot, phóng đại, bị động dịch từng chữ và rào đón chồng lớp. | Bỏ qua khẩu hiệu chỉ đạo, danh từ hóa quyền nghĩa vụ và bảng giải thích từ ngữ. |
| `marketing` | Chặn lỗi chatbot, ẩn dụ sáo rỗng và toàn bộ nhóm dịch thô. | Cho phép lời mời khám phá, bộ ba tính từ và mở bài câu khách. |
| `social_media` | Chặn lỗi chatbot, đối lập giả, danh sách in đậm và dịch thô. | Cho phép giọng cá nhân, bộ ba tính từ và kết bài ngắn. |
| `translation` | Kích hoạt tối đa nhóm dịch thô và nhóm AI. | Bỏ qua gạch ngang hội thoại văn học và nghĩa đen của ẩn dụ địa lý. |

## 4. Ghi chú ngữ cảnh, không cấm từ đơn

Các mục dưới đây là lưu ý biên tập. Chúng không phải lệnh cấm từ và không thay thế ngữ cảnh thật.

| Mục | Ghi chú sử dụng |
| :--- | :--- |
| tính thời sự | Chỉ dùng cho mức độ được bàn luận. Khi nói về hạn xử lý, dùng tính kịp thời. |
| lần xác nhận | Khi nói về lịch sử thay đổi mã nguồn, dùng lần commit hoặc lịch sử commit. |
| đẩy lên | Khi nói về công bố thông tin, dùng đưa lên hoặc công bố. |
| tính thực nghiệm | Khi nói về khả năng kiểm chứng, dùng có thể kiểm chứng hoặc bác bỏ. |
| một số thay đổi | Giữ nguyên. Tránh ghép thành một số các thay đổi. |
| phát hành và ban hành | Phát hành dùng cho ấn phẩm hoặc bản cập nhật. Ban hành dùng cho văn bản quy phạm. |
| soát xét | Dùng rà soát cho hành động kiểm tra lại. Dùng xem lại, phản biện hoặc tham vấn chuyên gia theo đúng sắc thái. |

soát xét từng bị dùng như động từ mặc định cho mọi hoạt động review. Cách dùng này đúng khi nói về vai trò hoặc hồ sơ rà soát chính thức, nhưng lặp ở mọi câu sẽ thành giọng dịch và nặng. Hãy chọn động từ theo hành động thật.
