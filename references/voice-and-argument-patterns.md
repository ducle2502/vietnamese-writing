# Mẫu giọng văn chức năng và kỷ luật lập luận từ thực tế (`DHDNA` & `Stylometry`)

Các nguyên tắc cấu trúc câu, đặt tiêu đề, dẫn số liệu và khóa ranh giới bằng chứng dưới đây đúc rút từ phân tích nhịp câu (`stylometry`) cùng khung lập luận `DHDNA v2.0`. Bộ tiêu chuẩn này phục vụ báo cáo quản trị, kiểm toán, giám sát dự án, giải trình kỹ thuật và bài phân tích chuyên môn.

## 1. Bốn kiểu giọng văn chính và một nhãn dự phòng

Tùy vai trò của đơn vị phát hành và quyết định mà người đọc cần đưa ra, hãy chọn một trong bốn kiểu giọng văn dưới đây. Lệnh `python scripts/vi_scanner.py profile` trong [scripts/vi_scanner.py](../scripts/vi_scanner.py) tự động tính các chỉ số này trên từng tệp.

| Kiểu giọng văn (`Archetype`) | Người đọc và mục đích chính | Nhịp câu và cấu trúc đoạn chuẩn | Dấu hiệu nhận diện cốt lõi |
| :--- | :--- | :--- | :--- |
| **Quản trị cổng chặn trực diện** (`DIRECT_EXECUTIVE_GATEKEEPER`) | Hội đồng quản trị, Ban kiểm soát, Chủ sở hữu hoặc cấp phê duyệt cuối cùng trước mốc vận hành. | Câu ngắn (15 đến 23 chữ/câu), biên độ nhịp câu rộng (`CV` từ 0,45 đến 0,66), đoạn ngắn dưới 2 câu (1,7 đến 1,9 câu/đoạn). | Mở đoạn bằng kết luận trực diện. Dùng nhãn phân đoạn ngắn kết thúc bằng dấu chấm (*Thực trạng và bằng chứng.*, *Nguyên nhân kiểm soát.*, *Rủi ro và ảnh hưởng.*, *Kiến nghị.*). Khóa chặt điều kiện chặn và thời hạn đếm ngược. |
| **Giám sát đối sánh hai chiều** (`BALANCED_COMPARATIVE_SUPERVISORY`) | Ban chỉ đạo, Ủy ban điều hành hoặc báo cáo phối hợp giám sát độc lập giữa các kỳ. | Câu vừa (20 đến 25 chữ/câu), cân đối giữa vế ghi nhận tiến bộ và vế chỉ ra điểm nghẽn tồn đọng. | Đặt tiêu đề mục dạng câu ghép hai vế đối lập (*Chủ đề: Điểm tiến bộ, nhưng điểm nghẽn cốt lõi vẫn hạn chế kết quả*). Trình bày hộp đối sánh hai cột song hành và tam giác đối chứng đa nguồn. |
| **Bảo đảm kỹ thuật và giải trình cơ chế** (`TECHNICAL_RCA_ASSURANCE`) | Hội đồng công nghệ, nhóm kỹ thuật hoặc văn bản giải trình sự cố, nghiệm thu hệ thống. | Câu ngắn (10 đến 19 chữ/câu), mật độ số liệu và thông số kỹ thuật cao (35 đến 50 con số / 1.000 chữ). | Đi theo ba bước: xác nhận hiện tượng trên nhật ký gốc và bóc tách cơ chế sinh lỗi khỏi triệu chứng. Cuối cùng, chốt rõ điều kiện kiểm tra lại trước mốc mở cổng. |
| **Chuyên khảo thẩm định đa tầng** (`MULTI_READER_ASSURANCE`) | Hồ sơ thẩm định độc lập hoặc báo cáo tổng hợp dài phục vụ nhiều cấp lãnh đạo và chuyên gia. | Kết hợp tóm tắt điều hành cô đọng ở đầu chương với bảng truy vết mã bằng chứng ở phần thân. | Mở đầu bằng bảng phân luồng người đọc theo cấp phê duyệt chiến lược, cấp điều hành và cấp kỹ thuật. Kèm theo bảng định nghĩa nhãn bằng chứng và danh mục điều kiện dừng bắt buộc. |

`CLEAN_GENERAL_VIETNAMESE` là nhãn dự phòng, không phải kiểu thứ năm. Nhãn này dùng khi văn bản mạch lạc và chưa đủ tín hiệu của bốn kiểu trên. Nếu nhịp câu đều hoặc câu quá dài, kết quả trả về nhãn dự phòng kèm cảnh báo `BUREAUCRATIC_OR_MONOTONE_DRAFT`.

`MULTI_READER_ASSURANCE` chỉ được sinh khi có ít nhất `2` tín hiệu phân luồng. Tín hiệu gồm nhãn `[FACT]`, `[CLAIM]`, `[INFERENCE]`, `[GAP]`, `[RISK]`, `[DECISION]`, `[MÂU THUẪN]` hoặc cấu trúc phân cấp người đọc, bảng truy vết bằng chứng.

## 2. Mười hai chiều `DHDNA` dùng khi hiệu chỉnh giọng

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

Khi trình cấp phê duyệt cao nhất, hãy dùng cụm danh từ ngắn từ 3 đến 8 chữ gọi thẳng mảng rủi ro. Trong bảng tóm tắt, có thể đặt câu hỏi trực diện (*Hạ tầng đã sẵn sàng đáp ứng tải thực tế chưa?*, *Dữ liệu chuyển đổi đã đủ điều kiện nghiệm thu chưa?*) rồi chốt ngay trạng thái đạt hay chưa đạt ở câu đầu.

### 3.2. Tiêu đề câu ghép hai vế đối lập (`BALANCED_COMPARATIVE_SUPERVISORY`)

Cách đặt tiêu đề này ghi nhận kết quả bước đầu của đơn vị thực hiện mà không làm mờ rủi ro trọng yếu. Mở vế đầu bằng tên mảng việc và điểm tiến bộ, nối bằng chữ *nhưng* rồi nêu thẳng điểm nghẽn cốt lõi để người đọc nắm trọn kết luận ngay từ mục lục.

### 3.3. Nhãn phân đoạn văn xuôi kết thúc bằng dấu chấm (`.`)

Áp dụng cho đoạn văn độc lập theo khung 5 bước (*Thực trạng và bằng chứng.*, *Yêu cầu cần đạt.*, *Nguyên nhân kiểm soát.*, *Rủi ro và ảnh hưởng.*, *Kiến nghị kiểm toán.*). Đặt nhãn ngắn kết thúc bằng dấu chấm ngay đầu đoạn văn xuôi (không thêm dấu gạch đầu dòng `-` hay số thứ tự) rồi viết tiếp câu chủ đề trên cùng một dòng.

### 3.4. Thứ tự nén nhận định trong ô bảng theo dõi (2 đến 4 mệnh đề ngắn)

Khi viết cột nhận xét tiến độ trong bảng lớn, hãy giữ thứ tự cố định. Mở đầu bằng trạng thái thời hạn (*quá hạn 62 ngày*, *còn 13 ngày đến hạn*, *chưa giao hạn cụ thể*), tiếp theo là độ lùi hạn (*dự kiến lùi 92 ngày*). Cuối cùng, chốt chất lượng đầu ra (*kết quả mới dừng ở hoạt động trung gian, chưa có sản phẩm kiểm chứng*).

## 4. Sáu kỷ luật dẫn số liệu và khóa ranh giới bằng chứng

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
| "Sự cố mất kết nối cổng tích hợp lúc 10:40 gây sập toàn tuyến trong 16 phút do thiếu cơ chế giao dịch phân tán hai pha, khiến 01 giao dịch mở sổ tiết kiệm 9 tỷ đồng bị trừ tiền nhưng chưa sinh hợp đồng." | "Từ 10:40 đến 10:56, cổng tích hợp mất kết nối làm gián đoạn giao dịch trực tuyến trong 16 phút. Do thiếu cơ chế đồng bộ hai chiều, tài khoản khách hàng đã bị trừ 9 tỷ đồng. Hệ thống lõi khi đó vẫn chưa khởi tạo hợp đồng tiền gửi." | "Lỗ hổng đồng bộ giao dịch trên kênh số có thể gây trừ tiền khống của khách hàng. Trong 16 phút ngắt kết nối, khách hàng bị trừ 9 tỷ đồng nhưng hệ thống không sinh sổ tiết kiệm và không tự hoàn tiền. Yêu cầu khóa cổng chuyển đổi cho đến khi nghiệm thu xong cơ chế tự động hoàn trả." |

## 6. Quy trình biên tập đầu vào và hậu kiểm

Tài liệu này gom quy trình xử lý từ vựng, quy trình dịch, khung yêu cầu đầu vào và nhịp hậu kiểm. Mục tiêu là giữ dữ kiện gốc và hạ tầng câu chữ sạch trước khi bàn giao.

### 6.1. Bốn bước xử lý từ vựng AI

1. Xóa biển báo dẫn dắt. Cắt các cụm chỉ báo thông tin sắp xuất hiện. Ví dụ: "Điều quan trọng cần lưu ý là", "Không thể phủ nhận rằng", "Hãy cùng khám phá". Mở câu ngay bằng chủ thể hoặc dữ kiện.
2. Hạ động từ vĩ mô. Đổi động từ khẩu hiệu sang động từ kiểm chứng được. Ví dụ: "mở rộng" thành "phân tích", "xây dựng" thành "lập", "tối ưu hóa" thành "giảm 12% thời gian chờ".
3. Khóa tính từ bằng số liệu. Chỉ giữ tính từ khi nó đi kèm kích thước, tốc độ, chi phí hoặc hiệu suất. Bỏ "đầy đủ", "liền mạch", "đột phá" nếu không có số đo.
4. Thay ẩn dụ và từ nối cứng. Bỏ "tấm thảm đa sắc", "ngọn hải đăng", "bức tranh toàn cảnh". Thay từ nối đầu đoạn bằng mạch ý tự nhiên.

### 6.2. Bốn bước phi ngôn từ hóa khi dịch

1. Đọc hiểu toàn đoạn. Nắm ngữ cảnh, giọng điệu và đơn vị ý nghĩa trước khi chuyển ngữ.
2. Phi ngôn từ hóa. Xóa vỏ từ ngữ và trật tự cú pháp nguồn khỏi trí nhớ ngắn hạn. Giữ lại các đơn vị ý nghĩa.
3. Tái ngôn từ hóa. Viết lại bằng cấu trúc Đề–Thuyết, chuỗi động từ và từ láy tiếng Việt. Không giữ trật tự giới từ, định ngữ hay bị động của bản gốc.
4. Đọc thầm liên tục. Chỗ nào làm chậm nhịp đọc hoặc vấp nghĩa là chỗ còn cấu trúc ngoại lai. Sửa lại trước khi bàn giao.

### 6.3. Khung yêu cầu đầu vào `VEC`

Khung `VEC` khóa bốn thông tin tối thiểu trước khi viết.

| Thành phần | Câu hỏi phải trả lời | Ví dụ |
| :--- | :--- | :--- |
| `V` — Vai trò | Ai viết và chịu trách nhiệm nội dung? | Chuyên viên kiểm soát nội bộ viết cho Ban điều hành. |
| `E` — Bằng chứng | Dữ kiện nào bắt buộc phải giữ? | Số liệu, ngày tháng, điều kiện, tên nguồn. |
| `C` — Cấu trúc | Người đọc cần kết luận gì trước? | Kết luận trước, bằng chứng sau, kiến nghị cuối. |

### 6.4. Master Prompt sáu tầng

1. Role. Nêu vai trò chuyên môn cụ thể, không dùng vai trò chung.
2. Context. Nêu sản phẩm, nhóm người đọc hẹp và lợi thế cạnh tranh.
3. Task. Nêu sản phẩm bàn giao, độ dài và định dạng.
4. Anti-AI Constraints. Cấm từ trong [pattern-bank.md](pattern-bank.md), cấm gạch ngang dài và cấu trúc đối lập giả.
5. Examples. Dán 2 đến 3 đoạn mẫu do người viết tự viết để nạp nhịp điệu.
6. Output Format. Chốt kiểu trình bày, đơn vị số liệu và nhãn trạng thái.

### 6.5. Ba tầng kiểm soát

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
3. Kỷ luật bằng chứng. Chưa có bằng chứng thì chưa được xem là hoàn thành.
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
[GAP]       Khoảng trống dữ liệu hoặc hồ sơ chưa thu thập.
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

Mười tám điều kiện dừng bắt buộc `SL01–SL18`:

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
SL11  Chưa khóa phạm vi triển khai.
SL12  Thiếu kế hoạch quay lui đã diễn tập.
SL13  Lỗ hổng phân quyền đặc quyền hoặc mật khẩu trống.
SL14  Chưa tách nhiệm vụ tạo lập và phê duyệt.
SL15  Thiếu biên bản xác nhận của đơn vị nghiệp vụ.
SL16  Thiếu chứng từ gốc cho giao dịch trọng yếu.
SL17  Công cụ đối soát chưa được kiểm định.
SL18  Chưa đủ bộ hồ sơ tối thiểu trước mốc chuyển đổi.
```

Hai mươi hai yêu cầu bằng chứng `ER01–ER22`:

```text
ER01  Danh mục phạm vi và mốc khóa dữ liệu.
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
4. Phân tích nguyên nhân kiểm soát hoặc khoảng trống.
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

Giới hạn sử dụng: sổ tay này mô tả lựa chọn văn bản, không phải thước đo phẩm chất cá nhân. Khi chuyển sang thể loại khác, cần hiệu chỉnh lại nhịp câu và mật độ thuật ngữ.
