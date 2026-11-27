# Kỹ thuật đặt câu tiếng Việt tự nhiên, cú pháp nội tại và lọc từ rác AI

Tài liệu này bổ sung tầng ngữ pháp nội tại tiếng Việt và bộ từ rác AI mới phát sinh, giúp người viết dựng câu tự nhiên thay vì chỉ né lỗi dịch thô.

## 1. Năm lỗi cấu trúc nòng cốt C–V nội tại

Ngoài lỗi giới từ đầu câu nuốt chủ ngữ đã nêu tại [pattern-bank.md](pattern-bank.md), văn bản tiếng Việt còn hay vấp năm lỗi cấu trúc `C–V` dưới đây:

1. Lỗi thiếu vị ngữ xảy ra khi nhồi định ngữ quá dài sau danh từ đầu câu. Cả câu khi đó chỉ còn một cụm danh từ treo lơ lửng.
2. Thiếu cả chủ ngữ lẫn vị ngữ khi mở đầu bằng chuỗi trạng ngữ *"Từ... đến..."* rồi kết câu mà quên mệnh đề chính `C–V`.
3. Câu ghép thiếu vế hô ứng khi mở bằng *"Mặc dù..."*, *"Vì..."*, *"Nếu..."* rồi kéo dài giải thích, bỏ quên vế kết quả tương ứng.
4. Nhập nhằng trạng ngữ với chủ ngữ ở mẫu *"Qua... của... cho thấy..."*. Hãy chữa theo một trong hai cách là bỏ chữ *"Qua"* hoặc bỏ chữ *"của"*.
5. Sai trật tự thành phần khi đưa cụm mục đích lên đầu một vế bị động khuyết chủ thể, làm câu mất tác nhân thực hiện hành động.

```text
[Thiếu vị ngữ]
Sai:  Hình ảnh người dũng sĩ mặc áo giáp sắt, vung gậy sắt, xông thẳng vào quân thù.
Sửa:  Hình ảnh người dũng sĩ mặc áo giáp sắt... đã gây ấn tượng mạnh mẽ.

[Thiếu cả C-V]
Sai:  Từ những chị dân quân canh giữ đồng quê, đến những bà mẹ chèo đò anh dũng.
Sửa:  Từ những chị dân quân... đến những bà mẹ chèo đò..., tất cả đều biểu lộ tinh thần kiên cường.

[Nhập nhằng trạng ngữ - chủ ngữ]
Sai:  Qua bản báo cáo của ông cho chúng ta thấy tình hình sản xuất còn nhiều khó khăn.
Sửa1: Bản báo cáo của ông cho chúng ta thấy tình hình sản xuất còn nhiều khó khăn.
Sửa2: Qua bản báo cáo, ông cho chúng ta thấy tình hình sản xuất còn nhiều khó khăn.

[Sai trật tự với cụm mục đích]
Sai:  Nhằm tăng cường giáo dục bảo vệ thiên nhiên, chi hội bảo vệ thiên nhiên được thành lập.
Sửa:  Chi hội bảo vệ thiên nhiên được thành lập nhằm tăng cường giáo dục bảo vệ thiên nhiên.
```

## 2. Tương hợp ngữ nghĩa, quan hệ logic và thông tin mới

Các lỗi này lọt qua máy kiểm tra chính tả vì từng chữ đều đúng. Tuy nhiên, câu sẽ sai nghĩa ngay khi đối chiếu thực tế.

- Liệt kê lệch trường logic do ghép hai đối tượng khác hệ quy chiếu vào cùng một vế, như trộn vị trí cơ thể với địa danh hành chính.
- Sai hoặc thiếu quan hệ từ so với quan hệ nghĩa thực tế, như dùng *"nhưng"* nối hai vế tăng tiến hay thiếu chữ *"vì"* làm mất quan hệ nguyên nhân.
- Sai tương hợp từ loại và kết hợp trục ngang khi viết nháp. Sau *"bị"* không đi trực tiếp tính từ thuần túy, còn sau *"trở nên"* phải là tính từ hoặc danh từ trạng thái. Không đặt *"rất"* hay *"rất là"* trực tiếp trước danh từ. Chủ thể phải khớp tính chất vật lý, đồng thời phân biệt danh từ *"kết cấu"* với động từ *"cấu kết"*.
- Tránh câu thừa thông tin hiển nhiên, vô bổ. Mỗi câu phải mang thuộc tính hoặc dữ kiện khu biệt mới.

```text
[Lệch trường logic]
Sai: Người chiến sĩ bị hai vết thương: một ở đùi trái và một ở Quảng Trị.

[Sai/thiếu quan hệ từ]
Sai: Tác giả tố cáo bọn thống trị bóc lột thuế má nhưng ông vạch mặt bọn thực dân. -> Đổi "nhưng" thành "hơn nữa".
Sai: Số người mắc và chết các bệnh truyền nhiễm đã giảm. -> Thêm "vì": "...mắc và chết vì các bệnh...".

[Sai từ loại và kết hợp từ]
Sai: Lượng mưa năm nay kéo dài.              -> Sửa: Mùa mưa năm nay kéo dài.
Sai: Anh ấy làm việc rất là năng lực.       -> Sửa: Anh ấy làm việc rất có năng lực.
Sai: Các bông cúc trở nên tưng bừng nhảy múa. -> Sửa: Các bông cúc trở nên tươi đẹp hơn.
Sai: Nhóm xấu đã kết cấu với nhau.          -> Sửa: Nhóm xấu đã cấu kết với nhau.

[Thông tin vô bổ -> thông tin mới]
Vô bổ: Nó nhìn tôi bằng mắt.
Đạt:   Nó nhìn tôi bằng ánh mắt nghi ngờ.
```

## 3. Bốn thao tác biến đổi câu tự nhiên

Chỉnh câu không chỉ là xóa lỗi. Bốn thao tác dưới đây giúp điều chỉnh nhịp điệu và sắc thái theo đúng ngữ cảnh.

1. Mở rộng câu có chủ đích bằng cách thêm định ngữ, bổ ngữ, trạng ngữ hoặc đề ngữ để cụ thể hóa dữ kiện. Ngược lại, rút gọn thành phần phụ khi cần câu chốt gọn hoặc tóm lược.
2. Đảo trật tự Đề–Thuyết để đẩy phần cần nhấn mạnh hoặc cần nối ý ra đầu câu mà vẫn giữ nguyên nghĩa sự việc. Cần tránh các cặp đảo làm đổi nghĩa như *"đá bóng"* với *"bóng đá"*. Có thể dùng trợ từ *"thì"* để tách đề khi đối chiếu hai vế.
3. Chuyển đổi kiểu câu linh hoạt thay vì xóa chữ *"được"* một cách máy móc. Hãy giữ bị động tiếng Việt thuần khi cần giữ một chủ thể xuyên suốt đoạn văn. Phủ định của phủ định (*"không phải là không tốt"*) giúp khẳng định chừng mực. Câu hỏi tu từ đầy đủ nghĩa và tiểu từ tình thái (*"chăng"*, *"đâu"*, *"thôi"*, *"chứ"*, *"nhỉ"*) chỉ dùng trong văn nghị luận hoặc chia sẻ, tuyệt đối không đưa vào `audit_report` hay `legal`.
4. Chuyển lời dẫn trực tiếp sang gián tiếp theo ba bước rõ ràng. Bỏ dấu hai chấm cùng ngoặc kép, đổi ngôi đại từ rồi chỉnh lại từ định vị thời gian và địa điểm theo mốc thuật lại.

```text
[1. Mở rộng cụ thể hóa]
Gốc: Giá hàng tăng.
Mở:  Giá các mặt hàng tiêu dùng tăng 1,3% trong 7 tháng đầu năm qua.

[2. Bốn trật tự Đề-Thuyết cùng nghĩa sự việc]
- Chúng ta hãy dành những gì tốt đẹp nhất cho trẻ em.
- Chúng ta hãy dành cho trẻ em những gì tốt đẹp nhất.
- Những gì tốt đẹp nhất, chúng ta hãy dành cho trẻ em.
- Cho trẻ em, chúng ta hãy dành những gì tốt đẹp nhất.

[3. Giữ bị động nối mạch & phủ định giảm nhẹ]
- Thằng này rất ngạc nhiên. Hết ngạc nhiên thì hắn thấy mắt mình ươn ướt. Bởi vì lần này là lần đầu hắn được một người đàn bà cho.
- Anh ta không phải là không tốt, nhưng... / Không ai là không vấp ngã một lần.

[4. Trực tiếp -> Gián tiếp]
Trực tiếp: Tối hôm qua, anh ấy còn bảo rằng: "Ngày mai tôi sẽ đến kiểm tra".
Gián tiếp: Tối hôm qua, anh ấy còn bảo rằng hôm nay anh ấy đến kiểm tra.
```

## 4. Năm phép liên kết câu và ba lỗi phá mạch lạc

Khi giảm từ nối đầu câu sách vở theo `VIS-FMT-002`, hãy nối câu bằng năm phép liên kết tự nhiên sau:

- Lặp từ khóa có chủ ý hoặc lặp móc xích, lấy ý cuối câu trước làm điểm tựa mở câu sau.
- Thay thế cụm danh từ đã nêu bằng đại từ hoặc từ đồng nghĩa ngắn gọn.
- Liên tưởng ngữ nghĩa bằng cách đặt các từ cùng trường nghĩa cạnh nhau qua nhiều câu liên tiếp.
- Tỉnh lược có ngữ cảnh để rút gọn thành phần đã rõ ở câu liền trước.
- Chuyển ý bằng cụm nối đời thường (*"Ấy vậy mà"*, *"Vẫn biết... nhưng"*, *"Còn... thì"*) thay cho *"Hơn nữa"* hay *"Bên cạnh đó"*.

Đồng thời rà ba lỗi phá vỡ mạch lạc đoạn văn gồm lạc chủ đề chung, hai câu kế nhau mâu thuẫn ý và dùng sai phương tiện liên kết.

```text
[Phép liên tưởng theo trường nghĩa]
Cuộc sống của quê tôi gắn bó với cây cọ. Cha làm cho tôi chiếc chổi cọ để quét nhà, quét sân.
Mẹ đựng hạt giống đầy các móm lá cọ, treo trên gác bếp. Chị tôi đan nón lá cọ xuất khẩu.

[Lặp móc xích nối mạch lập luận]
... Đừng sợ thất bại. Thất bại chỉ là điểm dừng tạm để bạn rà soát lại cách làm.
```

## 5. Ba lỗi dấu câu nội tại tiếng Việt

Ngoài gạch ngang dài và chấm phẩy đã chặn ở `VIS-FMT-003`, người viết hay vấp ba lỗi dấu câu dưới đây:

1. Ngắt dấu chấm sớm khi cụm đứng trước mới là phần chủ ngữ dài, khiến câu bị tách đôi thành câu cụt thiếu vị ngữ.
2. Quên dấu phẩy tách trạng ngữ dài đầu câu hoặc quên dấu chấm tách hai câu hoàn chỉnh, sinh ra câu dồn dài trên `35` từ.
3. Đặt nhầm dấu chấm hỏi cuối câu tường thuật gián tiếp chỉ vì trong câu có từ *"cái gì"*, *"tại sao"* hay *"như thế nào"*.

```text
[Quên dấu phẩy và dấu chấm]
Sai: Với mạng lưới y tế cơ sở rộng khắp trong những năm chống Mỹ (-) y tế xã phường đã đóng góp công sức to lớn (*) gương tiêu biểu là anh hùng Trần Chữ.
Sửa: Thêm dấu phẩy ở (-) và dấu chấm ở (*).

[Dùng nhầm dấu chấm hỏi ở câu tường thuật]
Sai: Họ chưa hiểu rõ cái gì là ưu điểm, cái gì là hạn chế trong nền kinh tế thị trường?
Sửa: Họ chưa hiểu rõ cái gì là ưu điểm, cái gì là hạn chế trong nền kinh tế thị trường.
```

## 6. Chọn từ theo 2 trục, nghĩa biểu thái và 7 cụm lỗi chính âm

Khi chọn từ, cần đối chiếu trên **trục dọc liên tưởng** để chọn đúng sắc thái từ đồng nghĩa hoặc từ láy (*"nho nhỏ"*, *"nhỏ nhắn"*, *"nhỏ nhẻ"*, *"nhỏ nhoi"*, *"nhỏ nhặt"*, *"nhỏ nhen"*). Sau đó kiểm tra **trục ngang kết hợp** để xem từ trung tâm có hợp với động từ, danh từ xung quanh hay không.

Người viết cũng phải giữ đúng **nghĩa biểu thái** (*"biếu"* với người trên, *"thí"* với kẻ dưới, *"hiến"* cho sự nghiệp lớn). Giữ nhất quán trường nghĩa ẩn dụ toàn đoạn và loại từ địa phương khỏi văn bản chính luận hoặc khoa học.

| Cụm lỗi | Cách viết đúng | Lý do | Hướng xử lý |
| :--- | :--- | :--- | :--- |
| `khuyên góp` | `quyên góp` | Sai chính tả gần âm | Báo `VIS-LEX-001` |
| `chí lực` | `trí lực` | Sai chính tả gần âm | Báo `VIS-LEX-001` |
| `bất chắc` | `bất trắc` | Sai chính tả gần âm | Báo `VIS-LEX-001` |
| `năng xuất` | `năng suất` | Sai chính tả gần âm | Báo `VIS-LEX-001` |
| `kết cấu với nhau` | `cấu kết với nhau` | Nhầm danh từ với động từ | Báo `VIS-LEX-001` |
| `rất là năng lực` | `rất có năng lực` | Đặt phó từ trước danh từ | Báo `VIS-LEX-001` |
| `không ngừng ngày một` | `không ngừng` hoặc `ngày một` | Thừa vế trùng nghĩa | Báo `VIS-CLICHE-003` |
| `hoạt động thầm kín` | `hoạt động thầm lặng` | Nhầm sắc thái nghĩa | Ghi chú ngữ cảnh |
| `ghi nhớ trong hành trang` | `ghi nhớ trong hành trình` | Nhầm cặp từ gần nghĩa | Ghi chú ngữ cảnh |

## 7. Viết hoa tên riêng, 4 cách xử lý từ ngoại ngữ và kỹ thuật nghị luận

- Danh từ chung gắn chặt với tên người hoặc địa danh viết hoa mọi âm tiết, như Ông Gióng, Tây Bắc hay Vàm Cỏ Đông. Tên cơ quan Việt Nam viết hoa chữ cái đầu từng bộ phận mang nghĩa khu biệt như Bộ Ngoại giao Hoa Kỳ. Danh từ chung chỉ viết hoa tu từ khi mang sắc thái tôn kính, như Tổ quốc hoặc Đảng.
- Có bốn phương thức xử lý từ và tên riêng nước ngoài: giữ nguyên dạng chữ Latin quen ngành, dịch nghĩa kèm nguyên ngữ ở lần đầu, chuyển tự và phiên âm. Chuyển tự áp dụng cho hệ chữ khác Latin (`Mockba` thành `Moskva`), còn phiên âm tách âm tiết có gạch nối (`Na-pô-lê-ông`). Cần giữ nhất quán một kiểu trong cả tài liệu.
- Mở đoạn nghịch lý `A↑ B↑ C↓` đặt hai dữ kiện tăng tiến tạo kỳ vọng rồi lật sang nghịch lý thực tế để thay mở bài sáo. Khi bàn một quan điểm, hãy thêm **Phản đề** chỉ rõ câu nói đúng ở đâu, sai ở đâu và thử trên một người so với số đông.
- Khi tham khảo bài văn nghị luận mẫu, tuyệt đối không học theo câu dồn dài quá `35` từ thiếu dấu ngắt, sáo ngữ, lỗi đánh máy hay gạch ngang nối mệnh đề.

## 8. Bộ từ rác AI tiếng Việt mới bổ sung (`VIS-LEX-001`, `VIS-AI-004`, `VIS-RHET-002/003`)

Các mô hình ngôn ngữ hay tạo vẻ sắc bén giả bằng chữ *"thẳng"*, động từ *"khóa"* hoặc động từ cơ học, y khoa. Bộ lọc cũng chặn các cụm dẫn dắt làm màu. Công cụ `scripts/vi_scanner.py` tự động gắn cờ bốn nhóm dưới đây và giữ ngoại lệ cho nghĩa thật.

| Nhóm rác AI | Quy tắc | Hướng xử lý | Ngoại lệ hợp lệ |
| :--- | :--- | :--- | :--- |
| Cụm gắn chữ `thẳng` dư thừa | `VIS-LEX-001` | Bỏ chữ dư hoặc dùng rõ ràng, trực tiếp | Đường thẳng, bay thẳng, đi thẳng 200 mét |
| Động từ `khóa` ý trừu tượng | `VIS-LEX-001` | Thay bằng cố định, xác định rõ | Khóa sổ kế toán, khóa tài khoản, khóa cửa |
| Động từ cơ học và y khoa | `VIS-LEX-001`, `VIS-RHET-003` | Đổi sang phân tích, đối chiếu, rút gọn | Máy soi chiếu hành lý, bóc tách khối lượng, giải phẫu bệnh |
| Cụm dẫn và tính từ gồng mình | `VIS-AI-004`, `VIS-RHET-002/003`, `VIS-TONE-001` | Bỏ cụm dẫn thừa, nêu số liệu trực tiếp | Lời thoại trong ngoặc kép hoặc mã nguồn |

```text
[Cụm gắn chữ "thẳng" bị chặn]  nói thẳng, ghi nhận thẳng, nêu thẳng, đi thẳng vào vấn đề
[Động từ "khóa" bị chặn]       khóa số liệu, khóa ranh giới, khóa thuật ngữ, khóa chặt điều kiện
[Cơ học/y khoa làm màu]        neo bằng chứng, nén nhận định, siết câu chữ, đóng khung vấn đề, bóc tách, giải phẫu, soi chiếu
[Dẫn dắt/tính từ gồng mình]    thành thật mà nói, nói thẳng ra, điều thú vị là, mấu chốt nằm ở chỗ, chuẩn chỉnh, sắc lẹm, sự thật phũ phàng, con dao hai lưỡi, gói trọn
[Ngoại lệ sạch lỗi]            đường thẳng, bay thẳng Hà Nội, khóa sổ kế toán, khóa tài khoản, máy soi chiếu hành lý, bóc tách khối lượng, giải phẫu bệnh, nén tệp ảnh PNG, siết tín dụng
```
