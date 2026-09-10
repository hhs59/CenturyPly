"""Prompt and approved reference configuration for Century Ply portraits."""

from __future__ import annotations

import hashlib
from collections.abc import Mapping
from pathlib import Path
from typing import Any


REFERENCE_ROOT = Path(__file__).with_name("reference_images")


def _lines(*values: str) -> str:
    return "\n".join(values)


_COMPOSITION_RULES = (
    "một người chiếm khoảng 52–62% chiều cao ảnh, đứng giữa hoặc lệch nhẹ; đầu, mặt, hai tay, gấu áo và hai bàn chân đều nằm trong khung.",
    "cặp hai người cân bằng, mặt có kích thước tương đương và cùng mặt phẳng nét; có khe hở nhỏ giữa thân, vai không dính, tay không chéo qua mặt hoặc thân người kia.",
    "ba người xếp tam giác/vòng cung nông, không ai nhỏ hơn đáng kể; mọi mặt không bị che, không có đầu trực tiếp sau đầu khác, sáu bàn tay và gấu áo/chân phân biệt được.",
    "bốn người xếp vòng cung nông hoặc hai trung tâm/hai bên trên một lớp sâu; bốn đầu tách biệt, không hai hàng sâu, tay không cắt qua mặt/thân và tất cả bàn chân cùng gấu áo còn trong khung.",
)


def _pose_variants(
    names: tuple[str, str, str],
    actions: tuple[tuple[str, str, str, str], tuple[str, str, str, str], tuple[str, str, str, str]],
    expressions: tuple[str, str, str],
) -> str:
    lines: list[str] = []
    for number, (name, count_actions, expression) in enumerate(zip(names, actions, expressions, strict=True), start=1):
        lines.append(f"BIẾN THỂ {number} — {name}")
        for count, (action, composition) in enumerate(zip(count_actions, _COMPOSITION_RULES, strict=True), start=1):
            lines.append(f"- {count} người: {action} Giữ {composition}")
        lines.append(f"- Biểu cảm: {expression}")
    return "\n".join(lines)


def _clothing(details: str, reference: str) -> str:
    return (
        f"{details} "
        f"Chỉ dùng {reference} để lấy trang phục và phụ kiện; không sao chép khuôn mặt, tỷ lệ cơ thể, tóc, tư thế, vị trí tay, hướng nhìn, biểu cảm, góc máy, ánh sáng hoặc hậu cảnh người mẫu."
    )


SCENARIO_CONFIGS = {
    "thang_long_imperial": {
        "concept_prompt": _lines(
            "Ý NIỆM VÀ KHÔNG KHÍ:",
            "Chân dung nghi lễ của khách mời quan trọng đang đến Hoàng Thành Thăng Long, thể hiện sự trang nghiêm, hiếu khách và niềm tự hào văn hóa trong một bộ ảnh sự kiện cao cấp.",
            "KIẾN TRÚC BẮT BUỘC:",
            "Tái dựng đúng Đoan Môn của Hoàng Thành Thăng Long trong ẢNH 4: bệ thành gạch đá dài đã nhuốm thời gian có năm cửa vòm, cửa chính giữa lớn nhất và bốn cửa nhỏ hơn ở hai bên; phía trên là lầu trung tâm ba tầng, mái ngói cong và tường vàng đất. Đây là công trình bắt buộc, không thay bằng một cổng cung đình bất kỳ.",
            "DẤU HIỆU NHẬN DIỆN BẮT BUỘC:",
            "Trong một lần nhìn phải thấy đồng thời đủ năm cửa vòm, khối lầu trung tâm ba tầng và mảng tường thành gạch xám–vàng kéo dài. Giữ đúng nhịp một cửa lớn ở giữa và hai cửa nhỏ mỗi bên, hình khối, vật liệu cùng góc nhìn ba phần tư của ẢNH 4.",
            "BỐ CỤC KHÔNG GIAN:",
            "Đặt nhóm khách trên sân ở tiền cảnh, lệch nhẹ khỏi trục để cửa chính giữa, ít nhất hai cửa bên và lầu trung tâm còn nhìn rõ. Công trình chiếm phần lớn nửa trên hậu cảnh, đủ nét để nhận ra ngay; không làm mờ mạnh và không để mái hoặc cạnh cổng xuyên qua đầu người.",
            "ÁNH SÁNG VÀ MÀU SẮC:",
            "Ánh sáng ban ngày miền Bắc trong trẻo, bóng mềm. Bảng màu gồm gạch ấm, đỏ son tiết chế, xanh chàm đậm, gỗ nâu và sắc kiến trúc đã cũ; da người tự nhiên.",
            "KHÔNG ĐƯỢC XUẤT HIỆN:",
            "Không có cổng Ngọ Môn sơn đỏ, nội thất ngai vàng Điện Thái Hòa, mặt tiền Pháp màu vàng của Cung An Định, lam bê tông Dinh Độc Lập, núi đá Hoa Lư, cung điện kỳ ảo kiểu Trung Hoa, biển hiệu/chữ hoặc đám đông.",
        ),
        "male_clothing": _clothing(
            "Khách nam mặc áo tấc lễ nghi Việt Nam màu xanh chàm đậm, cảm hứng cổ phục miền Bắc. Thân áo dài qua gối, phom thẳng, cổ đứng kín và hàng khuy phía trước; tay áo dài rộng, có lớp áo trong ở cổ/cổ tay. Vải lụa hoặc gấm mờ có trọng lượng, thêu trang nhã ở ngực, viền cổ và tay áo; khăn đóng đúng cấu trúc mẫu, quần dài màu trầm và giày kín mũi khi thấy. Khi đứng hoặc bước nhẹ, tà và tay áo rủ theo trọng lực.",
            "ẢNH 2",
        ),
        "female_clothing": _clothing(
            "Khách nữ mặc áo tấc nghi lễ đỏ son với mấn được duyệt, cảm hứng cổ phục miền Bắc. Thân áo dài qua gối, nhiều lớp gọn, cổ đứng kín và hàng khuy trước thân; tay áo dài rộng vừa phải, lớp áo trong nhìn thấy. Vải lụa/gấm bóng vừa phải, thêu ở cổ, ngực, viền tay và viền tà; mấn không che mắt, quần dài và giày kín mũi khi thấy. Khi xoay hoặc bước nhẹ, tà áo chuyển động mềm và không che bàn chân.",
            "ẢNH 3",
        ),
        "pose_expression": _pose_variants(
            ("ĐÓN KHÁCH QUA ĐOAN MÔN", "BƯỚC TRÊN SÂN GẠCH", "TỰ HÀO TRƯỚC HOÀNG THÀNH"),
            (
                ("đứng hơi lệch trục, một chân dẫn nhẹ và một tay giữ hờ tay áo.", "đứng thành cặp, một người tiến nửa bước và người kia xoay vai về Đoan Môn.", "tạo vòng cung nông hướng vào trục cổng, người giữa tiến nhẹ.", "tạo vòng cung nông một lớp, hai người giữa ở trục cổng và hai người ngoài xoay vào."),
                ("bước chậm về máy ảnh trên sân gạch, vai mở và tà áo chuyển động.", "hai khách bước cùng hướng, một người dẫn rất ít và người kia xoay về bạn đồng hành.", "ba khách bước theo hàng cong nông, người giữa gần máy ảnh hơn rất ít.", "bốn khách tiến nhẹ theo vòng cung nông, không tạo hai hàng."),
                ("đứng cân bằng hơi xoay ba phần tư, tay thả tự nhiên hoặc giữ hờ tay áo.", "đứng cạnh nhau với vai và hướng nhìn hơi khác.", "tạo tam giác nông, người giữa chỉ nhô nhẹ và hai bên xoay vào.", "tạo bố cục hai trung tâm/hai bên trên một lớp nông, vai và tay khác nhau."),
            ),
            ("điềm tĩnh, tự tin, hiếu khách và tự hào; nụ cười nhẹ khác nhau.", "tự tin và thân thiện; ánh mắt có thể lệch nhẹ về Đoan Môn nhưng mặt vẫn rõ.", "tự hào kín đáo, bình tĩnh và trang trọng; không diễn kịch."),
        ),
        "male": "thang-long-imperial-male.jpg",
        "female": "thang-long-imperial-female.jpg",
        "location": "thang-long-imperial-scene.jpg",
    },
    "hoa_lu_capital": {
        "concept_prompt": _lines(
            "Ý NIỆM VÀ KHÔNG KHÍ:",
            "Chân dung nghi lễ gắn với Cố đô Hoa Lư và ký ức về kinh đô đầu thời Đinh–Tiền Lê. Khách mời quan trọng vững chãi, gần gũi với thiên nhiên và tự tin tiết chế giữa núi đá.",
            "KIẾN TRÚC BẮT BUỘC:",
            "Tái dựng đúng khu Đền Vua Đinh Tiên Hoàng tại Cố đô Hoa Lư trong ẢNH 4: lối nghi lễ lát gạch chạy thẳng giữa hai lan can đá phong hóa, hai trụ biểu đá cao phía trước, chính điện mái ngói nâu thấp ở cuối trục và các khối núi đá vôi dựng đứng phủ cây phía sau.",
            "DẤU HIỆU NHẬN DIỆN BẮT BUỘC:",
            "Dãy núi karst đá vôi phải chiếm đường chân trời và hiện rõ phía trên mái Đền Vua Đinh; hai trụ biểu đá, lối đi chính giữa và lan can đá phải dẫn mắt thẳng tới chính điện. Các yếu tố này phải xuất hiện đồng thời và bám sát ẢNH 4.",
            "BỐ CỤC KHÔNG GIAN:",
            "Đặt khách trên phần lối đi trống ở tiền cảnh, tránh che cả hai trụ biểu, mái chính điện và đỉnh núi. Chính điện nằm giữa hậu cảnh, núi cao hiện rõ hai bên và phía trên; dùng độ sâu trường ảnh vừa phải để đá, mái và núi vẫn nhận diện được.",
            "ÁNH SÁNG VÀ MÀU SẮC:",
            "Ánh sáng tự nhiên ấm của buổi sáng hoặc cuối buổi chiều, bóng mềm và da người tự nhiên. Bảng màu gồm xám đá, đỏ đất, nâu gỗ, xanh rừng và xanh xám núi.",
            "KHÔNG ĐƯỢC XUẤT HIỆN:",
            "Không dùng tường thành vàng Hoàng Thành, cổng đỏ Ngọ Môn, đại sảnh ngai vàng Huế, biệt thự Pháp, tòa nhà hiện đại, lâu đài kỳ ảo, sương che kín núi, tượng không liên quan, biển hiệu hoặc đám đông.",
        ),
        "male_clothing": _clothing(
            "Khách nam mặc lễ phục lấy cảm hứng Đinh–Tiền Lê màu đỏ rượu vang sẫm. Áo dài qua gối, phom chắc, cổ đứng kín và hàng khuy trước thân; tay áo dài rộng vừa phải, lớp áo trong ở cổ/cổ tay. Vải gấm hoặc lụa dày mờ, hoa văn cổ thêu ở ngực, viền cổ và tay áo, màu phụ đỏ đất/vàng trầm; khăn đóng theo mẫu, quần dài cùng tông và giày kín mũi. Khi đứng vững hoặc bước một chân, tà áo rủ nặng tự nhiên.",
            "ẢNH 2",
        ),
        "female_clothing": _clothing(
            "Khách nữ mặc lễ phục xanh rừng đậm. Áo dài hoặc áo tấc dài qua gối, thân thanh thoát, cổ đứng kín và hàng khuy trước thân; tay áo dài rộng vừa phải, có lớp áo trong. Vải lụa/gấm rủ thật, thêu ở cổ, thân trước, viền tay và tà, màu phụ xanh rêu/vàng đồng tiết chế; mấn được duyệt, quần dài và giày kín mũi. Khi đứng ổn định giữa sân, tà áo rơi thẳng và không che bàn chân.",
            "ẢNH 3",
        ),
        "pose_expression": _pose_variants(
            ("ĐỨNG CÙNG NÚI ĐÁ", "KẾT NỐI VỚI SÂN ĐỀN", "NHÌN VỀ HOA LƯ"),
            (
                ("đứng thẳng trước cổng, thân hơi xoay và hai tay đặt nhẹ trước thân.", "đứng cạnh nhau trên cùng mặt phẳng, khoảng hở nhỏ, vai và tay khác nhau.", "tạo tam giác nông, người giữa hơi tiến và hai bên hướng nhẹ về núi.", "tạo vòng cung nông trước cổng, cùng một lớp sâu và hai người ngoài xoay vào."),
                ("một chân bước nhẹ, vai xoay theo cổng và một tay thả tự nhiên.", "một người bước rất nhẹ, người còn lại đứng cạnh nhưng không tạo hàng sâu.", "đứng lệch nhẹ thành cung nông, người giữa nhìn máy ảnh và hai bên hướng về cổng.", "tạo bố cục hai người trung tâm/hai bên trên mặt phẳng nông, vai khác nhau."),
                ("đứng hơi lệch trục, mắt hướng nhẹ về núi nhưng mặt đủ rõ.", "một người nhìn máy ảnh, một người nhìn núi, đứng gần nhưng không chạm vai.", "vòng cung nông, người giữa quay về máy ảnh và hai bên hướng cảnh quan.", "vòng cung rộng vừa đủ thấy núi, bốn đầu tách biệt và không có hàng sau."),
            ),
            ("ổn định, bình thản, ấm áp và tự hào kín đáo.", "tự tin tiết chế, ánh mắt có chiều sâu; một nụ cười nhẹ là đủ.", "điềm tĩnh, chân thành, tự hào và kết nối cảnh quan."),
        ),
        "male": "hoa-lu-capital-male.jpg",
        "female": "hoa-lu-capital-female.jpg",
        "location": "hoa-lu-capital-scene.jpg",
    },
    "hue_imperial_city": {
        "concept_prompt": _lines(
            "Ý NIỆM VÀ KHÔNG KHÍ:",
            "Chân dung đón tiếp thanh lịch trong Đại Nội Huế, thể hiện vẻ mềm mại, quyền quý và hiếu khách của triều đình Nguyễn. Đây là ảnh đón tiếp cao cấp với người thật, không phải cung điện Đông Á kỳ ảo.",
            "KIẾN TRÚC BẮT BUỘC:",
            "Tái dựng đúng Ngọ Môn theo ẢNH 4: đài thành đá–gạch hình chữ U có năm lối vào, phía trên là Lầu Ngũ Phụng bằng gỗ sơn son với chín bộ mái; mái chính giữa lợp ngói lưu ly vàng và tám mái còn lại lợp ngói xanh. Không đổi thành một cổng thành một tháp.",
            "DẤU HIỆU NHẬN DIỆN BẮT BUỘC:",
            "Trong khung hình dọc phải thấy rõ phần giữa của đài chữ U, cửa chính giữa, các lầu gỗ đỏ đối xứng và sự tương phản giữa mái vàng trung tâm với các mái xanh hai bên. Cho phép cắt bớt phần kéo dài ngoài cùng để phù hợp tỷ lệ 9:16, nhưng phải giữ hình khối Lầu Ngũ Phụng và đủ dấu hiệu nhận diện từ ẢNH 4.",
            "BỐ CỤC KHÔNG GIAN:",
            "Đặt khách ở sân đá rộng phía trước, thấp hơn đường mái và không che cổng trung tâm. Phần nhận diện chính của Ngọ Môn nằm rõ ở nửa trên hậu cảnh; chỉ tách nền nhẹ để kiến trúc vẫn đủ nét.",
            "ÁNH SÁNG VÀ MÀU SẮC:",
            "Ánh sáng ban ngày vàng ấm nhưng tự nhiên, tương phản vừa phải và da người không bị vàng. Bảng màu sơn đỏ, mái ngói, xanh cổ vịt đậm, tím hoàng gia, gỗ nâu và vàng tiết chế.",
            "KHÔNG ĐƯỢC XUẤT HIỆN:",
            "Không chuyển cảnh vào nội thất ngai vàng Điện Thái Hòa, không dùng cổng thành vàng Hoàng Thành Thăng Long, đền giữa núi Hoa Lư, bia mộ, công trình hiện đại, kiến trúc kỳ ảo kiểu Trung Hoa, chữ/biển hiệu hoặc khách du lịch.",
        ),
        "male_clothing": _clothing(
            "Khách nam mặc áo ngũ thân nghi lễ xanh cổ vịt đậm và khăn đóng, lấy cảm hứng từ lễ phục triều Nguyễn. Thân áo dài qua gối, phom thẳng, cổ đứng kín, hàng khuy trước thân và áo trong hiện ở cổ; tay áo dài rộng vừa phải. Vải lụa/gấm mờ cao cấp, thêu ở cổ, ngực, tay và viền với điểm vàng/đồng; quần dài sẫm và giày kín mũi. Khi bước chậm hoặc xoay ba phần tư, tà áo giữ nếp. Giữ dáng toàn thân cân đối và khí chất nghi lễ tự nhiên; không sao chép tư thế từ ảnh trang phục.",
            "ẢNH 2",
        ),
        "female_clothing": _clothing(
            "Khách nữ mặc áo Nhật Bình tím hoàng gia và mấn. Áo dài dưới gối, thân trang trọng, cổ đứng hoặc viền cổ kín, hàng khuy trước thân, tay áo dài rủ; lớp áo trong, quần dài và giày kín mũi khi phù hợp. Vải lụa/gấm bóng vừa phải, họa tiết hoa lá/cung đình được thêu tập trung ở cổ, ngực, tay và viền tà, mấn không che mắt. Khi xoay hoặc bước chậm, tà và tay áo chuyển động mềm, không giẫm lên chân.",
            "ẢNH 3",
        ),
        "pose_expression": _pose_variants(
            ("TIẾP ĐÓN TRONG SÂN ĐẠI NỘI", "ĐÓN KHÁCH TRÊN TRỤC KIẾN TRÚC", "NÉT DUYÊN CUNG ĐÌNH"),
            (
                ("đứng ba phần tư, một tay nâng rất nhẹ mép tay áo và tay kia tự nhiên.", "đứng thành cặp với vai khác góc, một người hướng sân và một người hướng máy ảnh.", "tạo vòng cung nông, người giữa tiến nhẹ và hai bên xoay vào trung tâm.", "tạo vòng cung nông trước lớp cột/cổng, bốn mặt cùng lớp nét."),
                ("bước chậm nửa nhịp về trước, vai mở và mặt hướng máy ảnh.", "hai người di chuyển nhẹ trên trục, một người dẫn và người kia xoay về trung tâm.", "xếp cung nông, người giữa tiến nhẹ và hai bên giữ độ cao mặt tương đương.", "hai người giữa tiến ít, hai người ngoài lùi ít để tạo cung một lớp."),
                ("đứng nghiêng ba phần tư, một tay chạm hờ tay áo, cằm và vai thả lỏng.", "đứng cạnh nhau với khoảng cách nhỏ, hướng nhìn hơi khác.", "tạo tam giác nông, người giữa vừa đủ trung tâm và hai bên xoay vào.", "tạo hai trung tâm/hai bên, vai khác nhau và bốn đầu tách biệt."),
            ),
            ("thanh lịch, điềm tĩnh, mềm mại; nụ cười nhẹ khác nhau.", "quyền quý nhưng gần gũi; không cười đồng loạt.", "tinh tế, tự tin, dịu và có thẩm quyền mềm."),
        ),
        "male": "hue-imperial-city-male.jpg",
        "female": "hue-imperial-city-female.jpg",
        "location": "hue-imperial-city-scene.jpg",
    },
    "thai_hoa_palace": {
        "concept_prompt": _lines(
            "Ý NIỆM VÀ KHÔNG KHÍ:",
            "Chân dung nghi lễ chính thức trước Điện Thái Hòa, thể hiện quyền uy bình tĩnh và sự đón tiếp trang trọng dành cho khách mời quan trọng. Cảnh sân chầu trang nghiêm, cân đối và chân thực, không phải nội thất ngai vàng hay cung điện kỳ ảo.",
            "KIẾN TRÚC BẮT BUỘC:",
            "Tái dựng đúng mặt chính Điện Thái Hòa trong ẢNH 4: đại điện một tầng kéo dài theo phương ngang, hệ mái kép lợp ngói lưu ly vàng, hàng linh vật trang trí trên bờ nóc, hiên gỗ tối với dãy cột đều nhau, cửa gỗ nâu đỏ và sân Đại Triều Nghi lát đá rộng phía trước.",
            "DẤU HIỆU NHẬN DIỆN BẮT BUỘC:",
            "Phải nhìn thấy đồng thời hai lớp mái vàng chạy ngang, bờ nóc trang trí rồng, hàng cột hiên và sân đá chính diện rộng. Giữ đúng tỷ lệ đại điện thấp, dài, đối xứng và không biến công trình thành Ngọ Môn nhiều lầu.",
            "BỐ CỤC KHÔNG GIAN:",
            "Đặt khách trên sân Đại Triều Nghi ở tiền cảnh, lệch nhẹ khỏi trục cửa giữa. Chừa khoảng nhìn giữa nhóm để bậc thềm, hàng cột hiên và cả hai lớp mái vẫn rõ; không đặt khách trên hiên hoặc che kín cửa chính.",
            "ÁNH SÁNG VÀ MÀU SẮC:",
            "Ánh sáng ban ngày dịu, hơi ấm, làm rõ ngói vàng, gỗ nâu đỏ và nền sân đá mà không cháy sáng. Da người tự nhiên, hậu cảnh đủ nét, không dùng đèn rọi kiểu sân khấu.",
            "KHÔNG ĐƯỢC XUẤT HIỆN:",
            "Không tạo nội thất ngai vàng, hàng cột rồng trong điện, mặt ngoài Ngọ Môn, cổng nhiều tầng, không để khách ngồi ngai, không vương miện khổng lồ, giáp kỳ ảo, đồ hiện đại, chữ giả hoặc vàng lấp kín cảnh.",
        ),
        "male_clothing": _clothing(
            "Khách nam mặc lễ phục lấy cảm hứng từ long bào vàng hoàng gia, thể hiện tinh thần nghi lễ Việt Nam tinh tế. Áo dài qua gối, thân có trọng lượng, cổ đứng kín, hàng khuy trước thân, tay áo dài rộng vừa phải và lớp áo trong ở cổ/tay. Vải gấm/lụa dày mờ, họa tiết rồng được duyệt và chỉ thêu ở ngực, vai, tay và viền, màu phụ đỏ son/đồng; khăn đóng theo mẫu, quần dài và giày kín mũi. Khi đứng cân bằng, tà áo rủ thẳng, không thành áo giáp hoặc áo choàng kỳ ảo.",
            "ẢNH 2",
        ),
        "female_clothing": _clothing(
            "Khách nữ mặc lễ phục lấy cảm hứng từ phượng bào đỏ thẫm. Áo dài qua gối, thân gọn, cổ đứng kín, hàng khuy trước thân, tay áo dài và lớp áo trong ở cổ/tay; tà áo có trọng lượng. Vải gấm/lụa đỏ, điểm vàng/cam đồng; họa tiết phượng được thêu ở ngực, vai, tay, cổ và viền tà, không thành giáp hoặc váy dạ hội. Mấn đúng mẫu, quần dài và giày kín mũi. Khi xoay vai hoặc đặt tay trước thân, tà áo rơi tự nhiên và bàn chân rõ.",
            "ẢNH 3",
        ),
        "pose_expression": _pose_variants(
            ("TRỤC ĐẠI LỄ", "CỬ CHỈ NGHI LỄ TIẾT CHẾ", "ĐÓN TIẾP TRANG TRỌNG"),
            (
                ("đứng cân bằng trên trục sân chầu, hai tay đặt nhẹ trước thân.", "đứng đối xứng mềm trên sân với khoảng hở nhỏ, không che cửa giữa.", "người giữa hơi tiến, hai người bên lệch thành vòng cung nông để lộ bậc thềm và mái điện.", "tạo cung nông hoặc hai trung tâm/hai bên trên sân đá, không che trục chính điện."),
                ("thân hơi xoay ba phần tư trên sân, một tay thả dọc tà áo và tay kia tự nhiên.", "một người xoay vào trung tâm, người kia hướng nhẹ về chính điện, tay không giao nhau.", "tạo vòng cung nông trước bậc thềm, người giữa nhìn máy ảnh và hai bên hướng về giữa.", "hai người giữa cân bằng, hai người ngoài xoay vào trên cùng một lớp, chừa khoảng nhìn tới cửa giữa."),
                ("đứng hơi lệch trục trước chính điện như chủ nhà, một chân dẫn nhẹ và tay giữ hờ tà.", "đứng cân bằng trước bậc thềm nhưng hướng vai khác nhau.", "tạo tam giác nông trên sân đá, người giữa tiến rất ít và hai bên giữ vai mở.", "tạo cung nông với hai trung tâm và hai bên trước hàng cột hiên, bốn đầu cách nhau rõ."),
            ),
            ("uy nghi, bình tĩnh, tự tin; nụ cười rất nhẹ.", "thẩm quyền mềm và tự chủ, không cười đồng loạt.", "trang trọng, điềm đạm, tự hào và chuyên nghiệp."),
        ),
        "male": "thai-hoa-palace-male.jpg",
        "female": "thai-hoa-palace-female.jpg",
        "location": "thai-hoa-palace-scene.jpg",
    },
    "an_dinh_palace": {
        "concept_prompt": _lines(
            "Ý NIỆM VÀ KHÔNG KHÍ:",
            "Chân dung đón tiếp thân mật tại Cung An Định, kết hợp sự duyên dáng thời Nguyễn với tinh thần kiến trúc châu Âu. Không khí thanh lịch, gần gũi và có chiều sâu như một bộ ảnh cao cấp.",
            "KIẾN TRÚC BẮT BUỘC:",
            "Tái dựng đúng Khải Tường Lâu ba tầng theo ẢNH 4: mặt tiền vàng mù tạt, các cột cổ điển màu trắng, phù điêu vữa trắng dày đặc hình hoa lá và huy hiệu, ban công lan can con tiện, ô cửa vòm cùng trán giữa trang trí cầu kỳ theo phong cách Nguyễn–châu Âu.",
            "DẤU HIỆU NHẬN DIỆN BẮT BUỘC:",
            "Mảng tường vàng, cột trắng, phù điêu hoa lá trắng, ban công con tiện và trán giữa cầu kỳ phải cùng hiện diện. Giữ góc nhìn hơi thấp và chính diện như ẢNH 4 để mặt tiền nhận ra ngay; đây không phải biệt thự Pháp màu trắng thông thường.",
            "BỐ CỤC KHÔNG GIAN:",
            "Đặt khách ở sân tiền cảnh, lệch khỏi trục cửa và ban công để ít nhất hai tầng mặt tiền cùng phần trán giữa còn nhìn rõ. Không để cây hoặc họa tiết trang trí che người hay che các phù điêu nhận diện.",
            "ÁNH SÁNG VÀ MÀU SẮC:",
            "Ánh sáng ấm mềm như cuối buổi chiều hoặc dưới hiên. Bảng màu vàng cung điện, trắng ngà, xanh lam ngọc, gỗ nâu và xanh cây tiết chế; vải và da không bóng nhựa.",
            "KHÔNG ĐƯỢC XUẤT HIỆN:",
            "Không biến thành mặt tiền trắng đối xứng của Dinh Gia Long, không lam bê tông Dinh Độc Lập, không cổng thành/mái cung đình, phòng khiêu vũ kiểu Pháp chung chung, chi tiết trang trí kỳ ảo quá mức, người đi ngang hoặc vật thể hiện đại.",
        ),
        "male_clothing": _clothing(
            "Khách nam mặc áo ngũ thân phong cách Nguyễn màu ngà ấm. Áo dài qua gối, phom thẳng, cổ đứng kín, hàng khuy trước thân và lớp áo trong ở cổ/tay; tay áo dài vừa rộng. Vải lụa, gấm nhẹ hoặc vải pha cotton–lụa, thêu vàng nhạt/nâu ở cổ, ngực, viền tay và tà; khăn đóng theo mẫu, quần dài trung tính và giày kín mũi. Khi đứng ba phần tư hoặc bước nhẹ, tà áo giữ nếp thanh lịch.",
            "ẢNH 2",
        ),
        "female_clothing": _clothing(
            "Khách nữ mặc áo dài phong cách Nguyễn màu xanh lam ngọc. Thân áo dài qua gối, phom thanh lịch, cổ đứng kín, hàng khuy trước thân, tay dài và tà rủ; quần dài, lớp áo trong nếu có và giày kín mũi. Vải lụa/gấm bóng vừa phải, thêu vàng/xanh nhạt ở cổ, ngực, viền tay và dọc tà, không thành trang phục dạ hội đính kim sa; phụ kiện đầu được duyệt không che mắt. Khi xoay ba phần tư hoặc bước nhẹ, tà và tay áo chuyển động mềm.",
            "ẢNH 3",
        ),
        "pose_expression": _pose_variants(
            ("DUYÊN DÁNG TRƯỚC MẶT TIỀN", "BƯỚC NHẸ TRONG SÂN", "TIẾP KHÁCH TRONG KHOẢNG SÂN"),
            (
                ("đứng ba phần tư trước mặt tiền, một tay giữ hờ tay áo.", "đứng thành cặp với khoảng hở nhỏ, vai khác góc và hướng nhẹ vào nhau.", "tạo tam giác nông trước cửa đối xứng, giữa nổi bật vừa phải.", "tạo vòng cung nông theo sân, giữa gần trục và ngoài xoay vào."),
                ("một chân bước nhẹ, thân thả lỏng và vai hơi xoay.", "một người bước trước rất ít, người kia giữ nhịp bên cạnh.", "ba người đứng lệch thành cung nông, giữa nhìn máy ảnh và hai bên nhìn vào nhau.", "hai người giữa tiến nhẹ, hai người bên giữ khoảng hở cùng một lớp sâu."),
                ("đứng hơi lệch để lộ mặt tiền, vai mở và một tay hướng về không gian.", "đứng cạnh nhau, một người hướng máy ảnh và người kia hướng mặt tiền.", "tạo vòng cung nông, giữa hướng người xem và hai bên xoay vào.", "tạo hai trung tâm/hai bên với vai và trọng tâm khác nhau."),
            ),
            ("thân thiện, tinh tế, tự tin; nụ cười nhẹ.", "nhẹ nhàng, hiếu khách và thanh lịch; mức cười khác nhau.", "duyên dáng, ấm áp, điềm tĩnh và có phong thái chủ nhà."),
        ),
        "male": "an-dinh-palace-male.jpg",
        "female": "an-dinh-palace-female.jpg",
        "location": "an-dinh-palace-scene.jpg",
    },
    "independence_palace": {
        "concept_prompt": _lines(
            "Ý NIỆM VÀ KHÔNG KHÍ:",
            "Chân dung nghi lễ hiện đại tại Dinh Độc Lập/Dinh Thống Nhất, thể hiện khách mời quốc tế hòa mình vào văn hóa Việt Nam với phong thái tự tin, trang trọng và gần gũi. Đây là bộ ảnh đón tiếp cao cấp, không phải cảnh cung đình cổ.",
            "KIẾN TRÚC BẮT BUỘC:",
            "Tái dựng đúng mặt tiền chính Dinh Độc Lập trong ẢNH 4: khối nhà hiện đại thấp và rất rộng màu trắng–xám, hàng lam bê tông đứng lặp đều như rèm hoa đá, ban công trung tâm, đài phun nước tròn và thảm cỏ xanh lớn phía trước.",
            "DẤU HIỆU NHẬN DIỆN BẮT BUỘC:",
            "Trong khung hình dọc phải thấy rõ nhịp lam bê tông đứng, ban công giữa, đài phun nước tròn và thảm cỏ. Cho phép cắt đối xứng phần ngoài cùng của hai cánh nhà để phù hợp tỷ lệ 9:16, nhưng phải giữ trục chính diện và đủ dấu hiệu để nhận ra ngay Dinh Độc Lập, không phải văn phòng hiện đại bất kỳ.",
            "BỐ CỤC KHÔNG GIAN:",
            "Đặt nhóm khách trên thảm cỏ hoặc lối trước đài phun, hơi lệch khỏi trục giữa để không che vòi phun và ban công. Phần trung tâm cùng nhịp lam đặc trưng nằm rõ ở nửa trên hậu cảnh và vẫn đủ nét; chỉ tách nền nhẹ.",
            "ÁNH SÁNG VÀ MÀU SẮC:",
            "Ánh sáng ban ngày miền Nam sáng, mềm và sạch, tương phản vừa phải. Da người tự nhiên; kiến trúc trắng/xám, cỏ xanh, trang phục tím hoặc ngà là điểm màu chính. Không dùng đèn rọi tím/vàng giả hoặc hiệu ứng tương phản động quá mức.",
            "KHÔNG ĐƯỢC XUẤT HIỆN:",
            "Không có mặt tiền thuộc địa với cột/vòm của Dinh Gia Long, mặt tiền vàng Cung An Định, mái cung đình Nguyễn, cột rồng, đền chùa, ngai vàng, lâu đài châu Âu, chữ/biển hiệu, giao thông hoặc người đi ngang.",
        ),
        "male_clothing": _clothing(
            "Khách nam mặc áo dài nghi lễ Việt Nam màu ngà, tinh thần hiện đại và trang trọng. Thân áo dài qua gối, phom thẳng không bó, cổ đứng kín, hàng khuy trước thân; tay áo dài gọn và rủ. Vải lụa/gấm mờ, thêu vàng và trắng ngà tiết chế ở cổ, ngực, tay và dọc tà; quần dài, giày kín mũi và phụ kiện đầu đúng mẫu nếu có. Khi đứng vai mở hoặc bước trên cỏ, tà áo rơi tự nhiên và không che bàn chân.",
            "ẢNH 2",
        ),
        "female_clothing": _clothing(
            "Khách nữ mặc áo dài nghi lễ tím hoàng gia: cổ đứng kín, thân ôm tự nhiên không bó, hàng khuy trước thân, tay áo dài, hai tà dài rủ, quần lụa và giày kín mũi. Lụa bóng vừa phải, thêu vàng ở thân trước, cổ, tay và dọc tà; không cổ khoét sâu, xuyên thấu hay váy dạ hội, phụ kiện đầu chỉ theo mẫu. Khi bước hoặc xoay vai, hai tà tách mềm và không che chân. Giữ dáng toàn thân cân đối, thanh lịch và tự nhiên; không sao chép bố cục hoặc tư thế từ ảnh trang phục.",
            "ẢNH 3",
        ),
        "pose_expression": _pose_variants(
            ("ĐỨNG TRÊN TRỤC MẶT TIỀN", "ĐÓN KHÁCH TRÊN LỐI TIẾP CẬN", "HÒA NHẬP VÀO DI SẢN HIỆN ĐẠI"),
            (
                ("đứng giữa hoặc hơi lệch trục, vai mở và một chân tự nhiên.", "đứng thành cặp cân bằng với khoảng hở nhỏ, vai và tay khác nhau.", "tạo vòng cung nông trên cỏ, giữa tiến nhẹ và hai bên xoay vào trục.", "tạo vòng cung nông hoặc hai trung tâm/hai bên trước mặt tiền."),
                ("bước nhẹ trên trục lối vào, vai mở và tay thả tự nhiên.", "hai khách bước cùng hướng, một người dẫn và người kia xoay về bạn đồng hành.", "ba khách xếp cung nông theo lối vào, giữa tiến rất ít.", "bốn khách tiến nhẹ trong cung nông, hai người ngoài lùi ít, không hàng sâu."),
                ("đứng ba phần tư để vừa thấy mặt tiền vừa giữ dáng tự nhiên.", "đứng cạnh nhau, vai mở, hướng nhìn hơi khác, không chạm vai.", "tạo tam giác nông, giữa hướng máy ảnh và hai bên hướng nhẹ ra ngoài.", "tạo hai trung tâm/hai bên với khoảng cách rõ giữa bốn đầu."),
            ),
            ("tự tin, thân thiện, chuyên nghiệp; nụ cười tự nhiên khác mức.", "cởi mở, vui nhẹ và hiện đại; mặt vẫn rõ.", "tự nhiên, ấm áp, tự tin và phù hợp đón tiếp khách mời quan trọng."),
        ),
        "male": "independence-palace-male.jpg",
        "female": "independence-palace-female.jpg",
        "location": "independence-palace-scene.jpg",
    },
    "gia_long_palace": {
        "concept_prompt": _lines(
            "Ý NIỆM VÀ KHÔNG KHÍ:",
            "Chân dung thanh lịch và có chiều sâu tại Dinh Gia Long, một công trình lịch sử miền Nam. Khách mời quan trọng hiện diện như chủ thể văn hóa được đón tiếp trong không gian ấm áp, tự tin và được chăm chút.",
            "KIẾN TRÚC BẮT BUỘC:",
            "Tái dựng đúng Dinh Gia Long, nay là Bảo tàng Thành phố Hồ Chí Minh, trong ẢNH 4: công trình thuộc địa hai tầng màu trắng–kem, mặt tiền dài với nhịp cửa và hàng cột cổ điển đều nhau; sảnh đón trung tâm nhô ra có mái cong, bốn cột tròn, bậc thang nông, lan can con tiện và trán mái tam giác có phù điêu.",
            "DẤU HIỆU NHẬN DIỆN BẮT BUỘC:",
            "Trong khung hình dọc phải thấy rõ sảnh mái cong với bốn cột tròn, bậc thang, phần trán mái tam giác và một phần hàng cột/cửa của ít nhất một cánh nhà. Cho phép cắt bớt mép ngoài hai cánh để phù hợp tỷ lệ 9:16, nhưng phải giữ màu trắng–kem và cấu trúc sảnh đúng ẢNH 4.",
            "BỐ CỤC KHÔNG GIAN:",
            "Đặt khách ở tiền cảnh trên lối xe trước bậc thang, lệch nhẹ khỏi khối sảnh để bốn cột, mái cong và trán tam giác còn rõ. Mặt tiền chiếm phần lớn hậu cảnh, ít nhất một phần hai cánh nhà vẫn nhìn thấy và đủ nét để nhận diện; không xóa phông mạnh.",
            "ÁNH SÁNG VÀ MÀU SẮC:",
            "Ánh sáng miền Nam ấm và trong, bóng mềm, da người tự nhiên. Bảng màu kem/đá sáng, gỗ, cây xanh, đỏ mận sẫm trên nam phục và xanh ngọc trên nữ phục; tránh vàng cung đình mạnh.",
            "KHÔNG ĐƯỢC XUẤT HIỆN:",
            "Không dùng lam bê tông và khối ngang thấp của Dinh Độc Lập; không dùng mặt tiền vàng nhiều phù điêu của Cung An Định, không dựng lâu đài ba tầng nhiều vòm, vườn tròn cây cọ, chi tiết đại điện Huế, cổng thành, máy bay, trực thăng, xe cộ, chữ hoặc đám đông.",
        ),
        "male_clothing": _clothing(
            "Khách nam mặc áo ngũ thân đỏ mận sẫm và khăn đóng. Áo dài qua gối, phom thẳng, cổ đứng kín, hàng khuy trước thân và lớp áo trong ở cổ/tay; tay áo dài rộng vừa phải. Vải lụa/gấm mờ sâu màu, thêu xanh ngọc, vàng trầm và đỏ mận ở cổ, ngực, tay và viền; quần dài và giày kín mũi. Khi bước chậm hoặc đứng ba phần tư, tà áo giữ nếp có trọng lượng.",
            "ẢNH 2",
        ),
        "female_clothing": _clothing(
            "Khách nữ mặc áo dài hoặc áo ngũ thân xanh ngọc và mấn. Phom áo dài qua gối, cổ đứng kín, hàng khuy trước thân, tay áo dài và tà rủ; lớp áo trong nếu mẫu có, quần dài và giày kín mũi. Vải lụa/gấm bóng vừa, thêu vàng nhạt, màu kem và xanh đậm ở cổ, thân trước, tay và viền tà; mấn không che mắt. Khi xoay hoặc bước nhẹ, tà áo mềm và bàn chân tách nền.",
            "ẢNH 3",
        ),
        "pose_expression": _pose_variants(
            ("PHONG THÁI THANH LỊCH", "DẠO QUA SÂN TRƯỚC", "TIẾP KHÁCH TRƯỚC CÔNG TRÌNH"),
            (
                ("đứng ba phần tư, một chân hơi đưa trước và tay đặt gần eo.", "đứng cạnh nhau với vai/hướng nhìn khác nhau, khoảng hở nhỏ.", "tạo tam giác nông trước dãy cửa, giữa nhô nhẹ và hai bên hướng trung tâm.", "tạo cung nông hoặc hai trung tâm/hai bên, bốn đầu có khoảng cách."),
                ("bước chậm, một tay giữ hờ tà áo và mắt hướng máy ảnh.", "bước cùng hướng, một người dẫn nhẹ và người kia xoay về bạn đồng hành.", "xếp cung nông theo lối đi, người giữa tiến rất ít.", "bốn người đi nhẹ trên một lớp nông, hai người ngoài xoay vào trục."),
                ("đứng hơi lệch để lộ mặt tiền, vai mở và một tay hướng không gian.", "đứng gần nhưng không chạm, một người nhìn máy ảnh và một người nhìn mặt tiền.", "người giữa hướng máy ảnh, hai bên xoay nhẹ ra ngoài.", "tạo hai trung tâm/hai bên với vai và trọng tâm khác nhau, giữ khoảng trống."),
            ),
            ("điềm đạm, thanh lịch, ấm áp và có chiều sâu; cười kín đáo.", "tự tin, thân thiện và tự nhiên; không phô trương.", "bình tĩnh, trang nhã, ấm áp và đáng tin cậy; không nghi lễ cứng."),
        ),
        "male": "gia-long-palace-male.jpg",
        "female": "gia-long-palace-female.jpg",
        "location": "gia-long-palace-scene.jpg",
    },
}


SCENARIO_IDS = frozenset(SCENARIO_CONFIGS)
ALLOWED_PEOPLE_COUNTS = frozenset({1, 2, 3, 4})
PROMPT_SCENARIO_FIELDS = ("concept_prompt", "male_clothing", "female_clothing", "pose_expression")

BASE_IMAGE_GENERATION_PROMPT = """=== VAI TRÒ VÀ MỤC ĐÍCH ===
Bạn là đạo diễn hình ảnh cho trải nghiệm buồng chụp ảnh AI "Dấu Ấn Hoàng Gia – The Imperial Connection" của Century Ply. Tạo một ảnh chân dung di sản Việt Nam cao cấp, biến nhóm khách trong ẢNH 1 thành nhân vật mặc cổ phục trong bối cảnh chủ đề đã chọn. Đây là ảnh chụp người thật phục vụ khách mời quan trọng, không phải tranh minh họa hay cảnh kỳ ảo.

=== SỐ KHÁCH VÀ CHỌN NHÓM TIỀN CẢNH ===
- Số khách cần xuất hiện: đúng {people_count} người, không hơn không kém.
- Trong ẢNH 1, chỉ sử dụng đúng {people_count} khuôn mặt lớn nhất, gần camera nhất và tạo thành nhóm tiền cảnh chính. Bỏ qua hoàn toàn mọi người nhỏ hơn, xa hơn, đi ngang phía sau, xuất hiện trên màn hình, áp phích, tranh, tượng hoặc ảnh phản chiếu.
- Giữ thứ tự nhận diện trái sang phải của nhóm tiền cảnh chính để không hoán đổi khuôn mặt giữa các nhân vật.
- Không tái tạo bất kỳ người phụ, khách qua đường hoặc khuôn mặt nền nào thành nhân vật chính.

=== BẢO TOÀN NHẬN DIỆN ===
- ẢNH 1 là nguồn duy nhất cho danh tính khuôn mặt, hình dáng mặt, màu da tự nhiên, độ tuổi nhìn thấy, kính, kiểu tóc, râu, ria mép và đặc điểm cá nhân.
- Giữ tự nhiên tông da của khách Ấn Độ; không làm trắng da, đổi sắc tộc, làm trẻ hóa, làm thon mặt hoặc biến một người thành người khác.
- Giữ kính khi không che mắt, giữ râu/ria mép và kiểu tóc đặc trưng; chỉ để phụ kiện đầu được duyệt che một phần tóc. Đây là hướng dẫn tạo ảnh, không phải lời hứa về độ chính xác sinh trắc học.
- Không sao chép tư thế, cử chỉ, góc máy hoặc biểu cảm ban đầu của ẢNH 1; chỉ dùng danh tính và đặc điểm nhận diện cần thiết.

=== VAI TRÒ CỦA TỪNG ẢNH THAM CHIẾU ===
ẢNH 1 — ẢNH NHẬN DIỆN KHÁCH:
- Chỉ lấy danh tính và các đặc điểm nhận diện của đúng nhóm tiền cảnh đã chọn.

ẢNH 2 — MẪU TRANG PHỤC NAM:
- Chỉ tham khảo trang phục: kiểu dáng, cấu trúc lớp áo, cổ áo, hàng khuy phía trước, tay áo, chất liệu, màu sắc, hoa văn, thêu, khăn đóng hoặc phụ kiện đầu, quần và giày.
- Tuyệt đối không sao chép khuôn mặt, tỷ lệ cơ thể, tóc, tư thế, vị trí tay, hướng nhìn, biểu cảm, góc chụp, ánh sáng hoặc hậu cảnh người mẫu.

ẢNH 3 — MẪU TRANG PHỤC NỮ:
- Chỉ tham khảo trang phục: kiểu dáng, cấu trúc lớp áo, cổ áo, hàng khuy phía trước, tay áo, tà áo, chất liệu, màu sắc, hoa văn, thêu, mấn hoặc phụ kiện đầu, quần và giày.
- Tuyệt đối không sao chép khuôn mặt, tỷ lệ cơ thể, tóc, tư thế, vị trí tay, hướng nhìn, biểu cảm, góc chụp, ánh sáng hoặc hậu cảnh người mẫu.

ẢNH 4 — MẪU ĐỊA ĐIỂM:
- Đây là bản thiết kế hình ảnh bắt buộc của hậu cảnh, không chỉ là gợi ý phong cách. Tái dựng đúng cùng địa điểm, mặt đứng chủ đạo, hình khối, số tầng, nhịp cột/cửa, vật liệu, bảng màu và góc nhìn đặc trưng trong ẢNH 4.
- Được điều chỉnh ranh giới khung hình từ ảnh mẫu ngang sang ảnh dọc 9:16, nhưng không đổi phối cảnh đặc trưng hoặc làm mất các dấu hiệu nhận diện bắt buộc được nêu trong phần BỐI CẢNH.
- Không thay địa điểm bằng một cung điện, đền, cổng thành, biệt thự hoặc tòa nhà khác dù cùng thời kỳ hay cùng vùng miền. Phần BỐI CẢNH giải thích các dấu hiệu nào của ẢNH 4 bắt buộc phải giữ.
- Công trình phải đủ lớn và đủ nét để người xem nhận ra trong hai giây; không xóa phông mạnh, dùng sương, cây, người hoặc hiệu ứng ánh sáng che các dấu hiệu kiến trúc chính.
- Chỉ bỏ qua người, khuôn mặt, chữ, biểu trưng, hình mờ và vật thể thừa có trong ẢNH 4; không bỏ qua hoặc sáng tạo lại cấu trúc nhận diện của công trình.

=== PHÂN BỔ TRANG PHỤC TRONG NHÓM ===
- Dùng cách trình bày nam/nữ phù hợp với từng khách trong ẢNH 1, không suy đoán hoặc thay đổi danh tính.
- Với nhóm hỗn hợp, áp dụng riêng mẫu ẢNH 2 cho khách nam và mẫu ẢNH 3 cho khách nữ; không trộn hai mẫu thành một trang phục sai.
- Giữ tỷ lệ cơ thể thật và làm cho trang phục phù hợp với tư thế đã chọn.

=== TƯ THẾ VÀ BIỂU CẢM ĐÃ CHỌN ===
- Biến thể tư thế bắt buộc: BIẾN THỂ {variation_hint}.
- Trong phần TƯ THẾ VÀ BIỂU CẢM, chỉ thực hiện đúng biến thể này và đúng dòng dành cho {people_count} người. Không kết hợp với biến thể khác.
{pose_expression}
- Không dùng tư thế của ảnh mẫu trang phục hoặc ảnh ví dụ.
- Hai bàn tay của từng khách phải để trống, nhìn thấy rõ và ở tư thế tự nhiên; khách không cầm, mang, đeo hoặc tương tác với bất kỳ đạo cụ hay vật thể nào.
- Không tạo sách, bản đồ, cuộn giấy, quạt, ô, vũ khí, điện thoại, máy ảnh, túi, hoa, cốc, trang sức cầm tay hoặc bất kỳ vật thể nào trong tay hay gắn vào người, kể cả khi vật thể đó phù hợp với chủ đề.

=== MÁY ẢNH VÀ ÁNH SÁNG ===
- Góc máy ngang tầm mắt, phối cảnh tự nhiên như máy ảnh cảm biến toàn khung với tiêu cự 35–50mm.
- Không dùng góc siêu rộng, ống kính mắt cá hoặc làm méo khuôn mặt, cơ thể và kiến trúc.
- Ánh sáng chính mềm, tự nhiên và có hướng; chiếu rõ khuôn mặt của tất cả khách.
- Dùng ánh sáng bù nhẹ để giữ chi tiết da, mắt và trang phục; không để khuôn mặt bị tối.
- Độ sâu trường ảnh vừa phải: khách sắc nét, hậu cảnh tách nhẹ nhưng công trình đặc trưng vẫn phải rõ và nhận diện được ngay.
- Màu sắc sạch, hiện đại, cao cấp; tương phản vừa phải và tông da tự nhiên.
- Không xóa phông mạnh, không vùng nhòe sáng lớn che kiến trúc, không cháy sáng, không hiệu ứng tương phản động quá mức và không dùng ánh sáng trường quay không phù hợp với bối cảnh.

=== BỐ CỤC VÀ GIẢI PHẪU ===
- Ảnh dọc 9:16, tầm mắt, chất lượng 2K, phong cách ảnh biên tập giàu chất điện ảnh như ảnh chụp sự kiện cao cấp nhưng chân thực.
- Toàn thân từng người nằm gọn trong khung: thấy đầu, mặt, tay, trang phục, gấu áo, chân và cả hai bàn chân; không cắt đỉnh đầu, bàn tay, gấu áo hoặc bàn chân.
- Mọi khuôn mặt không bị che và có kích thước tương đối so sánh được; không đặt người trực tiếp sau đầu người khác.
- Giữ khoảng cách nông giữa các thành viên; bàn tay không cắt qua mặt hoặc thân người khác; vai, trọng tâm và biểu cảm thay đổi nhẹ, không sao chép cùng một tư thế cho nhiều người.
- Giữ chiều sâu đủ nông để mọi khuôn mặt rõ và tư thế vật lý phù hợp với cổ phục. Không tạo người bay, quỳ, ngồi, võ thuật, tay/ngón/chân dị dạng hoặc cơ thể dính nhau.
- Giữ khoảng nền/sàn tự nhiên bằng 3–5% chiều cao ảnh dưới hai bàn chân hoặc gấu áo. Không tạo khoảng trống quá lớn. Photo Jacket sẽ được ứng dụng ghép bên ngoài ảnh sau khi AI hoàn tất.

=== KHÔNG TẠO THƯƠNG HIỆU HOẶC CHỮ ===
- Không tự vẽ chữ, biểu trưng, hình mờ, đường viền, khung, chân trang, khẩu hiệu, huy hiệu hoặc bất kỳ nhận diện Century Ply nào trong ảnh AI.
- Không tạo biển hiệu/chữ giả, chữ lỗi, mặt nạ, khăn che mặt, da sáp, người trùng lặp, vật thể hiện đại hoặc đám đông phụ.
- Photo Jacket và mọi thiết kế chân trang do ứng dụng ghép bên ngoài sau bước sinh ảnh; không yêu cầu Gemini tái tạo chúng.

=== KẾT QUẢ ===
Trả về đúng một ảnh hoàn chỉnh, không kèm mô tả hay nhiều phương án."""


def split_scenario_prompt(prompt: str) -> dict[str, str]:
    """Split the previous combined scenario prompt into editable sections."""

    context, marker, clothing = prompt.partition("TRANG PHỤC:")
    if not marker:
        return {
            "concept_prompt": prompt.strip(),
            "male_clothing": "Tuân thủ mẫu trang phục nam trong ẢNH 2.",
            "female_clothing": "Tuân thủ mẫu trang phục nữ trong ẢNH 3.",
        }

    male_clothing, female_marker, female_clothing = clothing.partition("; khách nữ")
    if not female_marker:
        return {
            "concept_prompt": context.strip(),
            "male_clothing": clothing.strip(),
            "female_clothing": "Tuân thủ mẫu trang phục nữ trong ẢNH 3.",
        }

    return {
        "concept_prompt": context.strip(),
        "male_clothing": male_clothing.strip(),
        "female_clothing": f"khách nữ{female_clothing}".strip(),
    }


def default_prompt_configuration() -> dict[str, Any]:
    """Return the canonical editable prompt fields in a JSON-safe shape."""

    scenarios = {
        scenario_id: {field: config[field] for field in PROMPT_SCENARIO_FIELDS}
        for scenario_id, config in SCENARIO_CONFIGS.items()
    }
    return {"base_prompt": BASE_IMAGE_GENERATION_PROMPT, "scenarios": scenarios}


def select_pose_variant(scenario_id: str, people_count: int, variation_key: str) -> int:
    """Select a stable, human-readable pose variant number for one request."""

    seed = f"{scenario_id}:{people_count}:{variation_key or 'default'}".encode("utf-8")
    return (hashlib.sha256(seed).digest()[0] % 3) + 1


def select_pose_instructions(pose_expression: str, pose_variant: int, people_count: int) -> str:
    """Return only the selected variant, guest-count line and expression."""

    selected_heading = f"BIẾN THỂ {pose_variant} —"
    count_prefix = f"- {people_count} người:"
    heading = ""
    count_line = ""
    expression_line = ""
    in_selected_variant = False

    for raw_line in pose_expression.splitlines():
        line = raw_line.strip()
        if line.startswith("BIẾN THỂ "):
            if in_selected_variant:
                break
            in_selected_variant = line.startswith(selected_heading)
            if in_selected_variant:
                heading = line
            continue
        if not in_selected_variant:
            continue
        if line.startswith(count_prefix):
            count_line = line
        elif line.startswith("- Biểu cảm:"):
            expression_line = line

    if heading and count_line and expression_line:
        return _lines(heading, count_line, expression_line)
    return pose_expression.strip()


def build_image_generation_prompt(
    people_count: int,
    scenario_id: str,
    variation_key: str = "",
    prompt_configuration: Mapping[str, Any] | None = None,
) -> str:
    if people_count not in ALLOWED_PEOPLE_COUNTS:
        raise ValueError("people_count must be 1, 2, 3, or 4")
    if scenario_id not in SCENARIO_CONFIGS:
        raise ValueError("scenario_id is not supported")

    configuration = prompt_configuration or default_prompt_configuration()
    base_prompt = str(configuration.get("base_prompt") or BASE_IMAGE_GENERATION_PROMPT)
    configured_scenarios = configuration.get("scenarios")
    scenario_config = configured_scenarios.get(scenario_id) if isinstance(configured_scenarios, Mapping) else None
    if not isinstance(scenario_config, Mapping):
        scenario_config = SCENARIO_CONFIGS[scenario_id]

    pose_variant = select_pose_variant(scenario_id, people_count, variation_key)
    pose_expression = str(
        scenario_config.get("pose_expression") or SCENARIO_CONFIGS[scenario_id]["pose_expression"]
    )
    selected_pose_instructions = select_pose_instructions(
        pose_expression,
        pose_variant,
        people_count,
    )
    rendered_prompt = (
        base_prompt
        .replace("{people_count}", str(people_count))
        .replace("{variation_hint}", str(pose_variant))
        .replace("{pose_expression}", selected_pose_instructions)
    )

    legacy_prompt = str(scenario_config.get("prompt") or "")
    split_prompt = split_scenario_prompt(legacy_prompt) if legacy_prompt else {}
    defaults = SCENARIO_CONFIGS[scenario_id]
    concept_prompt = str(scenario_config.get("concept_prompt") or split_prompt.get("concept_prompt") or defaults["concept_prompt"])
    male_clothing = str(scenario_config.get("male_clothing") or split_prompt.get("male_clothing") or defaults["male_clothing"])
    female_clothing = str(scenario_config.get("female_clothing") or split_prompt.get("female_clothing") or defaults["female_clothing"])
    scenario_prompt = _lines(
        concept_prompt,
        "TRANG PHỤC NAM:",
        male_clothing,
        "TRANG PHỤC NỮ:",
        female_clothing,
    )
    return rendered_prompt + "\n\n=== BỐI CẢNH VÀ TRANG PHỤC ĐƯỢC CHỌN ===\n" + scenario_prompt


def load_scenario_references(scenario_id: str) -> list[tuple[str, bytes, str]]:
    if scenario_id not in SCENARIO_CONFIGS:
        raise ValueError("scenario_id is not supported")
    config = SCENARIO_CONFIGS[scenario_id]
    files = (
        ("ẢNH 2 — mẫu tham chiếu trang phục nam; chỉ lấy trang phục", REFERENCE_ROOT / "clothing" / config["male"]),
        ("ẢNH 3 — mẫu tham chiếu trang phục nữ; chỉ lấy trang phục", REFERENCE_ROOT / "clothing" / config["female"]),
        ("ẢNH 4 — mẫu tham chiếu địa điểm; chỉ lấy kiến trúc và không gian", REFERENCE_ROOT / "locations" / config["location"]),
    )
    return [(label, path.read_bytes(), "image/jpeg") for label, path in files]
