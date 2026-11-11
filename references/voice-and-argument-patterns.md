# Mẫu giọng văn chức năng và kỷ luật lập luận từ thực tế (`DHDNA` & `Stylometry`)

Các nguyên tắc cấu trúc câu, đặt tiêu đề, dẫn số liệu và khóa ranh giới bằng chứng dưới đây đúc rút từ phân tích nhịp câu (`stylometry`) cùng khung lập luận `DHDNA v2.0`. Bộ tiêu chuẩn này phục vụ báo cáo quản trị, kiểm toán, giám sát dự án, giải trình kỹ thuật và bài phân tích chuyên môn.

## 1. Bốn kiểu giọng văn chức năng theo mục đích trình duyệt

Tùy vai trò của đơn vị phát hành và quyết định mà người đọc cần đưa ra, hãy chọn một trong bốn kiểu giọng văn dưới đây. Lệnh `python scripts/vi_scanner.py profile` trong [scripts/vi_scanner.py](../scripts/vi_scanner.py) tự động tính các chỉ số này trên từng tệp.

| Kiểu giọng văn (`Archetype`) | Người đọc và mục đích chính | Nhịp câu và cấu trúc đoạn chuẩn | Dấu hiệu nhận diện cốt lõi |
| :--- | :--- | :--- | :--- |
| **Quản trị cổng chặn trực diện** (`DIRECT_EXECUTIVE_GATEKEEPER`) | Hội đồng quản trị, Ban kiểm soát, Chủ sở hữu hoặc cấp phê duyệt cuối cùng trước mốc vận hành. | Câu ngắn (15 đến 23 chữ/câu), biên độ nhịp câu rộng (`CV` từ 0,45 đến 0,66), đoạn ngắn dưới 2 câu (1,7 đến 1,9 câu/đoạn). | Mở đoạn bằng kết luận trực diện. Dùng nhãn phân đoạn ngắn kết thúc bằng dấu chấm (*Thực trạng và bằng chứng.*, *Nguyên nhân kiểm soát.*, *Rủi ro và ảnh hưởng.*, *Kiến nghị.*). Khóa chặt điều kiện chặn và thời hạn đếm ngược. |
| **Giám sát đối sánh hai chiều** (`BALANCED_COMPARATIVE_SUPERVISORY`) | Ban chỉ đạo, Ủy ban điều hành hoặc báo cáo phối hợp giám sát độc lập giữa các kỳ. | Câu vừa (20 đến 25 chữ/câu), cân đối giữa vế ghi nhận tiến bộ và vế chỉ ra điểm nghẽn tồn đọng. | Đặt tiêu đề mục dạng câu ghép hai vế đối lập (*Chủ đề: Điểm tiến bộ, nhưng điểm nghẽn cốt lõi vẫn hạn chế kết quả*). Trình bày hộp đối sánh hai cột song hành và tam giác đối chứng đa nguồn. |
| **Bảo đảm kỹ thuật và giải trình cơ chế** (`TECHNICAL_RCA_ASSURANCE`) | Hội đồng công nghệ, nhóm kỹ thuật hoặc văn bản giải trình sự cố, nghiệm thu hệ thống. | Câu ngắn (10 đến 19 chữ/câu), mật độ số liệu và thông số kỹ thuật cao (35 đến 50 con số / 1.000 chữ). | Đi theo ba bước: xác nhận hiện tượng trên nhật ký gốc và bóc tách cơ chế sinh lỗi khỏi triệu chứng. Cuối cùng, chốt rõ điều kiện kiểm tra lại trước mốc mở cổng. |
| **Chuyên khảo thẩm định đa tầng** (`MULTI_READER_ASSURANCE`) | Hồ sơ thẩm định độc lập hoặc báo cáo tổng hợp dài phục vụ nhiều cấp lãnh đạo và chuyên gia. | Kết hợp tóm tắt điều hành cô đọng ở đầu chương với bảng truy vết mã bằng chứng ở phần thân. | Mở đầu bằng bảng phân luồng người đọc theo cấp phê duyệt chiến lược, cấp điều hành và cấp kỹ thuật. Kèm theo bảng định nghĩa nhãn bằng chứng và danh mục điều kiện dừng bắt buộc. |

## 2. Kỹ thuật đặt tiêu đề và mở đoạn theo từng kiểu giọng

### 2.1. Tiêu đề cụm danh từ ngắn hoặc câu hỏi điều hành trực diện (`DIRECT_EXECUTIVE_GATEKEEPER`)

Khi trình cấp phê duyệt cao nhất, hãy dùng cụm danh từ ngắn từ 3 đến 8 chữ gọi thẳng mảng rủi ro. Trong bảng tóm tắt, có thể đặt câu hỏi trực diện (*Hạ tầng đã sẵn sàng đáp ứng tải thực tế chưa?*, *Dữ liệu chuyển đổi đã đủ điều kiện nghiệm thu chưa?*) rồi chốt ngay trạng thái đạt hay chưa đạt ở câu đầu.

### 2.2. Tiêu đề câu ghép hai vế đối lập (`BALANCED_COMPARATIVE_SUPERVISORY`)

Cách đặt tiêu đề này ghi nhận kết quả bước đầu của đơn vị thực hiện mà không làm mờ rủi ro trọng yếu. Mở vế đầu bằng tên mảng việc và điểm tiến bộ, nối bằng chữ *nhưng* rồi nêu thẳng điểm nghẽn cốt lõi để người đọc nắm trọn kết luận ngay từ mục lục.

### 2.3. Nhãn phân đoạn văn xuôi kết thúc bằng dấu chấm (`.`)

Áp dụng cho đoạn văn độc lập theo khung 5 bước (*Thực trạng và bằng chứng.*, *Yêu cầu cần đạt.*, *Nguyên nhân kiểm soát.*, *Rủi ro và ảnh hưởng.*, *Kiến nghị kiểm toán.*). Đặt nhãn ngắn kết thúc bằng dấu chấm ngay đầu đoạn văn xuôi (không thêm dấu gạch đầu dòng `-` hay số thứ tự) rồi viết tiếp câu chủ đề trên cùng một dòng.

### 2.4. Thứ tự nén nhận định trong ô bảng theo dõi (2 đến 4 mệnh đề ngắn)

Khi viết cột nhận xét tiến độ trong bảng lớn, hãy giữ thứ tự cố định. Mở đầu bằng trạng thái thời hạn (*quá hạn 62 ngày*, *còn 13 ngày đến hạn*, *chưa giao hạn cụ thể*), tiếp theo là độ lùi hạn (*dự kiến lùi 92 ngày*). Cuối cùng, chốt chất lượng đầu ra (*kết quả mới dừng ở hoạt động trung gian, chưa có sản phẩm kiểm chứng*).

## 3. Sáu kỷ luật dẫn số liệu và khóa ranh giới bằng chứng

Công cụ [scripts/vi_scanner.py](../scripts/vi_scanner.py) tự động rà 6 nguyên tắc này qua quy tắc `VIS-STRUCT-002` và lệnh `profile`:

### 3.1. Ghép cặp `Tử số/Mẫu số (Tỷ lệ %)` khi chốt kết luận

Không viết tỷ lệ phần trăm đứng trơ một mình. Cách viết thiếu mẫu số rất dễ che giấu quy mô mẫu nhỏ. Hãy ghi đủ cả tử số, mẫu số và tỷ lệ, chẳng hạn *Có 138/213 đơn vị gửi báo cáo đánh giá, tương đương 64,8%*.

### 3.2. Tách bạch hoạt động trung gian với đầu ra kiểm chứng được

Họp bàn, gửi công văn nhắc hay hướng dẫn lại chưa phải kết quả hoàn thành. Các hoạt động này chỉ phản ánh tiến độ xử lý trung gian. Chỉ ghi nhận đã đóng lỗi khi đơn vị có biên bản nghiệm thu hoặc kết quả kiểm tra lại thực tế đạt yêu cầu.

### 3.3. Tách tỷ lệ hoàn thành không lỗi khỏi tỷ lệ thực hiện còn vướng mắc

Tuyệt đối không gộp giao dịch còn lỗi vào tỷ lệ hoàn thành chung. Báo cáo kiểm thử phải tách rõ ba nhóm kết quả: hoàn thành không lỗi, thực hiện được nhưng còn vướng thao tác và không thực hiện được.

### 3.4. Không dùng cân đối tổng hợp hoặc bù trừ ròng để kết luận khớp đúng từng dòng

Tổng phát sinh Nợ bằng tổng phát sinh Có không chứng minh dữ liệu khớp ở cấp giao dịch đơn lẻ. Tương tự, tổng chênh lệch ròng bằng 0 do các khoản thừa thiếu tự bù trừ nhau vẫn có thể che khuất lỗi. Khi đối soát dữ liệu tài chính, hãy kiểm tra theo tổng giá trị tuyệt đối của chênh lệch trên từng tài khoản và hợp đồng.

### 3.5. Tam giác đối chứng đa nguồn và kiểm soát trôi mẫu số

Khi nhiều nguồn cùng báo cáo về một sự kiện, hãy đặt các con số cạnh nhau trong cùng một câu để đối chiếu trực tiếp. Kết hợp chạy `python scripts/vi_scanner.py profile` để rà trường `ung_vien_lech_mau_so`, phát hiện sớm chỗ lệch mẫu số giữa các trang hoặc sót tiêu đề từ tệp mẫu kỳ trước (`template_title_mismatch`).

### 3.6. Chuẩn hóa từ tình thái và ranh giới phạm vi đánh giá (`Metacognition`)

Với sự kiện đã xảy ra và có số liệu, dùng động từ khẳng định hoặc phủ định dứt khoát (*mới đạt 48,6%*, *chưa hoàn thành*). Khi nêu hệ quả rủi ro tương lai nếu vận hành sớm, chỉ dùng đúng một từ tình thái *có thể* (*Khách hàng có thể bị tính sai dư nợ*). Không khẳng định tuyệt đối vô căn cứ và không chồng nhiều từ rào đón. Đầu báo cáo luôn nêu rõ nguồn dữ liệu tạm giả định, phạm vi chưa kiểm chứng độc lập và điều kiện thay đổi ý kiến đánh giá.

## 4. Chuyển ngữ từ dữ liệu kỹ thuật và báo cáo tiến độ sang văn phong quản trị

Ba tình huống dưới đây đối chiếu cách chuyển câu chữ từ báo cáo tiến độ hoặc nhật ký kỹ thuật sang giọng văn quản trị. Cả hai phương án viết lại đều bảo toàn 100% số liệu gốc:

| Câu gốc trong báo cáo tiến độ hoặc nhật ký kỹ thuật | Chuyển sang giọng **Giám sát đối sánh hai chiều** (`BALANCED_COMPARATIVE_SUPERVISORY`) | Chuyển sang giọng **Quản trị cổng chặn trực diện** (`DIRECT_EXECUTIVE_GATEKEEPER`) |
| :--- | :--- | :--- |
| "Trong mẫu khảo sát, 84,9% giao dịch được ghi nhận hoàn thành, kể cả các trường hợp còn vướng mắc thao tác; 65/67 phiếu lỗi đã được đánh dấu xử lý xong sau khi hướng dẫn lại trên bảng theo dõi." | "Đợt diễn tập đã thu thập được phản hồi trên diện rộng (điểm cải thiện). Tuy nhiên, tỷ lệ giao dịch hoàn thành không lỗi chỉ đạt 67,5%, còn 17,4% giao dịch vẫn vướng thao tác. Riêng 65/67 phiếu lỗi mới dừng ở bước hướng dẫn lại trên bảng theo dõi, chưa có bằng chứng kiểm tra thực tế." | "Chất lượng vận hành chưa đạt điều kiện nghiệm thu. Nhóm giao dịch còn lỗi hoặc không thực hiện được chiếm tới 32,5%. Cả 65/67 phiếu lỗi báo đóng mới dừng ở bước hướng dẫn trung gian, chưa có kết quả kiểm chứng lại." |
| "Tổng số dư Nợ bằng tổng số dư Có trên bảng tổng hợp cuối ngày. Có 06 giao dịch gốc báo lệch nhưng là 03 cặp bút toán điều chỉnh thủ công bù trừ đúng nhau nên tổng chênh lệch bằng 0." | "Bảng cân đối tổng hợp cuối ngày ghi nhận tổng Nợ khớp tổng Có. Tuy nhiên, số tổng hợp cân bằng nhờ 03 cặp bút toán thủ công tự bù trừ nhau. Kết quả này chưa chứng minh dữ liệu khớp từng dòng nếu chưa đối soát theo tổng giá trị tuyệt đối." | "Rủi ro sai lệch sổ kế toán ở cấp giao dịch đơn lẻ. Quy tắc ghép cặp hiện tại cho phép các khoản lệch tự bù trừ nhau khi tổng Nợ bằng tổng Có. Cơ chế này có thể che khuất sai sót số dư từng khách hàng nếu không đối soát theo giá trị tuyệt đối." |
| "Sự cố mất kết nối cổng tích hợp lúc 10:40 gây sập toàn tuyến trong 16 phút do thiếu cơ chế giao dịch phân tán hai pha, khiến 01 giao dịch mở sổ tiết kiệm 9 tỷ đồng bị trừ tiền nhưng chưa sinh hợp đồng." | "Từ 10:40 đến 10:56, cổng tích hợp mất kết nối làm gián đoạn giao dịch trực tuyến trong 16 phút. Do thiếu cơ chế đồng bộ hai chiều, tài khoản khách hàng đã bị trừ 9 tỷ đồng. Hệ thống lõi khi đó vẫn chưa khởi tạo hợp đồng tiền gửi." | "Lỗ hổng đồng bộ giao dịch trên kênh số có thể gây trừ tiền khống của khách hàng. Trong 16 phút ngắt kết nối, khách hàng bị trừ 9 tỷ đồng nhưng hệ thống không sinh sổ tiết kiệm và không tự hoàn tiền. Yêu cầu khóa cổng chuyển đổi cho đến khi nghiệm thu xong cơ chế tự động hoàn trả." |
