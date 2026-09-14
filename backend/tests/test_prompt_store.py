import json
from io import BytesIO
import tempfile
import unittest
from pathlib import Path

from PIL import Image

from backend.app.prompt_store import (
    MAX_BASE_PROMPT_LENGTH,
    MAX_SCENARIO_PROMPT_LENGTH,
    PromptConfigurationError,
    PromptStore,
)
from backend.app.prompts import build_image_generation_prompt, default_prompt_configuration


def reference_image_bytes(size=(2000, 1200)):
    output = BytesIO()
    Image.new("RGB", size, "#8a5b3d").save(output, format="PNG")
    return output.getvalue()


class PromptStoreTests(unittest.TestCase):
    def test_defaults_keep_the_existing_four_field_scenario_schema(self):
        defaults = default_prompt_configuration()

        self.assertEqual(set(defaults), {"base_prompt", "scenarios"})
        for scenario_id, scenario in defaults["scenarios"].items():
            with self.subTest(scenario_id=scenario_id):
                self.assertEqual(
                    set(scenario),
                    {"concept_prompt", "male_clothing", "female_clothing", "pose_expression"},
                )

    def test_longer_defaults_stay_below_configured_length_limits(self):
        defaults = default_prompt_configuration()

        self.assertLessEqual(len(defaults["base_prompt"]), MAX_BASE_PROMPT_LENGTH)
        for scenario_id, scenario in defaults["scenarios"].items():
            for field, value in scenario.items():
                with self.subTest(scenario_id=scenario_id, field=field):
                    self.assertLessEqual(len(value), MAX_SCENARIO_PROMPT_LENGTH)

    def test_defaults_round_trip_and_custom_prompt_is_used_for_generation(self):
        with tempfile.TemporaryDirectory() as directory:
            store = PromptStore(Path(directory))
            config = store.defaults()
            config["scenarios"]["hue_imperial_city"]["concept_prompt"] = (
                "Ý NIỆM VÀ KHÔNG KHÍ:\nĐại Nội Huế – thử nghiệm Unicode.\n"
                "KIẾN TRÚC BẮT BUỘC:\nCổng sơn son.\n"
                "BỐ CỤC KHÔNG GIAN:\nTiền cảnh.\n"
                "ÁNH SÁNG VÀ MÀU SẮC:\nVàng ấm.\n"
                "KHÔNG ĐƯỢC XUẤT HIỆN:\nChữ giả."
            )

            saved = store.save(config)
            loaded = store.read()

            self.assertEqual(loaded, saved)
            self.assertIn("Đại Nội Huế – thử nghiệm Unicode", build_image_generation_prompt(
                2,
                "hue_imperial_city",
                prompt_configuration=loaded,
            ))

            for heading in (
                "Ý NIỆM VÀ KHÔNG KHÍ:",
                "KIẾN TRÚC BẮT BUỘC:",
                "BỐ CỤC KHÔNG GIAN:",
                "ÁNH SÁNG VÀ MÀU SẮC:",
                "KHÔNG ĐƯỢC XUẤT HIỆN:",
            ):
                self.assertIn(heading, loaded["scenarios"]["hue_imperial_city"]["concept_prompt"])

    def test_missing_prompts_file_falls_back_to_canonical_defaults(self):
        with tempfile.TemporaryDirectory() as directory:
            store = PromptStore(Path(directory))

            self.assertFalse(store.path.exists())
            self.assertEqual(store.read(), default_prompt_configuration())

    def test_valid_runtime_prompts_file_takes_precedence_over_defaults(self):
        with tempfile.TemporaryDirectory() as directory:
            store = PromptStore(Path(directory))
            runtime = default_prompt_configuration()
            runtime["scenarios"]["hue_imperial_city"]["concept_prompt"] = "RUNTIME OVERRIDE — Đại Nội Huế"
            store.path.parent.mkdir(parents=True, exist_ok=True)
            store.path.write_text(json.dumps(runtime, ensure_ascii=False), encoding="utf-8")

            loaded = store.read()

            self.assertEqual(loaded, runtime)
            self.assertNotEqual(loaded, default_prompt_configuration())
            self.assertIn("RUNTIME OVERRIDE", loaded["scenarios"]["hue_imperial_city"]["concept_prompt"])

    def test_base_prompt_must_keep_runtime_variables(self):
        with tempfile.TemporaryDirectory() as directory:
            store = PromptStore(directory)
            config = store.defaults()
            config["base_prompt"] = "No runtime variables"

            with self.assertRaisesRegex(PromptConfigurationError, "people_count"):
                store.save(config)

    def test_invalid_saved_file_falls_back_to_source_defaults(self):
        with tempfile.TemporaryDirectory() as directory:
            store = PromptStore(directory)
            store.path.parent.mkdir(parents=True, exist_ok=True)
            store.path.write_text("not json", encoding="utf-8")

            self.assertEqual(store.read(), store.defaults())

    def test_invalid_runtime_placeholders_fall_back_and_save_rejects_them(self):
        with tempfile.TemporaryDirectory() as directory:
            store = PromptStore(directory)
            defaults = store.defaults()
            invalid = dict(defaults)
            invalid["base_prompt"] = defaults["base_prompt"].replace("{variation_hint}", "")
            store.path.parent.mkdir(parents=True, exist_ok=True)
            store.path.write_text(json.dumps(invalid, ensure_ascii=False), encoding="utf-8")

            self.assertEqual(store.read(), defaults)
            with self.assertRaisesRegex(PromptConfigurationError, "variation_hint"):
                store.save(invalid)

    def test_legacy_combined_scenario_prompt_is_migrated(self):
        with tempfile.TemporaryDirectory() as directory:
            store = PromptStore(directory)
            defaults = store.defaults()
            legacy = {
                "base_prompt": defaults["base_prompt"],
                "scenarios": {
                    scenario_id: {
                        "prompt": "BỐI CẢNH: Test; TRANG PHỤC: khách nam áo xanh; khách nữ áo đỏ",
                        "pose_expression": config["pose_expression"],
                    }
                    for scenario_id, config in defaults["scenarios"].items()
                },
            }

            normalized = store.save(legacy)

            self.assertEqual(normalized["scenarios"]["hue_imperial_city"]["concept_prompt"], "BỐI CẢNH: Test;")
            self.assertEqual(normalized["scenarios"]["hue_imperial_city"]["male_clothing"], "khách nam áo xanh")
            self.assertEqual(normalized["scenarios"]["hue_imperial_city"]["female_clothing"], "khách nữ áo đỏ")

    def test_reference_override_is_used_and_can_return_to_default(self):
        with tempfile.TemporaryDirectory() as directory:
            store = PromptStore(directory)
            default_path = store.reference_path("hue_imperial_city", "location")
            store.save_reference("hue_imperial_city", "location", reference_image_bytes(), "image/png")

            override_path = store.reference_path("hue_imperial_city", "location")
            self.assertNotEqual(override_path, default_path)
            self.assertEqual(override_path.suffix, ".jpg")
            self.assertEqual(store.load_references("hue_imperial_city")[2][2], "image/jpeg")
            with Image.open(override_path) as optimized:
                self.assertLessEqual(max(optimized.size), 1920)

            store.reset_reference("hue_imperial_city", "location")
            self.assertEqual(store.reference_path("hue_imperial_city", "location"), default_path)

    def test_style_reference_is_loaded_and_can_be_overridden(self):
        with tempfile.TemporaryDirectory() as directory:
            store = PromptStore(directory)
            default_path = store.reference_path("hue_imperial_city", "style")

            self.assertEqual(default_path.parent.name, "styles")
            self.assertTrue(default_path.is_file())
            self.assertEqual(store.load_references("hue_imperial_city")[3][0].split(" — ")[0], "ẢNH 5")

            store.save_reference("hue_imperial_city", "style", reference_image_bytes(), "image/png")
            self.assertEqual(store.reference_path("hue_imperial_city", "style").suffix, ".jpg")
            self.assertEqual(store.load_references("hue_imperial_city")[3][2], "image/jpeg")

            store.reset_reference("hue_imperial_city", "style")
            self.assertEqual(store.reference_path("hue_imperial_city", "style"), default_path)


if __name__ == "__main__":
    unittest.main()
