"""Prompt configuration for the Century Ply multi-person portrait POC."""

from __future__ import annotations


SCENARIO_PROMPTS = {
    "imperial_hue": (
        "Scenario: Imperial Hue. Dress every guest in elegant, historically "
        "inspired Vietnamese imperial clothing with realistic silk, brocade, "
        "embroidery, layered construction, and natural fabric weight. Place the "
        "group naturally in a refined Hue imperial palace with warm architectural "
        "light, restrained ornamental detail, and believable depth."
    ),
    "temple_aodai": (
        "Scenario: Timeless Ao Dai. Dress every guest in an elegant traditional "
        "Vietnamese áo dài with realistic silk texture, tailored construction, "
        "subtle embroidery, and culturally respectful styling. Place the group at "
        "the Temple of Literature in Hanoi with warm daylight, historic courtyards, "
        "and softly defocused architecture."
    ),
    "hoian_heritage": (
        "Scenario: Hoi An Heritage. Dress every guest in refined traditional "
        "Vietnamese clothing with realistic woven fabric, tasteful details, and "
        "natural fit. Place the group in lantern-lit Hoi An at blue hour with warm "
        "lantern glow, an atmospheric old-town street, and convincing photographic depth."
    ),
}

SCENARIO_IDS = frozenset(SCENARIO_PROMPTS)
ALLOWED_PEOPLE_COUNTS = frozenset({1, 2, 3, 4})


BASE_IMAGE_GENERATION_PROMPT = """Use the uploaded group photograph as the identity reference.

The input contains exactly {people_count} distinct guests. Preserve exactly those
same {people_count} guests and transform every guest. Preserve each guest's
recognizable facial identity, facial proportions, skin tone, natural skin texture,
age, hairstyle, expression, body position, relative height, and left-to-right
arrangement. Keep the guests distinct and clearly visible.

Do not add, remove, replace, merge, swap, or duplicate any person or face. Do not
assign one guest's face to another guest's body. Do not add background people,
face-like portraits, statues with visible faces, additional people, or crowds. Do not turn one person
into multiple people. Keep every complete face and the top of every head visible.

Create one cohesive, photorealistic vertical 3:4 group photograph. Use natural
skin detail, realistic eyes and hair, physically believable light, and a flattering
eye-level perspective. Transform every guest with the selected clothing and place
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
