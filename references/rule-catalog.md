# Danh mục 31 quy tắc trong `scripts/vi_scanner.py`

Tài liệu này tóm tắt 31 mã quy tắc thuộc 6 nhóm để Agent tra cứu nhanh khi đọc kết quả JSON từ lệnh `python scripts/vi_scanner.py scan`.

## Nhóm 1: Rào đón và dàn dựng kiểu chatbot (`AI_META_AND_STAGING`)

| Mã quy tắc | Mức | Dấu hiệu nhận diện | Cách viết lại tự nhiên |
| :--- | :---: | :--- | :--- |
| `VIS-AI-001` | `error` | Câu rào đón hoặc nịnh người dùng của chatbot (`Chắc chắn rồi! Dưới đây là`, `Một câu hỏi rất hay`, `Hy vọng thông tin này hữu ích`, `Là một mô hình ngôn ngữ`) hoặc hộp răn đe pháp lý tự phát. | Cắt bỏ hoàn toàn câu giao tiếp với người nhập lệnh và hộp giảng đạo lý thừa, vào thẳng thông tin chính. |
| `VIS-AI-002` | `error` | Chỗ trống nhắc điền chưa xóa (`[Điền tên...]`, `[Chèn...]`) hoặc đuôi theo dõi nguồn chatbot (`utm_source=chatgpt.com`). | Điền thông tin thật hoặc xóa bỏ phần đuôi theo dõi trong đường dẫn. |
| `VIS-AI-003` | `warning` | Mở bài vĩ mô sáo rỗng (`Trong bối cảnh... ngày càng phát triển`). | Mở trực tiếp bằng sự kiện, con số hoặc vấn đề thực tế của chủ thể. |
| `VIS-AI-004` | `info` | Câu dẫn dắt vòng vo (`Hãy cùng khám phá...`, `Câu hỏi đặt ra là... Câu trả lời là`, `Đó mới là điều quan trọng`). | Nêu thẳng luận điểm hoặc số liệu ngay từ câu đầu. |
| `VIS-AI-005` | `warning` | Đoạn kết hứa hẹn tương lai chung chung (`Tóm lại... hứa hẹn mở ra kỷ nguyên mới`, `Dù đối mặt thách thức... vẫn vươn lên`). | Kết bằng kết luận giới hạn trong bằng chứng hoặc bước hành động cụ thể. |

## Nhóm 2: Phóng đại và ẩn dụ văn mẫu (`AI_RHETORICAL_INFLATION`)

| Mã quy tắc | Mức | Dấu hiệu nhận diện | Cách viết lại tự nhiên |
| :--- | :---: | :--- | :--- |
| `VIS-RHET-001` | `warning` | Mẫu câu đòn bẩy `Không chỉ (đơn thuần) là X, mà (còn) là Y`, `Không phải vì X mà vì Y` hoặc lặp từ 3 lần các cụm phủ định bắc cầu (`chưa đồng nghĩa với`, `không có nghĩa là`). | Viết thành câu khẳng định nêu thẳng chức năng hoặc kết quả. |
| `VIS-RHET-002` | `warning` | Lời khen phóng đại tầm vóc (`đóng vai trò then chốt`, `bước ngoặt lịch sử`, `minh chứng sống động`, `qua đó khẳng định`, `bứt phá ngoạn mục`). | Bỏ tính từ tán dương, để số liệu và sự kiện tự thể hiện mức độ. |
| `VIS-RHET-003` | `warning` | Ẩn dụ dịch sát từ tiếng Anh của AI (`tấm thảm đa sắc`, `bức tranh toàn cảnh`, `ngọn hải đăng dẫn đường`, `đi sâu vào khám phá bản chất`, `tảng băng chìm`). | Gọi đúng tên sự vật, rủi ro hoặc phạm vi công việc thực tế. |
| `VIS-RHET-004` | `info` | Ghép gượng hai vế không cùng trục đo (`Từ những A cho đến các B, tất cả đều...`). | Liệt kê cụ thể các bộ phận thực sự liên quan. |
| `VIS-RHET-005` | `warning` | Mượn uy tín không tên (`Các chuyên gia cho rằng`, `Nhiều nghiên cứu chỉ ra rằng`) mà không kèm trích dẫn ngay sau. | Ghi rõ tên tác giả, năm xuất bản hoặc bỏ vế mượn lời nếu câu sau đã có dữ kiện. |

## Nhóm 3: Định dạng và nhịp đoạn máy móc (`AI_STRUCTURAL_AND_FORMATTING`)

| Mã quy tắc | Mức | Dấu hiệu nhận diện | Cách viết lại tự nhiên |
| :--- | :---: | :--- | :--- |
| `VIS-FMT-001` | `warning` | Từ 3 dòng danh sách liên tiếp đóng khuôn `- **Nhãn in đậm:**` rồi giải thích lặp lại nhãn. | Bỏ nhãn giả đầu dòng, viết thành câu hoàn chỉnh hoặc gộp gọn các ý cùng loại. |
| `VIS-FMT-002` | `warning` | Đặt quá nhiều từ nối sách vở đầu câu (`Hơn nữa,`, `Thêm vào đó,`, `Bên cạnh đó,`, `Ngoài ra,`) từ 3 lần trong một đoạn. | Mở câu bằng chủ thể thực hiện hành động hoặc nối nhân quả trực tiếp. |
| `VIS-FMT-003` | `info` | Dùng dấu gạch ngang dài (`—`, `--`) hoặc dấu chấm phẩy (`;`) nối mệnh đề kiểu tiếng Anh. | Thay bằng dấu phẩy, dấu hai chấm, ngoặc đơn hoặc tách câu ngắn. |
| `VIS-FMT-004` | `info` | Xếp chồng 3 tính từ khen ngợi theo nhịp văn mẫu (`nhanh chóng, chính xác và hiệu quả`, `chạy mượt mà trên cả`). | Thay bằng chỉ tiêu định lượng cụ thể (thời gian, số lượng, tỷ lệ lỗi). |
| `VIS-FMT-005` | `info` | Từ 4 đoạn liên tiếp có độ dài quá đều (`CV < 0,15`), 3 câu liền nhau mở đầu cùng một từ (trừ dòng bảng và mục `Bước/Phần/Điều`) hoặc xoay vòng động từ đồng nghĩa đầu cột bảng để lách máy quét. | Chia đoạn theo ý thực tế, đổi chủ ngữ mở câu tự nhiên và bỏ động từ dẫn đầu trong ô bảng kỹ thuật. |

## Nhóm 4: Dịch từng chữ từ tiếng Anh (`TRANSLATIONESE_EN_VI`)

| Mã quy tắc | Mức | Dấu hiệu nhận diện | Cách viết lại tự nhiên |
| :--- | :---: | :--- | :--- |
| `VIS-TRANS-001` | `warning` | Bị động dịch sát từ tiếng Anh (`được/bị + V + bởi`, `được CMake tự động tải`, `đều được thiết kế bằng`, `được đọc/ghi ra`). | Đưa tác nhân lên đầu câu làm chủ ngữ chủ động hoặc dùng động từ trực tiếp. |
| `VIS-TRANS-002` | `warning` | Lặp dày chữ `được` trước động từ trung tính (`được thực hiện`, `được sử dụng`, `được tiến hành`) từ 3 lần trong đoạn. | Bổ sung chủ thể thực hiện hoặc chuyển sang cấu trúc Đề - Thuyết tự nhiên. |
| `VIS-TRANS-003` | `warning` | Danh từ hóa nặng nề (`sự/việc + động từ + của + chủ thể`) lặp từ 2 lần trong đoạn. | Chuyển danh từ hóa trở lại thành động từ của chủ thể. |
| `VIS-TRANS-004` | `info` | Lặp cụm `một cách + tính từ` dịch từ trạng từ đuôi `-ly` tiếng Anh từ 2 lần trong đoạn. | Dùng trạng từ ngắn trực tiếp (`tăng mạnh` thay cho `tăng một cách đáng kể`). |
| `VIS-TRANS-005` | `warning` | Chủ ngữ giả (`Nó là cần thiết để`, `Có một sự... trong việc`), đại từ quan hệ dịch thô (`nơi mà`, `điều mà`), lặp `vẫn... vẫn`, đuôi khoe phủ định (`và không cần cài thêm thư viện ngoài`), cấu trúc `hỗ trợ + động từ` (`hỗ trợ lọc/hủy`) hoặc đảo ngược bổ ngữ (`báo mất kết nối nhầm`, `giới hạn thời gian chờ rõ ràng`). | Nêu chủ ngữ thật chỉ người hoặc đơn vị, dùng động từ trực tiếp, tách câu dài và đặt bổ ngữ đúng trật tự tiếng Việt. |

## Nhóm 5: Sáo ngữ hành chính và câu khách (`BUREAUCRATIC_AND_SEO_CLICHE`)

| Mã quy tắc | Mức | Dấu hiệu nhận diện | Cách viết lại tự nhiên |
| :--- | :---: | :--- | :--- |
| `VIS-CLICHE-001` | `info` | Khẩu hiệu hành chính hoặc kiến nghị thiếu đầu ra (`đẩy mạnh công tác tuyên truyền`, `cần đẩy nhanh tiến độ`, `không lượng hóa được`). | Ghi rõ ai làm việc gì, sản phẩm bàn giao là gì và thời hạn hoàn thành. |
| `VIS-CLICHE-002` | `info` | Né động từ `là`, `có`, nhét động từ rỗng (`đóng vai trò như là một`, `thực hiện kiểm tra`) hoặc gắn tính từ quảng cáo rỗng (`cảnh báo thông minh`, `bảng trực quan`, `giao diện mượt`). | Dùng trực tiếp động từ `là`, `có`, động từ hành động chính (`kiểm tra`) và mô tả cơ chế thật. |
| `VIS-CLICHE-003` | `info` | Ghép thừa hai từ trùng nghĩa (`hoàn toàn tuyệt đối`, `tương lai sắp tới`, `nguyên nhân chính cốt lõi`, `phối hợp cùng nhau`). | Giữ lại một từ mang nghĩa chính xác nhất. |
| `VIS-CLICHE-004` | `warning` | Mở bài câu khách kiểu SEO hoặc câu chốt một dòng giật gân (`Bạn đã bao giờ tự hỏi`, `Tất tần tật những điều bạn cần biết`, `Hãy đọc lại câu này`). | Giới thiệu trực diện nội dung tài liệu mà không mồi tương tác giả tạo. |
| `VIS-CLICHE-005` | `warning` | Chồng từ 2 lớp từ rào đón trở lên (`có thể có khả năng sẽ`, `dường như có vẻ như là`, `một cách nào đó`). | Chỉ giữ một từ tình thái phản ánh đúng mức chắc chắn của bằng chứng (`có thể`). |

## Nhóm 6: Giọng văn thực tế và trình bày bảng (`VOICE_AND_STRUCTURE`)

| Mã quy tắc | Mức | Dấu hiệu nhận diện | Cách viết lại tự nhiên |
| :--- | :---: | :--- | :--- |
| `VIS-LEX-001` | `warning` | Dùng sai chữ `thực chứng`, dịch từng chữ thuật ngữ phần mềm (`khung hợp đồng`, `khung vận hành`, `khóa hợp đồng`, `giao kèo dữ liệu`, `khung chạy sẵn`, `hiện thực lớp`, `lớp phụ trách`, `di chuyển vệt sáng`, `túi chứa dữ liệu`, `mẫu thông điệp`, `tác vụ/thành viên`, `Kỹ sư giao thức mạng`) hoặc tự chế từ ngô nghê (`in đúp`, `cho máy tính ghép`). | Dùng đúng từ công việc thực tế (`dựa trên bằng chứng`, `file header dùng chung`, `viết lớp`, `di chuyển dòng đang chọn`, `mẫu git commit`, `lặp dòng`). |
| `VIS-LEX-002` | `info` | Dịch ngược từ tiếng Anh đã quen dùng (`thư điện tử`, `yêu cầu kéo`) hoặc để lọt mã kỹ thuật, từ tiếng Anh chưa Việt hóa ngoài danh sách cho phép. | Giữ nguyên từ quen dùng (`email`, `pull request`, `web`) và Việt hóa thuật ngữ hẹp cho người ngoài ngành. |
| `VIS-TONE-001` | `warning` | Chào sồn sã (`Anh X ơi,`), dùng từ kịch tính hóa hoặc cảm thán hiện trường (`rủi ro sát sườn`, `cố bấm nút`, `tê liệt`, `sập toàn tuyến`, `khủng hoảng hệ thống`, `trực chiến 24/7`, `tử huyệt`), tự khoe xếp loại hoặc khen xã giao. | Giữ giọng điềm tĩnh, lễ độ chừng mực và bỏ hẳn câu tự khen hoặc khen xã giao. |
| `VIS-STRUCT-001` | `warning` | Tự thuyết minh bố cục hoặc tài liệu (`Để tránh trùng lặp...`, `Bảng dưới đây trình bày...`, `Tài liệu X mô tả chi tiết...`, `ghi lại lý do chọn`), lộ nhãn dàn ý (`Điểm nghẽn:`, `Bước ngoặt tư duy:`) hoặc đếm tuần tự né máy quét. | Xóa câu giải thích bố cục và nhãn dàn ý, nối thẳng mạch nội dung hoặc gộp liên kết vào danh sách. |
| `VIS-STRUCT-002` | `warning` | Ký tự ẩn, chồng dấu `****`, lỗi `#REF!`, viết `Thiếu -10%`, mũi tên `->`, emoji trang trí, phần trăm dấu chấm `59.9%`, tiêu đề Title Case kiểu Anh, mục con đơn độc, thuộc tính `alt` ảnh nhồi từ khóa (`> 12` từ hoặc kèm khẩu hiệu quảng cáo), hộp HTML `01`–`04` lặp lại bảng, chú thích `#` trong cây thư mục dài quá `10` từ, bọc dấu nháy ngược quanh từ tiếng Việt thường, cộng sai dòng `Tổng cộng`, gộp hạng mục còn lỗi vào tỷ lệ hoàn thành, đánh đồng hướng dẫn trung gian với đã đóng lỗi, dùng bù trừ ròng kết luận không sai lệch, chốt tỷ lệ hoàn thành thiếu `Tử số/Mẫu số` hoặc lệch thuộc tính `Title` kỳ cũ của tệp `.docx`. | Chuẩn hóa dấu phẩy thập phân tiếng Việt, giữ `alt` ảnh và chú thích cây thư mục ngắn gọn, tách riêng tỷ lệ không lỗi và còn lỗi, kèm đủ `Tử số/Mẫu số (%)`, đối soát theo giá trị tuyệt đối và cộng khớp dòng tổng. |
| `VIS-LEN-001` | `error` | Câu văn xuôi dài quá `45` từ (`55` từ với văn bản pháp lý), câu từ `36` từ trở lên nối đuôi từ `6` mệnh đề bằng dấu phẩy, mở câu bằng cụm danh từ hóa `Việc ...` kéo dài hoặc dẫn dắt vòng vo (`Thông qua việc...`, `Liên quan đến vấn đề...`, `Đối với việc thực hiện...`, `Không thể phủ nhận rằng...`, `với mục đích nhằm`). Trọng số phạt lũy tiến từ `1,0` lên tới `2,5` theo số từ vượt trần. | Cắt bỏ cụm rào đón đầu câu và tách thành `2` đến `3` câu ngắn độc lập (`15` đến `25` từ mỗi câu), mỗi câu một chủ thể và một động từ chính. |
