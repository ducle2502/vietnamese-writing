# Ngân hàng khuôn câu tổng hợp

Tệp này gom hai bộ khuôn câu vào một chỗ: 25 cấu trúc văn AI, 25 cấu trúc dịch thô, 500 khuôn câu và 16 mẫu rà soát tài liệu kỹ thuật. Mỗi mục ghi rõ rule đang bắt hoặc lý do chuyển sang rà thủ công. Khuôn câu dài đặt trong khối mã để không lẫn với văn xuôi.

## Phần A. Khuôn câu văn AI

Tệp này gom 25 cấu trúc, 250 khuôn câu và 16 mẫu rà soát từ tài liệu huấn luyện nội bộ. Mỗi mục ghi rõ rule đang bắt hoặc lý do chuyển sang rà thủ công. Khuôn câu dài đặt trong khối mã để không lẫn với văn xuôi.

### 1. Hai mươi lăm cấu trúc AI

| Mã | Tên cấu trúc | Rule xử lý |
| :--- | :--- | :--- |
| `C01` | Cấu trúc Bánh kẹp 5 đoạn (5-Paragraph Sandwich) | `VIS-STRUCT-001`, `VIS-AI-005` |
| `C02` | Nhịp đoạn văn Máy đếm nhịp (Paragraph Metronome) | `VIS-FMT-005` |
| `C03` | Song hành phủ định sáo rỗng (Negative Parallelism) | `VIS-RHET-001` |
| `C04` | Đóng khung nâng tầm kiểu Claude (More-than Framing) | `VIS-RHET-006` |
| `C05` | Đóng khung đính chính kiểu GPT (Corrective Framing) | `VIS-RHET-008` |
| `C06` | Đuôi phân từ bình luận hời hợt (Participial Tail) | `VIS-FMT-007`, `VIS-RHET-002` |
| `C07` | Hội chứng né tránh từ "Là" & "Có" (Copula Avoidance) | `VIS-CLICHE-002` |
| `C08` | Quy tắc Số 3 cưỡng bức (Compulsive Rule of Three) | `VIS-FMT-004` |
| `C09` | Dải phổ bao quát giả tạo (False Ranges) | `VIS-RHET-004` |
| `C10` | Lạm dụng dấu gạch ngang dài (Formulaic Em-Dash —) | `VIS-FMT-003` |
| `C11` | Danh sách Bullet In đậm + Hai chấm (Bold-Colon Listitis) | `VIS-FMT-001` |
| `C12` | Nhịp câu cụt giả triết lý (Staccato Fragments) | `VIS-FMT-006`, `VIS-FMT-008` |
| `C13` | Câu hỏi 1 chữ tự biên tự diễn (Fake-Suspense Q&A) | `VIS-FMT-008` |
| `C14` | Giải thích "vì sao quan trọng" cưỡng bức (Matter-Claiming) | `VIS-RHET-008` |
| `C15` | Kết bài "Mặc dù thách thức... tương lai hứa hẹn" | `VIS-AI-005` |
| `C16` | Lập luận "Ba phải – Dĩ hòa vi quý" (Fence-Sitting) | `VIS-RHET-009` |
| `C17` | Cấu trúc đối xứng giả biện chứng (Tưởng chừng... nhưng...) | `VIS-RHET-007` |
| `C18` | Ẩn dụ mở màn "Hãy tưởng tượng" (Forced Analogy) | `VIS-AI-006` |
| `C19` | Câu điều kiện gom mọi độc giả | `VIS-AI-007` |
| `C20` | Khoe phủ sóng truyền thông thừa thãi (Metacoverage) | `VIS-RHET-009` |
| `C21` | Ví dụ giả định vô danh (Placeholder Examples) | `VIS-AI-002` và rà thủ công |
| `C22` | Lặp luận điểm bằng cách tráo từ (Paraphrase Looping) | rà thủ công |
| `C23` | Khen nịnh tâm lý người đọc quá đà (Dramatic Flattery) | `VIS-RHET-009` |
| `C24` | Viết hoa Tiêu đề kiểu Tiếng Anh (Title Case) | `VIS-STRUCT-002` |
| `C25` | Bội thực In đậm, Markdown sống & Emoji | `VIS-STRUCT-002` |

### 2. Hai trăm năm mươi khuôn câu

#### 01. Khuôn mở đoạn định nghĩa & đóng khung chủ đề (25 khuôn)

```text
Trong bối cảnh [X] ngày càng phát triển, [Y] đã trở thành...
Trong thế giới [X] đầy biến động, việc [Y] là...
Với sự ra đời của [X], cách chúng ta [Y] đã thay đổi...
[X] được định nghĩa rộng rãi là quá trình...
Về bản chất, [X] đề cập đến hệ thống...
[X] có thể được phân loại khái quát thành...
Xét trong lĩnh vực [X], ít có yếu tố nào quan trọng hơn [Y]
Khi ranh giới giữa [X] và [Y] mờ dần...
Sự trỗi dậy của [X] đã mở ra...
Từ góc độ tổng quan, [X] đại diện cho...
Hiểu một cách đơn giản, [X] chính là...
Cốt lõi của [X] nằm ở khả năng...
Trên hành trình hướng tới [X], [Y] nổi lên như...
Giữa làn sóng [X], các tổ chức đang ráo riết...
Chưa bao giờ câu chuyện về [X] lại cấp thiết như...
Khi bàn về [X], người ta thường nghĩ ngay đến...
Trong bức tranh lớn của [X], [Y] giữ một...
Đối diện với áp lực từ [X], việc áp dụng [Y]...
Nhìn lại chặng đường phát triển của [X]...
Ngay tại giao điểm của [X] và [Y] là...
[X] đã đi một chặng đường dài trong những năm qua
Sự chuyển dịch sang [X] đang định hình lại...
Mục tiêu của bài viết này là làm sáng tỏ...
Để đặt nền tảng cho cuộc thảo luận về [X]...
Trước làn sóng bùng nổ của [X], câu hỏi đặt ra là...10.
```

#### 02. Khuôn mệnh đề mục đích "Để [Động từ]..." đầu câu (25 khuôn)

```text
Để hiểu rõ hơn về [X], chúng ta cần xem xét...
Để khám phá trọn vẹn [X], hãy nhìn vào...
Để khai phá tiềm năng của [X], doanh nghiệp phải...
Để điều hướng sự phức tạp của [X], người dùng nên...
Để làm sáng tỏ vấn đề [X], bài viết sẽ...
Để minh họa cho luận điểm này, hãy xét...
Để đi sâu vào bản chất của [X], trước hết...
Để tận dụng tối đa sức mạnh của [X]...
Để nắm bắt cơ hội từ [X], việc trang bị...
Để vượt qua những rào cản của [X]...
Để tối ưu hóa hiệu suất của [X], cần phải...
Để kiến tạo một [X] bền vững, không thể thiếu...
Để bắt kịp nhịp độ của [X], các nhà lãnh đạo...
Để thu hẹp khoảng cách giữa [X] và [Y]...
Để hiện thực hóa tầm nhìn về [X]...
Để xây dựng nền tảng vững chắc cho [X]...
Để đảm bảo tích hợp liền mạch giữa [X] và [Y]...
Để đánh giá khách quan tác động của [X]...
Để giải mã sức hút của [X], hãy điểm qua...
Để trả lời câu hỏi này một cách thấu đáo...
Để đưa [X] lên một tầm cao mới, bạn cần...
Để thích ứng linh hoạt với bối cảnh [X]...
Để chắt lọc những giá trị cốt lõi từ [X]...
Để mở đường cho những đổi mới trong [X]...
Để khái quát hóa bức tranh về [X]...12.
```

#### 03. Khuôn song hành phủ định & đối lập nhân tạo (25 khuôn)

```text
Không chỉ [X], mà còn [Y]
Không chỉ dừng lại ở [X], [chủ thể] còn vươn tới [Y]
Không đơn thuần là [X], đó còn là [Y]
Đây không phải là [X], mà chính là [Y]
Vấn đề không nằm ở [X], mà nằm ở [Y]
Không phải vì thiếu [X], mà vì thiếu [Y]
Hơn cả một [X], đây thực sự là một [Y]
Vượt xa khái niệm [X] thông thường, [Y] mang đến...
Thay vì chỉ dựa vào [X], giải pháp này tập trung vào [Y]
Thay vì chạy theo [X], hãy ưu tiên [Y]
[Y] hơn là chỉ đơn giản [X]
Không chỉ giúp [X], công cụ này còn trao quyền [Y]
Không những tối ưu [X] mà còn nâng tầm [Y]
Không phải là sự thay thế cho [X], mà là chất xúc tác cho [Y]
Điều thực sự tạo khác biệt không phải [X], mà là [Y]
Đừng nghĩ đây chỉ là [X], hãy xem nó là [Y]
Không ồn ào như [X], nhưng lại sâu sắc như [Y]
Vừa đảm bảo [X], lại vừa duy trì trọn vẹn [Y]
Tưởng chừng như chỉ là [X], nhưng hóa ra lại là [Y]
Không phải ngẫu nhiên mà [X], tất cả là nhờ [Y]
Ít thiên về [X] hơn, mà nghiêng hẳn sang [Y]
Không còn bó hẹp trong [X], nay đã mở rộng sang [Y]
Chẳng những giải quyết [X] mà còn mở khóa [Y]
Không phải điểm kết thúc của [X], mà là bình minh của [Y]
Không chỉ cho hôm nay, mà còn cho cả tương lai [Y]1.
```

#### 04. Khuôn né tránh hệ từ & nâng tầm danh vị (25 khuôn)

```text
[X] đóng vai trò là [Y]
[X] đóng vai trò then chốt trong việc [Y]
[X] giữ vị trí như một [Y] không thể thiếu
[X] phục vụ như một cầu nối giữa...
[X] hiện lên như một biểu tượng của...
[X] nổi lên như một giải pháp hàng đầu cho...
[X] tồn tại như một minh chứng sống động cho...
[X] được xem như xương sống của...
[X] được mệnh danh là trái tim của...
[X] tự hào sở hữu hệ thống [Y]
[X] tự hào mang đến trải nghiệm [Y]
[X] nổi bật với hàng loạt tính năng [Y]
[X] gây ấn tượng mạnh nhờ sự kết hợp [Y]
[X] khoác lên mình diện mạo [Y]
[X] đại diện cho bước ngoặt lớn trong...
[X] đánh dấu sự chuyển mình mạnh mẽ của...
[X] là hiện thân hoàn hảo của...
[X] đặt nền móng vững chắc cho...
[X] trở thành kim chỉ nam dẫn dắt...
[X] chính là chất xúc tác thúc đẩy...
[X] đã cách mạng hóa hoàn toàn cách chúng ta [Y]
[X] mở ra cánh cửa bước vào thế giới [Y]
[X] định hình lại toàn bộ tiêu chuẩn về [Y]
[X] thiết lập một chuẩn mực mới cho [Y]
[X] nép mình duyên dáng giữa lòng [Y]12.
```

#### 05. Khuôn đuôi phân từ bình luận ý nghĩa cuối câu (25 khuôn)

```text
..., qua đó khẳng định tầm quan trọng của [X]
..., qua đó làm nổi bật vai trò của [X]
..., từ đó mở ra nhiều cơ hội mới cho [X]
..., từ đó tạo tiền đề vững chắc cho [X]
..., góp phần thúc đẩy sự phát triển của [X]
..., góp phần nâng cao trải nghiệm của [X]
..., phản ánh xu hướng rộng lớn hơn trong ngành
..., phản ánh cam kết không ngừng nghỉ đối với [X]
..., nhấn mạnh sự cần thiết phải đổi mới [X]
..., minh chứng cho sức sống bền bỉ của [X]
..., đảm bảo mọi quy trình diễn ra liền mạch
..., tạo nên một bức tranh đa sắc màu về [X]
..., mang lại giá trị thiết thực cho cộng đồng
..., củng cố vị thế tiên phong trên thị trường
..., khơi dậy tiềm năng to lớn vốn có của [X]
..., đánh dấu một chương mới đầy hứa hẹn
..., để lại dấu ấn khó phai trong lòng [X]
..., nuôi dưỡng văn hóa đổi mới sáng tạo
..., thu hẹp khoảng cách giữa lý thuyết và thực tiễn
..., đáp ứng trọn vẹn kỳ vọng ngày càng cao
..., biến thách thức thành động lực tăng trưởng
..., hài hòa giữa lợi ích kinh tế và bền vững
..., mở đường cho các thế hệ giải pháp tiếp theo
..., định hình tương lai của toàn ngành [X]
..., phù hợp hoàn hảo với định hướng chiến lược19.
```

#### 06. Khuôn Bộ ba đối xứng (Rule of Three) & Dải phổ giả (25 khuôn)

```text
Nhanh chóng, hiệu quả và toàn diện
Sáng tạo, đột phá và bền vững
Linh hoạt, bảo mật và dễ mở rộng
Tinh tế, hiện đại và đẳng cấp
Tỉ mỉ, chính xác và đáng tin cậy
Từ [cá nhân], [đội nhóm] đến [tập đoàn lớn]
Từ [ý tưởng sơ khai] đến [thực thi hoàn chỉnh]
Từ [những chi tiết nhỏ nhất] đến [chiến lược tổng thể]
Trải dài từ [A] sang [B] và chạm tới [C]
Bao quát mọi khía cạnh từ [X] cho tới [Y]
Giúp bạn tiết kiệm thời gian, tối ưu chi phí và nâng cao năng suất
Kết hợp hài hòa giữa [con người], [quy trình] và [công nghệ]
Đáp ứng đồng thời ba tiêu chí: [A], [B] và [C]
Dù xét về [kinh tế], [xã hội] hay [môi trường]
Phục vụ đa dạng đối tượng từ [người mới], [chuyên viên] đến [lãnh đạo]
Mở rộng quy mô từ [địa phương], [khu vực] đến [toàn cầu]
Vận hành trơn tru ở cả ba khâu: [trước], [trong] và [sau]
Không ngừng học hỏi, thích nghi và bứt phá
Kiến thức sâu rộng, kỹ năng sắc bén và tư duy đổi mới
Mang lại sự rõ ràng, minh bạch và nhất quán
Kết nối quá khứ, hiện tại và tương lai
Giao thoa giữa nghệ thuật, khoa học và công nghệ
Hội tụ đủ tâm, tầm và tài
Vững vàng trước biến động, nhạy bén trước cơ hội và kiên định với mục tiêu
Đơn giản trong thao tác, mạnh mẽ trong tính năng và tối ưu về chi phí19.
```

#### 07. Khuôn câu hỏi mồi 1 chữ & nhịp cụt mạng xã hội (25 khuôn)

```text
Kết quả là gì?
Câu trả lời nằm ở đâu?
Và phần tuyệt vời nhất?
Điểm mấu chốt ở đây là gì?
Bí mật thực sự là gì?
Nhưng khoan đã, còn hơn thế nữa:
Điều đáng kinh ngạc là gì?
Tại sao điều này lại xảy ra?
Điều gì khiến [X] trở nên khác biệt?
Đây mới là cú ngoặt thực sự:
Đây là phần mà 90% mọi người bỏ lỡ:
Hãy dừng lại một giây để suy ngẫm.
Không màu mè. Chỉ có giá trị thực.
Không lý thuyết rườm rà. Đi thẳng vào việc.
Không ồn ào. Không phô trương. Chỉ kết quả.
Ngắn gọn. Súc tích. Đầy sức nặng.
Không phải sự hỗn loạn. Mà là sự rõ ràng.
Một thay đổi nhỏ. Một tác động khổng lồ.
Đọc kỹ lại câu đó một lần nữa.
Và thành thật mà nói? Điều đó rất hiếm.
Nghe có vẻ quen thuộc phải không?
Tin tốt là gì? Bạn hoàn toàn kiểm soát được.
Tin xấu là gì? Hầu hết đều làm sai cách.
Bài học rút ra ở đây rất đơn giản:
Một khi đã nhận ra, bạn không thể làm ngơ.11.
```

#### 08. Khuôn quy chụp uy tín giả & lập luận trung lập ba phải (25 khuôn)

```text
Nhiều nghiên cứu khoa học đã chỉ ra rằng...
Các chuyên gia đầu ngành đều đồng thuận rằng...
Giới quan sát thị trường nhận định rằng...
Theo nhiều báo cáo uy tín trong ngành...
Không ít nhà phê bình đã lên tiếng cho rằng...
Người ta thường truyền tai nhau rằng...
Dư luận rộng rãi đang nghiêng về quan điểm...
Một mặt, [X] mang lại lợi ích..., mặt khác, nó cũng tiềm ẩn...
Mặc dù [X] có nhiều ưu điểm vượt trội, chúng ta vẫn cần lưu ý...
Tuy [X] rất hấp dẫn, nhưng không phải không có hạn chế
Mỗi phương pháp đều có những điểm mạnh và điểm yếu riêng
Lựa chọn tối ưu nhất còn tùy thuộc vào bối cảnh cụ thể của bạn
Không có một công thức chung nào áp dụng cho tất cả
Điều quan trọng là tìm ra điểm cân bằng hài hòa giữa [X] và [Y]
Cần cân nhắc kỹ lưỡng cả hai mặt của đồng xu trước khi...
Trong một số trường hợp, [X] phát huy tốt, nhưng ở trường hợp khác...
Kết quả thực tế có thể thay đổi tùy theo nhiều biến số
Sẽ là khôn ngoan hơn cả nếu kết hợp linh hoạt cả hai hướng
Vẫn còn quá sớm để đưa ra kết luận cuối cùng về [X]
Cuộc tranh luận xung quanh [X] chắc chắn sẽ còn tiếp diễn
Bạn có thể cân nhắc tham khảo thêm ý kiến chuyên gia để...
Dù chọn hướng đi nào, sự chuẩn bị kỹ lưỡng vẫn là trên hết
Mặc dù thông tin chi tiết hiện còn khá hạn chế, nhưng...
Xét một cách công tâm, cả [A] và [B] đều có lý lẽ riêng
Tùy vào khẩu vị rủi ro và mục tiêu dài hạn mà bạn quyết định6.
```

#### 09. Khuôn giải thích tầm quan trọng & suy luận máy móc (25 khuôn)

```text
Điều này đặc biệt quan trọng bởi vì...
Lý do khiến [X] trở nên sống còn là bởi...
Hiểu rõ [X] là yếu tố thiết yếu để đạt được [Y]
Bằng cách thực hiện [X], bạn có thể dễ dàng đạt được [Y]
Chính nhờ khả năng [X] mà [Y] trở nên vượt trội
Do đó, hoàn toàn có cơ sở để kết luận rằng...
Từ đó, chúng ta có thể suy ra một cách rõ ràng rằng...
Điều này chứng minh một thực tế không thể chối cãi rằng...
Điều này càng củng cố thêm quan điểm cho rằng...
Hệ quả tất yếu kéo theo là [X] sẽ dẫn đến [Y]
Nếu nhìn sâu hơn vào [X], ta dễ dàng nhận thấy...
Không khó để lý giải vì sao [X] lại được ưa chuộng đến vậy
Mối tương quan chặt chẽ giữa [X] và [Y] cho thấy rằng...
Chính tại điểm này, giá trị thực sự của [X] mới tỏa sáng
Nếu bỏ qua yếu tố [X], mọi nỗ lực với [Y] đều trở nên vô nghĩa
Đây chính là mảnh ghép còn thiếu giúp hoàn thiện [X]
Qua ví dụ trên, bài học cốt lõi hiện lên rất rõ nét:
Điều đó đồng nghĩa với việc doanh nghiệp cần phải...
Xét đến cùng, thành bại của [X] phụ thuộc vào việc...
Như một lẽ tự nhiên, khi [X] tăng lên thì [Y] cũng...
Điểm giao thoa này cho phép chúng ta nhìn nhận [X] theo cách mới
Nhờ nắm vững quy luật này, người dùng hoàn toàn làm chủ...
Nói một cách ngắn gọn, [X] chính là câu trả lời cho [Y]
Rõ ràng, lợi ích mà [X] đem lại vượt xa chi phí bỏ ra
Tất cả những dữ kiện trên đều hội tụ về một điểm chung:9.
```

#### 10. Khuôn chốt đoạn, kết bài lạc quan & rào đón Chatbot (25 khuôn)

```text
Tóm lại, [X] đóng một vai trò không thể thay thế trong...
Nhìn chung, việc đầu tư vào [X] là bước đi chiến lược...
Tựu trung lại, qua những phân tích chi tiết ở trên...
Để kết lại bài viết này, có thể khẳng định rằng...
Xét trên mọi phương diện, [X] thực sự là giải pháp...
Mặc dù chặng đường phía trước còn nhiều chông gai, nhưng tương lai của [X] rất xán lạn
Với đà phát triển hiện tại, [X] hứa hẹn sẽ còn bùng nổ hơn nữa
Khi công nghệ tiếp tục tiến bộ không ngừng, chúng ta có quyền kỳ vọng...
Suy cho cùng, công nghệ chỉ là công cụ, con người mới là trung tâm
Hành trình chinh phục [X] chỉ mới thực sự bắt đầu
Hãy bắt tay vào áp dụng những chiến lược trên ngay hôm nay để...
Chắc chắn rồi! Dưới đây là bản phân tích chi tiết dành cho bạn:
Tuyệt vời! Tôi rất sẵn lòng hỗ trợ bạn soạn thảo nội dung này:
Dựa trên các yêu cầu bạn vừa nêu, đây là phương án tối ưu:
Hy vọng rằng những thông tin tổng hợp trên sẽ giúp ích cho bạn!
Nếu bạn muốn điều chỉnh giọng văn hoặc mở rộng phần nào, hãy cho tôi biết nhé!
Chúc bạn áp dụng thành công và gặt hái nhiều thành tựu!
Hy vọng bức thư này đến tay bạn khi mọi công việc đều thuận lợi
Xin lưu ý rằng thông tin trên chỉ mang tính chất tham khảo chung
Với tư cách là một trợ lý AI, tôi không thể đưa ra lời khuyên pháp lý...
Dưới đây là bản tóm tắt ngắn gọn các ý chính vừa trình bày:
Như chúng ta đã cùng nhau khám phá xuyên suốt bài viết...
Với tất cả những yếu tố vừa nêu trong tâm trí, hãy...
Một điều chắc chắn rằng [X] sẽ còn định hình tương lai lâu dài
Cảm ơn bạn đã đồng hành đến cuối bài viết chuyên sâu này12.
```

### 3. Mười sáu mẫu từ tài liệu kỹ thuật

| Mẫu | Dấu hiệu | Cách xử lý |
| :---: | :--- | :--- |
| 1 | Nhồi định ngữ, trạng từ thừa và đuôi phủ định kể công ở đoạn mở đầu. | Bỏ định ngữ thừa, cắt đuôi phủ định và mở bằng dữ kiện chính. |
| 2 | Vế sau giải thích lại hệ quả hiển nhiên. | Chấm câu ngay sau dữ kiện, bỏ vế giải thích. |
| 3 | Hộp tóm tắt `01–04` lặp lại bảng chi tiết ngay bên dưới. | Giữ một tầng trình bày, xóa hộp lặp. |
| 4 | Tự bịa mục so sánh với công cụ lớn và mục "khi nào chọn công cụ khác". | Xóa mục không có dữ liệu kiểm chứng. |
| 5 | Tự bịa bảng tiến độ `G1–G4` sáo rỗng. | Xóa bảng, thay bằng mốc số liệu thực tế. |
| 6 | Xoay vòng động từ đồng nghĩa ở đầu ô bảng để lách cờ lặp từ. | Bỏ động từ dẫn đầu, ghi thẳng tên tệp hoặc lớp. |
| 7 | Dịch can thuật ngữ lập trình sang cụm tiếng Việt kỳ dị. | Dùng từ quen thuộc của lập trình viên hoặc giữ nguyên thuật ngữ. |
| 8 | Phóng đại thao tác bình thường trong bảng chức năng và bảng phím tắt. | Ghi đúng thao tác, bỏ tính từ quảng cáo. |
| 9 | Nhét tính từ quảng cáo rỗng vào tài liệu kỹ thuật. | Thay bằng thông số hoặc mô tả cơ chế. |
| 10 | Tự phong chức danh tập đoàn và thuật ngữ quản trị dự án cho nhóm nhỏ. | Dùng chức danh thật và phạm vi thật. |
| 11 | Giảng đạo lý, cảnh báo pháp lý tự phát và bảng giải thích điều hiển nhiên. | Xóa hộp răn đe và bảng hiển nhiên. |
| 12 | Nhồi từ khóa, số liệu kiểu SEO vào thuộc tính `alt`. | Giữ `alt` tối đa `8` chữ nêu tên hình. |
| 13 | Chú thích cây thư mục và nhãn Mermaid viết dài như văn xuôi. | Giữ nhãn tối đa `8` chữ. |
| 14 | Đặt tên tiêu đề và thanh điều hướng rườm rà kiểu sách giáo khoa. | Dùng tiêu đề ngắn, đúng chức năng mục. |
| 15 | Tự thuyết minh bố cục tài liệu ở đầu hoặc cuối bài. | Xóa câu mô tả mục lục và câu kết lặp liên kết. |
| 16 | Dựng kịch bản hù dọa rủi ro và phương án bù nhìn. | Nêu điều kiện và hệ quả cụ thể, bỏ phương án bù nhìn. |

### 4. Cách dùng

Quét tệp sau khi viết bằng `python scripts/vi_scanner.py scan TEP.md --json`. Đối chiếu mã `C` với rule tương ứng trong [rule-catalog.md](rule-catalog.md). Mẫu không có rule tự động phải đưa vào danh sách rà thủ công.

## Phần B. Khuôn câu dịch thô

Tệp này gom 25 cấu trúc, 250 khuôn câu và 12 bộ lọc regex từ tài liệu huấn luyện nội bộ. Khuôn câu dài đặt trong khối mã. Regex chỉ dùng để phát hiện, không tự động sửa.

### 1. Hai mươi lăm cấu trúc dịch thô

| Mã | Tên cấu trúc | Rule xử lý |
| :--- | :--- | :--- |
| `G01` | Bệnh Danh từ hóa tràn lan (Sự / Việc / Tính / Cuộc) | `VIS-TRANS-003` |
| `G02` | Danh từ hóa kép nối bằng Động từ rỗng | `VIS-TRANS-003` |
| `G03` | Lạm dụng trạng ngữ "Một cách + [Tính từ]" | `VIS-TRANS-004` |
| `G04` | Bị động Tây hóa kèm giới từ "Bởi" | `VIS-TRANS-001` |
| `G05` | Nhầm tình thái "Bị / Được" ở câu trung tính | `VIS-TRANS-011` |
| `G06` | Bị động truyền tin vô nhân xưng cụt chủ ngữ | `VIS-TRANS-011` |
| `G07` | Chủ ngữ giả vô nghĩa "Nó là... để..." | `VIS-TRANS-005` |
| `G08` | Đại từ quan hệ chồng chất "Người mà / Cái mà" | `VIS-TRANS-005` |
| `G09` | Dư thừa lượng từ số/giống "Những / Các / Một" | `VIS-LEX-001` và rà thủ công |
| `G10` | Chuỗi giới từ sở hữu "Của... của... của..." | `VIS-TRANS-006` |
| `G11` | Giới từ mở đầu câu làm mất Chủ ngữ ("Bất thành cú") | `VIS-LEX-001` và rà thủ công |
| `G12` | Phối hợp thừa cặp liên từ sai logic | `VIS-TRANS-007` |
| `G13` | Mệnh đề động từ làm chủ ngữ gượng cho "Khiến cho" | `VIS-TRANS-007` |
| `G14` | Cấu trúc lai căng chỉ nơi xuất thân "Đến từ" | `VIS-TRANS-008` |
| `G15` | Câu chữ 把 Trung Hoa ("Đem + Tân ngữ + Động từ") | `VIS-TRANS-012` |
| `G16` | Mẫu rào đón Trung Hoa "Đối với... mà nói" | `VIS-TRANS-012` |
| `G17` | Định ngữ ngược Trung – Việt & Trợ từ "Đích" | `VIS-TRANS-013` |
| `G18` | Trạng ngữ thời gian / nơi chốn kẹp sai chỗ | `VIS-TRANS-013` |
| `G19` | Giới từ 给 (cho) / 对 (với) đặt ngược trước Động từ | `VIS-TRANS-012` |
| `G20` | Lặp từ chỉ vị trí kép "Ở trong... bên trong" | `VIS-TRANS-009` |
| `G21` | Bổ ngữ xu hướng dịch cứng "[V] + đứng lên / đi xuống" | `VIS-TRANS-013` |
| `G22` | Liên từ đặt lùi sau Chủ ngữ & dịch cào bằng | `VIS-TRANS-007`, `VIS-TRANS-012` |
| `G23` | Giới từ phân công 由 (Do) dịch thành câu bị động | `VIS-TRANS-012` |
| `G24` | Hậu tố "Mang tính..." & Bị động chắp dính Hàn – Nhật | `VIS-TRANS-010` |
| `G25` | Mệnh đề SOV Nhật – Hàn dồn động từ xuống đáy câu | `VIS-TRANS-014` |

### 2. Hai trăm năm mươi khuôn câu

#### 01. Cụm Danh từ hóa Sự / Việc / Tính / Cuộc lạm dụng (25 mẫu)

```text
Sự gia tăng nhanh chóng của [X]
Sự sụt giảm đáng kể của [X]
Sự xuất hiện đột ngột của [X]
Sự hiện diện thường xuyên của [X]
Sự vắng mặt kéo dài của [X]
Sự thiếu hụt trầm trọng của [X]
Sự phát triển mạnh mẽ của [X]
Sự thay đổi liên tục của [X]
Sự biến đổi đột biến của [X]
Sự mở rộng quy mô của [X]
Sự chịu đựng duy nhất của [ai] đối với
Sự phẫn nộ của [ai] trước việc
Sự cẩu thả của [ai] trong khâu
Sự am hiểu của [ai] về
Việc sử dụng quá mức của [X]
Việc thực hiện thành công của [X]
Việc thiếu kiến thức cơ bản của [ai]
Việc vứt bỏ thực phẩm của người mua
Việc nộp đơn thông qua kênh này
Việc giáo dục người dân của chính phủ
Tính khả thi cao của dự án
Tính hiệu quả vượt trội của phương pháp
Tính linh hoạt lớn của hệ thống
Tiến hành một cuộc điều tra toàn diện về
Thực hiện một sự quan sát kỹ lưỡng đối với49.
```

#### 02. Trạng ngữ "Một cách..." & Cụm giới từ tiếng Anh dịch can (25 mẫu)

```text
Một cách nhanh chóng
Một cách chậm rãi
Một cách cẩn thận
Một cách tỉ mỉ
Một cách hiệu quả
Một cách thành công
Một cách suôn sẻ
Một cách dễ dàng
Một cách tự nhiên
Một cách rõ ràng
Một cách chính xác
Một cách hoàn hảo
Một cách nhiệt tình
Một cách nhất quán
Một cách tình cờ
Một cách bất ngờ
Một cách nghiêm túc
Một cách thẳng thắn
Một cách mơ hồ
Một cách khiên cưỡng
Trong một cách mà - in a way that
Theo một phong cách lịch sự - in a polite manner
Với sự dễ dàng lớn - with great ease
Với tốc độ cao của - at a high speed
Trong sự chi tiết tuyệt vời - in great detail38.
```

#### 03. Mẫu câu Bị động Tây hóa & Sai tình thái Bị / Được (25 mẫu)

```text
Bị oanh tạc bởi [X]
Bị phá hủy bởi [X]
Bị vây quanh bởi [X]
Bị chi phối bởi [X]
Bị thu hút bởi [X]
Được hoàn thành bởi [X]
Được viết bởi [X]
Được sửa chữa bởi [X]
Được gửi bởi [X]
Được đọc bởi [X]
Được bao quanh bởi [X]
Được thu hoạch bởi [X]
Được thực hiện bởi [X]
Được tin là đã [V]
Được cho là đang [V]
Được biết rằng [mệnh đề]
Được công nhận rằng [mệnh đề]
Được kỳ vọng sẽ [V]
Đã bị đặt chỗ xong (tình huống tốt)
Cửa bị gió đóng lại (vô sinh)
Bị chết / bị mệt / bị bất ngờ (nội động từ lạm dụng)
Chiếc hộp được phủ với tấm chăn
Kết hôn với ba đứa con hiểu sai married with
Được làm từ giấy (giữ nguyên chất)
Được làm bằng gỗ (đã hóa giấy)90.
```

#### 04. Chủ ngữ giả, Đại từ quan hệ thô & Lượng từ dư thừa (25 mẫu)

```text
Nó là khó khăn để [V]
Nó là cần thiết để [V]
Nó là quan trọng để [V]
Nó là không thể để [V]
Nó là dễ dàng để chỉ ra rằng
Nó mất của tôi 2 giờ để [V]
Nó dường như rằng [mệnh đề]
Nó xảy ra rằng [mệnh đề]
Có một sự thật rằng
Có nhiều lý do tại sao mà
Người đàn ông người mà đang đứng
Cuốn sách cái mà tôi mua hôm qua
Thành phố nơi mà tôi sinh ra
Lý do tại sao mà anh ấy nghỉ
Thời điểm khi mà sự việc nổ ra
Cách thức mà bằng nó chúng ta giải quyết
Tắc nghẽn cái mà mọi người hài lòng vướng vào
Những con người luôn mưu cầu
Các trẻ em cần được bảo vệ
Những con cừu ăn cỏ trên đồi
Anh ấy là một bác sĩ giỏi (dư chữ "một")
Cô ấy có một mái tóc dài (dư chữ "một")
Mỗi một cá nhân trong số các thành viên
Tất cả những các vấn đề trên
Một số những người tiêu dùng2.
```

#### 05. Câu "Bất thành cú" do giới từ mở đầu nuốt Chủ ngữ (25 mẫu)

```text
Qua kinh nghiệm cho ta thấy rằng...
Qua khảo sát thực tế chứng minh rằng...
Qua lời dạy trên đã khẳng định...
Qua cảnh bắt bớ cho thấy sự bất minh...
Qua sự việc vàng tăng giá khiến nhiều người...
Với nghệ thuật so sánh đã làm nổi bật...
Với những sai sót năm qua yêu cầu phải...
Với hình ảnh sinh động ấy đã nói lên...
Với sức mạnh phong trào khiến kẻ thù khiếp sợ...
Bằng bốn câu thơ tuyệt tác đã thể hiện...
Bằng hình tượng nhân vật đã khắc họa...
Bằng nỗ lực không ngừng đã giúp công ty...
Trước muôn vàn thử thách đòi hỏi người lính...
Giữa các tác phẩm ấy đã bộc lộ...
Từ quần chúng đã đào tạo được...
Trên nền tối tăm ấy đã vẽ lên...
Trong những hoạt động ấy đã đem lại...
Trong năm qua đã xây dựng nhiều công trình...
Trong cách lập luận chưa chứng minh được...
Thông qua hội thảo nhằm thúc đẩy...
Nhờ áp dụng công nghệ đã rút ngắn...
Dưới sự chỉ đạo sát sao đã hoàn thành...
Sau túp lều nhìn thấy một cây cau
Trên tường treo lên một bức tranh (sai chữ "lên")
Sau nhà trồng lên một bụi tre106.
```

#### 06. Ghép sai cặp liên từ & Chủ ngữ động từ gây khiến gượng gạo (25 mẫu)

```text
Qua sông cho nên ta dùng thuyền
Qua kinh nghiệm nên ta thấy rằng
Với quyết tâm cao nên công nhân đã vượt mức
Cùng một hoàn cảnh nên tôi rất thông cảm
Cùng học một trường nên hai đứa rất thân
Trong khi gặp khó khăn nhưng họ không sờn lòng
Trong khi cả lớp nghe giảng nhưng nó nhìn ra cửa
Mặc dù trời mưa to song nhưng anh vẫn đến
Tuy giá hơi cao nhưng mà tuy nhiên chất lượng tốt
Là đoàn viên nên ta phải cố gắng
Là người quản lý cho nên anh phải gương mẫu
Để đạt mục tiêu nên chúng ta cần đồng lòng
Vì do chủ quan nên dẫn đến thất bại
Bởi tại thiếu vốn cho nên dự án đình trệ
Thấy nước sông dâng cao khiến cho dân làng lo sợ
Nghe tin dữ làm cho bà cụ ngất xỉu
Bị mất của khiến cho anh chàng cuống quýt
Bị trượt kỳ thi nên làm cho nó buồn bã
Chính vì chị yếu quá là nguyên nhân chị thất bại
Anh ăn nói thô tục không xứng đáng với...
Họ làm ăn bê bối chứng tỏ họ thiếu trách nhiệm
Lão giàu có như vậy làm thành ưu thế của lão
Nhìn vào bảng số liệu phản ánh rõ xu hướng
Dựa trên kết quả này suy ra giả thuyết đúng
So sánh hai phương án cho thấy cách đầu rẻ hơn106.
```

#### 07. Câu chữ 把 (Đem) & Giới từ ngược 给 / 对 tiếng Trung (25 mẫu)

```text
Đem tiền lương giao cho vợ
Đem bài tập làm cho xong
Đem đồ đạc chuyển lên lầu
Đem lời hắn nói để ở trong lòng
Đem sách lật đến trang 13
Đem cửa sổ mở ra cho thoáng
Đem cậu xem như bạn bè
Đem chìa khóa đặt ở trên bàn
Đem thất bại coi làm động lực
Đem tiếng Trung học cho thật tốt
Đem thuốc uống hết đi
Đem điện thoại nhét vào trong túi
Đem bài khóa này dịch sang tiếng Trung
Không đem tôi để ở trong mắt
Thích đem đồ đạc vứt lung tung
Con cho mẹ rót một cốc nước
Tôi cho bạn nấu cơm rồi
Tôi cho bạn nộp học phí
Cậu cho tôi xem một chút
Hắn đi qua đi cấp cô nắm bả vai
Anh ấy đối với tôi rất tốt
Anh ấy đối với chuyện tình cảm rất nghiêm túc
Anh ấy đối với âm nhạc phi thường nhạy cảm
Tôi đối với hắn không hiểu rõ lắm
Chuyện này đối với hắn căn bản không có ảnh hưởng59.
```

#### 08. Mẫu rào đón, Liên từ bậc cao & Phương vị kép tiếng Trung (25 mẫu)

```text
Đối với tôi mà nói, vấn đề này...
Đối với doanh nghiệp mà giảng...
Ở chuyên gia xem tới - 在...看来
Từ góc độ dài hạn đến xem - 从...来看
Cầm trường hợp này đến nói - 拿...来说
Đến hôm nay làm dừng - 到...为止
Đối với vấn đề này cậu có cách nhìn gì?
Đối với chuyện này tôi đã nghĩ xong cách
Từ hồi cấp ba đã đối với tiếng Trung nảy sinh hứng thú
Cậu nếu không bận thì ở lại chơi
Ta mấy ngày nữa sẽ tới thăm nàng
Hôm nay ta ở chợ nghe tin đồn về ngươi
Cô từ trong ví lấy ra tờ hóa đơn
Ở trong phòng họp bên trong
Đặt ở trên bàn phía trên
Đứng ở ngoài cửa bên ngoài
Ngồi ở dưới gốc cây phía dưới
Chôn ở dưới đất bên dưới
Giấu ở sau lưng phía sau
Nằm ở giữa trung tâm chính giữa
Câu hỏi này bị do cậu trả lời - 由
Đã khóa sổ, nếu sai thì không sửa được (dịch non chữ 一旦)
Làm vậy để giảm chi phí (dịch non chữ 以便 = để tiện)
Đổi quy trình nên tăng năng suất (dịch non chữ 从而 = nhờ đó mà)
Trừ phi cậu xin lỗi, mới tha thứ nếu không chia tay (ghép sai 除非...否则)95.
```

#### 09. Định ngữ ngược, Trợ từ Đích / Địa / Đắc & Bổ ngữ xu hướng Trung (25 mẫu)

```text
Trần Quốc hoàng hậu
Lan Lăng vương phi
Đại Tư Mã phủ
Tuyên Thất điện
Ninh Tĩnh lộ (đặt ngược danh từ chung ra sau)
Người gia đích hoa quả
Muốn nứt ra đích biểu tình
Phi thường nghiêm túc đích thái độ
Anh ấy thương tâm địa khóc rống
Chậm rãi địa bước vào phòng
Tức giận đắc nói không ra lời
Mệt mỏi đắc ngã lăn ra giường
Ăn liễu cơm chiều liền đi
Nhìn trứ bóng lưng nàng rời đi
Ta là đang nói về âm thanh a
Không cần rất sinh khí nha
Khóc đứng lên - 哭起来
Cười đứng lên - 笑起来
Mưa đứng lên - 下起雨来
Đánh nhau đứng lên - 打起来
Thảo luận đứng lên - 讨论起来
Nóng đứng lên - 热起来
Nói đi xuống - 说下去
Nghe đi xuống - 听下去
Kiên trì đi xuống - 坚持下去3.
```

#### 10. Hậu tố chắp dính Hàn – Nhật & Định ngữ phân nhánh trái SOV (25 mẫu)

```text
Mang tính cơ bản
Mang tính tất yếu
Mang tính hệ thống
Mang tính khả thi
Mang tính minh họa
Mang tính bắt buộc
Mang tính khuyến nghị
Mang tính chuyển hóa cao
Mang tính khách quan
Mang tính tiêu cực
Đi đến việc hoàn thành - 끝내게 되었다
Đi đến việc quyết định nghỉ làm - 하게 되다
Trở nên được mở ra - 열리게 되다
Có việc đã từng đi Nhật - 간 적이 있다
Nhận được sự chú mục từ công chúng
Nhận được sự tôn kính từ học trò
Nhận được sự khen ngợi từ cấp trên
Bị gánh chịu sự đe dọa từ đối thủ
Bị trở thành giam giữ trong phòng
Sự thật rằng anh ấy đã từ chức - ...라는 사실
Trong trường hợp của việc trời mưa - ...의 경우에는
Thông qua việc phân tích số liệu - ...을 통해서
Về phía của chúng tôi thì thấy rằng
Cuốn sách mà hôm qua ở hiệu sách cạnh ga tàu tôi đã mua rất hay (định ngữ dài trước danh từ)
Do vì nguyên nhân tuyết rơi dày nên chuyến bay bị hoãn mất rồi (dồn vị ngữ cuối câu)65.
```

### 3. Mười hai bộ lọc regex

```text
RX01  Mở bài đóng khung:        (?i)\b(?:trong\s+bối\s+cảnh|trong\s+kỷ\s+nguyên|giữa\s+làn\s+sóng)\b
RX02  Động từ vĩ mô:            (?i)\b(?:khai\s+phá|mở\s+khóa|kiến\s+tạo|nâng\s+tầm|tái\s+định\s+hình)\b
RX03  Ẩn dụ và tính từ sáo:     (?i)\b(?:bức\s+tranh\s+toàn\s+cảnh|tấm\s+thảm\s+đa\s+sắc|ngọn\s+hải\s+đăng)\b
RX04  Đối xứng và đuôi phân từ: (?i)(?:không\s+chỉ\s+[^.,;]+?\s+mà\s+còn|,\s*qua\s+đó\s+khẳng\s+định)\b
RX05  Gạch ngang dài:           \s*—\s*
RX06  Một cách + tính từ:       (?i)\bmột\s+cách\s+[a-zà-ỹđ]+(?:\s+[a-zà-ỹđ]+)?\b
RX07  Danh từ hóa:              (?i)\b(?:sự|việc|tính|cuộc)\s+[a-zà-ỹđ]+(?:\s+[a-zà-ỹđ]+)?\s+của\b
RX08  Bị động Tây hóa:          (?i)\b(?:bị|được)\s+[a-zà-ỹđ]+(?:\s+[a-zà-ỹđ]+){0,3}\s+bởi\b
RX09  Chủ ngữ giả:              (?i)\b(?:nó\s+là\s+[a-zà-ỹđ]+\s+để|người\s+mà|cái\s+mà)\b
RX10  Thành ngữ dịch từng chữ:  (?i)\b(?:làm\s+có\s+ý\s+nghĩa|ở\s+cuối\s+ngày|một\s+miếng\s+bánh)\b
RX11  Hán – Việt lậm convert:   (?i)\b(?:biểu\s+tình\s+cứng\s+ngắc|tiểu\s+tâm\s+dực\s+dực|tổ\s+hạng\s+mục)\b
RX12  Cú pháp Trung Hoa:        (?i)\b(?:đem\s+[^.,;]{2,35}\s+(?:giao|đưa|làm)|đối\s+với\s+[^.,;]+\s+mà\s+nói|bị\s+do)\b
```

### 4. Cách dùng

Quét tệp sau khi viết bằng `python scripts/vi_scanner.py scan TEP.md --json`. Đối chiếu mã `G` với rule tương ứng trong [rule-catalog.md](rule-catalog.md). Mẫu chưa có rule phải đưa vào danh sách rà thủ công.
