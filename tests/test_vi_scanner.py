#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Bộ kiểm thử độc lập cho vi_scanner.py v2.0.0.

Bao gồm:
1. Toàn bộ 100 mẫu kiểm thử độc lập (TF-G1-01 đến TF-G5-20) trên 7 nhóm văn bản.
2. Kiểm thử hành vi mặc định `profile="all"` xuất đủ 100% tín hiệu mọi nhóm.
3. Kiểm thử Nhóm 6 (VIS-LEX-001..002, VIS-TONE-001, VIS-STRUCT-001..002) và danh sách từ mượn.
4. Kiểm thử bảo toàn 6 nhóm dữ kiện (SemanticMasker & verify_text) và che đường dẫn Markdown.
5. Kiểm thử chống treo máy ReDoS (> 210.000 ký tự dưới 500 ms) và tự rà sạch dữ liệu dự án.
"""
from __future__ import annotations

import datetime as dt
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import time
import unittest

ROOT = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = ROOT / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

import vi_scanner  # noqa: E402
from vi_scanner import SemanticMasker, ViScanner, check_loanwords_maintenance, main, verify_text  # noqa: E402


# 100 mẫu kiểm thử độc lập (mã, rule mục tiêu, profile, kỳ vọng bắt lỗi, văn bản)
BENCHMARK_100_FIXTURES: tuple[tuple[str, str, str, bool, str], ...] = (
    # --- NHÓM 1: AI_META_AND_STAGING (20 mẫu) ---
    ("TF-G1-01", "VIS-AI-001", "audit_report", True, "Tất nhiên rồi! Dưới đây là báo cáo đối chiếu công nợ phải thu khách hàng tính đến ngày 31/12/2025 của Chi nhánh Miền Nam."),
    ("TF-G1-02", "VIS-AI-001", "academic", True, "Kết quả hồi quy tuyến tính cho thấy hệ số R2 đạt 0,84. Hy vọng phân tích này sẽ hữu ích cho bạn trong quá trình hoàn thiện luận văn."),
    ("TF-G1-03", "VIS-AI-001", "legal", True, "Là một mô hình ngôn ngữ AI, tôi không thể đưa ra tư vấn pháp lý chính thức về tranh chấp hợp đồng thuê kho bãi số 44/HĐKT."),
    ("TF-G1-04", "VIS-AI-002", "marketing", True, "Biên bản bàn giao thiết bị giữa đại diện [Điền tên nhà cung cấp] và Ban Quản lý dự án được lập thành 04 bản có giá trị pháp lý như nhau."),
    ("TF-G1-05", "VIS-AI-002", "translation", True, "Số liệu xuất khẩu thủy sản quý II đạt 2,4 tỷ USD theo báo cáo tại https://vasep.com.vn/baocao-q2?utm_source=chatgpt.com."),
    ("TF-G1-06", "VIS-AI-003", "audit_report", True, "Trong bối cảnh thị trường tài chính toàn cầu ngày càng biến đổi phức tạp, khoản dự phòng giảm giá hàng tồn kho tại kho Bình Dương tăng thêm 4,8 tỷ đồng."),
    ("TF-G1-07", "VIS-AI-003", "academic", True, "Trong kỷ nguyên trí tuệ nhân tạo ngày càng phát triển mạnh mẽ, nghiên cứu này khảo sát 420 sinh viên trường Đại học Bách khoa về thói quen tự học."),
    ("TF-G1-08", "VIS-AI-004", "general", True, "Tại sao áp suất đường ống giảm đột ngột? Câu hỏi đặt ra là liệu van an toàn có bị rò rỉ? Câu trả lời ngắn gọn là do gioăng cao su đã lão hóa sau 5 năm."),
    ("TF-G1-09", "VIS-AI-004", "translation", True, "Hãy cùng chúng tôi đi sâu vào khám phá trong bài viết này các thông số kỹ thuật của động cơ điện 3 pha công suất 15kW."),
    ("TF-G1-10", "VIS-AI-005", "general", True, "Nhìn chung, việc thay thế hệ thống đèn LED nhà xưởng số 2 hứa hẹn sẽ mở ra một kỷ nguyên mới cho hoạt động tiết kiệm năng lượng của xí nghiệp."),
    ("TF-G1-11", "VIS-AI-001", "academic", False, 'Khi khảo sát lỗi giao diện chatbot, nhóm nghiên cứu ghi nhận câu mẫu: "Chắc chắn rồi! Dưới đây là kết quả tìm kiếm" xuất hiện trong 78% phiên hội thoại.'),
    ("TF-G1-12", "VIS-AI-002", "general", False, "Để cấu hình đường dẫn theo dõi, lập trình viên cần lọc bỏ chuỗi `utm_source=chatgpt.com` trong hàm xử lý truy vấn trước khi lưu vào cơ sở dữ liệu."),
    ("TF-G1-13", "VIS-AI-003", "academic", False, "Trong bối cảnh lạm phát năm 2024 giữ ở mức 3,63% theo số liệu công bố, lãi suất cho vay ngắn hạn tại các ngân hàng thương mại giảm trung bình 0,8%/năm."),
    ("TF-G1-14", "VIS-AI-004", "marketing", False, "Hãy cùng chúng tôi đi sâu vào khám phá trong bài viết hôm nay bộ sưu tập gốm sứ thủ công dành riêng cho mùa lễ hội cuối năm."),
    ("TF-G1-15", "VIS-AI-005", "audit_report", False, "Tóm lại, tổng giá trị chênh lệch kiểm kê tài sản cố định tại ngày 30/09/2025 là 185 triệu đồng, đã được đơn vị hạch toán điều chỉnh vào biên bản số 12/BB-KT."),
    ("TF-G1-16", "VIS-AI-001", "legal", False, "Căn cứ Điều 117 Bộ luật Dân sự 2015, giao dịch dân sự có hiệu lực khi chủ thể có năng lực pháp luật dân sự và tự nguyện."),
    ("TF-G1-17", "VIS-AI-002", "audit_report", False, "Kiểm toán viên đã đối chiếu 100% sao kê ngân hàng [Phụ lục 03A] với sổ cái tài khoản 1121 tại thời điểm khóa sổ kế toán."),
    ("TF-G1-18", "VIS-AI-003", "translation", False, "Khi nhiệt độ buồng đốt vượt quá 850 độ C, cảm biến nhiệt điện trở sẽ tự động ngắt mạch cấp nhiên liệu trong vòng 0,5 giây."),
    ("TF-G1-19", "VIS-AI-004", "social_media", False, "Câu hỏi đặt ra là làm sao chạy bộ 21km không bị chuột rút? Câu trả lời ngắn gọn là hãy bổ sung điện giải mỗi 45 phút!"),
    ("TF-G1-20", "VIS-AI-005", "general", False, 'Tại buổi họp báo, ông Nguyễn Văn An phát biểu: "Tóm lại, tuyến đường cao tốc này hứa hẹn sẽ mở ra một kỷ nguyên mới cho giao thương vùng Tây Nguyên".'),

    # --- NHÓM 2: AI_RHETORICAL_INFLATION (20 mẫu) ---
    ("TF-G2-01", "VIS-RHET-001", "general", True, "Bản cập nhật phần mềm kế toán v3.2 không chỉ đơn thuần là một bản vá lỗi kỹ thuật, mà còn là một tuyên ngôn về tầm nhìn chuyển đổi số."),
    ("TF-G2-02", "VIS-RHET-001", "audit_report", True, "Biên bản đối chiếu công nợ này không đơn thuần là một thủ tục kiểm toán định kỳ, mà chính là chiếc chìa khóa thay đổi văn hóa minh bạch của tập đoàn."),
    ("TF-G2-03", "VIS-RHET-002", "academic", True, "Thí nghiệm đo độ bền kéo của mẫu bê tông M300 đóng một vai trò vô cùng then chốt và đánh dấu một bước ngoặt lịch sử trong ngành vật liệu xây dựng."),
    ("TF-G2-04", "VIS-RHET-002", "translation", True, "Ký kết phụ lục hợp đồng gia hạn 6 tháng là một minh chứng sống động cho tinh thần hợp tác bền bỉ giữa hai doanh nghiệp."),
    ("TF-G2-05", "VIS-RHET-003", "marketing", True, "Giữa bức tranh toàn cảnh đầy biến động của chuỗi cung ứng, quy trình mua hàng mới nổi lên như ngọn hải đăng dẫn đường cho phòng vật tư."),
    ("TF-G2-06", "VIS-RHET-003", "academic", True, "Chương 2 của luận văn sẽ đi sâu vào khám phá bản chất của tấm thảm đa sắc trong hành vi tiêu dùng thực phẩm hữu cơ tại đô thị."),
    ("TF-G2-07", "VIS-RHET-004", "general", True, "Từ những ốc vít nhỏ bé trong kho linh kiện cho đến những định hướng chiến lược vĩ mô của ban giám đốc, tất cả đều hòa nhịp trong quy trình ISO 9001."),
    ("TF-G2-08", "VIS-RHET-004", "translation", True, "Từ các buổi họp nhóm 15 phút mỗi sáng cho đến những khát vọng vươn tầm châu lục, mọi thứ đều phụ thuộc vào kỷ luật thực thi."),
    ("TF-G2-09", "VIS-RHET-005", "academic", True, "Các chuyên gia hàng đầu đều cho rằng tỷ lệ thất thoát nhiệt qua tường kính có thể lên tới 40% nếu không sử dụng lớp phủ Low-E."),
    ("TF-G2-10", "VIS-RHET-005", "audit_report", True, "Nhiều nghiên cứu khoa học đã chỉ ra rằng phân tách nhiệm vụ giữa kế toán thanh toán và thủ quỹ giúp ngăn ngừa gian lận tiền mặt."),
    ("TF-G2-11", "VIS-RHET-001", "legal", False, "Khoản tiền 500 triệu đồng này không đơn thuần là tiền đặt cọc bảo đảm giao kết hợp đồng, mà còn là khoản thanh toán đợt 1 theo Điều 4.2 Hợp đồng số 08/HĐMB."),
    ("TF-G2-12", "VIS-RHET-002", "marketing", False, "Sự kiện ra mắt dòng xe điện mới đánh dấu một bước ngoặt mang tính lịch sử của thương hiệu và là một minh chứng sống động cho cam kết giao thông xanh."),
    ("TF-G2-13", "VIS-RHET-003", "general", False, "Ngọn hải đăng dẫn đường cho tàu thuyền ra vào vịnh được xây dựng trên đảo ở độ cao 118m so với mực nước biển."),
    ("TF-G2-14", "VIS-RHET-004", "audit_report", False, "Từ ngày 01/01/2025 cho đến ngày 31/12/2025, tất cả đều được hạch toán theo tỷ giá trung tâm công bố."),
    ("TF-G2-15", "VIS-RHET-005", "academic", False, "Nhiều nghiên cứu khoa học đã chỉ ra rằng (Nguyễn và cộng sự, 2023; Trần, 2024) nồng độ bụi mịn PM2.5 tăng cao vào các tháng mùa đông tại miền Bắc."),
    ("TF-G2-16", "VIS-RHET-005", "academic", False, "Các chuyên gia hàng đầu nhận định rằng [14, 15] cấu trúc đề - thuyết phản ánh sát thực tế cú pháp tiếng Việt hơn cấu trúc chủ - vị châu Âu."),
    ("TF-G2-17", "VIS-RHET-002", "general", False, "Chiến dịch năm 1954 đánh dấu một bước ngoặt lịch sử trong cuộc kháng chiến giành độc lập dân tộc."),
    ("TF-G2-18", "VIS-RHET-003", "translation", False, "Tại khu trưng bày nghề dệt, du khách có thể chiêm ngưỡng tấm thảm đa sắc được dệt thủ công bằng tơ tằm từ thế kỷ XVII."),
    ("TF-G2-19", "VIS-RHET-001", "general", False, "Lợi nhuận ròng quý IV/2025 đạt 128 tỷ đồng, tăng 14,5% so với cùng kỳ năm trước nhờ tiết giảm chi phí vận tải đường biển."),
    ("TF-G2-20", "VIS-RHET-004", "legal", False, "Thời hạn khiếu nại là 90 ngày kể từ ngày nhận được quyết định hành chính hoặc biết được quyết định hành chính theo Điều 9 Luật Khiếu nại 2011."),

    # --- NHÓM 3: AI_STRUCTURAL_AND_FORMATTING (20 mẫu) ---
    ("TF-G3-01", "VIS-FMT-001", "social_media", True, "Các lợi ích:\n- **Tính sẵn sàng cao:** Tính sẵn sàng cao giúp duy trì kết nối.\n- **Khả năng mở rộng:** Khả năng mở rộng đáp ứng 10.000 người.\n- **Tiết kiệm chi phí:** Tiết kiệm chi phí vận hành tới 25% mỗi năm."),
    ("TF-G3-02", "VIS-FMT-001", "translation", True, "Ba nội dung chính:\n* **Quản trị rủi ro:** Quản trị rủi ro giúp nhận diện sớm sai sót.\n* **Tuân thủ pháp lý:** Tuân thủ pháp lý bảo đảm đúng quy định.\n* **Kiểm soát nội bộ:** Kiểm soát nội bộ ngăn ngừa sai lệch kế toán."),
    ("TF-G3-03", "VIS-FMT-002", "general", True, "Hệ thống lọc nước mới đạt công suất 50m3/giờ. Hơn nữa, điện năng tiêu thụ giảm 12%. Thêm vào đó, tuổi thọ màng lọc tăng lên 3 năm. Bên cạnh đó, chi phí bảo trì định kỳ giảm 30 triệu đồng/năm."),
    ("TF-G3-04", "VIS-FMT-002", "academic", True, "Mẫu khảo sát gồm 300 doanh nghiệp vừa và nhỏ. Ngoài ra, dữ liệu thứ cấp được thu thập từ cơ quan thuế. Mặt khác, nhóm tác giả phỏng vấn sâu 15 giám đốc tài chính. Hơn nữa, mô hình SEM được dùng để kiểm định giả thuyết."),
    ("TF-G3-05", "VIS-FMT-003", "general", True, "Khoản đầu tư vào nhà máy điện mặt trời—trị giá 1.200 tỷ đồng—đã hoàn vốn sau 6 năm vận hành—sớm hơn kế hoạch ban đầu 14 tháng."),
    ("TF-G3-06", "VIS-FMT-003", "translation", True, "Các mô hình ngôn ngữ lớn—chẳng hạn như các hệ thống hội thoại tự động—thường lạm dụng dấu gạch ngang dài—ngay cả khi dịch sang tiếng Việt."),
    ("TF-G3-07", "VIS-FMT-004", "audit_report", True, "Đơn vị cần rà soát lại quy trình phê duyệt tạm ứng để kiểm soát chi phí nhanh chóng, chính xác và hiệu quả trong quý tới."),
    ("TF-G3-08", "VIS-FMT-004", "academic", True, "Phương án đề xuất mang lại hướng tiếp cận sáng tạo, đột phá và bền vững cho bài toán lập lộ trình giao hàng đô thị."),
    ("TF-G3-09", "VIS-FMT-005", "general", True, "Cửa hàng thứ nhất bán được mười hai thùng sữa tươi trong buổi sáng nay.\n\nNhân viên kho kiểm tra đủ mười bốn kiện hàng thực phẩm khô lúc trưa.\n\nBộ phận giao nhận chuyển xong mười sáu đơn hàng nội thành trước giờ nghỉ.\n\nQuầy thu ngân tổng kết đúng mười tám hóa đơn thanh toán thẻ cuối ngày."),
    ("TF-G3-10", "VIS-FMT-004", "legal", True, "Cơ chế giải quyết tranh chấp nội bộ cần thiết kế linh hoạt, minh bạch và tối ưu cho các bên tham gia liên doanh."),
    ("TF-G3-11", "VIS-FMT-001", "legal", False, "Giải thích từ ngữ tại Điều 3:\n- **Bên A:** Công ty Cổ phần Vận tải Biển Đông.\n- **Bên B:** Ngân hàng Thương mại Cổ phần Ngoại thương.\n- **Ngày làm việc:** Ngày từ thứ Hai đến thứ Sáu."),
    ("TF-G3-12", "VIS-FMT-002", "general", False, "Doanh thu xuất khẩu hạt điều đạt 3,6 tỷ USD năm 2025. Bên cạnh đó, thị trường Trung Quốc tăng trưởng 18% so với năm 2024."),
    ("TF-G3-13", "VIS-FMT-003", "general", False, "Tuyến đường sắt tốc độ cao Bắc – Nam dự kiến đi qua 20 tỉnh, thành phố từ Hà Nội đến Thành phố Hồ Chí Minh."),
    ("TF-G3-14", "VIS-FMT-004", "marketing", False, "Dịch vụ chuyển tiền quốc tế giúp giao dịch nhanh chóng, chính xác và hiệu quả chỉ trong 5 phút."),
    ("TF-G3-15", "VIS-FMT-005", "legal", False, "Điều 1 quy định phạm vi điều chỉnh của nghị định quản lý thương mại.\n\nĐiều 2 quy định đối tượng áp dụng bao gồm thương nhân kinh doanh kho.\n\nĐiều 3 giải thích các thuật ngữ chuyên ngành dùng trong văn bản này.\n\nĐiều 4 quy định nguyên tắc phối hợp kiểm tra giữa các cơ quan."),
    ("TF-G3-16", "VIS-FMT-005", "audit_report", False, "Khoản mục tiền mặt tại quỹ khớp đúng với biên bản kiểm kê thực tế.\n\nKhoản mục tiền gửi ngân hàng khớp với thư xác nhận số dư cuối kỳ.\n\nKhoản mục phải thu khách hàng đã trích lập dự phòng theo tuổi nợ.\n\nKhoản mục hàng tồn kho được theo dõi chi tiết theo từng mã vật tư."),
    ("TF-G3-17", "VIS-FMT-001", "general", False, "Ví dụ định dạng:\n```markdown\n- **Mục 1:** Nội dung 1.\n- **Mục 2:** Nội dung 2.\n- **Mục 3:** Nội dung 3.\n```"),
    ("TF-G3-18", "VIS-FMT-003", "translation", False, "Nhân vật chính nói:\n— Tôi không ngờ ông ấy lại rời đi sớm như vậy!\n— Chuyện đã đành, chúng ta phải tính bước tiếp theo."),
    ("TF-G3-19", "VIS-FMT-002", "audit_report", False, "Đơn vị chưa đối chiếu công nợ với 12 nhà cung cấp. Ngoài ra, 03 hợp đồng mua sắm thiết bị chưa có biên bản nghiệm thu kỹ thuật."),
    ("TF-G3-20", "VIS-FMT-005", "general", False, "Doanh thu tháng Chín tăng nhẹ.\n\nTrong quý III, công ty đã mở rộng thêm hai dây chuyền đóng gói tự động tại nhà máy phía Nam để kịp đơn hàng xuất khẩu sang Nhật Bản và châu Âu.\n\nChi phí điện giảm 4%.\n\nBan giám đốc dự kiến tuyển thêm 15 kỹ sư vận hành máy vào đầu quý tới."),

    # --- NHÓM 4: TRANSLATIONESE_EN_VI (20 mẫu) ---
    ("TF-G4-01", "VIS-TRANS-001", "translation", True, "Bản thiết kế kỹ thuật cầu dây văng đã được thẩm định bởi các chuyên gia tư vấn độc lập trước khi trình duyệt."),
    ("TF-G4-02", "VIS-TRANS-001", "audit_report", True, "Toàn bộ 45 chứng từ thanh toán tiền mặt trên 20 triệu đồng đã được phê duyệt bởi ông Giám đốc điều hành mà không qua chuyển khoản."),
    ("TF-G4-03", "VIS-TRANS-002", "general", True, "Dữ liệu cảm biến được thu thập mỗi 5 phút. Quy trình làm sạch được thực hiện tự động, sau đó thuật toán phân cụm được sử dụng để phát hiện điểm bất thường và báo cáo được gửi cho kỹ sư trực ca."),
    ("TF-G4-04", "VIS-TRANS-002", "translation", True, "Khung tiêu chuẩn mới được áp dụng từ tháng 6, trong đó các chỉ số an toàn được thiết kế lại và quy trình kiểm định được tiến hành hàng quý."),
    ("TF-G4-05", "VIS-TRANS-003", "translation", True, "Sự tăng trưởng của các doanh nghiệp bán lẻ nội địa trong năm 2025 đã bù đắp cho sự sụt giảm của thị trường xuất khẩu dệt may."),
    ("TF-G4-06", "VIS-TRANS-003", "social_media", True, "Việc triển khai của hệ thống quản lý kho tự động đã làm giảm việc xuất hiện của các lỗi nhặt sai mã hàng xuống dưới 0,05%."),
    ("TF-G4-07", "VIS-TRANS-004", "translation", True, "Thuật toán nén ảnh mới giúp giảm dung lượng tệp một cách đáng kể và hiển thị khung hình một cách nhanh chóng trên mạng di động."),
    ("TF-G4-08", "VIS-TRANS-004", "academic", True, "Nồng độ muối trong đất đã tăng một cách rõ rệt tại 8 trạm quan trắc, tác động một cách tiêu cực và một cách nghiêm trọng đến năng suất lúa đông xuân."),
    ("TF-G4-09", "VIS-TRANS-005", "translation", True, "Nó là rất quan trọng để sao lưu cơ sở dữ liệu PostgreSQL trước khi chạy kịch bản di trú bảng hóa đơn."),
    ("TF-G4-10", "VIS-TRANS-005", "general", True, "Trong quý III/2025, có một sự gia tăng đáng kể trong việc khách hàng hủy đơn hàng giao chậm quá 48 giờ."),
    ("TF-G4-11", "VIS-TRANS-001", "general", False, "Nhà máy nhiệt điện đã giảm 18% lượng khí thải SO2 bởi công ty vừa lắp đặt hệ thống khử lưu huỳnh bằng đá vôi ướt."),
    ("TF-G4-12", "VIS-TRANS-002", "legal", False, "Hồ sơ đề nghị cấp giấy phép môi trường được thực hiện theo quy định tại Điều 43 Luật Bảo vệ môi trường và được sử dụng làm căn cứ thanh tra định kỳ."),
    ("TF-G4-13", "VIS-TRANS-002", "audit_report", False, "Cuộc kiểm toán được thực hiện theo các Chuẩn mực Kiểm toán Việt Nam; phương pháp chọn mẫu thống kê được áp dụng cho các giao dịch trên 500 triệu đồng."),
    ("TF-G4-14", "VIS-TRANS-002", "academic", False, "Trong nghiên cứu này, mô hình PhoBERT-base được sử dụng để trích xuất đặc trưng ngữ nghĩa và phương pháp kiểm định chéo 5-fold được tiến hành trên tập dữ liệu ViDetect."),
    ("TF-G4-15", "VIS-TRANS-003", "legal", False, "Việc thực hiện của các bên theo hợp đồng liên danh không làm thay đổi nghĩa vụ liên đới đối với chủ đầu tư theo Điều 288 Bộ luật Dân sự."),
    ("TF-G4-16", "VIS-TRANS-004", "general", False, "Đội cứu hộ đã tiếp cận hiện trường sạt lở một cách nhanh chóng chỉ sau 20 phút nhận tin báo từ chính quyền xã."),
    ("TF-G4-17", "VIS-TRANS-005", "translation", False, "Cần sao lưu cơ sở dữ liệu trước khi nâng cấp vì số lượng giao dịch đồng thời vào giờ cao điểm tăng gấp 3 lần."),
    ("TF-G4-18", "VIS-TRANS-001", "academic", False, "Biến phụ thuộc Y được xác định bởi công thức Y = aX + b, trong đó hệ số góc a phản ánh độ nhạy cảm của cầu theo giá."),
    ("TF-G4-19", "VIS-TRANS-002", "general", False, "Năm 2025, 120 hộ dân xã Tân Lập được cấp giấy chứng nhận quyền sử dụng đất sau khi hoàn tất đo đạc địa chính."),
    ("TF-G4-20", "VIS-TRANS-003", "general", False, "Thị trường bán lẻ nội địa năm 2025 tăng trưởng 9,2%, bù đắp cho kim ngạch xuất khẩu dệt may bị sụt giảm 4%."),

    # --- NHÓM 5: BUREAUCRATIC_AND_SEO_CLICHE (20 mẫu) ---
    ("TF-G5-01", "VIS-CLICHE-001", "audit_report", True, "Để khắc phục tình trạng lệch kho 320 triệu đồng, phòng vật tư cần đẩy mạnh công tác tuyên truyền và nâng cao nhận thức và trách nhiệm của các cấp."),
    ("TF-G5-02", "VIS-CLICHE-001", "general", True, "Để giảm thời gian phản hồi giao diện xuống dưới 100ms, nhóm kỹ thuật quyết tâm triển khai đồng bộ và quyết liệt các giải pháp kỹ thuật."),
    ("TF-G5-03", "VIS-CLICHE-002", "general", True, "Hệ thống tường lửa thế hệ mới này đóng vai trò như là một lá chắn bảo mật và sở hữu những tính năng vượt trội chống tấn công DDoS."),
    ("TF-G5-04", "VIS-CLICHE-002", "translation", True, "Thành phố cảng được biết đến như là một trong những trung tâm logistics quan trọng của miền Trung với năng lực bốc dỡ 12 triệu tấn/năm."),
    ("TF-G5-05", "VIS-CLICHE-003", "audit_report", True, "Kết quả cuối cùng đạt được sau đợt kiểm kê là số liệu sổ sách khớp hoàn toàn tuyệt đối với tồn kho thực tế tại 4 phân xưởng."),
    ("TF-G5-06", "VIS-CLICHE-003", "general", True, "Nguyên nhân chính cốt lõi gây nghẽn mạng cục bộ sẽ được xử lý trong tương lai sắp tới bằng cách nâng băng thông lên 10Gbps."),
    ("TF-G5-07", "VIS-CLICHE-004", "academic", True, "Bạn đã bao giờ tự hỏi vì sao thuật toán Quy hoạch động lại nhanh hơn đệ quy thuần túy? Bài báo này tổng hợp tất tần tật những điều bạn cần biết về độ phức tạp O(n)."),
    ("TF-G5-08", "VIS-CLICHE-004", "audit_report", True, "Báo cáo kiểm toán nội bộ quý II: Bí quyết không thể bỏ qua để tăng vòng quay vốn lưu động cho doanh nghiệp sản xuất."),
    ("TF-G5-09", "VIS-CLICHE-005", "audit_report", True, "Khoản chênh lệch tỷ giá hối đoái 1,5% trong tháng 11 dường như có vẻ như là nguyên nhân làm giảm lợi nhuận trước thuế của công ty con."),
    ("TF-G5-10", "VIS-CLICHE-005", "academic", True, "Áp dụng thuế carbon ở một góc độ nhất định nào đó có thể được xem là có thể có khả năng sẽ làm thay đổi cơ cấu xuất khẩu thép."),
    ("TF-G5-11", "VIS-CLICHE-001", "legal", False, "Ủy ban nhân dân cấp tỉnh có trách nhiệm đẩy mạnh công tác tuyên truyền, phổ biến pháp luật về phòng cháy và chữa cháy theo Nghị định 136/2020/NĐ-CP."),
    ("TF-G5-12", "VIS-CLICHE-001", "general", False, 'Chỉ thị số 05/CT-UBND nêu rõ: "Các sở, ban, ngành cần triển khai đồng bộ và quyết liệt các giải pháp giải ngân vốn đầu tư công năm 2026".'),
    ("TF-G5-13", "VIS-CLICHE-002", "legal", False, "Trong hợp đồng ủy thác xuất khẩu này, Bên B hoạt động với tư cách là một đại lý thương mại nhân danh chính mình theo Điều 155 Luật Thương mại 2005."),
    ("TF-G5-14", "VIS-CLICHE-004", "marketing", False, "Bạn đã bao giờ tự hỏi làm sao để giữ làn da ẩm mượt suốt mùa đông? Khám phá ngay tất tần tật những điều bạn cần biết về serum cấp ẩm Hyaluronic Acid!"),
    ("TF-G5-15", "VIS-CLICHE-004", "social_media", False, "Cuối tuần đi Đà Lạt ăn gì? Lưu ngay 5 bí quyết không thể bỏ qua để săn mây sáng sớm nhé mọi người ơi!"),
    ("TF-G5-16", "VIS-CLICHE-005", "audit_report", False, "Khoản phải thu quá hạn 180 ngày trị giá 4,2 tỷ đồng có thể phải trích lập dự phòng 50% theo Thông tư 48/2019/TT-BTC nếu khách hàng không thanh toán trước 31/12."),
    ("TF-G5-17", "VIS-CLICHE-005", "legal", False, "Trừ khi các bên có thỏa thuận khác, bên vi phạm nghĩa vụ giao hàng có thể phải bồi thường thiệt hại thực tế phát sinh nhưng không vượt quá 8% giá trị phần nghĩa vụ bị vi phạm."),
    ("TF-G5-18", "VIS-CLICHE-003", "general", False, "Nguyên nhân cốt lõi gây nghẽn mạng là do bộ định tuyến trung tâm quá tải khi lưu lượng tăng đột biến lên 8,5Gbps."),
    ("TF-G5-19", "VIS-CLICHE-002", "general", False, "Tường lửa thế hệ mới là lá chắn bảo mật giúp ngăn chặn các cuộc tấn công DDoS ở tầng ứng dụng."),
    ("TF-G5-20", "VIS-CLICHE-001", "audit_report", False, "Để khắc phục chênh lệch kho 320 triệu đồng, thủ kho phải lập phiếu nhập – xuất trên phần mềm ERP ngay tại thời điểm giao nhận hàng hóa."),
)


class TestViScannerV2(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.scanner = ViScanner()

    def test_benchmark_100_fixtures_precision_recall_zero_fpr(self) -> None:
        """Kiểm tra toàn bộ 100 mẫu độc lập đạt Precision = 1.0, Recall = 1.0, FPR = 0.0%."""
        tp = fp = tn = fn = 0
        failures: list[str] = []
        for fid, target_rule, profile, expected_pos, text in BENCHMARK_100_FIXTURES:
            report = self.scanner.scan_text(text, profile=profile)
            found_ids = {f.rule_id for f in report.findings}
            if expected_pos:
                if target_rule in found_ids:
                    tp += 1
                else:
                    fn += 1
                    failures.append(f"{fid}: Bỏ sót {target_rule} (chỉ thấy {found_ids})")
            else:
                if not found_ids:
                    tn += 1
                else:
                    fp += 1
                    failures.append(f"{fid} ({profile}): Báo nhầm {found_ids}")

        self.assertEqual(failures, [], "Lỗi trên bộ 100 mẫu:\n" + "\n".join(failures))
        self.assertEqual(tp, 50)
        self.assertEqual(tn, 50)
        self.assertEqual(fp, 0)
        self.assertEqual(fn, 0)

    def test_default_scan_outputs_100_percent_all_profiles(self) -> None:
        """Mặc định không truyền profile phải chạy ở chế độ 'all' và xuất tín hiệu của mọi nhóm."""
        sample = (
            "Hãy cùng chúng tôi đi sâu vào khám phá trong bài viết hôm nay! "
            "Phương pháp này được sử dụng rộng rãi, quy trình được thực hiện tự động "
            "và kết quả được ghi nhận hàng ngày. "
            "Anh Hùng ơi, bên mình cần đẩy mạnh công tác tuyên truyền ngay."
        )
        rep_all = self.scanner.scan_text(sample)
        self.assertEqual(rep_all.profile, "all")
        all_ids = {f.rule_id for f in rep_all.findings}
        # Bao gồm cả rule bị miễn ở marketing (VIS-AI-004), bị miễn ở audit_report (VIS-TRANS-002),
        # bị miễn ở legal (VIS-CLICHE-001) và rule riêng của audit_report (VIS-TONE-001)
        self.assertIn("VIS-AI-004", all_ids)
        self.assertIn("VIS-TRANS-002", all_ids)
        self.assertIn("VIS-CLICHE-001", all_ids)
        self.assertIn("VIS-TONE-001", all_ids)
        for f in rep_all.findings:
            self.assertTrue(len(f.applicable_profiles) >= 1)

    def test_group6_voice_lexical_and_structure_rules(self) -> None:
        """Kiểm tra 5 quy tắc thực chiến ở Nhóm 6 (từ vựng sai nghĩa, từ mượn, giọng sồn sã, bảng số liệu)."""
        # VIS-LEX-001: 'thực chứng' sai nghĩa vs 'chủ nghĩa thực chứng' đúng nghĩa
        r_bad_lex = self.scanner.scan_text("Hồ sơ dự án thực chứng này cho máy tính ghép để tìm dòng in đúp.")
        self.assertIn("VIS-LEX-001", {f.rule_id for f in r_bad_lex.findings})
        r_good_phil = self.scanner.scan_text("Bài viết phân tích trường phái chủ nghĩa thực chứng trong triết học thế kỷ XIX.")
        self.assertNotIn("VIS-LEX-001", {f.rule_id for f in r_good_phil.findings})

        # VIS-LEX-002: dịch ngược 'thư điện tử', từ tiếng Anh chưa nhập tịch 'workaround/cutover', nhưng cho phép 'email/website'
        r_rev = self.scanner.scan_text("Đơn vị gửi thư điện tử xin dùng workaround trước giờ cutover.")
        self.assertIn("VIS-LEX-002", {f.rule_id for f in r_rev.findings})
        r_nat = self.scanner.scan_text("Đơn vị gửi email kèm tài liệu pdf đăng trên website chính thức.", profile="audit_report")
        self.assertEqual(r_nat.findings_count, 0)

        # VIS-TONE-001: chào sồn sã & khen xã giao
        r_tone = self.scanner.scan_text(
            "Anh Khoa ơi, báo cáo ghi nhận sự nỗ lực rất lớn của nhóm nhưng vẫn còn rủi ro sát sườn.",
            profile="audit_report",
        )
        self.assertIn("VIS-TONE-001", {f.rule_id for f in r_tone.findings})

        # VIS-STRUCT-001: lộ nhãn dàn ý & vặn câu tuần tự né máy quét
        r_meta = self.scanner.scan_text(
            "Bước ngoặt tư duy: Hồ sơ thứ nhất lệch 5 triệu, sang hồ sơ thứ hai thiếu 5 triệu.",
            profile="social_media",
        )
        self.assertIn("VIS-STRUCT-001", {f.rule_id for f in r_meta.findings})

        # VIS-STRUCT-002: Title Case kiểu Anh, mục con đơn độc, đường dẫn file:/// không báo nhầm, bảng lệch tổng
        doc_struct = (
            "## 1. Hồ Sơ Dự Án Chọn Lọc\n"
            "### 1.1. Mục con duy nhất\n"
            "- Xem chi tiết tại [tài liệu gốc](file:///d:/Experiment/vietnamese-writing/README.md).\n\n"
            "| Khách hàng | Số dư |\n"
            "| --- | --- |\n"
            "| Bạn A | 100 |\n"
            "| Khách B | 200 |\n"
            "| Tổng cộng | 250 |\n"
        )
        r_struct = self.scanner.scan_text(doc_struct, profile="general")
        struct_hits = [f for f in r_struct.findings if f.rule_id == "VIS-STRUCT-002"]
        # Gồm: Title Case, mục con đơn độc, đại từ 'Bạn' trong bảng, và lệch Tổng cộng (250 != 300)
        self.assertGreaterEqual(len(struct_hits), 4)
        # Đường dẫn file:/// đã được che nên không bị bắt nhầm
        for f in struct_hits:
            self.assertNotIn("file:///", f.matched_text)

    def test_semantic_invariants_and_verify_safety(self) -> None:
        """Mọi ví dụ sửa mẫu trong bộ quy tắc phải bảo toàn số liệu, điều kiện và URL."""
        for rule in self.scanner.rules.values():
            if rule.rule_id == "VIS-FMT-005":
                continue
            ok, errs = SemanticMasker.validate_rewrite_safety(
                rule.bad_example, rule.better_example, strict_negations_and_modals=False
            )
            self.assertTrue(ok, f"Rule {rule.rule_id} làm lệch dữ kiện mẫu: {errs}")

        # Kiểm tra bắt lỗi làm rơi từ phủ định hoặc từ chỉ mức độ chắc chắn
        v_drop_modal = verify_text(
            "Phương án này có thể giảm 15% thời gian chờ nếu lưu lượng ổn định.",
            "Phương án này giảm 15% thời gian chờ nếu lưu lượng ổn định.",
        )
        self.assertFalse(v_drop_modal["passed"])

        v_drop_code = verify_text(
            "Chạy lệnh `python scripts/vi_scanner.py scan a.md` ngày 10/11/2026.",
            "Chạy lệnh `python scripts/vi_scanner.py scan b.md` ngày 10/11/2026.",
        )
        self.assertFalse(v_drop_code["passed"])

    def test_redos_linear_time_on_210k_chars(self) -> None:
        """Chuỗi tấn công lặp trên 210.000 ký tự phải quét xong dưới 500 ms."""
        adversarial = ("Trong bối cảnh nền kinh tế số " * 7200) + "!"
        self.assertGreater(len(adversarial), 210_000)
        t0 = time.perf_counter()
        _ = self.scanner.scan_text(adversarial)
        elapsed_ms = (time.perf_counter() - t0) * 1000.0
        self.assertLess(elapsed_ms, 500.0, f"Quét quá chậm ({elapsed_ms:.1f} ms), nghi ngờ ReDoS!")

    def test_maintenance_schedule_and_cli(self) -> None:
        """Kiểm tra cơ chế nhắc rà soát hàng quý/năm cho danh sách từ tiếng Anh quen dùng."""
        fresh = check_loanwords_maintenance(dt.date(2026, 12, 1))
        self.assertFalse(fresh["due_for_quarterly_review"])
        due_q = check_loanwords_maintenance(dt.date(2027, 3, 1))
        self.assertTrue(due_q["due_for_quarterly_review"])
        self.assertFalse(due_q["overdue_annual_review"])
        overdue_y = check_loanwords_maintenance(dt.date(2027, 12, 1))
        self.assertTrue(overdue_y["overdue_annual_review"])

        with tempfile.TemporaryDirectory() as tmp:
            sample = Path(tmp) / "clean.md"
            sample.write_text("Doanh thu quý IV đạt 120 tỷ đồng, tăng 10% so với kế hoạch.\n", encoding="utf-8")
            out_json = Path(tmp) / "report.json"
            rc = main(["scan", str(sample), "--json", "--output", str(out_json)])
            self.assertEqual(rc, 0)
            parsed = json.loads(out_json.read_text(encoding="utf-8"))
            self.assertEqual(parsed["profile"], "all")
            self.assertEqual(parsed["findings_count"], 0)

    def test_skill_repo_structure_manifests_and_self_lint(self) -> None:
        """Kiểm tra cấu trúc chuẩn Skill repo, manifest đa nền tảng, liên kết nội bộ và tự quét sạch 100% tài liệu."""
        import re

        skill_md = ROOT / "SKILL.md"
        self.assertTrue(skill_md.exists(), "Thiếu SKILL.md ở thư mục gốc")
        self.assertTrue((ROOT / "LICENSE").exists(), "Thiếu LICENSE")
        self.assertTrue((ROOT / "AGENTS.md").exists(), "Thiếu AGENTS.md")
        self.assertTrue((ROOT / "scripts" / "vi_scanner.py").exists(), "Thiếu scripts/vi_scanner.py")
        self.assertTrue((ROOT / "references" / "rule-catalog.md").exists(), "Thiếu references/rule-catalog.md")
        self.assertTrue((ROOT / "references" / "loanwords-and-exceptions.md").exists(), "Thiếu references/loanwords-and-exceptions.md")

        skill_text = skill_md.read_text(encoding="utf-8")
        fm_match = re.match(r"\A---\n([\s\S]+?)\n---\n", skill_text)
        self.assertIsNotNone(fm_match, "SKILL.md thiếu YAML frontmatter")
        fm = fm_match.group(1) if fm_match else ""
        self.assertRegex(fm, r"(?m)^name:\s*vietnamese-writing\s*$")
        self.assertRegex(fm, r"(?m)^description:")
        self.assertRegex(fm, r"(?m)^license:\s*MIT\s*$")

        for manifest_rel in (
            ".claude-plugin/plugin.json",
            ".claude-plugin/marketplace.json",
            ".cursor-plugin/plugin.json",
        ):
            mpath = ROOT / manifest_rel
            self.assertTrue(mpath.exists(), f"Thiếu {manifest_rel}")
            mdata = json.loads(mpath.read_text(encoding="utf-8"))
            self.assertEqual(mdata["name"], "vietnamese-writing")

        md_docs = [
            ROOT / "SKILL.md",
            ROOT / "AGENTS.md",
            ROOT / "README.md",
            ROOT / "references" / "rule-catalog.md",
            ROOT / "references" / "loanwords-and-exceptions.md",
        ]
        link_re = re.compile(r"\[[^\]]+\]\(([^)#\s]+)")
        for doc_path in md_docs:
            txt = doc_path.read_text(encoding="utf-8")
            for m in link_re.finditer(txt):
                target = m.group(1)
                if "://" in target or target.startswith("mailto:"):
                    continue
                resolved = (doc_path.parent / target).resolve()
                self.assertTrue(resolved.exists(), f"Liên kết hỏng '{target}' trong {doc_path.name}")

            rep = self.scanner.scan_text(txt, profile="all")
            self.assertEqual(
                rep.findings_count,
                0,
                f"Tài liệu {doc_path.name} của chính Skill bị gắn cờ: {[f.rule_id + ':' + f.matched_text for f in rep.findings]}",
            )

        for rule in self.scanner.rules.values():
            rep_ex = self.scanner.scan_text(rule.better_example, profile="all")
            self.assertEqual(
                rep_ex.findings_count,
                0,
                f"Câu mẫu sửa đúng của {rule.rule_id} lại bị chính máy quét gắn cờ: {rep_ex.findings}",
            )

    def test_zero_hardcoded_project_leaks_in_repo(self) -> None:
        """Đảm bảo không tệp mã nguồn hay tài liệu nào trong repo chứa chuỗi dự án nội bộ cũ.
        Dùng mã băm SHA-256 của từng token nhạy cảm để ngay cả tệp test cũng không lưu chữ thô.
        """
        forbidden_token_sha256 = {
            "de5361d8112f0dde7953be6b17d6b77a3b045f4cc4c7de3b3f4795c0804c4972",
            "c46de749138d2338c289accea4b71af71cce21ca378e42cf73273c1a1fb00e7b",
            "55b3da6b0f5d7a66861544492455a146aac5c3f2bd6810969bad7756d43c9a99",
            "bd3dcf25ed023afb49c1ad1f154f4eeb7d8e51087718fc5cbc284ba556683280",
            "d9947bbf8f34c7bd1f3739112048993f8253f1cabe6f8441736d6ca2e78d9252",
            "3ec20fe6b71dc063cbbd7c283c606c30fe10577857c34d2563f61400b49078ad",
        }
        tracked_files = [
            ROOT / "scripts" / "vi_scanner.py",
            ROOT / "SKILL.md",
            ROOT / "AGENTS.md",
            ROOT / "README.md",
            ROOT / "LICENSE",
            ROOT / "references" / "rule-catalog.md",
            ROOT / "references" / "loanwords-and-exceptions.md",
            ROOT / ".claude-plugin" / "plugin.json",
            ROOT / ".claude-plugin" / "marketplace.json",
            ROOT / ".cursor-plugin" / "plugin.json",
            Path(__file__).resolve(),
        ]
        import re

        for fpath in tracked_files:
            content = fpath.read_text(encoding="utf-8")
            tokens = set(re.findall(r"[A-Za-z0-9_./-]+", content))
            for tok in tokens:
                h = hashlib.sha256(tok.lower().encode("utf-8")).hexdigest()
                self.assertNotIn(h, forbidden_token_sha256, f"Phát hiện token nhạy cảm trong {fpath.name}")
            self.assertNotRegex(content, r"\b212\s+đơn vị kinh doanh\b")
            self.assertNotRegex(content, r"\b226\s+đơn vị\b")


if __name__ == "__main__":
    unittest.main()
