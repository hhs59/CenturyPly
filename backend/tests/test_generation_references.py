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
    def test_every_scenario_has_three_readable_jpeg_references(self):
        self.assertEqual(len(SCENARIO_CONFIGS), 7)
        for scenario_id in SCENARIO_CONFIGS:
            references = load_scenario_references(scenario_id)
            self.assertEqual([item[0].split(" — ")[0] for item in references], ["ẢNH 2", "ẢNH 3", "ẢNH 4"])
            self.assertTrue(all(data.startswith(b"\xff\xd8\xff") and mime == "image/jpeg" for _, data, mime in references))
            for _, data, _ in references:
                with Image.open(BytesIO(data)) as image:
                    image.load()
                    self.assertGreaterEqual(image.width, 1500)
                    self.assertGreaterEqual(image.height, 990)

    def test_prompt_has_fixed_format_composition_and_reference_roles(self):
        variation_key = "known-human-readable-variant"
        selected_variant = select_pose_variant("hue_imperial_city", 3, variation_key)
        prompt = build_image_generation_prompt(3, "hue_imperial_city", variation_key)
        for required in (
            "9:16",
            "2K",
            "đúng 3 người",
            "cả hai bàn chân",
            "3–5%",
            "ẢNH 1",
            "ẢNH 2",
            "ẢNH 3",
            "ẢNH 4",
            "Đại Nội Huế",
            "khuôn mặt lớn nhất, gần camera nhất",
            "Giữ thứ tự nhận diện trái sang phải",
            "bản thiết kế hình ảnh bắt buộc của hậu cảnh",
            "đủ lớn và đủ nét để người xem nhận ra trong hai giây",
            "MÁY ẢNH VÀ ÁNH SÁNG",
            "35–50mm",
            "Độ sâu trường ảnh vừa phải",
            "không vùng nhòe sáng lớn che kiến trúc",
            "Được điều chỉnh ranh giới khung hình từ ảnh mẫu ngang sang ảnh dọc 9:16",
            "Hai bàn tay của từng khách phải để trống",
            "Không tạo sách, bản đồ, cuộn giấy",
            "Photo Jacket",
            "ghép bên ngoài",
            f"BIẾN THỂ {selected_variant}",
        ):
            self.assertIn(required, prompt)
        self.assertIn("Chỉ tham khảo trang phục", prompt)
        self.assertIn("Không sao chép", prompt)
        self.assertIn("Bỏ qua hoàn toàn mọi người nhỏ hơn, xa hơn", prompt)
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
            "bokeh",
            "fisheye",
            "fantasy",
            "editorial",
            "hospitality",
        ):
            self.assertNotIn(english_instruction, prompt.lower())

    def test_gia_long_prompt_does_not_invite_scholarly_props(self):
        prompt = build_image_generation_prompt(3, "gia_long_palace", "props-audit")

        self.assertNotIn("PHONG THÁI TRÍ THỨC", prompt)
        self.assertNotIn("thông thái", prompt)
        self.assertNotIn("hiếu học", prompt)
        self.assertIn("bất kỳ vật thể nào trong tay", prompt)

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

    def test_every_scenario_has_three_named_variants_and_all_counts(self):
        for scenario_id, config in SCENARIO_CONFIGS.items():
            self.assertIn("pose_expression", config, scenario_id)
            pose = config["pose_expression"]
            for variant in range(1, 4):
                self.assertIn(f"BIẾN THỂ {variant} —", pose)
                for people_count in range(1, 5):
                    self.assertIn(f"- {people_count} người:", pose)
            for field in ("concept_prompt", "male_clothing", "female_clothing"):
                self.assertIn(field, config)
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

    def test_pose_variant_is_sha256_deterministic_and_all_three_are_reachable(self):
        self.assertEqual(
            select_pose_variant("hue_imperial_city", 2, "same-key"),
            select_pose_variant("hue_imperial_city", 2, "same-key"),
        )
        known_keys = ["variant-key-a", "variant-key-b", "known-key-4"]
        self.assertEqual(
            {select_pose_variant("hue_imperial_city", 2, key) for key in known_keys},
            {1, 2, 3},
        )

    def test_jpeg_dimensions_are_read_from_header(self):
        self.assertEqual(raster_dimensions(JPEG), (4320, 7680))


class ProviderPayloadTests(unittest.IsolatedAsyncioTestCase):
    async def test_request_sends_identity_clothing_location_and_2k_9_16_config(self):
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
        references = [("IMAGE 2", b"male", "image/jpeg"), ("IMAGE 3", b"female", "image/jpeg"), ("IMAGE 4", b"place", "image/jpeg")]

        with patch("backend.app.services.image_generation.httpx.AsyncClient", return_value=context):
            result = await ImageGenerationService(Settings(_env_file=None, gemini_api_key="test")).generate_image(
                image_bytes=JPEG,
                mime_type="image/jpeg",
                prompt="prompt",
                request_id="request",
                reference_images=references,
            )

        payload = client.post.await_args.kwargs["json"]
        self.assertEqual(payload["generationConfig"]["imageConfig"], {"aspectRatio": "9:16", "imageSize": "2K"})
        self.assertEqual(len(payload["contents"][0]["parts"]), 9)
        self.assertEqual((result.width, result.height), (4320, 7680))


if __name__ == "__main__":
    unittest.main()
