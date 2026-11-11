# Bảo trì từ mượn tiếng Anh và lưu ý ngoại lệ theo nhóm văn bản

## 1. Quy trình rà soát hàng quý hoặc hàng năm cho danh sách từ mượn

Công cụ `scripts/vi_scanner.py` dò các từ tiếng Anh chêm giữa câu tiếng Việt thông qua đặc trưng mặt chữ. Các dấu hiệu gồm chữ cái `f, j, w, z`, cụm phụ âm đầu/cuối tiếng Anh như `bl-, cr-, st-, -ck, -tion, -ment` hoặc cách viết `SNAKE_CASE`. Sau đó, máy quét đối chiếu trực tiếp bảng từ vựng [../data/vocab.csv](../data/vocab.csv) (chuẩn `UTF-8 BOM` mở bằng Excel):
1. Nhóm `loanword_universal` (`UNIVERSAL_NATURALIZED_LOANWORDS`) dành cho những từ đã đi hẳn vào tiếng Việt hàng ngày (`email`, `web`, `website`, `internet`, `wifi`, `video`, `logic`, `logistics`, `container`, `pdf`, `qr`, `otp`...). Các từ này xuất hiện tự nhiên trong cả báo cáo kiểm toán, văn bản pháp lý lẫn bài báo khoa học.
2. Nhóm `loanword_workplace` (`WORKPLACE_TECH_LOANWORDS`) dành cho những từ thông dụng trong giao tiếp công sở, truyền thông và kỹ thuật (`app`, `file`, `link`, `code`, `team`, `slide`, `deadline`, `feedback`, `api`, `sql`, `cloud`...). Nhóm từ này hợp lệ ở bài viết chung hoặc mạng xã hội, nhưng máy quét vẫn nhắc cân nhắc Việt hóa khi trình báo cáo quản trị cấp cao (`audit_report`).
3. Nhóm `reverse_calque` bắt các cụm dịch ngược ngô nghê (`thư điện tử`, `yêu cầu kéo`, `kho mã nguồn`) kèm gợi ý từ gốc thông dụng ở cột `replacement_hint`, còn nhóm `banned_phrase` gắn các cụm từ cấm cố định vào mã `rule_id` tương ứng bên [../data/grammar.csv](../data/grammar.csv).

Mỗi quý (90 ngày) hoặc ít nhất mỗi năm một lần, chạy lệnh sau để kiểm tra hạn rà soát:

```bash
python scripts/vi_scanner.py check-maintenance
```

Khi cập nhật hai danh sách trên, áp dụng ba tiêu chí chọn từ:
1. Chỉ đưa vào `UNIVERSAL_NATURALIZED_LOANWORDS` khi người đọc phổ thông ngoài ngành kỹ thuật đều hiểu ngay không cần giải thích, và nếu dịch sang tiếng Việt sẽ tạo ra cụm từ xa lạ hoặc dài dòng (ví dụ dịch `email` thành *"thư điện tử"* hay `pull request` thành *"yêu cầu kéo"*).
2. Không đưa tên sản phẩm nội bộ, tên dự án riêng hoặc từ lóng chỉ dùng trong một nhóm hẹp vào danh sách chung. Nếu một dự án cần kiểm tra bảng thuật ngữ riêng, hãy truyền qua tham số `--custom-rules <tep.json>`.
3. Sau khi sửa danh sách và cập nhật ngày `last_reviewed` trong `LOANWORDS_REVIEW_META`, bắt buộc chạy lại `python -m unittest discover -s tests -v` để đảm bảo không ảnh hưởng tới bộ 100 mẫu chuẩn.

## 2. Các trường hợp hợp lệ không được sửa máy móc

Khi chạy `scripts/vi_scanner.py scan` ở chế độ mặc định (`all`), Agent nhận toàn bộ tín hiệu của cả 7 nhóm văn bản. Trước khi sửa câu, hãy đối chiếu bảng ngoại lệ dưới đây:

| Tín hiệu máy quét báo | Khi nào cần sửa | Khi nào phải giữ nguyên |
| :--- | :--- | :--- |
| Cụm `được thực hiện`, `được áp dụng`, `được sử dụng` (`VIS-TRANS-002`) | Bài viết phổ thông, bản dịch hoặc mạng xã hội lặp dày chữ `được` làm câu trì trệ, thiếu chủ thể. | Báo cáo kiểm toán (`audit_report`), bài báo khoa học (`academic`) và văn bản pháp quy (`legal`) dùng câu khuyết chủ thể theo chuẩn nghề nghiệp (*"Cuộc kiểm toán được thực hiện theo..."*). |
| Cụm danh từ `việc thực hiện của`, `sự thay đổi của` (`VIS-TRANS-003`) | Câu văn thường có thể viết thẳng bằng động từ (*"vì thị trường giảm"* thay cho *"do sự sụt giảm của thị trường"*). | Điều khoản hợp đồng hoặc luật định (`legal`) cần gọi tên hành vi pháp lý làm chủ ngữ (*"Việc thực hiện của các bên theo Điều 288..."*). |
| Danh sách `- **Nhãn:** Nội dung` (`VIS-FMT-001`) | Mọi gạch đầu dòng trong bài đăng hoặc cột phải của bảng đều gắn nhãn in đậm giả lặp khuôn. | Điều khoản *"Giải thích từ ngữ"* trong hợp đồng (`legal`) hoặc bảng chú giải thuật ngữ. |
| Mẫu câu `không đơn thuần là X, mà còn là Y` (`VIS-RHET-001`) | Dùng làm đòn bẩy khen ngợi sáo rỗng (*"không đơn thuần là phần mềm, mà còn là cuộc cách mạng"*). | Phân định hai nghĩa vụ tài chính hoặc pháp lý có thật kèm viện dẫn Điều, Khoản cụ thể (*"không đơn thuần là tiền đặt cọc, mà còn là khoản thanh toán đợt 1 theo Điều 4.2"*). |
| Đoạn văn có độ dài đồng đều (`VIS-FMT-005`) | Bài luận hoặc bài chia sẻ chia thành 4 đến 5 đoạn có số câu và số chữ y hệt nhau như đúc khuôn. | Văn bản pháp luật chia theo từng Điều hoặc thuyết minh báo cáo kiểm toán trình bày song song từng khoản mục. |
| Câu mời gọi `Hãy cùng khám phá`, `Bí quyết không thể bỏ qua` (`VIS-AI-004`, `VIS-CLICHE-004`) | Lọt vào báo cáo quản trị, tài liệu học thuật, pháp lý hoặc bản dịch kỹ thuật. | Bài quảng cáo thương mại (`marketing`) hoặc bài đăng tương tác ngắn trên mạng xã hội (`social_media`) khi đúng giọng thương hiệu. |
