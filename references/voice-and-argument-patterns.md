# Mẫu giọng văn chức năng và nguyên tắc lập luận từ thực tế (`DHDNA` & `Stylometry`)

Các nguyên tắc cấu trúc câu, đặt tiêu đề, dẫn số liệu và xác định ranh giới bằng chứng dưới đây đúc rút từ phân tích nhịp câu (`stylometry`) cùng khung lập luận `DHDNA v2.0`. Bộ tiêu chuẩn này phục vụ báo cáo quản trị, kiểm toán, giám sát dự án, giải trình kỹ thuật và bài phân tích chuyên môn.

## 1. 4 kiểu giọng văn chính và 1 nhãn mặc định

Tùy vai trò của đơn vị phát hành và quyết định mà người đọc cần đưa ra, hãy chọn một trong bốn kiểu giọng văn dưới đây. Lệnh `python scripts/vi_scanner.py profile` trong [scripts/vi_scanner.py](../scripts/vi_scanner.py) tự động tính các chỉ số này trên từng tệp.

| Kiểu giọng văn (`Archetype`) | Người đọc và mục đích chính | Nhịp câu và cấu trúc đoạn chuẩn | Dấu hiệu nhận diện cốt lõi |
| :--- | :--- | :--- | :--- |
| **Quản trị cổng chặn trực diện** (`DIRECT_EXECUTIVE_GATEKEEPER`) | Hội đồng quản trị, Ban kiểm soát, Chủ sở hữu hoặc cấp phê duyệt cuối cùng trước mốc vận hành. | Câu ngắn (15 đến 23 chữ/câu), biên độ nhịp câu rộng (`CV` từ 0,45 đến 0,66), đoạn ngắn dưới 2 câu (1,7 đến 1,9 câu/đoạn). | Mở đoạn bằng kết luận trực diện. Dùng nhãn phân đoạn ngắn kết thúc bằng dấu chấm (*Thực trạng và bằng chứng.*, *Nguyên nhân kiểm soát.*, *Rủi ro và ảnh hưởng.*, *Kiến nghị.*). Xác định rõ điều kiện chặn và thời hạn đếm ngược. |
| **Giám sát đối sánh hai chiều** (`BALANCED_COMPARATIVE_SUPERVISORY`) | Ban chỉ đạo, Ủy ban điều hành hoặc báo cáo phối hợp giám sát độc lập giữa các kỳ. | Câu vừa (20 đến 25 chữ/câu), cân đối giữa vế ghi nhận tiến bộ và vế chỉ ra điểm nghẽn tồn đọng. | Đặt tiêu đề mục dạng câu ghép hai vế đối lập (*Chủ đề: Điểm tiến bộ, nhưng điểm nghẽn cốt lõi vẫn hạn chế kết quả*). Trình bày hộp đối sánh hai cột song hành và tam giác đối chứng đa nguồn. |
| **Bảo đảm kỹ thuật và giải trình cơ chế** (`TECHNICAL_RCA_ASSURANCE`) | Hội đồng công nghệ, nhóm kỹ thuật hoặc văn bản giải trình sự cố, nghiệm thu hệ thống. | Câu ngắn (10 đến 19 chữ/câu), mật độ số liệu và thông số kỹ thuật cao (35 đến 50 con số / 1.000 chữ). | Đi theo ba bước: xác nhận hiện tượng trên nhật ký gốc và bóc tách cơ chế sinh lỗi khỏi triệu chứng. Cuối cùng, chốt rõ điều kiện kiểm tra lại trước mốc mở cổng. |
| **Chuyên khảo thẩm định đa tầng** (`MULTI_READER_ASSURANCE`) | Hồ sơ thẩm định độc lập hoặc báo cáo tổng hợp dài phục vụ nhiều cấp lãnh đạo và chuyên gia. | Kết hợp tóm tắt báo cáo cô đọng ở đầu chương với bảng truy vết mã bằng chứng ở phần thân. | Mở đầu bằng bảng phân luồng người đọc theo cấp phê duyệt chiến lược, cấp điều hành và cấp kỹ thuật. Kèm theo bảng định nghĩa nhãn bằng chứng và danh mục điều kiện dừng bắt buộc. |

`CLEAN_GENERAL_VIETNAMESE` là nhãn mặc định, không phải kiểu thứ năm. Nhãn này dùng khi văn bản mạch lạc và chưa đủ tín hiệu của bốn kiểu trên. Nếu nhịp câu đều hoặc câu quá dài, kết quả trả về nhãn mặc định kèm cảnh báo `BUREAUCRATIC_OR_MONOTONE_DRAFT`.

`MULTI_READER_ASSURANCE` chỉ được sinh khi có ít nhất `2` tín hiệu phân luồng. Tín hiệu gồm nhãn `[FACT]`, `[CLAIM]`, `[INFERENCE]`, `[GAP]`, `[RISK]`, `[DECISION]`, `[MÂU THUẪN]` hoặc cấu trúc phân cấp người đọc, bảng truy vết bằng chứng.

## 2. 12 chiều `DHDNA` dùng khi hiệu chỉnh giọng

| Mã | Chiều | Câu hỏi kiểm tra trên bản thảo |
| :---: | :--- | :--- |
| `D1` | Phân tích | Kết luận có đi từ hiện tượng xuống nguyên nhân kiểm soát không? |
| `D2` | Sáng tạo | Cách tổ chức thông tin có giúp người đọc quyết định nhanh hơn không? |
| `D3` | Cảm xúc | Có từ ngữ biểu cảm cá nhân lấn át dữ kiện không? |
| `D4` | Chính xác ngôn ngữ | Thuật ngữ, số liệu và đơn vị có nhất quán không? |
| `D5` | Đạo đức | Bản thảo có bảo vệ quyền lợi khách hàng và tính toàn vẹn số liệu không? |
| `D6` | Tư duy chiến lược | Kiến nghị có điều kiện, phương án dự phòng và người chịu trách nhiệm không? |
| `D7` | Truy vết lịch sử | Có đối chiếu cam kết và kết quả các kỳ trước không? |
| `D8` | Thích ứng người đọc | Mỗi cấp người đọc có phần tóm tắt phù hợp không? |
| `D9` | Chuyên môn | Thuật ngữ chuyên ngành có đúng và đủ sâu không? |
| `D10` | Trực giác | Có nhận định nào dựa trên cảm tính thay vì dữ liệu không? |
| `D11` | Thời gian | Mốc quá hạn, đếm ngược và hạn xử lý có cụ thể không? |
| `D12` | Tự giới hạn | Bản thảo có nêu rõ giới hạn bằng chứng và điều kiện đổi kết luận không? |

## 3. Kỹ thuật đặt tiêu đề và mở đoạn theo từng kiểu giọng

### 3.1. Tiêu đề cụm danh từ ngắn hoặc câu hỏi điều hành trực diện (`DIRECT_EXECUTIVE_GATEKEEPER`)

Khi trình cấp phê duyệt cao nhất, hãy dùng cụm danh từ ngắn từ 3 đến 8 chữ gọi rõ mảng rủi ro. Trong bảng tóm tắt, có thể đặt câu hỏi trực diện (*Hạ tầng đã sẵn sàng đáp ứng tải thực tế chưa?*, *Dữ liệu chuyển đổi đã đủ điều kiện nghiệm thu chưa?*) rồi chốt ngay trạng thái đạt hay chưa đạt ở câu đầu.

### 3.2. Tiêu đề câu ghép hai vế đối lập (`BALANCED_COMPARATIVE_SUPERVISORY`)

Cách đặt tiêu đề này ghi nhận kết quả bước đầu của đơn vị thực hiện mà không làm mờ rủi ro trọng yếu. Mở vế đầu bằng tên mảng việc và điểm tiến bộ, nối bằng chữ *nhưng* rồi nêu rõ điểm nghẽn cốt lõi để người đọc nắm trọn kết luận ngay từ mục lục.

### 3.3. Nhãn phân đoạn văn xuôi kết thúc bằng dấu chấm (`.`)

Áp dụng cho đoạn văn độc lập theo khung 5 bước (*Thực trạng và bằng chứng.*, *Yêu cầu cần đạt.*, *Nguyên nhân kiểm soát.*, *Rủi ro và ảnh hưởng.*, *Kiến nghị kiểm toán.*). Đặt nhãn ngắn kết thúc bằng dấu chấm ngay đầu đoạn văn xuôi (không thêm dấu gạch đầu dòng `-` hay số thứ tự) rồi viết tiếp câu chủ đề trên cùng một dòng.

### 3.4. Thứ tự tóm tắt nhận định trong ô bảng theo dõi (2 đến 4 mệnh đề ngắn)

Khi viết cột nhận xét tiến độ trong bảng lớn, hãy giữ thứ tự cố định. Mở đầu bằng trạng thái thời hạn (*quá hạn 62 ngày*, *còn 13 ngày đến hạn*, *chưa giao hạn cụ thể*), tiếp theo là độ lùi hạn (*dự kiến lùi 92 ngày*). Cuối cùng, chốt chất lượng đầu ra (*kết quả mới dừng ở hoạt động trung gian, chưa có sản phẩm kiểm chứng*).

## 4. 6 nguyên tắc dẫn số liệu và xác định ranh giới bằng chứng

Công cụ [scripts/vi_scanner.py](../scripts/vi_scanner.py) tự động rà 6 nguyên tắc này qua quy tắc `VIS-STRUCT-002` và lệnh `profile`:

### 4.1. Ghép cặp `Tử số/Mẫu số (Tỷ lệ %)` khi chốt kết luận

Không viết tỷ lệ phần trăm đứng trơ một mình. Cách viết thiếu mẫu số rất dễ che giấu quy mô mẫu nhỏ. Hãy ghi đủ cả tử số, mẫu số và tỷ lệ, chẳng hạn *Có 138/213 đơn vị gửi báo cáo đánh giá, tương đương 64,8%*.

### 4.2. Tách bạch hoạt động trung gian với đầu ra kiểm chứng được

Họp bàn, gửi công văn nhắc hay hướng dẫn lại chưa phải kết quả hoàn thành. Các hoạt động này chỉ phản ánh tiến độ xử lý trung gian. Chỉ ghi nhận đã đóng lỗi khi đơn vị có biên bản nghiệm thu hoặc kết quả kiểm tra lại thực tế đạt yêu cầu.

### 4.3. Tách tỷ lệ hoàn thành không lỗi khỏi tỷ lệ thực hiện còn vướng mắc

Tuyệt đối không gộp giao dịch còn lỗi vào tỷ lệ hoàn thành chung. Báo cáo kiểm thử phải tách rõ ba nhóm kết quả: hoàn thành không lỗi, thực hiện được nhưng còn vướng thao tác và không thực hiện được.

### 4.4. Không dùng cân đối tổng hợp hoặc bù trừ ròng để kết luận khớp đúng từng dòng

Tổng phát sinh Nợ bằng tổng phát sinh Có không chứng minh dữ liệu khớp ở cấp giao dịch đơn lẻ. Tương tự, tổng chênh lệch ròng bằng 0 do các khoản thừa thiếu tự bù trừ nhau vẫn có thể che khuất lỗi. Khi đối soát dữ liệu tài chính, hãy kiểm tra theo tổng giá trị tuyệt đối của chênh lệch trên từng tài khoản và hợp đồng.

### 4.5. Tam giác đối chứng đa nguồn và kiểm soát trôi mẫu số

Khi nhiều nguồn cùng báo cáo về một sự kiện, hãy đặt các con số cạnh nhau trong cùng một câu để đối chiếu trực tiếp. Kết hợp chạy `python scripts/vi_scanner.py profile` để rà trường `ung_vien_lech_mau_so`, phát hiện sớm chỗ lệch mẫu số giữa các trang hoặc sót tiêu đề từ tệp mẫu kỳ trước (`template_title_mismatch`).

### 4.6. Chuẩn hóa từ tình thái và ranh giới phạm vi đánh giá (`Metacognition`)

Với sự kiện đã xảy ra và có số liệu, dùng động từ khẳng định hoặc phủ định dứt khoát (*mới đạt 48,6%*, *chưa hoàn thành*). Khi nêu hệ quả rủi ro tương lai nếu vận hành sớm, chỉ dùng đúng một từ tình thái *có thể* (*Khách hàng có thể bị tính sai dư nợ*). Không khẳng định tuyệt đối vô căn cứ và không chồng nhiều từ rào đón. Đầu báo cáo luôn nêu rõ nguồn dữ liệu tạm giả định, phạm vi chưa kiểm chứng độc lập và điều kiện thay đổi ý kiến đánh giá.

## 5. Chuyển ngữ từ dữ liệu kỹ thuật và báo cáo tiến độ sang văn phong quản trị

Ba tình huống dưới đây đối chiếu cách chuyển câu chữ từ báo cáo tiến độ hoặc nhật ký kỹ thuật sang giọng văn quản trị. Cả hai phương án viết lại đều bảo toàn 100% số liệu gốc:

| Câu gốc trong báo cáo tiến độ hoặc nhật ký kỹ thuật | Chuyển sang giọng **Giám sát đối sánh hai chiều** (`BALANCED_COMPARATIVE_SUPERVISORY`) | Chuyển sang giọng **Quản trị cổng chặn trực diện** (`DIRECT_EXECUTIVE_GATEKEEPER`) |
| :--- | :--- | :--- |
| "Trong mẫu khảo sát, 84,9% giao dịch được ghi nhận hoàn thành, kể cả các trường hợp còn vướng mắc thao tác; 65/67 phiếu lỗi đã được đánh dấu xử lý xong sau khi hướng dẫn lại trên bảng theo dõi." | "Đợt diễn tập đã thu thập được phản hồi trên diện rộng (điểm cải thiện). Tuy nhiên, tỷ lệ giao dịch hoàn thành không lỗi chỉ đạt 67,5%, còn 17,4% giao dịch vẫn vướng thao tác. Riêng 65/67 phiếu lỗi mới dừng ở bước hướng dẫn lại trên bảng theo dõi, chưa có bằng chứng kiểm tra thực tế." | "Chất lượng vận hành chưa đạt điều kiện nghiệm thu. Nhóm giao dịch còn lỗi hoặc không thực hiện được chiếm tới 32,5%. Cả 65/67 phiếu lỗi báo đóng mới dừng ở bước hướng dẫn trung gian, chưa có kết quả kiểm chứng lại." |
| "Tổng số dư Nợ bằng tổng số dư Có trên bảng tổng hợp cuối ngày. Có 06 giao dịch gốc báo lệch nhưng là 03 cặp bút toán điều chỉnh thủ công bù trừ đúng nhau nên tổng chênh lệch bằng 0." | "Bảng cân đối tổng hợp cuối ngày ghi nhận tổng Nợ khớp tổng Có. Tuy nhiên, số tổng hợp cân bằng nhờ 03 cặp bút toán thủ công tự bù trừ nhau. Kết quả này chưa chứng minh dữ liệu khớp từng dòng nếu chưa đối soát theo tổng giá trị tuyệt đối." | "Rủi ro sai lệch sổ kế toán ở cấp giao dịch đơn lẻ. Quy tắc ghép cặp hiện tại cho phép các khoản lệch tự bù trừ nhau khi tổng Nợ bằng tổng Có. Cơ chế này có thể che khuất sai sót số dư từng khách hàng nếu không đối soát theo giá trị tuyệt đối." |
| "Sự cố mất kết nối cổng tích hợp lúc 10:40 gây sập toàn tuyến trong 16 phút do thiếu cơ chế giao dịch phân tán hai pha, khiến 01 giao dịch mở sổ tiết kiệm 9 tỷ đồng bị trừ tiền nhưng chưa sinh hợp đồng." | "Từ 10:40 đến 10:56, cổng tích hợp mất kết nối làm gián đoạn giao dịch trực tuyến trong 16 phút. Do thiếu cơ chế đồng bộ hai chiều, tài khoản khách hàng đã bị trừ 9 tỷ đồng. Hệ thống lõi khi đó vẫn chưa khởi tạo hợp đồng tiền gửi." | "Lỗ hổng đồng bộ giao dịch trên kênh số có thể gây trừ tiền khống của khách hàng. Trong 16 phút ngắt kết nối, khách hàng bị trừ 9 tỷ đồng nhưng hệ thống không sinh sổ tiết kiệm và không tự hoàn tiền. Yêu cầu tạm dừng bước chuyển đổi cho đến khi nghiệm thu xong cơ chế tự động hoàn trả." |

### Chuyển ngữ thuật ngữ kỹ thuật CNTT sang ngôn ngữ quản trị

| Diễn đạt kỹ thuật | Cách viết cho cấp phê duyệt |
| :--- | :--- |
| `Deadlock bảng dữ liệu, API timeout 502/504 ở tải 100 tps` | Khi tải giao dịch tăng cao, hệ thống bị nghẽn và gián đoạn xử lý trong `[N]` phút. |
| `Thiếu giao dịch phân tán hai pha qua ESB` | Kênh số chưa đồng bộ hoàn trả khi mất kết nối, có thể trừ tiền khách nhưng chưa tạo hợp đồng. |
| `Chưa mask dữ liệu PII trên môi trường thử nghiệm` | Đơn vị dùng dữ liệu khách hàng thật khi thử nghiệm, vi phạm quy định bảo vệ dữ liệu cá nhân. |
| `Chạy khóa sổ cuối ngày chưa đạt, lỗi đối chiếu sổ cái` | Chưa kiểm chứng khóa sổ cuối ngày, số dư giữa sổ chi tiết và sổ cái đang lệch `[X]` đồng. |
| `Kế hoạch quay lui hệ thống chưa được kiểm thử` | Đơn vị chưa diễn tập phương án quay lại hệ thống cũ khi chuyển đổi gặp sự cố. |
| `Tỷ lệ đạt kiểm thử 89% nhưng còn lỗi mức nghiêm trọng 1 và 2` | Kiểm thử người dùng còn `[N]` lỗi nghiêm trọng chưa xử lý nên chưa đủ điều kiện vận hành an toàn. |

## 6. Quy trình biên tập đầu vào và hậu kiểm

Phần này tổng hợp quy trình xử lý từ vựng, quy trình dịch, khung yêu cầu đầu vào và nhịp hậu kiểm để giữ nguyên dữ kiện gốc trước khi bàn giao.

### 6.1. 4 bước xử lý từ vựng AI

1. Xóa biển báo dẫn dắt. Cắt các cụm chỉ báo thông tin sắp xuất hiện. Ví dụ: "Điều quan trọng cần lưu ý là", "Không thể phủ nhận rằng", "Hãy cùng khám phá". Mở câu ngay bằng chủ thể hoặc dữ kiện.
2. Hạ động từ vĩ mô. Đổi động từ khẩu hiệu sang động từ kiểm chứng được. Ví dụ: "mở rộng" thành "phân tích", "xây dựng" thành "lập", "tối ưu hóa" thành "giảm 12% thời gian chờ".
3. Kiểm soát tính từ bằng số liệu. Chỉ giữ tính từ khi nó đi kèm kích thước, tốc độ, chi phí hoặc hiệu suất. Bỏ "đầy đủ", "liền mạch", "đột phá" nếu không có số đo.
4. Thay ẩn dụ và từ nối cứng. Bỏ "tấm thảm đa sắc", "ngọn hải đăng", "bức tranh toàn cảnh". Thay từ nối đầu đoạn bằng mạch ý tự nhiên.

### 6.2. 4 bước phi ngôn từ hóa khi dịch

1. Đọc hiểu toàn đoạn. Nắm ngữ cảnh, giọng điệu và đơn vị ý nghĩa trước khi chuyển ngữ.
2. Phi ngôn từ hóa. Xóa vỏ từ ngữ và trật tự cú pháp nguồn khỏi trí nhớ ngắn hạn. Giữ lại các đơn vị ý nghĩa.
3. Tái ngôn từ hóa. Viết lại bằng cấu trúc Đề–Thuyết, chuỗi động từ và từ láy tiếng Việt. Không giữ trật tự giới từ, định ngữ hay bị động của bản gốc.
4. Đọc thầm liên tục. Chỗ nào làm chậm nhịp đọc hoặc vấp nghĩa là chỗ còn cấu trúc ngoại lai. Sửa lại trước khi bàn giao.

### 6.3. Khung yêu cầu đầu vào `VEC`

Khung `VEC` xác định bốn thông tin tối thiểu trước khi viết.

| Thành phần | Câu hỏi phải trả lời | Ví dụ |
| :--- | :--- | :--- |
| `V` (Vai trò) | Ai viết và chịu trách nhiệm nội dung? | Chuyên viên kiểm soát nội bộ viết cho Ban điều hành. |
| `E` (Bằng chứng) | Dữ kiện nào bắt buộc phải giữ? | Số liệu, ngày tháng, điều kiện, tên nguồn. |
| `C` (Cấu trúc) | Người đọc cần kết luận gì trước? | Kết luận trước, bằng chứng sau, kiến nghị cuối. |

### 6.4. Master Prompt 6 tầng

1. Role. Nêu vai trò chuyên môn cụ thể, không dùng vai trò chung.
2. Context. Nêu sản phẩm, nhóm người đọc hẹp và lợi thế cạnh tranh.
3. Task. Nêu sản phẩm bàn giao, độ dài và định dạng.
4. Anti-AI Constraints. Cấm từ trong [pattern-bank.md](pattern-bank.md), cấm gạch ngang dài và cấu trúc đối lập giả.
5. Examples. Dán 2 đến 3 đoạn mẫu do người viết tự viết để nạp nhịp điệu.
6. Output Format. Chốt kiểu trình bày, đơn vị số liệu và nhãn trạng thái.

### 6.5. 3 tầng kiểm soát

1. Bước đầu vào. Khóa `VEC` và Master Prompt sáu tầng. Buộc gắn nhãn `[CHECK]` ở mọi chỗ thiếu nguồn.
2. Bước trọng tài. Dùng một phiên độc lập đối chiếu 25 cấu trúc AI và 25 cấu trúc dịch thô. Chỉ xuất mã lỗi và hướng sửa trong một dòng.
3. Bước hậu kiểm. Kiểm tra từng số liệu, mở từng đường dẫn, thay ví dụ chung bằng tình huống thật và đọc to để bắt câu giống thông cáo.

### 6.6. Lệnh kiểm tra trước khi bàn giao

```bash
python -B scripts/vi_scanner.py scan TEP.md --json
python -B scripts/vi_scanner.py profile TEP.md --json
python -B scripts/vi_scanner.py verify BAN_GOC.md BAN_SAU_SUA.md
```

`scan` phải có `error_count = 0`. `profile` phải trả đúng một trong năm mã giọng văn. `verify` phải giữ nguyên số liệu, phủ định, điều kiện và mức chắc chắn.

## 7. Sổ tay giọng văn báo cáo quản trị và bảo đảm

Đây là bản tổng hợp theo chức năng, không phải bản sao của một hồ sơ cá nhân. Nội dung chỉ mô tả lựa chọn câu chữ, cấu trúc và cách dẫn bằng chứng trên bề mặt văn bản. Sổ tay không dùng để suy đoán tính cách, năng lực hay động cơ của người viết.

### 7.1. Nguyên tắc chung

1. Kết luận trước. Câu đầu mỗi mục trả lời câu hỏi quan trọng nhất của người đọc.
2. Câu ngắn, ý rõ. Giữ câu văn xuôi trong khoảng `15–23` từ. Câu dài hơn `35` từ phải tách.
3. Nguyên tắc bằng chứng. Chưa có bằng chứng thì chưa được xem là hoàn thành.
4. Cổng điều kiện. Mọi kiến nghị phải nêu điều kiện, mốc thời gian và người chịu trách nhiệm.
5. Nhãn trạng thái. Dùng nhãn cố định cho hoạt động trung gian và đầu ra kiểm chứng.
6. Số liệu có mẫu số. Không nêu tỷ lệ phần trăm đứng một mình.
7. Một ẩn dụ tối đa. Chỉ dùng khi giúp giải thích cơ chế, không dùng để trang trí.
8. Ẩn danh. Không ghi tên đơn vị, dự án, khách hàng hoặc mã định danh nội bộ.

### 7.2. Cấu trúc báo cáo và tiêu đề

Báo cáo chuẩn chia ba phần theo chức năng, không chia theo nguồn dữ liệu.

| Phần | Nội dung | Người đọc chính |
| :--- | :--- | :--- |
| Mở đầu | Phạm vi, căn cứ, giới hạn bằng chứng và kết luận tổng quát. | Cấp phê duyệt |
| Thân bài | Hiện trạng, đối sánh, nguyên nhân gốc và điều kiện kiểm chứng. | Cấp điều hành và chuyên môn |
| Kết luận | Kết luận, kiến nghị, điều kiện dừng và phụ lục truy vết. | Cấp phê duyệt và kiểm soát |

Quy tắc tiêu đề:

- Tiêu đề cấp 1 viết hoa, đánh số La Mã và nêu đúng chức năng phần.
- Tiêu đề cấp 2 là một câu nhận định hoàn chỉnh, có thể dùng dấu hai chấm để tách hai vế.
- Không đặt tiêu đề rỗng kiểu "Kết quả", "Tình hình" hoặc "Một số vấn đề".
- Không dùng Title Case kiểu tiếng Anh cho tiêu đề tiếng Việt.

Khối kết luận `takeaway` đặt cuối mỗi mục. Khối này mở bằng trạng thái bằng chứng, rồi nêu hệ quả vận hành. Hộp `comparison_box` đặt hai cột "Điểm cải thiện" và "Điểm chưa cải thiện" để giữ tính khách quan hai chiều.

### 7.3. Nhịp câu và số liệu

- Câu văn xuôi trung bình `15–23` từ. Đoạn ngắn dưới `2` câu.
- Biên độ nhịp câu `CV` từ `0,45` đến `0,66` cho báo cáo quản trị.
- Số đếm dưới `10` viết hai chữ số cho sự cố, hồ sơ, mẫu và hệ thống: `01` đến `09`.
- Dấu thập phân dùng dấu phẩy. Dấu phân tách hàng nghìn dùng dấu chấm.
- Cặp số liệu luôn ghi `Tử số/Mẫu số (Tỷ lệ %)`.
- Nhãn hoàn thành chỉ dùng khi có đầu ra kiểm chứng.

| Bối cảnh | Độ dài câu mục tiêu | Mật độ số / 1.000 từ | Ghi chú |
| :--- | :---: | :---: | :--- |
| Báo cáo ngắn trình cấp phê duyệt | `15–20` từ | `40–50` | Ưu tiên kết luận và điều kiện dừng. |
| Báo cáo giám sát nhiều kỳ | `20–25` từ | `45–60` | Giữ nhãn đối sánh và truy vết lịch sử. |
| Hồ sơ bảo đảm kỹ thuật | `10–19` từ | `60–85` | Giữ mã lỗi, khung giờ và phép tính. |

### 7.4. Bằng chứng và truy vết

Bảy nhãn bằng chứng dùng thống nhất trong toàn bộ hồ sơ:

```text
[FACT]      Hiện vật hoặc số liệu đã kiểm chứng.
[CLAIM]     Lời tự công bố của đơn vị, chưa kiểm chứng độc lập.
[INFERENCE] Suy luận có căn cứ từ dữ kiện đã nêu.
[GAP]       Phần dữ liệu còn thiếu hoặc hồ sơ chưa thu thập.
[RISK]      Hệ quả tiềm ẩn nếu không xử lý.
[DECISION]  Quyết định hoặc điều kiện do cấp có thẩm quyền ban hành.
[MÂU THUẪN] Hai nguồn hoặc hai trang nêu số liệu khác nhau.
```

Bảng truy vết tối thiểu gồm năm cột.

| Mã | Nhận định | Nhãn | Nguồn hoặc hiện vật | Trạng thái |
| :--- | :--- | :---: | :--- | :--- |
| `E01` | Số liệu hoàn thành | `[FACT]` | Biên bản đối chiếu có chữ ký | Đã kiểm chứng |
| `E02` | Tỷ lệ tham gia | `[CLAIM]` | Báo cáo tự cập nhật của đơn vị | Chưa kiểm chứng |
| `E03` | Nguyên nhân chênh lệch | `[INFERENCE]` | Nhật ký và phép tính đối chiếu | Cần rà lại |

Phân luồng người đọc theo ba cấp: cấp phê duyệt nhận kết luận và điều kiện dừng, cấp điều hành nhận đối sánh và kiến nghị, cấp kỹ thuật nhận mã lỗi và phụ lục. Mỗi cấp chỉ đọc phần phục vụ quyết định của mình.

### 7.5. Cổng và quyết định

Năm cổng chuyển đổi kiểm soát điều kiện trước khi mở vận hành chính thức.

```text
G0  Điều kiện tiên quyết, runbook khóa, mốc đóng băng dữ liệu nguồn.
G1  Sau nạp dữ liệu: bảng kiểm soát tệp, nhật ký nạp và bản ghi bị từ chối.
G2  Sau đối soát: cân đối sổ cái, đối soát từng tầng và chữ ký đồng phê duyệt.
G3  Sau chạy xử lý cuối ngày đầu tiên: chuyển ngày, lỗi tồn đọng và bút toán dồn tích.
G4  Sau kiểm thử vận hành: luồng trọng yếu, kênh số và quyết định mở hoặc quay lui.
```

Bảy lớp đối soát dữ liệu, không dùng tổng ròng để kết luận khớp đúng.

```text
L1  Số lượng bản ghi giữa nguồn và hệ thống đích.
L2  Tổng giá trị tài chính tách theo Nợ, Có và từng loại tiền tệ.
L3  Trường định danh và tham số nghiệp vụ trọng yếu.
L4  Số dư từng tài khoản theo tổng giá trị tuyệt đối của chênh lệch.
L5  Khớp đúng giữa sổ cái và sổ chi tiết.
L6  Biến động dữ liệu trước và sau lần chạy xử lý cuối ngày đầu tiên.
L7  Chọn mẫu phân tầng đủ độ tin cậy thống kê.
```

18 điều kiện dừng bắt buộc `SL01–SL18`:

```text
SL01  Lệch số dư ngoài danh mục đã được phê duyệt.
SL02  Sai lệch số lượng bản ghi chưa giải trình.
SL03  Thiếu chữ ký đồng phê duyệt của kế toán và quản trị rủi ro.
SL04  Sổ cái mất cân đối.
SL05  Bút toán dồn tích sai kỳ hoặc sai lãi suất.
SL06  Sự cố nghiêm trọng chưa đóng.
SL07  Luồng giao dịch trọng yếu chưa kiểm thử đầu cuối.
SL08  Kênh số chưa đạt kiểm thử chịu tải.
SL09  Chưa có kết quả kiểm thử lại của lỗi nghiêm trọng.
SL10  Chưa đối soát dữ liệu chuyển đổi theo đơn vị.
SL11  Chưa xác định phạm vi triển khai.
SL12  Thiếu kế hoạch quay lui đã diễn tập.
SL13  Lỗ hổng phân quyền đặc quyền hoặc mật khẩu trống.
SL14  Chưa tách nhiệm vụ tạo lập và phê duyệt.
SL15  Thiếu biên bản xác nhận của đơn vị nghiệp vụ.
SL16  Thiếu chứng từ gốc cho giao dịch trọng yếu.
SL17  Công cụ đối soát chưa được kiểm định.
SL18  Chưa đủ bộ hồ sơ tối thiểu trước mốc chuyển đổi.
```

22 yêu cầu bằng chứng `ER01–ER22`:

```text
ER01  Danh mục phạm vi và mốc chốt dữ liệu.
ER02  Runbook đã phê duyệt.
ER03  Bảng kiểm soát tệp nạp.
ER04  Nhật ký nạp và bản ghi bị từ chối.
ER05  Báo cáo đối soát từng lớp.
ER06  Chữ ký đồng phê duyệt của kế toán và quản trị rủi ro.
ER07  Nhật ký chạy xử lý cuối ngày.
ER08  Danh mục lỗi nghiêm trọng và trạng thái đóng.
ER09  Biên bản kiểm thử lại có xác nhận của đơn vị.
ER10  Kết quả kiểm thử đầu cuối luồng trọng yếu.
ER11  Báo cáo kiểm thử chịu tải kênh số.
ER12  Kế hoạch quay lui đã diễn tập.
ER13  Danh mục thay đổi cấu hình trước mốc chuyển đổi.
ER14  Báo cáo phân quyền và tách nhiệm vụ.
ER15  Danh mục tài khoản đặc quyền và biện pháp kiểm soát.
ER16  Biên bản đối chiếu dữ liệu theo đơn vị.
ER17  Danh mục chênh lệch và biên bản xử lý.
ER18  Xác nhận của kế toán trưởng.
ER19  Xác nhận của giám đốc quản trị rủi ro.
ER20  Kế hoạch truyền thông và hỗ trợ người dùng.
ER21  Nhật ký sự cố và thời gian khắc phục.
ER22  Báo cáo tổng hợp sau chuyển đổi.
```

Quy trình ra quyết định bốn bước:

1. Công bố tiêu chí nghiệm thu bằng số liệu và danh mục điều kiện bắt buộc.
2. Chỉ ghi nhận hoàn thành khi có đầu ra kiểm chứng.
3. Lập sổ ngoại lệ ghi rõ người chấp nhận rủi ro, biện pháp thay thế và hạn xử lý.
4. Chọn giảm phạm vi, thử nghiệm hẹp hoặc dời mốc nếu điều kiện chặn chưa đạt.

### 7.6. Kiến nghị và đối chiếu

Công thức kiến nghị: `Chỉ ... khi ...`. Ví dụ: "Chỉ đóng lỗi khi có biên bản kiểm thử lại đạt." Câu kiến nghị phải nêu chủ thể, điều kiện và bằng chứng hoàn tất.

Bảng đối chiếu hai chiều tối thiểu gồm bốn cột.

| Tiêu chí | Điểm cải thiện | Điểm chưa cải thiện | Bằng chứng |
| :--- | :--- | :--- | :--- |
| Phạm vi | Mở rộng số kịch bản | Thiếu kịch bản lõi | Danh mục kịch bản |
| Dữ liệu | Giảm chênh lệch tổng | Còn lệch từng tài khoản | Báo cáo đối soát |
| Kiểm soát | Bổ sung chữ ký | Chưa tách nhiệm vụ | Biên bản phê duyệt |

Một nhận định chuẩn đi theo năm bước:

1. Nêu trạng thái bằng một câu kết luận.
2. Dẫn số liệu tử số, mẫu số và tỷ lệ.
3. Chỉ ra yêu cầu chuẩn hoặc điều kiện phải đạt.
4. Phân tích nguyên nhân kiểm soát hoặc phần còn thiếu sót.
5. Chốt hệ quả vận hành và kiến nghị có điều kiện.

### 7.7. Danh mục kiểm tra trước khi bàn giao

- Mỗi mục mở bằng kết luận, không mở bằng bối cảnh chung.
- Câu văn xuôi không vượt `35` từ.
- Tỷ lệ phần trăm phải có tử số và mẫu số.
- Nhận định phải có nhãn bằng chứng hoặc nguồn cụ thể.
- Kiến nghị phải có điều kiện, chủ thể và hạn xử lý.
- Tránh câu ba phải, khen nịnh hoặc khoe phủ sóng truyền thông.
- Loại bỏ lộ trình giả, bảng giải thích điều hiển nhiên hoặc kịch bản hù dọa.
- Tuyệt đối không ghi tên đơn vị, dự án, khách hàng hoặc mã định danh nội bộ.
- Chạy `scan`, `profile` và `verify` trước khi bàn giao.

### 7.8. Bố cục ba lớp, khung 5C và chống nói quá hoặc nói nhẹ

Quy chuẩn dưới đây tổng hợp từ 15 báo cáo kiểm toán và tư vấn giám sát đã duyệt.

| Lớp tài liệu | Dung lượng mục tiêu | Nội dung bắt buộc | Phần cấm đưa ra ngoài |
| :--- | :--- | :--- | :--- |
| Trang đầu | Tối đa 1 trang, `150–350` từ kèm bảng `3–6` dòng | Kết luận câu đầu, mốc quá hạn, giới hạn phạm vi, `3–5` quyết định cần chỉ đạo | Nhật ký theo phút, tên bảng dữ liệu, mã lỗi kỹ thuật, danh sách sự cố lẻ |
| Thân bài | `2.000–4.000` từ, mỗi đoạn dưới `2` câu | Tác động quy đổi sang tiền, khách hàng, dịch vụ hoặc tuân thủ | Bảng lặp số liệu, chép nguyên văn báo cáo đơn vị, mô tả kỹ thuật thừa |
| Phụ lục | Đánh số `Phụ lục 1`, `Phụ lục 2`, `Phụ lục 3` | Chi tiết đủ đối chiếu hai chiều với từng nhận định thân bài | Kết luận mới không có ở thân bài, ảnh thừa, nhật ký thô hàng nghìn dòng |
| Giấy tờ làm việc | Lưu nội bộ, không gửi kèm báo cáo mặc định | Bằng chứng gốc kèm `SHA256`, biến thể tên đơn vị, biên bản soát xét | Mã theo dõi nội bộ (`EV-xx`, `WP-xx`, `CL-xx`, `GAP-xx`) |

Phát hiện kiểm toán trình bày theo khung `5C` rút gọn theo từng cấp đọc:
- Trang đầu chỉ giữ ba mảnh trên một dòng bảng: tiêu đề dẫn bằng Hệ quả (dưới `12` từ), Hiện trạng kèm mức xác minh và Quyết định cần chỉ đạo.
- Thân bài nêu ba thông tin phân loại (Hạng rủi ro, sáu mức bằng chứng kèm `not_measured` khi thiếu dữ liệu và năm màu giám sát). Mỗi phát hiện đi đủ Tiêu chí, Hiện trạng, Nguyên nhân, Hệ quả, Kiến nghị và Ý kiến Đơn vị.
- Mẫu phi thống kê nêu đủ năm thông số: quần thể, cỡ mẫu, số lỗi, tỷ lệ mẫu và câu không ngoại suy.
- Nguyên nhân gốc truy vấn 5 Whys tới bốn nhóm kiểm soát (thiết kế kiểm soát, trống đầu mối, thiếu đào tạo hoặc quá tải), không quy kết động cơ cá nhân.
- Bảng kiến nghị tách khắc phục ngay khỏi ngăn tái diễn với bốn cột: Kết quả cần đạt, Bằng chứng đóng, Một chức danh chủ trì và Ngày lịch `dd/mm/yyyy`.

Trích dẫn văn bản phải ghi rõ chủ đề ngay trong câu (*"theo Thông báo về tổ chức đào tạo ngày..."*), giữ đủ kính ngữ `Ông` hoặc `Bà` trước tên riêng và tránh viết tắt dễ nhầm. Trước khi phát hành, đối chiếu hai chiều số liệu, quét `audit_report` đạt `0` lỗi và soát bản PDF bằng mắt về phông chữ, tràn lề, thứ tự ưu tiên từ cao xuống thấp.

| Tình huống | Nói quá hoặc tuyệt đối (Cấm) | Nói nhẹ hoặc né tránh (Cấm) | Diễn đạt chuẩn xác |
| :--- | :--- | :--- | :--- |
| Đối chiếu pháp luật | "Quy định hiện đã lỗi thời, hết hiệu lực hoặc trái pháp luật." | "Nội dung quy định cơ bản vẫn phù hợp thực tế vận hành." | Quy định chưa cập nhật theo văn bản hiệu lực từ `[dd/mm]`, chưa khớp Khoản, Điều liên quan. |
| Không thấy hồ sơ | "Đơn vị bỏ sót hoàn toàn và không thực hiện kiểm thử." | "Hồ sơ đang trong quá trình hoàn thiện thủ tục ký duyệt." | Đơn vị chưa quy định nội dung này, hoặc đến `[dd/mm]` tổ kiểm toán chưa tìm thấy hồ sơ chứng minh. |
| Phạm vi kiểm tra | "Đối chiếu và đáp ứng 100% toàn bộ tiêu chí pháp luật." | "Cơ bản bám sát các yêu cầu trọng tâm của quy định." | Đã đối chiếu `[A]/[B]` tiêu chí thuộc phạm vi kỳ kiểm toán. Tỷ lệ đạt chỉ phản ánh tập tiêu chí đã chọn. |
| Quá hạn đóng lỗi | "Đơn vị trì trệ, thiếu trách nhiệm làm dự án thất bại." | "Nhiệm vụ đang tích cực phối hợp, dự kiến sớm hoàn tất." | Nhiệm vụ quá hạn `[N]` ngày. Cập nhật mới dừng ở bước trình phê duyệt, chưa có văn bản ban hành kiểm chứng. |
| Hai nguồn lệch nhau | "Bộ phận dự án cố ý làm sai lệch số liệu báo cáo." | "Số liệu chênh nhẹ do thời điểm tổng hợp khác nhau." | Hai nguồn cùng kỳ chốt ghi `[A]` và `[B]`. Khi chưa giải trình nguyên nhân lệch, chưa đủ căn cứ kết luận. |
| Còn lỗi chặn | "Hệ thống chắc chắn sẽ sập khi đưa vào vận hành thật." | "Tiến độ đạt 89%, cơ bản sẵn sàng, chỉ còn vài lưu ý nhỏ." | Kiểm thử đạt `[X]%` nhưng còn `[N]` lỗi nghiêm trọng và chưa đối soát sổ cái. Hệ thống chưa đủ điều kiện vận hành. |
| Sát mốc vận hành | "Hệ thống hoàn toàn không thể đưa vào vận hành." | "Hệ thống cơ bản đáp ứng kế hoạch, tiếp tục theo dõi thêm." | Đến `[dd/mm]`, chưa đủ cơ sở xác nhận sẵn sàng. Nếu chưa xong điều kiện chặn trước `[dd/mm]`, cần dời mốc. |
| Đơn vị tự báo cáo | "Toàn hàng đã hoàn tất 90% khối lượng chuyển đổi." | "Các đơn vị phản hồi nhìn chung đã sẵn sàng triển khai." | Theo số liệu đơn vị gửi, tỷ lệ đạt `[X]%`. Dữ liệu này chưa đối soát nhật ký hệ thống hay biên bản gốc. |
| Tổng khớp bù trừ | "Dữ liệu chuyển đổi khớp chính xác 100% từng dòng." | "Chênh lệch nhỏ không ảnh hưởng tới tổng số dư cuối ngày." | Tổng Nợ khớp tổng Có nhờ các khoản lệch tự bù trừ nhau. Bảng tổng hợp chưa chứng minh khớp từng tài khoản. |

Chuẩn định lượng thực đo trên thân bài báo cáo kiểm toán: văn xuôi `2.000–4.000` từ, dưới `2,0` câu mỗi đoạn và `dai_cau_tb` từ `15–23` từ. Giữ biên độ nhịp câu `CV` trong khoảng `0,45–0,65`, `MATTR-50` đạt `0,82–0,88`, mật độ số `40–90` trên `1.000` từ và thuật ngữ ngoại tối đa `20` từ trên `1.000` từ.

### 7.9. Quy tắc viết cột ghi chú bảng kiểm đánh giá (`Có / Một phần / Chưa có`)

Cột ghi chú trả lời một câu hỏi: **vì sao dòng này được chấm trạng thái đó**. Ghi chú không kể lại quy trình, không liệt kê bằng chứng và không thay thế cột trạng thái.

1. Viết đúng **một câu duy nhất**, tối đa `35` từ, viết hoa chữ đầu và kết thúc bằng dấu chấm.
2. Đi thẳng vào lý do, không mở bằng `"Có vì"`, `"Một phần vì"` hay `"Chưa có vì"`.
3. Nêu phần đáp ứng với trạng thái Có. Nêu phần có cùng phần chưa tìm thấy với trạng thái Một phần, và nêu thành phần chưa tìm thấy với trạng thái Chưa có.
4. Không đưa mã bằng chứng, số ô, tên trường kỹ thuật, tên tệp hay đường dẫn vào cột ghi chú.
5. Không khẳng định tuyệt đối `"không có"` hoặc `"thiếu"` khi chưa đọc toàn bộ hồ sơ. Thay bằng `"chưa tìm thấy"`.
6. Chỉ giữ số đếm, ngày tháng hay trạng thái chi tiết khi là căn cứ trực tiếp cho kết luận.
7. Không gọi chênh lệch số liệu là `"mâu thuẫn"`. Chỉ nêu `"chưa tìm thấy"`, `"khác phạm vi"` hoặc `"cần xác nhận"`.
8. Ưu tiên phạm vi theo kỳ đánh giá. Tài liệu nhắc nội dung kỳ đang xét vẫn giữ trong phạm vi dù nhãn ngày bị ghi lệch.
9. Chỉ ghi điều đọc được trong tệp, không suy diễn ý định hay quy kết động cơ.
10. Giữ câu tự nhiên, chủ thể rõ, động từ trực tiếp, tránh danh hóa và rào đón.

| Trạng thái | Dạng ghi chú | Ví dụ chuẩn |
| :--- | :--- | :--- |
| `Có` | Nêu thành phần bắt buộc đã có | "Sổ rủi ro có danh sách vấn đề mở, người phụ trách và hạn." |
| `Một phần` | Nêu phần có và phần chưa tìm thấy | "Có mốc chuẩn bị nhưng chưa tìm thấy lịch theo giờ trong ngày diễn tập." |
| `Chưa có` | Nêu thành phần chưa tìm thấy | "Chưa tìm thấy bằng chứng kiểm tra lại hoặc đóng lỗi." |

Lỗi cần tránh: viết `"Thiếu tài liệu X"` hoặc `"Không có bằng chứng"` khi chưa đọc hết hồ sơ. Không chèn mã bằng chứng hoặc tên trường vào ghi chú, không viết hai đến ba câu và không gọi lệch số liệu chưa rõ phạm vi là `"mâu thuẫn"`.

### 7.10. Biên tập chọn lọc báo cáo giám sát và sách thực hành (`K1–K8`, `G1–G13`)

Khi biên tập báo cáo giám sát kiểm toán (`K1–K8`) và sách thực hành kỹ thuật (`G1–G13`), cần rà kỹ các lỗi thường lọt máy quét tự động dưới đây.

Mở rộng từ rút gọn và đặt đúng chủ thể (`K1`, `K3`, `K4`). Hãy đổi động từ sổ ghi chú sang ngữ pháp đầy đủ ("rà" thành rà soát, "trình duyệt" dạng động từ thành trình phê duyệt, "duyệt" thành thông qua hoặc phê duyệt). Tương tự, đổi "chốt" thành xác định hoặc thống nhất và "vướng" thành vướng mắc. Đưa người hoặc đơn vị chịu trách nhiệm làm chủ ngữ thay cho văn bản hay đầu việc vô tri ("Báo cáo lưu ý...", "đầu việc tự ghi...").

Giữ `CV >= 0,40` bằng câu ngắn đủ chủ–vị (`K2`). Xen kẽ câu `7–10` từ có đủ chủ ngữ và vị ngữ với câu dữ kiện `22–31` từ. Tuyệt đối không chặt câu thành đoạn `4–6` từ cụt chủ ngữ.

Tách thẩm định pháp lý, kiểm bản ghép và hậu kiểm (`K5–K8`). Giữ nguyên mức độ chắc chắn gốc khi sửa câu. Gắn cờ `NEEDS_AUTHOR_DECISION` nếu đổi chữ có nguy cơ làm lệch nghĩa pháp lý hoặc gặp mã viết tắt nội bộ thiếu tên đầy đủ. Quét giải nghĩa chữ viết tắt ngay ở lần xuất hiện đầu tiên trên bản ghép hoàn chỉnh.

Giữ ngữ cảnh đọc lướt và rà ảnh sau biên tập (`K7`, `K8`): ghi đầy đủ tên văn bản quy phạm, đơn vị trọng yếu tài chính và ranh giới thẩm quyền ba tuyến phòng thủ. Kiểm tra chữ tiếng Việt trong ảnh PNG (`matplotlib`, `Pillow`) cùng phân trang PDF sau khi sửa. Lưu ý lệnh `verify` chỉ xuất cảnh báo đối chiếu cực tính khi chuyển từ vựng phủ định ("trái", "sai", "vướng", "thiếu") sang "chưa" hoặc "không".

Tránh đếm số listicle và đồng bộ sách thực hành (`G1–G13`): bỏ số đếm tùy ý trên tiêu đề và không thay máy móc bằng "một số", "những", "các". Chỉ giữ con số khi gắn với giới hạn thật của công cụ hoặc khung cấu trúc cố định. Giữ song hành ngữ pháp trong danh sách, bỏ văn điện tín, đổi cấu trúc mở và kết giữa các phần. Đồng bộ thuật ngữ xuyên suốt bìa, tiêu đề và thân bài, đồng thời đưa ví dụ đầu vào và đầu ra thật cho mọi câu lệnh hoặc `prompt`.

### 7.11. Vòng đọc lạnh bằng `subagent` theo vai người đọc

Đạt `0` lỗi trên `vi_scanner.py` mới là Bước 1 về hình thức. Với tài liệu từ `300` từ trở lên, hoặc bất kỳ văn bản `audit_report`, `legal` hay tài liệu gửi lãnh đạo, đối tác, Agent bắt buộc chạy Bước 2. Miễn bước này cho hội thoại hoặc email ngắn dưới `150` từ.

Ở Bước 2, Agent mở song song `2` đến `3` `subagent` ở ngữ cảnh mới, chỉ cấp bản thảo hoàn chỉnh và vai người đọc. Không gửi lịch sử chỉnh sửa hay kết quả quét để tránh thiên lệch xác nhận. Mỗi vai chấm bản thảo trên `4` trục dưới đây:

| Trục đánh giá | Câu hỏi kiểm tra bắt buộc |
| :--- | :--- |
| Tự nhiên ngôn ngữ | Đọc thành tiếng có chỗ nào khựng, dịch ngầm, rập khuôn hay lẫn khẩu ngữ sổ ghi chú không? |
| Khả năng hiểu nhanh | Đọc lướt 30 giây có thấy ngay kết luận, nghĩa viết tắt và hành động tiếp theo không? |
| Tính nhất quán | Số liệu, mẫu số, thuật ngữ, đơn vị và xưng hô có khớp nhau giữa tiêu đề, thân bài, bảng và phụ lục không? |
| Không thể hiểu sai | Có câu nào hiểu được theo hai nghĩa, lệch thẩm quyền, rơi điều kiện hay khẳng định vượt bằng chứng không? |

Chọn `2` đến `3` vai phù hợp theo thể loại từ bảng dưới đây:

| Nhóm văn bản | Vai `subagent` đọc lạnh khuyến nghị |
| :--- | :--- |
| `audit_report` | Lãnh đạo phê duyệt đọc 30 giây, Pháp chế hoặc đơn vị bị kiểm tra soi kẽ hở và Biên tập viên đọc thành tiếng. |
| `general` và tài liệu kỹ thuật | Người mới làm theo hướng dẫn, Chuyên gia nghiệp vụ rà tính chính xác và Biên tập viên đọc thành tiếng. |
| `legal` | Pháp chế bên đối tác tìm câu hai nghĩa và Người trực tiếp thực thi nghĩa vụ theo văn bản. |
| `academic` | Phản biện cùng ngành soi phạm vi chứng cứ và Độc giả ngoài chuyên ngành hẹp kiểm tra độ rõ thuật ngữ. |
| `translation` | Người đọc tiếng Việt chưa từng xem bản gốc và Chuyên gia ngành đối chiếu thuật ngữ chuyên môn. |
| `marketing` và `social_media` | Khách hàng mục tiêu đọc lướt trên điện thoại và Người kiểm tra cam kết số liệu thực tế. |

Dùng nguyên khuôn giao việc dưới đây cho từng `subagent`, thay phần trong ngoặc vuông bằng vai và bản thảo cụ thể:

```text
Bạn đóng vai [TÊN VAI NGƯỜI ĐỌC]. Chỉ đọc bản thảo dưới đây như một tài liệu độc lập, không suy đoán bối cảnh ngoài văn bản.
Đánh giá trên 4 trục: (1) Tự nhiên ngôn ngữ khi đọc thành tiếng, (2) Khả năng hiểu nhanh trong 30 giây, (3) Tính nhất quán số liệu và thuật ngữ, (4) Điểm có thể bị hiểu sai hoặc lệch thẩm quyền.
Cấm khen xã giao hay nhận xét chung chung. Chỉ trả về bảng gồm 5 cột: Mức độ (BLOCKER hoặc MINOR) | Vị trí | Trích dẫn nguyên văn | Trục lỗi | Cách sửa đề xuất.
Nếu không có lỗi đáng kể, ghi đúng một dòng: KHÔNG CÓ BLOCKER.
```

Agent chính xử lý triệt để mọi `BLOCKER`, sau đó chạy lại `scan` và `verify` trước khi bàn giao bản cuối. Nếu công cụ đang chạy không hỗ trợ `subagent`, tự rà tuần tự từng vai theo đúng `4` trục trên.

Giới hạn sử dụng: sổ tay này mô tả lựa chọn văn bản, không phải thước đo phẩm chất cá nhân. Khi chuyển sang thể loại khác, cần hiệu chỉnh lại nhịp câu và mật độ thuật ngữ.
