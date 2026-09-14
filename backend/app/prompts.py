"""Prompt and approved reference configuration for Century Ply portraits."""

from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path
from typing import Any


REFERENCE_ROOT = Path(__file__).with_name("reference_images")


def _lines(*values: str) -> str:
    return "\n".join(values)


_COMPOSITION_RULES = (
    "chụp toàn thân, thấy rõ đầu, hai tay, gấu áo và hai bàn chân; chừa một khoảng nền nhỏ dưới chân.",
    "hai người có kích thước cân bằng, mặt cùng rõ nét, thân có khoảng hở; thấy đủ bốn bàn tay và bốn bàn chân.",
    "đúng đội hình ba người đã mô tả; các đầu không chồng nhau, thấy đủ sáu bàn tay và sáu bàn chân.",
    "đúng đội hình bốn người và độ sâu đã mô tả; các đầu tách biệt, thấy đủ tám bàn tay và tám bàn chân.",
)

_PORTRAIT_EXPRESSION = (
    "Tất cả khách nhìn thẳng vào máy ảnh với mắt sáng và nụ cười nhẹ, tươi, tự nhiên; không cười quá rộng. "
    "Giữ biểu cảm riêng của từng người, không sao chép khuôn miệng hoặc nụ cười."
)


def _signature_pose(
    name: str,
    actions: tuple[str, str, str, str],
    expression: str,
) -> str:
    lines = [f"BIẾN THỂ 1 — {name}"]
    for count, (action, composition) in enumerate(zip(actions, _COMPOSITION_RULES, strict=True), start=1):
        lines.append(f"- {count} người: {action} Giữ {composition}")
    lines.append(f"- Biểu cảm: {expression} {_PORTRAIT_EXPRESSION}")
    return "\n".join(lines)


def _clothing(details: str, reference: str) -> str:
    return (
        f"{details} "
        f"{reference} chỉ tham khảo trang phục và phụ kiện. Bỏ qua hoàn toàn người mẫu/mannequin, cơ thể, tay chân, "
        "tư thế, ánh sáng và hậu cảnh trong ảnh tham chiếu."
    )


SCENARIO_CONFIGS = {
    "thang_long_imperial": {
        "concept_prompt": _lines(
            "Ý NIỆM VÀ KHÔNG KHÍ:",
            "Chân dung nghi lễ của khách mời quan trọng đang đến Hoàng Thành Thăng Long, thể hiện sự trang nghiêm, hiếu khách và niềm tự hào văn hóa trong một bộ ảnh sự kiện cao cấp.",
            "KIẾN TRÚC BẮT BUỘC:",
            "Tái dựng đúng Đoan Môn của Hoàng Thành Thăng Long trong ẢNH 4: bệ thành gạch đá dài đã nhuốm thời gian có năm cửa vòm, cửa chính giữa lớn nhất và bốn cửa nhỏ hơn ở hai bên; phía trên là lầu trung tâm ba tầng, mái ngói cong và tường vàng đất. Đây là công trình bắt buộc, không thay bằng một cổng cung đình bất kỳ.",
            "DẤU HIỆU NHẬN DIỆN BẮT BUỘC:",
            "Trong khung dọc phải thấy rõ khối lầu trung tâm ba tầng, cửa chính lớn và ít nhất một cửa nhỏ ở mỗi bên. Giữ đúng nhịp tổng thể năm cửa vòm, hình khối, vật liệu cùng góc nhìn ba phần tư của ẢNH 4; cho phép hai đầu ngoài của tường thành nằm ngoài khung để khách không bị thu nhỏ.",
            "BỐ CỤC KHÔNG GIAN:",
            "Bố cục chính diện, uy nghi và gần đối xứng: khách đứng giữa sân gạch, Đoan Môn hiện lên như một đại cổng khổng lồ chiếm phần lớn hậu cảnh. Hai đoạn tường thành và các cửa vòm tạo khung hai bên; góc máy hơi thấp làm lầu trung tâm cao lớn nhưng không biến dạng. Giữ rõ cửa chính và ít nhất một cửa bên ở mỗi phía; không xóa phông mạnh.",
            "ÁNH SÁNG VÀ MÀU SẮC:",
            "Bình minh nghi lễ trong trẻo: mặt trời thấp chiếu xiên từ một bên, tạo viền sáng vàng dịu quanh khách và các tia nắng mảnh xuyên qua lớp sương rất nhẹ nhưng không che kiến trúc. Bắt buộc có mảng nắng trên sân gạch, tường cổ và một phía trang phục, cùng bóng người đổ dài mềm về hướng đối diện. Bầu trời chuyển sắc xanh lam–vàng kim có chiều sâu; da người vẫn trung tính, sáng khỏe.",
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
        "pose_expression": _signature_pose(
            "NGHI THỨC TIẾN QUA ĐOAN MÔN",
            (
                "đang bước nửa nhịp trên trục sân gạch như tiến qua cổng thành; một tay đánh nhẹ cạnh hông theo bước chân, tay kia mở thấp về Đoan Môn, hai bàn tay cách xa nhau và mặt hướng máy ảnh.",
                "song hành tiến qua Đoan Môn theo hai nhịp lệch nhau: khách trái bước trước, một tay đánh ra sau và tay kia thả cạnh thân; khách phải lùi nửa nhịp, một lòng bàn tay mở thấp về cổng và tay còn lại thả tự nhiên.",
                "tạo đoàn nghi lễ hình mũi tên: khách giữa tiến trước một bước với hai tay đánh tự nhiên ngược nhịp chân; khách trái ở sau mở một tay thấp về cổng, tay kia thả cạnh thân; khách phải xoay vai ba phần tư, một tay ở ngang hông và tay kia đưa nhẹ ra sau.",
                "tạo đội hình đường chéo tiến lễ từ trái trước đến phải sau, khác hẳn đội hình ba người: lần lượt từ trái sang phải, khách 1 mở một tay thấp về cổng, khách 2 đánh hai tay tự nhiên khi bước, khách 3 đặt một tay ở hông và tay kia thả cạnh thân, khách 4 xoay vai vào nhóm với hai tay buông tách rời.",
            ),
            "tự hào, hiếu khách và trang trọng như đoàn khách quý vừa tiến qua cổng chính.",
        ),
        "male": "thang-long-imperial-male.jpg",
        "female": "thang-long-imperial-female.jpg",
        "location": "thang-long-imperial-scene.jpg",
        "style": "thang-long-imperial-style-v2.jpg",
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
            "Bố cục chính diện, trang nghiêm và gần đối xứng: khách đứng giữa lối đá dẫn vào đền, chính điện lớn nằm trực diện phía sau, núi đá vôi dựng cao như bức thành thiên nhiên. Hai trụ biểu cùng đôi nghê đá Việt Nam đúng lịch sử có thể tạo khung cân bằng ở hai bên tiền cảnh; không dùng sư tử Trung Hoa kỳ ảo. Góc máy hơi thấp, nền đủ nét để nhận ra Hoa Lư ngay.",
            "ÁNH SÁNG VÀ MÀU SẮC:",
            "Bình minh sau cơn mưa nhẹ: sương mỏng nằm giữa núi đá vôi, mây tách để nắng vàng dịu chiếu xiên thành vệt rõ xuống lối nghi lễ. Bắt buộc thấy nắng bắt trên vai, viền tóc, trụ biểu và nền gạch, cùng bóng người mềm kéo chéo trên mặt sân ẩm. Mặt đá và nền gạch chỉ phản chiếu rất nhẹ, không bóng như gương; núi, trụ biểu và chính điện vẫn rõ, da người sáng khỏe và không ám vàng.",
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
        "pose_expression": _signature_pose(
            "KHÍ PHÁCH TRƯỚC NON SÔNG HOA LƯ",
            (
                "đứng vững trên lối gạch với chân mở nhẹ và vai xoay về dãy núi; một cẳng tay mở thấp về cảnh quan, tay kia buông thẳng cạnh thân, cằm nâng nhẹ và mặt hướng máy ảnh.",
                "tạo cặp phản hướng vững chãi: khách trái đứng chính diện, một tay ở hông và tay kia buông cạnh thân; khách phải xoay ba phần tư về núi, một tay mở thấp về dãy karst và tay còn lại đưa nhẹ ra sau, hai người không chạm nhau.",
                "xếp thành thế kiềng ba chân có chiều sâu: khách giữa tiến trước một bước với hai tay buông tách rời; khách trái phía sau mở một tay về trụ biểu, khách phải phía sau đặt một tay ở hông; tay còn lại của hai khách bên đều thả cạnh thân, không chắp tay cầu nguyện.",
                "tạo đội hình kim cương vững chãi, khác hẳn nhóm ba người: khách 1 phía trước mở một tay thấp về chính điện; khách 2 và 3 ở giữa xoay vai ngược hướng, một người đặt tay ở hông và một người mở tay về núi; khách 4 lùi nửa bước với hai tay buông tách rời, tất cả đứng trên lối gạch.",
            ),
            "điềm tĩnh, ấm áp và kiêu hãnh; phong thái vững như địa thế núi bao quanh cố đô.",
        ),
        "male": "hoa-lu-capital-male.jpg",
        "female": "hoa-lu-capital-female.jpg",
        "location": "hoa-lu-capital-scene.jpg",
        "style": "hoa-lu-capital-style-v2.jpg",
    },
    "hue_imperial_city": {
        "concept_prompt": _lines(
            "Ý NIỆM VÀ KHÔNG KHÍ:",
            "Chân dung đón tiếp thanh lịch trong Đại Nội Huế, đẹp như một khung phim di sản cao cấp: quyền quý, trong trẻo và hơi lý tưởng hóa nhưng vẫn là địa điểm thật.",
            "KIẾN TRÚC BẮT BUỘC:",
            "Tái dựng đúng Ngọ Môn theo ẢNH 4: đài thành đá–gạch hình chữ U có năm lối vào, phía trên là Lầu Ngũ Phụng bằng gỗ sơn son với chín bộ mái; mái chính giữa lợp ngói lưu ly vàng và tám mái còn lại lợp ngói xanh. Không đổi thành một cổng thành một tháp.",
            "DẤU HIỆU NHẬN DIỆN BẮT BUỘC:",
            "Trong khung hình dọc phải thấy rõ phần giữa của đài chữ U, cửa chính giữa, các lầu gỗ đỏ đối xứng và sự tương phản giữa mái vàng trung tâm với các mái xanh hai bên. Cho phép cắt bớt phần kéo dài ngoài cùng để phù hợp tỷ lệ 9:16, nhưng phải giữ hình khối Lầu Ngũ Phụng và đủ dấu hiệu nhận diện từ ẢNH 4.",
            "BỐ CỤC KHÔNG GIAN:",
            "Bố cục chính diện, quyền quý và gần đối xứng như ảnh mẫu Đại Nội Huế: khách đứng chính giữa trên sân đá, Ngọ Môn hiện lên lớn và uy nghi trực diện phía sau. Hiên gỗ, cột son và lan can đá tạo khung mạnh ở hai mép như một cổng nghi lễ; góc máy hơi thấp làm mái Lầu Ngũ Phụng nổi bật. Không che cửa trung tâm và chỉ tách nền rất nhẹ.",
            "ÁNH SÁNG VÀ MÀU SẮC:",
            "Hoàng hôn ấm và sang trọng: nắng cuối ngày chiếu ngang từ một bên, lướt qua gỗ sơn son và ngói lưu ly, tạo viền sáng mềm quanh khách. Bắt buộc có một phía mặt và trang phục bắt nắng ấm, phía còn lại giữ bóng mềm có chi tiết, bóng người đổ chéo trên sân đá. Bầu trời chuyển từ xanh trong sang vàng hồng tiết chế; mái vàng và mái xanh bắt sáng tinh tế nhưng không phát quang giả, da người trung tính và sáng khỏe.",
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
        "pose_expression": _signature_pose(
            "CÁNH PHƯỢNG NGHÊNH KHÁCH TRƯỚC NGỌ MÔN",
            (
                "đứng dáng chữ S rất nhẹ, thân xoay ba phần tư; một cánh tay mở chéo thấp ra ngoài làm đường cánh phượng, tay kia buông mềm cạnh tà áo, một chân đưa trước nửa bước và mặt hướng máy ảnh.",
                "tạo đôi cánh phượng đối xứng: hai người xoay nhẹ vào nhau, mỗi người mở cánh tay phía ngoài chéo thấp theo hai hướng đối nhau và buông tay phía trong dọc thân; bốn bàn tay tách rời, không giao nhau.",
                "tạo hình quạt ba cánh: khách giữa lùi nửa bước, đứng chính diện với hai tay buông thành hai đường dọc; khách trái và phải tiến nhẹ, xoay vai ra ngoài và mỗi người mở cánh tay ngoài ở một cao độ khác nhau, tay trong thả dọc thân, không dang tay như múa.",
                "tạo hình cánh phượng bất đối xứng có hai lớp nông, khác nhóm ba người: khách 1 ngoài trái mở tay chéo thấp, khách 2 phía trước mở một tay ngang eo, khách 3 lùi nửa bước với hai tay buông tách rời, khách 4 ngoài phải mở tay chéo cao hơn nhẹ; các tay còn lại đều thả dọc thân.",
            ),
            "duyên dáng, quyền quý và gần gũi; nét mềm của cung đình Huế nhưng không tạo dáng sân khấu.",
        ),
        "male": "hue-imperial-city-male.jpg",
        "female": "hue-imperial-city-female.jpg",
        "location": "hue-imperial-city-scene.jpg",
        "style": "hue-imperial-city-style-v2.jpg",
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
            "Bố cục chính diện, quyền uy và đối xứng theo trục đại lễ: khách đứng giữa sân Đại Triều Nghi, Điện Thái Hòa lớn và hai lớp mái vàng chiếm phần lớn hậu cảnh. Bậc đá, lan can chạm rồng và hàng cột son tạo khung nghi lễ hai bên; góc máy hơi thấp hướng về chính điện. Không đặt khách trên hiên, không che cửa chính và không xóa phông mạnh.",
            "ÁNH SÁNG VÀ MÀU SẮC:",
            "Bình minh đỏ–vàng mang khí chất đại lễ: nắng thấp chiếu xiên qua sân Đại Triều Nghi thành các dải sáng và bóng dài rõ ràng, không che hàng cột hoặc mái điện. Bắt buộc thấy ánh nắng bắt trên một phía gương mặt, vai áo và hàng cột, cùng bóng người nối với bàn chân và đổ về phía đối diện. Nền đá chỉ phản chiếu rất nhẹ, không bóng như gương; gương mặt vẫn tươi tự nhiên, không dùng đèn rọi sân khấu.",
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
        "pose_expression": _signature_pose(
            "THẾ ĐẠI TRIỀU TRƯỚC ĐIỆN THÁI HÒA",
            (
                "đứng chính diện trên trục sân chầu, hai bàn chân song song và vai hạ; một tay buông thẳng cạnh thân, cẳng tay kia mở thấp với lòng bàn tay hướng vào điện, hai tay không chạm nhau và cằm ngang.",
                "đứng tách hai bên trục chính điện: khách trái xoay vai vào giữa, một tay mở thấp về cửa và tay kia buông cạnh thân; khách phải đứng chính diện, một tay đặt ở hông và tay kia buông thẳng, tạo thế nghi lễ cân bằng nhưng không sao chép.",
                "tạo đội hình phẩm cấp hình tam giác: khách giữa tiến trước nửa bước với hai tay buông tách rời; khách trái phía sau mở một cẳng tay thấp về điện, khách phải phía sau đặt một tay ở hông; tay còn lại của hai khách bên thả cạnh thân, không quỳ hoặc cúi lạy.",
                "tạo bố cục bốn trụ trên hai lớp nông, khác nhóm ba người: hai khách trong tiến nửa bước, một người mở tay về cửa và người kia đặt tay ở hông; hai khách ngoài lùi nhẹ, một người buông hai tay tách rời và người kia mở một tay thấp về hàng cột; không ai chắp tay hoặc giấu tay trong tay áo.",
            ),
            "uy nghi, bình tĩnh và hiếu khách; nụ cười tiết chế phù hợp không gian đại lễ, không nghiêm nghị hoặc lạnh lùng.",
        ),
        "male": "thai-hoa-palace-male.jpg",
        "female": "thai-hoa-palace-female.jpg",
        "location": "thai-hoa-palace-scene.jpg",
        "style": "thai-hoa-palace-style-v1.jpg",
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
            "Bố cục chính diện, sang trọng và gần đối xứng: khách đứng giữa sân hoặc đầu bậc thềm, Khải Tường Lâu vươn lớn phía sau như một dinh thự nghi lễ. Hai hàng cột trắng, bậc thang và phù điêu hoa lá tạo khung mạnh hai bên; góc máy hơi thấp làm phần trán giữa và ban công nổi bật. Giữ rõ ít nhất hai tầng mặt tiền, không để trang trí che người.",
            "ÁNH SÁNG VÀ MÀU SẮC:",
            "Cuối buổi chiều thanh lịch: nắng xiên mềm từ một bên làm mặt tiền vàng mù tạt sáng ấm, đồng thời tạo bóng phù điêu và bóng cột có chiều sâu. Bắt buộc thấy vệt nắng trên tóc, vai và một phía trang phục, bóng người đổ mềm trên sân về hướng đối diện. Bầu trời xanh lam nhạt và vùng sáng kem tạo phối màu điện ảnh kem–xanh–vàng, sang trọng nhưng không rực giả; da và vải giữ kết cấu tự nhiên.",
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
        "pose_expression": _signature_pose(
            "DẠO BƯỚC TÂN CỔ ĐIỂN TRƯỚC KHẢI TƯỜNG LÂU",
            (
                "tạo dáng thời trang đầu thế kỷ XX: thân xoay ba phần tư, hai chân bắt chéo nhẹ ở cổ chân; một tay đặt ở hông, tay kia buông dài cạnh tà áo và mặt hướng máy ảnh.",
                "tạo cặp phản hướng thanh lịch, gần lưng nhưng không chạm: khách trái bắt chéo chân và đặt một tay ở hông, tay kia buông thẳng; khách phải bước ngang nhẹ, một tay chạm rất nhẹ cổ áo và tay kia mở chéo thấp ra ngoài.",
                "tạo đường chéo thời trang ba nhịp: khách trái tiến trước với một tay ở hông và tay kia buông dọc thân; khách giữa lùi nửa bước, một tay sửa nhẹ mép cổ áo và tay kia buông thẳng; khách phải xoay ba phần tư, mở một tay chéo thấp và thả tay còn lại cạnh thân, không ai lặp dáng.",
                "tạo bố cục lookbook zigzag bất đối xứng, khác nhóm ba người: khách 1 bắt chéo chân với một tay ở hông, khách 2 bước tới với hai tay đánh nhẹ, khách 3 đứng chính diện với một tay chạm cổ áo và tay kia buông, khách 4 xoay ra ngoài với một tay mở chéo thấp; mọi người ở cao độ tay khác nhau.",
            ),
            "thanh lịch, duyên dáng và tự tin như chân dung thời trang tân cổ điển; không catwalk, khiêu vũ hoặc tạo dáng cường điệu.",
        ),
        "male": "an-dinh-palace-male.jpg",
        "female": "an-dinh-palace-female.jpg",
        "location": "an-dinh-palace-scene.jpg",
        "style": "an-dinh-palace-style-v2.jpg",
    },
    "independence_palace": {
        "concept_prompt": _lines(
            "Ý NIỆM VÀ KHÔNG KHÍ:",
            "Chân dung nghi lễ hiện đại tại Dinh Độc Lập/Dinh Thống Nhất, đẹp như ảnh quảng cáo di sản cao cấp: thanh lịch, sáng trong và hơi lý tưởng hóa nhưng vẫn chân thực.",
            "KIẾN TRÚC BẮT BUỘC:",
            "Tái dựng đúng mặt tiền chính Dinh Độc Lập trong ẢNH 4: khối nhà hiện đại thấp và rất rộng màu trắng–xám, hàng lam bê tông đứng lặp đều như rèm hoa đá, ban công trung tâm, đài phun nước tròn và thảm cỏ xanh lớn phía trước.",
            "DẤU HIỆU NHẬN DIỆN BẮT BUỘC:",
            "Trong khung hình dọc phải thấy rõ nhịp lam bê tông đứng, ban công giữa, đài phun nước tròn và thảm cỏ. Cho phép cắt đối xứng phần ngoài cùng của hai cánh nhà để phù hợp tỷ lệ 9:16, nhưng phải giữ trục chính diện và đủ dấu hiệu để nhận ra ngay Dinh Độc Lập, không phải văn phòng hiện đại bất kỳ.",
            "BỐ CỤC KHÔNG GIAN:",
            "Bố cục chính diện, mạnh mẽ và gần đối xứng như ảnh mẫu Dinh Độc Lập: khách đứng chính giữa trên nền đá của sảnh hoặc khu vực sân cứng, mặt tiền Dinh hiện lên lớn trực diện phía sau. Các mảng lam bê tông, khung cửa và mái sảnh tạo hai cánh kiến trúc bao quanh khách; góc máy hơi thấp làm công trình có sức nặng. Bàn chân tiếp xúc rõ với nền đá, không đứng trên cỏ và chỉ tách nền rất nhẹ.",
            "ÁNH SÁNG VÀ MÀU SẮC:",
            "Giờ vàng miền Nam sạch và hiện đại: nắng thấp chiếu chéo từ phía sau bên, tạo viền sáng tinh tế quanh tóc và vai trong khi bù sáng mềm giữ rõ gương mặt. Bắt buộc có nắng bắt trên nhịp lam bê tông, điểm lấp lánh nhỏ trên đài phun và bóng người dài mềm trên lối lát đá, nối đúng dưới bàn chân. Thảm cỏ chỉ nằm phía sau; bầu trời xanh–vàng trong trẻo, da người sáng khỏe và không dùng màu tím/vàng giả.",
            "KHÔNG ĐƯỢC XUẤT HIỆN:",
            "Không có mặt tiền thuộc địa với cột/vòm của Dinh Gia Long, mặt tiền vàng Cung An Định, mái cung đình Nguyễn, cột rồng, đền chùa, ngai vàng, lâu đài châu Âu, chữ/biển hiệu, giao thông hoặc người đi ngang.",
        ),
        "male_clothing": _clothing(
            "Khách nam mặc áo dài nghi lễ Việt Nam màu ngà, tinh thần hiện đại và trang trọng. Thân áo dài qua gối, phom thẳng không bó, cổ đứng kín, hàng khuy trước thân; tay áo dài gọn và rủ. Vải lụa/gấm mờ, thêu vàng và trắng ngà tiết chế ở cổ, ngực, tay và dọc tà; quần dài, giày kín mũi và phụ kiện đầu đúng mẫu nếu có. Khi đứng vai mở hoặc bước trên lối lát đá, tà áo rơi tự nhiên và không che bàn chân.",
            "ẢNH 2",
        ),
        "female_clothing": _clothing(
            "Khách nữ mặc áo dài nghi lễ tím hoàng gia: cổ đứng kín, thân ôm tự nhiên không bó, hàng khuy trước thân, tay áo dài, hai tà dài rủ, quần lụa và giày kín mũi. Lụa bóng vừa phải, thêu vàng ở thân trước, cổ, tay và dọc tà; không cổ khoét sâu, xuyên thấu hay váy dạ hội, phụ kiện đầu chỉ theo mẫu. Khi bước hoặc xoay vai, hai tà tách mềm và không che chân. Giữ dáng toàn thân cân đối, thanh lịch và tự nhiên; không sao chép bố cục hoặc tư thế từ ảnh trang phục.",
            "ẢNH 3",
        ),
        "pose_expression": _signature_pose(
            "BƯỚC TIẾN TRÊN LỐI ĐỘC LẬP",
            (
                "bước tự tin giữa nhịp trên lối lát đá, vai mở; một tay mở nhẹ ở ngang hông như giới thiệu mặt tiền và tay kia đánh tự nhiên theo bước chân, không đứng trên cỏ.",
                "đi song hành trên lối lát đá với bước chân lệch nhịp: khách trái bước trước, hai tay đánh tự nhiên; khách phải lùi nửa nhịp, một lòng bàn tay mở về mặt tiền và tay kia đưa nhẹ ra sau, bốn tay không chạm nhau.",
                "tạo đội hình chữ V tiến tới: khách giữa dẫn trước với một tay mở ngang hông về đài phun và tay kia đánh ra sau; khách trái phía sau đánh hai tay theo bước chân; khách phải phía sau đặt một tay ở hông và mở tay kia thấp về Dinh.",
                "tạo đội hình hai cặp so le trên lối lát đá, khác nhóm ba người: khách 1 và 3 tiến trước ở hai nhịp chân đối nhau, khách 2 và 4 lùi nửa bước; lần lượt từ trái sang phải là hai tay đánh tự nhiên, một tay mở về Dinh, một tay đặt ở hông và một tay mở về đài phun, các tay còn lại buông hoặc đánh theo bước chân; không chào quân đội.",
            ),
            "trẻ trung, tự tin và cởi mở như một đoàn khách quốc tế đang tiến vào công trình hiện đại.",
        ),
        "male": "independence-palace-male.jpg",
        "female": "independence-palace-female.jpg",
        "location": "independence-palace-scene.jpg",
        "style": "independence-palace-style-v2.jpg",
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
            "Bố cục chính diện, uy nghi và gần đối xứng: khách đứng giữa lối đá trước bậc thang, sảnh trung tâm Dinh Gia Long cùng bốn cột lớn vươn cao trực diện phía sau. Hai cánh nhà, lan can đá và hàng cột cổ điển tạo khung quyền lực hai bên; góc máy hơi thấp nhấn mạnh mái cong và trán tam giác. Mặt tiền chiếm phần lớn hậu cảnh và không xóa phông mạnh.",
            "ÁNH SÁNG VÀ MÀU SẮC:",
            "Chạng vạng xanh thanh lịch: ánh sáng kiến trúc vàng ấm từ sảnh và cửa sổ là nguồn sáng chính, hắt có hướng lên bậc thang, hàng cột và một phía khách; ánh xanh của bầu trời tạo viền lạnh nhẹ ở phía đối diện. Bắt buộc có chuyển sắc xanh–hổ phách trên mặt và trang phục, bóng tiếp xúc rõ dưới chân và bóng mềm đổ về vùng sân tối hơn. Mặt đường chỉ phản chiếu rất nhẹ như vừa qua mưa; gương mặt vẫn sáng, ấm và tự nhiên.",
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
        "pose_expression": _signature_pose(
            "NGHI THỨC ĐÓN KHÁCH TẠI TIỀN SẢNH GIA LONG",
            (
                "đứng lệch trục tiền sảnh, thân xoay ba phần tư về bậc thang; bàn tay gần công trình mở hướng lên ở ngang eo như lời mời vào sảnh, tay kia buông dọc thân và mặt hướng máy ảnh.",
                "đứng thành cặp chủ nhà hai bên lối vào: khách trái mở tay phía trong về bậc thang và buông tay ngoài; khách phải đặt một tay ở hông, tay còn lại mở chéo thấp về cửa, tạo hai cử chỉ đón tiếp khác nhau.",
                "tạo đội hình cổng chào ba điểm: khách giữa lùi nửa bước trước cửa với hai tay buông tách rời; khách trái tiến nhẹ và mở một tay về bậc thang; khách phải xoay ba phần tư, một tay đặt ở hông và tay kia mở về sảnh, không ai lặp cử chỉ.",
                "tạo hành lang đón khách bằng hai cặp so le, khác nhóm ba người: khách 1 và 4 lùi nhẹ hai bên với tay ngoài buông thẳng; khách 2 tiến trước và mở tay về cửa; khách 3 tiến trước nửa bước, đặt một tay ở hông và mở tay kia về bậc thang; bốn cơ thể tạo khoảng trống dẫn mắt vào sảnh.",
            ),
            "ấm áp, trang nhã và đáng tin cậy như chủ nhà đang mời khách bước vào một dinh thự lịch sử.",
        ),
        "male": "gia-long-palace-male.jpg",
        "female": "gia-long-palace-female.jpg",
        "location": "gia-long-palace-scene.jpg",
        "style": "gia-long-palace-style-v2.jpg",
    },
}


SCENARIO_IDS = frozenset(SCENARIO_CONFIGS)
ALLOWED_PEOPLE_COUNTS = frozenset({1, 2, 3, 4})
PROMPT_SCENARIO_FIELDS = ("concept_prompt", "male_clothing", "female_clothing", "pose_expression")

BASE_IMAGE_GENERATION_PROMPT = """=== YÊU CẦU ===
Tạo một ảnh dọc 9:16, 2K, toàn thân, photorealistic cinematic như ảnh quảng cáo du lịch và lookbook cao cấp. Chỉ tạo đúng {people_count} người là khách chính; không có chữ trong ảnh AI.
BẮT BUỘC thay toàn bộ quần áo hiện đại trong ẢNH 1 bằng cổ phục được chỉ định. Không giữ lại áo, quần, giày hoặc phụ kiện hiện đại từ ẢNH 1.

=== NHÂN VẬT ===
- Chọn {people_count} khuôn mặt lớn nhất và gần máy ảnh nhất trong ẢNH 1; bỏ qua mọi người phía sau, màn hình, áp phích, tranh, tượng và ảnh phản chiếu.
- ẢNH 1 là nguồn duy nhất cho danh tính. Giữ mỗi người dễ nhận ra, tách biệt; không sao chép, trộn hoặc hoán đổi khuôn mặt.
- Người có diện mạo nữ: mặt thon nhẹ, oval V-line tự nhiên, tóc chuyên nghiệp và trang điểm nhẹ. Người có diện mạo nam: mặt thon nhẹ, đường hàm cân đối, tóc gọn và da khỏe.
- Người trưởng thành trông trẻ hơn khoảng 5 tuổi: da sáng, đều màu, giảm quầng thâm, dấu hiệu mệt mỏi và nếp nhăn sâu nhưng vẫn giữ kết cấu da thật. Trẻ em giữ đúng độ tuổi.

=== ẢNH THAM CHIẾU ===
- ẢNH 1: chỉ lấy danh tính.
- ẢNH 2–3 là mẫu trang phục bắt buộc, không phải gợi ý phong cách. Chỉ lấy trang phục và phụ kiện; bỏ hoàn toàn người mẫu/mannequin, khuôn mặt, cơ thể, tay chân và tư thế trong ảnh, không sao chép bất kỳ bộ phận cơ thể nào.
- ẢNH 4: lấy đúng địa điểm và kiến trúc thật.
- ẢNH 5: chỉ tham khảo bố cục, màu và ánh sáng; không được thay đổi địa điểm từ ẢNH 4.

=== TRANG PHỤC VÀ TƯ THẾ ===
- Xác định diện mạo nam/nữ độc lập cho từng khách trong ẢNH 1. Không giả định nhóm phải có cả nam và nữ; tất cả khách có thể cùng là nữ hoặc cùng là nam. Giữ nguyên biểu hiện giới tính của từng người, không nam hóa người nữ và không nữ hóa người nam. Nếu không chắc chắn, ưu tiên giữ nguyên biểu hiện giới tính trong ẢNH 1.
- Phân trang phục nam/nữ riêng cho từng khách theo diện mạo đã xác định; không trộn hai mẫu. Vải và tay áo rủ tự nhiên.
- Chỉ dùng BIẾN THỂ {variation_hint} dành cho {people_count} người:
{pose_expression}
- Làm đúng vị trí của từng khách và từng cánh tay trong tư thế trên. Không tự đổi thành hàng ngang hoặc dáng đứng chắp tay.
- Mỗi khách chỉ có đúng hai cánh tay và hai bàn tay, đều nhìn thấy rõ và thuộc về chính người đó. Không có tay thừa, tay lặp, chi mannequin hoặc ống tay áo thừa; không tạo sách, bản đồ, quạt, điện thoại, hoa, vũ khí hay đạo cụ khác.

=== BỐI CẢNH, ÁNH SÁNG VÀ MÁY ẢNH ===
- Tái dựng đúng concept và địa điểm được mô tả bên dưới; công trình phải đủ rõ để nhận ra ngay.
- Bố cục chính diện, cân đối và gần đối xứng: khách ở trung tâm tiền cảnh, công trình nhận diện nằm trực diện phía sau. Khách chiếm khoảng 55–65% chiều cao khung hình; nền vẫn rõ và không bị xóa phông mạnh.
- Làm bối cảnh đẹp hơn thực tế một cách tiết chế: màu sắc giàu, chiều sâu điện ảnh, ánh sáng mềm và một lớp không khí óng nhẹ như phim di sản cao cấp. Không tạo kiến trúc giả, phép thuật, hào quang hoặc chi tiết fantasy quá mức.
- Nguồn sáng của concept là nguồn sáng chính, kết hợp bù sáng mềm để gương mặt sáng đẹp. Ánh sáng và bóng đổ trên người phải cùng hướng với bối cảnh, không giống ảnh cắt ghép.
- Màu phim 35 mm hiện đại, tương phản vừa, vùng sáng mềm, vùng tối sạch và hạt phim rất mịn. Máy thấp hơn tầm mắt một chút và hướng lên rất nhẹ để công trình có sức nặng, không dùng góc siêu rộng hoặc làm biến dạng người; thấy đủ đầu, tay, gấu áo và bàn chân.

=== KIỂM TRA CUỐI ===
Đúng {people_count} khách, đúng danh tính, đúng giới tính, đúng cổ phục, đúng tư thế và đúng địa điểm; toàn bộ khách đã thay cổ phục và không còn quần áo hiện đại. Không thêm người, không dị dạng cơ thể, không chữ, logo, watermark hoặc khung. Photo Jacket được ghép sau khi AI hoàn tất. Trả về đúng một ảnh."""


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
    """Return the single approved signature pose for every concept and group size."""

    return 1


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
        ("ẢNH 5 — mẫu dàn dựng nghệ thuật; chỉ lấy bố cục, ánh sáng và màu sắc", REFERENCE_ROOT / "styles" / config["style"]),
    )
    return [(label, path.read_bytes(), "image/jpeg") for label, path in files]
