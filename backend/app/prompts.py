"""Prompt configuration for the Century Ply multi-person portrait POC."""

from __future__ import annotations


SCENARIO_PROMPTS = {
    "thang_long_imperial": (
        "Location: Hoàng Thành Thăng Long, the Thang Long Imperial Citadel in "
        "northern Vietnam. Dress every guest in formal Vietnamese court-inspired "
        "áo tấc or áo ngũ thân with refined silk, brocade, restrained embroidery, "
        "and respectful khăn đóng details. Place the group naturally among the "
        "citadel's imperial courtyards and historic architecture with dignified "
        "northern light and believable depth."
    ),
    "hoa_lu_capital": (
        "Location: Cố đô Hoa Lư, the Hoa Lu Ancient Capital in northern Vietnam. "
        "Dress every guest in period-respectful Vietnamese áo tấc or áo ngũ thân "
        "with natural silk, brocade, subtle embroidery, and graceful construction. "
        "Place the group in the ancient capital's historic courtyards and gateways, "
        "with a calm mountain-framed setting and believable photographic depth."
    ),
    "hue_imperial_city": (
        "Location: Đại Nội Huế, the Hue Imperial City in central Vietnam. Dress "
        "every guest in elegant Vietnamese imperial court clothing with realistic "
        "silk, brocade, floral embroidery, and period-respectful áo Nhật Bình, áo "
        "tấc, or áo ngũ thân influences. Place the group naturally in the refined "
        "palace courtyards of the Đại Nội with warm architectural light and depth."
    ),
    "thai_hoa_palace": (
        "Location: Điện Thái Hòa, the Thai Hoa Palace in Huế. Dress every guest in "
        "formal Nguyễn-era Vietnamese court styling with rich but tasteful silk, "
        "brocade, embroidery, and áo Nhật Bình, áo tấc, or áo ngũ thân influences. "
        "Place the group inside a dignified ceremonial palace setting with lacquered "
        "wood, restrained imperial red and gold, and believable light."
    ),
    "an_dinh_palace": (
        "Location: Cung An Định, An Dinh Palace in Huế. Dress every guest in elegant "
        "Nguyễn court-inspired garments with tailored silk, brocade, quiet embroidery, "
        "and natural fabric weight. Place the group in the palace's ornate historic "
        "setting and intimate courtyards with refined warm light and convincing depth."
    ),
    "independence_palace": (
        "Location: Dinh Độc Lập / Dinh Thống Nhất, Independence Palace in southern "
        "Vietnam. Dress every guest in formal Vietnamese áo dài or refined heritage "
        "clothing with natural silk, tailored construction, and subtle embroidery. "
        "Place the group against the palace's composed architectural setting with "
        "warm southern light, dignified scale, and no modern crowds."
    ),
    "gia_long_palace": (
        "Location: Dinh Gia Long, Gia Long Palace in southern Vietnam. Dress every "
        "guest in formal áo ngũ thân, áo dài, or court-inspired Vietnamese heritage "
        "styling with realistic silk, brocade, and restrained embroidery. Place the "
        "group naturally among the palace's historic architecture and gracious "
        "courtyards with warm southern light and believable photographic depth."
    ),
}

SCENARIO_IDS = frozenset(SCENARIO_PROMPTS)
ALLOWED_PEOPLE_COUNTS = frozenset({1, 2, 3, 4})


BASE_IMAGE_GENERATION_PROMPT = """Use the captured group photograph as the identity reference.

The final image must contain exactly {people_count} distinct people. Use only the
{people_count} dominant foreground guests as the subjects and transform each selected guest. Preserve each selected guest's
recognizable facial identity, facial proportions, skin tone, natural skin texture,
age, hairstyle, expression, body position, relative height, and left-to-right
arrangement. Keep the guests distinct and clearly visible.

Preserve each selected guest's natural skin tone exactly as photographed. Do not lighten,
darken, recolor, homogenize, or stereotype skin tone or facial features.

Do not remove, replace, merge, swap, or duplicate any selected foreground guest or face. Do not
assign one selected guest's face to another guest's body. Replace the original background completely
and do not reproduce incidental background people. Do not add background people, face-like portraits,
statues with visible faces, additional people, or crowds. Do not turn one person into multiple people.
Keep every complete face and the top of every head visible.

Create one cohesive, photorealistic vertical 3:4 group photograph. Use natural
skin detail, realistic eyes and hair, physically believable light, and a flattering
eye-level perspective. Transform every selected guest with the selected clothing and place
the full group naturally inside the selected setting. Keep the composition tight
enough for every guest to remain recognizable while leaving comfortable space
around every head.

Avoid face coverings, masks, text, logos, borders, black bars, malformed hands,
duplicate limbs, illustration, animation, waxy skin, excessive beautification,
heavy smoothing, and artificial HDR. Return one edited image."""


def build_image_generation_prompt(people_count: int, scenario_id: str) -> str:
    """Build the single provider prompt after the API has validated both fields."""

    if people_count not in ALLOWED_PEOPLE_COUNTS:
        raise ValueError("people_count must be 1, 2, 3, or 4")
    if scenario_id not in SCENARIO_PROMPTS:
        raise ValueError("scenario_id is not supported")

    return (
        BASE_IMAGE_GENERATION_PROMPT.format(people_count=people_count)
        + "\n\n"
        + SCENARIO_PROMPTS[scenario_id]
    )
