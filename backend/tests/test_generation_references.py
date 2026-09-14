import base64
import unittest
from io import BytesIO
from unittest.mock import AsyncMock, MagicMock, patch

from PIL import Image

from backend.app.config import Settings
from backend.app.prompts import (
    SCENARIO_CONFIGS,
    build_image_generation_prompt,
    load_scenario_references,
    select_pose_variant,
)
from backend.app.services.image_generation import ImageGenerationService, raster_dimensions


JPEG = b"\xff\xd8\xff\xc0\x00\x11\x08\x1e\x00\x10\xe0\x03\x01\x11\x00\x02\x11\x00\x03\x11\x00\xff\xd9"


class PromptReferenceTests(unittest.TestCase):
    def test_every_scenario_has_four_readable_jpeg_references(self):
        self.assertEqual(len(SCENARIO_CONFIGS), 7)
        for scenario_id in SCENARIO_CONFIGS:
            references = load_scenario_references(scenario_id)
            self.assertEqual([item[0].split(" — ")[0] for item in references], ["ẢNH 2", "ẢNH 3", "ẢNH 4", "ẢNH 5"])
            self.assertTrue(all(data.startswith(b"\xff\xd8\xff") and mime == "image/jpeg" for _, data, mime in references))
            for _, data, _ in references:
                with Image.open(BytesIO(data)) as image:
                    image.load()
                    self.assertLessEqual(max(image.size), 1920)
                    self.assertGreaterEqual(min(image.size), 570)
            with Image.open(BytesIO(references[3][1])) as style_image:
                style_image.load()
                self.assertAlmostEqual(style_image.width / style_image.height, 9 / 16, delta=0.01)

    def test_prompt_has_fixed_format_composition_and_reference_roles(self):
        variation_key = "known-human-readable-variant"
        selected_variant = select_pose_variant("hue_imperial_city", 3, variation_key)
        prompt = build_image_generation_prompt(3, "hue_imperial_city", variation_key)
        for required in (
            "9:16",
            "2K",
            "đúng 3 người",
            "sáu bàn tay và sáu bàn chân",
            "ẢNH 1",
            "ẢNH 2–3",
            "ẢNH 4",
            "ẢNH 5",
            "Đại Nội Huế",
            "khuôn mặt lớn nhất và gần máy ảnh nhất",
            "công trình phải đủ rõ để nhận ra ngay",
            "bóng tiếp xúc dưới chân",
            "không dùng ánh sáng studio phẳng",
            "không giống ảnh cắt ghép",
            "Máy ngang tầm mắt",
            "Mỗi khách chỉ có đúng hai cánh tay và hai bàn tay",
            "không tạo sách, bản đồ",
            "Photo Jacket",
            "ghép sau khi AI hoàn tất",
            f"BIẾN THỂ {selected_variant}",
        ):
            self.assertIn(required, prompt)
        self.assertIn("chỉ lấy trang phục và phụ kiện", prompt)
        self.assertIn("không sao chép", prompt.lower())
        self.assertIn("bỏ qua mọi người phía sau", prompt)
        self.assertNotIn("4K", prompt)
        self.assertNotIn(variation_key, prompt)
        self.assertNotIn("14%", prompt)
        self.assertNotIn("3:4", prompt)
        self.assertNotIn("example.jpeg", prompt)
        self.assertNotIn("example2.jpeg", prompt)
        for english_instruction in (
            "closure",
            "headwear",
            "silhouette",
            "fisheye",
            "fantasy",
            "editorial",
            "hospitality",
            "smiling",
        ):
            self.assertNotIn(english_instruction, prompt.lower())

    def test_gia_long_prompt_does_not_invite_scholarly_props(self):
        prompt = build_image_generation_prompt(3, "gia_long_palace", "props-audit")

        self.assertNotIn("PHONG THÁI TRÍ THỨC", prompt)
        self.assertNotIn("thông thái", prompt)
        self.assertNotIn("hiếu học", prompt)
        self.assertIn("không tạo sách, bản đồ", prompt)

    def test_location_prompts_lock_real_architectural_identifiers(self):
        expected_identifiers = {
            "thang_long_imperial": ("Đoan Môn", "năm cửa vòm", "lầu trung tâm ba tầng"),
            "hoa_lu_capital": ("Đền Vua Đinh Tiên Hoàng", "hai trụ biểu đá", "núi karst"),
            "hue_imperial_city": ("Lầu Ngũ Phụng", "năm lối vào", "chín bộ mái"),
            "thai_hoa_palace": ("sân Đại Triều Nghi", "hệ mái kép", "đại điện một tầng"),
            "an_dinh_palace": ("Khải Tường Lâu ba tầng", "phù điêu", "ban công lan can con tiện"),
            "independence_palace": ("lam bê tông", "đài phun nước tròn", "ban công giữa"),
            "gia_long_palace": ("Bảo tàng Thành phố Hồ Chí Minh", "bốn cột tròn", "trán mái tam giác"),
        }

        for scenario_id, identifiers in expected_identifiers.items():
            with self.subTest(scenario_id=scenario_id):
                prompt = build_image_generation_prompt(2, scenario_id, "location-lock")
                for identifier in identifiers:
                    self.assertIn(identifier, prompt)

        gia_long = build_image_generation_prompt(2, "gia_long_palace", "location-lock")
        self.assertIn("không dựng lâu đài ba tầng nhiều vòm", gia_long)
        self.assertIn("máy bay, trực thăng", gia_long)

    def test_each_location_has_a_distinct_cinematic_atmosphere(self):
        expected_atmospheres = {
            "thang_long_imperial": ("Bình minh nghi lễ", "xanh lam–vàng kim", "sương rất nhẹ"),
            "hoa_lu_capital": ("Bình minh sau cơn mưa nhẹ", "sương mỏng", "mặt sân ẩm"),
            "hue_imperial_city": ("Hoàng hôn ấm", "vàng hồng tiết chế", "Ngọ Môn"),
            "thai_hoa_palace": ("Bình minh đỏ–vàng", "dải sáng và bóng dài", "bóng người nối với bàn chân"),
            "an_dinh_palace": ("Cuối buổi chiều thanh lịch", "kem–xanh–vàng", "mặt tiền vàng mù tạt"),
            "independence_palace": ("Giờ vàng miền Nam", "đài phun", "điểm lấp lánh nhỏ"),
            "gia_long_palace": ("Chạng vạng xanh", "ánh sáng kiến trúc vàng ấm", "xanh–hổ phách"),
        }

        for scenario_id, atmosphere_markers in expected_atmospheres.items():
            with self.subTest(scenario_id=scenario_id):
                concept_prompt = SCENARIO_CONFIGS[scenario_id]["concept_prompt"]
                for marker in atmosphere_markers:
                    self.assertIn(marker, concept_prompt)
                self.assertIn("Bắt buộc", concept_prompt)

    def test_wide_landmarks_allow_vertical_reframing_without_losing_identity(self):
        for scenario_id in ("hue_imperial_city", "independence_palace", "gia_long_palace"):
            with self.subTest(scenario_id=scenario_id):
                prompt = build_image_generation_prompt(4, scenario_id, "vertical-framing")
                self.assertIn("Cho phép cắt", prompt)
                self.assertIn("9:16", prompt)
                self.assertNotIn("Không cắt mất hai đầu công trình", prompt)

    def test_rendered_prompt_contains_only_selected_pose_and_guest_count(self):
        scenario_id = "independence_palace"
        people_count = 4
        variation_key = "selected-pose-only"
        selected_variant = select_pose_variant(scenario_id, people_count, variation_key)

        prompt = build_image_generation_prompt(people_count, scenario_id, variation_key)

        self.assertEqual(prompt.count("BIẾN THỂ 1 —") + prompt.count("BIẾN THỂ 2 —") + prompt.count("BIẾN THỂ 3 —"), 1)
        self.assertIn(f"BIẾN THỂ {selected_variant} —", prompt)
        self.assertEqual(sum(prompt.count(f"- {count} người:") for count in range(1, 5)), 1)
        self.assertIn(f"- {people_count} người:", prompt)
        self.assertEqual(prompt.count("- Biểu cảm:"), 1)

    def test_every_scenario_has_one_distinct_signature_pose_and_all_counts(self):
        headings = set()
        for scenario_id, config in SCENARIO_CONFIGS.items():
            self.assertIn("pose_expression", config, scenario_id)
            pose = config["pose_expression"]
            self.assertEqual(pose.count("BIẾN THỂ 1 —"), 1)
            self.assertNotIn("BIẾN THỂ 2 —", pose)
            self.assertNotIn("BIẾN THỂ 3 —", pose)
            headings.add(pose.splitlines()[0])
            for people_count in range(1, 5):
                self.assertEqual(pose.count(f"- {people_count} người:"), 1)
            for field in ("concept_prompt", "male_clothing", "female_clothing"):
                self.assertIn(field, config)
            self.assertIn("style", config)
            for heading in (
                "Ý NIỆM VÀ KHÔNG KHÍ:",
                "KIẾN TRÚC BẮT BUỘC:",
                "DẤU HIỆU NHẬN DIỆN BẮT BUỘC:",
                "BỐ CỤC KHÔNG GIAN:",
                "ÁNH SÁNG VÀ MÀU SẮC:",
                "KHÔNG ĐƯỢC XUẤT HIỆN:",
            ):
                self.assertIn(heading, config["concept_prompt"])
            self.assertIn("ẢNH 2", config["male_clothing"])
            self.assertIn("ẢNH 3", config["female_clothing"])
        self.assertEqual(len(headings), len(SCENARIO_CONFIGS))

    def test_signature_poses_match_each_location_character(self):
        expected_pose_markers = {
            "thang_long_imperial": ("tiến qua cổng thành", "đoàn nghi lễ hình mũi tên"),
            "hoa_lu_capital": ("thế kiềng ba chân", "không chắp tay cầu nguyện"),
            "hue_imperial_city": ("cánh phượng", "không dang tay như múa"),
            "thai_hoa_palace": ("thế nghi lễ", "không quỳ hoặc cúi lạy"),
            "an_dinh_palace": ("thời trang đầu thế kỷ XX", "lookbook zigzag"),
            "independence_palace": ("đội hình chữ V", "không đứng trên cỏ"),
            "gia_long_palace": ("lời mời vào sảnh", "hành lang đón khách"),
        }

        for scenario_id, markers in expected_pose_markers.items():
            with self.subTest(scenario_id=scenario_id):
                pose = SCENARIO_CONFIGS[scenario_id]["pose_expression"]
                for marker in markers:
                    self.assertIn(marker, pose)

    def test_group_poses_have_distinct_silhouettes_and_no_default_clasped_hands(self):
        three_person_poses = set()
        four_person_poses = set()
        forbidden_hand_defaults = (
            "hai tay đặt chồng",
            "tay đều đặt thấp",
            "tất cả giữ tay thấp",
            "giữ tay thấp trong tay áo",
        )

        for scenario_id, config in SCENARIO_CONFIGS.items():
            with self.subTest(scenario_id=scenario_id):
                pose = config["pose_expression"]
                lines = pose.splitlines()
                three_person = next(line for line in lines if line.startswith("- 3 người:"))
                four_person = next(line for line in lines if line.startswith("- 4 người:"))
                self.assertNotEqual(three_person, four_person)
                self.assertIn("khác", four_person)
                for forbidden in forbidden_hand_defaults:
                    self.assertNotIn(forbidden, pose)
                three_person_poses.add(three_person)
                four_person_poses.add(four_person)

        self.assertEqual(len(three_person_poses), len(SCENARIO_CONFIGS))
        self.assertEqual(len(four_person_poses), len(SCENARIO_CONFIGS))

    def test_every_scenario_uses_the_approved_fresh_portrait_direction(self):
        forbidden_expression_conflicts = (
            "không làm trẻ hóa",
            "không cười đồng loạt",
            "một nụ cười nhẹ là đủ",
            "cười kín đáo",
            "nụ cười rất nhẹ",
        )

        for scenario_id, config in SCENARIO_CONFIGS.items():
            with self.subTest(scenario_id=scenario_id):
                pose_prompt = config["pose_expression"]
                self.assertEqual(pose_prompt.count("Tất cả khách nhìn thẳng vào máy ảnh"), 1)
                for conflict in forbidden_expression_conflicts:
                    self.assertNotIn(conflict, pose_prompt)

                prompt = build_image_generation_prompt(2, scenario_id, "fresh-portrait")
                for required in (
                    "photorealistic cinematic như ảnh bìa tạp chí/lookbook cao cấp",
                    "ẢNH 1 là nguồn duy nhất cho danh tính",
                    "không sao chép, trộn hoặc hoán đổi khuôn mặt",
                    "Người có diện mạo nữ",
                    "oval V-line tự nhiên",
                    "Người có diện mạo nam",
                    "đường hàm cân đối",
                    "trông trẻ hơn khoảng 5 tuổi",
                    "giảm quầng thâm, dấu hiệu mệt mỏi và nếp nhăn sâu",
                    "giữ kết cấu da thật",
                    "Bỏ hoàn toàn người mẫu/mannequin",
                    "không sao chép bất kỳ bộ phận cơ thể nào",
                    "Phân trang phục nam/nữ riêng cho từng khách",
                    "Không tự đổi thành hàng ngang hoặc dáng đứng chắp tay",
                    "Mỗi khách chỉ có đúng hai cánh tay và hai bàn tay",
                    "Không có tay thừa, tay lặp, chi mannequin",
                    "Nguồn sáng của concept là nguồn sáng chính",
                    "bóng đổ đúng hướng trên mặt đất",
                    "không dùng ánh sáng studio phẳng",
                    "Màu phim 35 mm hiện đại",
                    "không giống ảnh cắt ghép",
                    "Trả về đúng một ảnh",
                ):
                    self.assertIn(required, prompt)
                self.assertLess(len(prompt), 7_000)

    def test_pose_selection_is_fixed_instead_of_random(self):
        for scenario_id in SCENARIO_CONFIGS:
            for people_count in range(1, 5):
                self.assertEqual(
                    {select_pose_variant(scenario_id, people_count, key) for key in ("a", "b", "c")},
                    {1},
                )

    def test_jpeg_dimensions_are_read_from_header(self):
        self.assertEqual(raster_dimensions(JPEG), (4320, 7680))


class ProviderPayloadTests(unittest.IsolatedAsyncioTestCase):
    async def test_request_sends_identity_clothing_location_style_and_2k_9_16_config(self):
        response = MagicMock()
        response.is_success = True
        response.status_code = 200
        response.json.return_value = {"candidates": [{"content": {"parts": [{"inlineData": {
            "mimeType": "image/jpeg", "data": base64.b64encode(JPEG).decode("ascii")
        }}]}}]}
        client = AsyncMock()
        client.post.return_value = response
        context = AsyncMock()
        context.__aenter__.return_value = client
        context.__aexit__.return_value = False
        references = [
            ("IMAGE 2", b"male", "image/jpeg"),
            ("IMAGE 3", b"female", "image/jpeg"),
            ("IMAGE 4", b"place", "image/jpeg"),
            ("IMAGE 5", b"style", "image/jpeg"),
        ]

        with patch("backend.app.services.image_generation.httpx.AsyncClient", return_value=context):
            result = await ImageGenerationService(Settings(_env_file=None, gemini_api_key="test")).generate_image(
                image_bytes=JPEG,
                mime_type="image/jpeg",
                prompt="prompt",
                request_id="request",
                reference_images=references,
            )

        payload = client.post.await_args.kwargs["json"]
        parts = payload["contents"][0]["parts"]
        self.assertEqual(payload["generationConfig"]["imageConfig"], {"aspectRatio": "9:16", "imageSize": "2K"})
        self.assertEqual(len(parts), 11)
        self.assertEqual(parts[0]["text"], "ẢNH 1 — ảnh tham chiếu nhận diện khách; chỉ lấy danh tính khuôn mặt")
        self.assertEqual(parts[-1]["text"], "YÊU CẦU THIẾT KẾ:\nprompt")
        self.assertEqual((result.width, result.height), (4320, 7680))


if __name__ == "__main__":
    unittest.main()
