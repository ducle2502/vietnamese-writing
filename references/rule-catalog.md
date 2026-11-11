# Danh mục 42 quy tắc trong `scripts/vi_scanner.py`

Bảng tra cứu nhanh 42 mã quy tắc thuộc 6 nhóm khi đọc kết quả JSON từ lệnh `python scripts/vi_scanner.py scan`.

## Nhóm 1: Rào đón và dàn dựng kiểu chatbot (`AI_META_AND_STAGING`)

| Mã quy tắc | Mức | Dấu hiệu nhận diện | Cách viết lại tự nhiên |
| :--- | :---: | :--- | :--- |
| `VIS-AI-001` | `error` | Câu rào đón hoặc nịnh người dùng của chatbot (`Chắc chắn rồi! Dưới đây là`, `Một câu hỏi rất hay`, `Hy vọng thông tin này hữu ích`, `Là một mô hình ngôn ngữ`) hoặc hộp răn đe pháp lý tự phát. | Cắt bỏ hoàn toàn câu giao tiếp với người nhập lệnh và hộp giảng đạo lý thừa, vào thẳng thông tin chính. |
| `VIS-AI-002` | `error` | Chỗ trống nhắc điền chưa xóa (`[Điền tên...]`, `[Chèn...]`) hoặc đuôi theo dõi nguồn chatbot (`utm_source=chatgpt.com`). | Điền thông tin thật hoặc xóa bỏ phần đuôi theo dõi trong đường dẫn. |
| `VIS-AI-003` | `warning` | Mở bài vĩ mô sáo rỗng (`Trong bối cảnh... ngày càng phát triển`). | Mở trực tiếp bằng sự kiện, con số hoặc vấn đề thực tế của chủ thể. |
| `VIS-AI-004` | `info` | Câu dẫn dắt vòng vo (`Hãy cùng khám phá...`, `Câu hỏi đặt ra là... Câu trả lời là`, `Đó mới là điều quan trọng`). | Nêu thẳng luận điểm hoặc số liệu ngay từ câu đầu. |
| `VIS-AI-005` | `warning` | Đoạn kết hứa hẹn tương lai chung chung (`Tóm lại... hứa hẹn mở ra kỷ nguyên mới`, `Dù đối mặt thách thức... vẫn vươn lên`). | Kết bằng kết luận giới hạn trong bằng chứng hoặc bước hành động cụ thể. |
| `VIS-AI-006` | `info` | Mở bài ép người đọc tưởng tượng tình huống giả định (`Hãy thử tưởng tượng...`, `Hãy hình dung...`) thay vì đi thẳng vào dữ kiện. | Mở thẳng bằng cơ chế vận hành, số liệu hoặc kết quả thực tế. |
| `VIS-AI-007` | `info` | Câu điều kiện bao sân nhiều nhóm người đọc (`Dù bạn là A, B hay C, bạn đều...`) không bổ sung thông tin thực chất. | Nêu thẳng chức năng cụ thể theo từng vai trò hoặc phạm vi sử dụng. |

## Nhóm 2: Phóng đại và ẩn dụ văn mẫu (`AI_RHETORICAL_INFLATION`)

| Mã quy tắc | Mức | Dấu hiệu nhận diện | Cách viết lại tự nhiên |
| :--- | :---: | :--- | :--- |
| `VIS-RHET-001` | `warning` | Mẫu câu đòn bẩy `Không chỉ (đơn thuần) là X, mà (còn) là Y`, `Không phải vì X mà vì Y` hoặc lặp từ 3 lần các cụm phủ định bắc cầu (`chưa đồng nghĩa với`, `không có nghĩa là`). | Viết thành câu khẳng định nêu thẳng chức năng hoặc kết quả. |
| `VIS-RHET-002` | `warning` | Lời khen phóng đại tầm vóc (`đóng vai trò then chốt`, `bước ngoặt lịch sử`, `minh chứng sống động`, `qua đó khẳng định`, `bứt phá ngoạn mục`). | Bỏ tính từ tán dương, để số liệu và sự kiện tự thể hiện mức độ. |
| `VIS-RHET-003` | `warning` | Ẩn dụ dịch sát từ tiếng Anh của AI (`tấm thảm đa sắc`, `bức tranh toàn cảnh`, `ngọn hải đăng dẫn đường`, `kim chỉ nam`, `viên đá tảng`, `lặn sâu vào`, `đòn bẩy hóa`). | Gọi đúng tên sự vật, rủi ro hoặc phạm vi công việc thực tế. |
| `VIS-RHET-004` | `info` | Ghép gượng hai vế không cùng trục đo (`Từ những A cho đến các B, tất cả đều...`). | Liệt kê cụ thể các bộ phận thực sự liên quan. |
| `VIS-RHET-005` | `warning` | Mượn uy tín không tên (`Các chuyên gia cho rằng`, `Nhiều nghiên cứu chỉ ra rằng`) mà không kèm trích dẫn ngay sau. | Ghi rõ tên tác giả, năm xuất bản hoặc bỏ vế mượn lời nếu câu sau đã có dữ kiện. |
| `VIS-RHET-006` | `warning` | Khung nâng tầm nhận định thiếu bằng chứng (`Hơn cả một X, đây là Y`, `Không phải X, mà chính là Y`). | Mô tả trực tiếp đầu ra hoặc tác nghiệp thực tế của công cụ. |
| `VIS-RHET-007` | `info` | Khung đối lập giả kịch tính (`Tưởng chừng..., nhưng...`, `Thoạt nhìn..., song...`) lặp dày trong văn bản. | Ghi thẳng quy mô lỗi, số bản ghi ảnh hưởng và bước xử lý cần làm. |

## Nhóm 3: Định dạng và nhịp đoạn máy móc (`AI_STRUCTURAL_AND_FORMATTING`)

| Mã quy tắc | Mức | Dấu hiệu nhận diện | Cách viết lại tự nhiên |
| :--- | :---: | :--- | :--- |
| `VIS-FMT-001` | `warning` | Từ 3 dòng danh sách liên tiếp đóng khuôn `- **Nhãn in đậm:**` rồi giải thích lặp lại nhãn. | Bỏ nhãn giả đầu dòng, viết thành câu hoàn chỉnh hoặc gộp gọn các ý cùng loại. |
| `VIS-FMT-002` | `warning` | Đặt quá nhiều từ nối sách vở đầu câu (`Hơn nữa,`, `Thêm vào đó,`, `Bên cạnh đó,`, `Ngoài ra,`) từ 3 lần trong một đoạn. | Mở câu bằng chủ thể thực hiện hành động hoặc nối nhân quả trực tiếp. |
| `VIS-FMT-003` | `info` | Dùng dấu gạch ngang dài (`—`, `--`) hoặc dấu chấm phẩy (`;`) nối mệnh đề kiểu tiếng Anh. | Thay bằng dấu phẩy, dấu hai chấm, ngoặc đơn hoặc tách câu ngắn. |
| `VIS-FMT-004` | `info` | Xếp chồng 3 tính từ khen ngợi theo nhịp văn mẫu (`nhanh chóng, chính xác và hiệu quả`, `chạy mượt mà trên cả`). | Thay bằng chỉ tiêu định lượng cụ thể (thời gian, số lượng, tỷ lệ lỗi). |
| `VIS-FMT-005` | `info` | Từ 4 đoạn liên tiếp có độ dài quá đều (`CV < 0,15`) hoặc 3 câu liền nhau mở đầu cùng một từ (trừ dòng bảng và mục `Bước/Phần/Điều`). Nhận diện cả lỗi xoay vòng động từ đồng nghĩa đầu cột bảng để lách máy quét. | Chia đoạn theo ý thực tế, đổi chủ ngữ mở câu tự nhiên và bỏ động từ dẫn đầu trong ô bảng kỹ thuật. |
| `VIS-FMT-006` | `info` | Chuỗi từ 3 câu cực ngắn liên tiếp dưới `6` từ mỗi câu dùng như khẩu hiệu (`Không ngoại lệ. Không trì hoãn. Không thỏa hiệp.`). | Gộp thành một câu hoàn chỉnh có chủ thể, hành động và thời hạn rõ ràng. |

## Nhóm 4: Dịch từng chữ từ tiếng Anh (`TRANSLATIONESE_EN_VI`)

| Mã quy tắc | Mức | Dấu hiệu nhận diện | Cách viết lại tự nhiên |
| :--- | :---: | :--- | :--- |
| `VIS-TRANS-001` | `warning` | Bị động dịch sát từ tiếng Anh (`được/bị + V + bởi`, `được CMake tự động tải`, `đều được thiết kế bằng`, `được đọc/ghi ra`). | Đưa tác nhân lên đầu câu làm chủ ngữ chủ động hoặc dùng động từ trực tiếp. |
| `VIS-TRANS-002` | `warning` | Lặp dày chữ `được` trước động từ trung tính (`được thực hiện`, `được sử dụng`, `được tiến hành`) từ 3 lần trong đoạn. | Bổ sung chủ thể thực hiện hoặc chuyển sang cấu trúc Đề - Thuyết tự nhiên. |
| `VIS-TRANS-003` | `warning` | Danh từ hóa nặng nề (`sự/việc + động từ + của + chủ thể`) lặp từ 2 lần trong đoạn. | Chuyển danh từ hóa trở lại thành động từ của chủ thể. |
| `VIS-TRANS-004` | `info` | Lặp cụm `một cách + tính từ` dịch từ trạng từ đuôi `-ly` tiếng Anh từ 2 lần trong đoạn. | Dùng trạng từ ngắn trực tiếp (`tăng mạnh` thay cho `tăng một cách đáng kể`). |
| `VIS-TRANS-005` | `warning` | Chủ ngữ giả (`Nó là cần thiết để`), đại từ dịch thô (`nơi mà`, `điều mà`), nhân hóa vật vô tri (`bảng tính vô tình bỏ quên`) hoặc lặp `vẫn... vẫn`. Bao gồm cả đuôi kể công phủ định (`và không cần cài thêm...`), cụm `hỗ trợ + động từ` và bổ ngữ đặt sai chỗ (`báo mất kết nối nhầm`). | Nêu chủ ngữ thật chỉ người hoặc đơn vị, không gán tâm lý cho bảng biểu vô tri, dùng động từ trực tiếp và đặt bổ ngữ đúng trật tự tiếng Việt. |
| `VIS-TRANS-006` | `warning` | Chuỗi ba quan hệ sở hữu nối tiếp (`của... của... của...`) làm câu nặng và khó tách thành phần. | Đưa đơn vị sở hữu lên làm chủ ngữ hoặc bỏ bớt chữ `của` trung gian. |
| `VIS-TRANS-007` | `info` | Lặp dày cặp liên từ sóng đôi (`mặc dù... nhưng`, `bởi vì... nên`) làm nhịp câu nặng nề. | Giữ lại vế đối lập hoặc nhân quả bằng một liên từ gọn ở mệnh đề sau. |
| `VIS-TRANS-008` | `info` | Dùng `đến từ` để chỉ nguồn gốc trừu tượng theo cú pháp tiếng Anh (`giải pháp đến từ nhóm vận hành`). | Đổi sang `của`, `do` hoặc đặt nhóm thực hiện làm chủ ngữ trực tiếp. |
| `VIS-TRANS-009` | `warning` | Lặp hai từ chỉ vị trí trong cùng một cụm (`nằm trong... bên trong`, `bên trong... ở trong`). | Thay một vế bằng quan hệ thuộc tính (`của`, `thuộc`) hoặc ghi thẳng đường dẫn. |
| `VIS-TRANS-010` | `info` | Lặp dày cụm `mang tính + danh/tính từ` (`mang tính chiến lược`, `mang tính định hướng`) làm câu trừu tượng. | Đổi sang động từ hoặc tính từ cụ thể gắn với số lượng và mốc thời gian. |

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
| `VIS-LEX-001` | `warning` | Dùng sai nghĩa từ Hán - Việt (`thực chứng`, `yếu điểm`) hoặc sai chính tả vỏ ngữ âm công sở (`chỉnh chu`, `chuẩn đoán`, `cập nhập`, `sát nhập`, `dậm chân`, `xoay sở`, `xuất sứ`). Nhận diện luôn khung dịch từng chữ thuật ngữ phần mềm (`khung + <danh từ>`, `hiện thực + <danh từ>`, `hợp đồng/giao kèo + <danh từ>`), từ tự chế (`in đúp`) và từ lậm convert. | Dùng đúng từ chuẩn trong công việc (`dựa trên bằng chứng`, `điểm yếu`, `chỉn chu`, `cập nhật`, `sáp nhập`, `đặc tả API`, `xây dựng lớp`, `lặp dòng`). |
| `VIS-LEX-002` | `info` | Dịch ngược từ tiếng Anh đã quen dùng (`thư điện tử`, `yêu cầu kéo`, `trang mạng`), chêm từ ngoại lai lửng lơ (`booking lịch`, `workaround`) hoặc bê nguyên mã bảng, công thức kỹ thuật vào văn xuôi. | Giữ nguyên từ đã quen dùng (`email`, `pull request`, `web`), diễn đạt bằng tiếng Việt cho từ chêm lửng lơ và giải thích thuật ngữ hẹp theo ngôn ngữ nghiệp vụ. |
| `VIS-TONE-001` | `warning` | Chào sồn sã (`Anh X ơi,`), dùng thành ngữ hoặc khẩu ngữ công sở suồng sã (`rủi ro sát sườn`, `cố bấm nút`, `trực chiến 24/7`, `tử huyệt`), tự khoe xếp loại hoặc khen xã giao. | Giữ giọng điềm tĩnh, lễ độ chừng mực và bỏ hẳn câu tự khen hoặc khen xã giao. |
| `VIS-TONE-002` | `warning` | Bê động từ điều tra hình sự, cổ văn hoặc báo chí (`phát lộ`, `phát giác`, `bại lộ`, `vạch trần`, `phơi bày`, `hé lộ`) vào báo cáo, dữ liệu kỹ thuật. Chặn cả cụm kịch tính hóa sự cố hoặc con số (`sập API`, `gây tê liệt`, `khủng hoảng hệ thống`, `vỏn vẹn`, `giậm chân tại chỗ`). | Dùng động từ trung tính (`phát hiện`, `ghi nhận`, `bộc lộ`), mô tả đúng hiện tượng kỹ thuật (`mất kết nối`, `giữ nguyên ở mức`) và bỏ từ bình phẩm số liệu. |
| `VIS-STRUCT-001` | `warning` | Tự thuyết minh bố cục hoặc tài liệu (`Để tránh trùng lặp...`, `Bảng dưới đây trình bày...`, `Tài liệu X mô tả chi tiết...`, `ghi lại lý do chọn`), lộ nhãn dàn ý (`Điểm nghẽn:`, `Bước ngoặt tư duy:`) hoặc đếm tuần tự né máy quét. | Xóa câu giải thích bố cục và nhãn dàn ý, nối thẳng mạch nội dung hoặc gộp liên kết vào danh sách. |
| `VIS-STRUCT-002` | `warning` | Ký tự ẩn, chồng dấu `****`, lỗi `#REF!`, viết `Thiếu -10%`, mũi tên `->`, emoji trang trí và phần trăm dấu chấm `59.9%`. Bao gồm tiêu đề Title Case kiểu Anh, mục con đơn độc, `alt` ảnh nhồi từ khóa (`> 12` từ) và hộp HTML `01` đến `04` lặp bảng. Kiểm tra cả chú thích `#` cây thư mục quá `10` từ, nháy ngược bọc từ Việt thường và dòng `Tổng cộng` cộng sai. Trong báo cáo giám sát, chặn lỗi gộp mục còn lỗi vào tỷ lệ hoàn thành, đóng lỗi bằng hướng dẫn trung gian, bù trừ ròng, thiếu `Tử số/Mẫu số` và lệch `Title` `.docx`. | Chuẩn hóa dấu phẩy thập phân tiếng Việt, giữ `alt` ảnh và chú thích cây thư mục ngắn gọn, đồng thời cộng khớp dòng tổng. Trong báo cáo giám sát, tách riêng tỷ lệ không lỗi và còn lỗi, ghi đủ `Tử số/Mẫu số (%)` và đối soát theo giá trị tuyệt đối. |
| `VIS-LEN-001` | `error` | Câu văn xuôi hoặc câu trong ô bảng dài quá `35` từ (`45` từ với văn bản pháp lý), chặn cứng ngay trên `scan` và `profile`. Bắt cả câu từ `28` từ nối từ `6` vế dấu phẩy hoặc mở đầu vòng vo (`Việc ...`, `Thông qua việc...`, `Liên quan đến vấn đề...`, `với mục đích nhằm`). Trọng số phạt lũy tiến từ `1,0` lên tới `2,5` theo số từ vượt trần. | Cắt bỏ cụm mở đầu vòng vo và chuyển danh sách dài sang gạch đầu dòng. Tách câu dài thành `2` đến `3` câu ngắn độc lập (`15` đến `25` từ mỗi câu), mỗi câu một chủ thể và một động từ chính. |
