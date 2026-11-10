# Danh mục 30 quy tắc trong `scripts/vi_scanner.py`

Tài liệu này tóm tắt 30 mã quy tắc thuộc 6 nhóm để Agent tra cứu nhanh khi đọc kết quả JSON từ lệnh `python scripts/vi_scanner.py scan`.

## Nhóm 1: Khung rào đón và dàn dựng của AI (`AI_META_AND_STAGING`)

| Mã quy tắc | Mức | Dấu hiệu nhận diện | Cách viết lại tự nhiên |
| :--- | :---: | :--- | :--- |
| `VIS-AI-001` | `error` | Câu rào đón đầu hoặc cuối bài của chatbot (`Chắc chắn rồi! Dưới đây là`, `Hy vọng thông tin này hữu ích`, `Hãy cho tôi biết nếu bạn cần`, `Là một mô hình ngôn ngữ`). | Cắt bỏ hoàn toàn câu giao tiếp với người nhập lệnh, vào thẳng thông tin chính. |
| `VIS-AI-002` | `error` | Chỗ trống nhắc điền chưa xóa (`[Điền tên...]`, `[Chèn...]`) hoặc đuôi theo dõi nguồn chatbot (`utm_source=chatgpt.com`). | Điền thông tin thật hoặc xóa bỏ phần đuôi theo dõi trong đường dẫn. |
| `VIS-AI-003` | `warning` | Mở bài vĩ mô sáo rỗng (`Trong bối cảnh... ngày càng phát triển`). | Mở trực tiếp bằng sự kiện, con số hoặc vấn đề thực tế của chủ thể. |
| `VIS-AI-004` | `info` | Câu dẫn dắt vòng vo (`Hãy cùng khám phá...`, `Câu hỏi đặt ra là... Câu trả lời là`). | Nêu thẳng luận điểm hoặc số liệu ngay từ câu đầu. |
| `VIS-AI-005` | `warning` | Đoạn kết hứa hẹn tương lai chung chung (`Tóm lại... hứa hẹn mở ra kỷ nguyên mới`). | Kết bằng kết luận giới hạn trong bằng chứng hoặc bước hành động cụ thể. |

## Nhóm 2: Phóng đại và ẩn dụ văn mẫu (`AI_RHETORICAL_INFLATION`)

| Mã quy tắc | Mức | Dấu hiệu nhận diện | Cách viết lại tự nhiên |
| :--- | :---: | :--- | :--- |
| `VIS-RHET-001` | `warning` | Mẫu câu đòn bẩy `Không chỉ (đơn thuần) là X, mà (còn) là Y` hoặc lặp từ 3 lần các cụm phủ định bắc cầu (`chưa đồng nghĩa với`, `không có nghĩa là`). | Viết thành câu khẳng định nêu thẳng chức năng hoặc kết quả. |
| `VIS-RHET-002` | `warning` | Lời khen phóng đại tầm vóc (`đóng vai trò then chốt`, `bước ngoặt lịch sử`, `minh chứng sống động`). | Bỏ tính từ tán dương, để số liệu và sự kiện tự thể hiện mức độ. |
| `VIS-RHET-003` | `warning` | Ẩn dụ dịch sát từ tiếng Anh của AI (`tấm thảm đa sắc`, `bức tranh toàn cảnh`, `ngọn hải đăng dẫn đường`, `đi sâu vào khám phá bản chất`, `tảng băng chìm`). | Gọi đúng tên sự vật, rủi ro hoặc phạm vi công việc thực tế. |
| `VIS-RHET-004` | `info` | Ghép gượng hai vế không cùng trục đo (`Từ những A cho đến các B, tất cả đều...`). | Liệt kê cụ thể các bộ phận thực sự liên quan. |
| `VIS-RHET-005` | `warning` | Mượn uy tín không tên (`Các chuyên gia cho rằng`, `Nhiều nghiên cứu chỉ ra rằng`) mà không kèm trích dẫn ngay sau. | Ghi rõ tên tác giả, năm xuất bản hoặc bỏ vế mượn lời nếu câu sau đã có dữ kiện. |

## Nhóm 3: Định dạng và nhịp đoạn máy móc (`AI_STRUCTURAL_AND_FORMATTING`)

| Mã quy tắc | Mức | Dấu hiệu nhận diện | Cách viết lại tự nhiên |
| :--- | :---: | :--- | :--- |
| `VIS-FMT-001` | `warning` | Từ 3 dòng danh sách liên tiếp đóng khuôn `- **Nhãn in đậm:**` rồi giải thích lặp lại nhãn. | Bỏ nhãn giả đầu dòng, viết thành câu hoàn chỉnh hoặc gộp gọn các ý cùng loại. |
| `VIS-FMT-002` | `warning` | Đặt quá nhiều từ nối sách vở đầu câu (`Hơn nữa,`, `Thêm vào đó,`, `Bên cạnh đó,`, `Ngoài ra,`) từ 3 lần trong một đoạn. | Mở câu bằng chủ thể thực hiện hành động hoặc nối nhân quả trực tiếp. |
| `VIS-FMT-003` | `info` | Dùng dấu gạch ngang dài (`—`) nối mệnh đề kiểu tiếng Anh từ 2 lần trong một đoạn. | Thay bằng dấu phẩy, dấu hai chấm hoặc ngoặc đơn. |
| `VIS-FMT-004` | `info` | Xếp chồng 3 tính từ khen ngợi theo nhịp văn mẫu (`nhanh chóng, chính xác và hiệu quả`). | Thay bằng chỉ tiêu định lượng cụ thể (thời gian, số lượng, tỷ lệ lỗi). |
| `VIS-FMT-005` | `info` | Từ 4 đoạn liên tiếp có độ dài quá đều (`CV < 0,15`) hoặc 3 câu liền nhau mở đầu cùng một từ. | Chia đoạn theo ý thực tế và đổi chủ ngữ mở câu tự nhiên. |

## Nhóm 4: Dịch từng chữ từ tiếng Anh (`TRANSLATIONESE_EN_VI`)

| Mã quy tắc | Mức | Dấu hiệu nhận diện | Cách viết lại tự nhiên |
| :--- | :---: | :--- | :--- |
| `VIS-TRANS-001` | `warning` | Bị động dịch sát từ chữ *by* (`được/bị + động từ + bởi + chủ thể`). | Đưa tác nhân đứng sau chữ *bởi* lên đầu câu làm chủ ngữ chủ động. |
| `VIS-TRANS-002` | `warning` | Lặp dày chữ `được` trước động từ trung tính (`được thực hiện`, `được sử dụng`, `được tiến hành`) từ 3 lần trong đoạn. | Bổ sung chủ thể thực hiện hoặc chuyển sang cấu trúc Đề - Thuyết tự nhiên. |
| `VIS-TRANS-003` | `warning` | Danh từ hóa nặng nề (`sự/việc + động từ + của + chủ thể`) lặp từ 2 lần trong đoạn. | Chuyển danh từ hóa trở lại thành động từ của chủ thể. |
| `VIS-TRANS-004` | `info` | Lặp cụm `một cách + tính từ` dịch từ trạng từ đuôi `-ly` tiếng Anh từ 2 lần trong đoạn. | Dùng trạng từ ngắn trực tiếp (`tăng mạnh` thay cho `tăng một cách đáng kể`). |
| `VIS-TRANS-005` | `warning` | Chủ ngữ giả (`Nó là cần thiết để`, `Có một sự... trong việc`), đại từ quan hệ dịch thô (`nơi mà`, `điều mà`), câu cụt chủ ngữ hoặc gán tâm lý người cho vật vô tri (`phép cộng vô tình lấy`). | Nêu chủ ngữ thật chỉ người hoặc đơn vị, tách câu dài có đại từ quan hệ. |

## Nhóm 5: Sáo ngữ hành chính và câu khách (`BUREAUCRATIC_AND_SEO_CLICHE`)

| Mã quy tắc | Mức | Dấu hiệu nhận diện | Cách viết lại tự nhiên |
| :--- | :---: | :--- | :--- |
| `VIS-CLICHE-001` | `info` | Khẩu hiệu hành chính hoặc kiến nghị thiếu đầu ra (`đẩy mạnh công tác tuyên truyền`, `cần đẩy nhanh tiến độ`, `không lượng hóa được`). | Ghi rõ ai làm việc gì, sản phẩm bàn giao là gì và thời hạn hoàn thành. |
| `VIS-CLICHE-002` | `info` | Né động từ `là`, `có` hoặc nhét động từ rỗng (`đóng vai trò như là một`, `sở hữu tính năng vượt trội`, `tiến hành việc kiểm tra`). | Dùng trực tiếp động từ `là`, `có` và động từ hành động chính (`kiểm tra`). |
| `VIS-CLICHE-003` | `info` | Ghép thừa hai từ trùng nghĩa (`hoàn toàn tuyệt đối`, `tương lai sắp tới`, `nguyên nhân chính cốt lõi`, `phối hợp cùng nhau`). | Giữ lại một từ mang nghĩa chính xác nhất. |
| `VIS-CLICHE-004` | `warning` | Mở bài câu khách kiểu SEO hoặc câu chốt một dòng giật gân (`Bạn đã bao giờ tự hỏi`, `Tất tần tật những điều bạn cần biết`, `Hãy đọc lại câu này`). | Giới thiệu trực diện nội dung tài liệu mà không mồi tương tác giả tạo. |
| `VIS-CLICHE-005` | `warning` | Chồng từ 2 lớp từ rào đón trở lên (`có thể có khả năng sẽ`, `dường như có vẻ như là`). | Chỉ giữ một từ tình thái phản ánh đúng mức chắc chắn của bằng chứng (`có thể`). |

## Nhóm 6: Giọng văn thực tế và trình bày bảng (`VOICE_AND_STRUCTURE`)

| Mã quy tắc | Mức | Dấu hiệu nhận diện | Cách viết lại tự nhiên |
| :--- | :---: | :--- | :--- |
| `VIS-LEX-001` | `warning` | Dùng sai chữ `thực chứng` để chỉ bằng chứng thực tế, hoặc tự bịa từ ngô nghê (`in đúp`, `cho máy tính ghép`, `kiểm tra tự động đối soát`, `điều gì vẫn có thể sai`). | Dùng đúng từ công việc thực tế (`dựa trên bằng chứng`, `lặp dòng`, `chạy đối soát tự động`). |
| `VIS-LEX-002` | `info` | Dịch ngược từ tiếng Anh đã quen dùng (`thư điện tử`, `yêu cầu kéo`) hoặc để lọt mã kỹ thuật, từ tiếng Anh chưa Việt hóa ngoài danh sách cho phép. | Giữ nguyên từ quen dùng (`email`, `pull request`, `web`) và Việt hóa thuật ngữ hẹp cho người ngoài ngành. |
| `VIS-TONE-001` | `warning` | Chào sồn sã (`Anh X ơi,`), dùng từ kịch tính hóa (`rủi ro sát sườn`, `cố bấm nút`, `tê liệt`, `tử huyệt`), tự khoe xếp loại hoặc khen xã giao. | Giữ giọng điềm tĩnh, lễ độ chừng mực và bỏ hẳn câu tự khen hoặc khen xã giao. |
| `VIS-STRUCT-001` | `warning` | Tự thuyết minh bố cục (`Để tránh trùng lặp...`, `Bảng dưới đây trình bày...`), lộ nhãn dàn ý (`Điểm nghẽn:`, `Bước ngoặt tư duy:`) hoặc đếm tuần tự né máy quét. | Xóa câu giải thích bố cục và nhãn dàn ý, nối thẳng mạch nội dung. |
| `VIS-STRUCT-002` | `warning` | Ký tự ẩn, chồng dấu `****`, lỗi `#REF!`, viết `Thiếu -10%`, mũi tên `->`, phần trăm dấu chấm `59.9%`, tiêu đề viết hoa từng chữ kiểu Anh, mục con đơn độc, 2 dấu `:` trong mục danh sách, đại từ trong bảng số hoặc cộng sai dòng `Tổng cộng`. | Chuẩn hóa dấu phẩy thập phân tiếng Việt, viết hoa đầu câu cho tiêu đề, giữ bảng khách quan và cộng khớp dòng tổng. |
