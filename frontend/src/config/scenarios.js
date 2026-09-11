export const SCENARIOS = [
  {
    id: "thang_long_imperial",
    name: "Thang Long Imperial Citadel",
    shortDescription: "Northern court elegance among ancient citadel walls",
    regionLabel: "Northern Vietnam",
    accent: "#b34a3f",
    previewImage: "/concepts/thang-long-imperial-scene.webp",
  },
  {
    id: "hoa_lu_capital",
    name: "Hoa Lu Ancient Capital",
    shortDescription: "Ceremonial heritage styling in Vietnam's first imperial capital",
    regionLabel: "Northern Vietnam",
    accent: "#9f613d",
    previewImage: "/concepts/hoa-lu-capital-scene.webp",
  },
  {
    id: "hue_imperial_city",
    name: "Hue Imperial City",
    shortDescription: "Graceful royal portraits in the heart of the Đại Nội",
    regionLabel: "Central Vietnam",
    accent: "#a65b43",
    previewImage: "/concepts/hue-imperial-city-scene.webp",
  },
  {
    id: "thai_hoa_palace",
    name: "Thai Hoa Palace",
    shortDescription: "Ceremonial Nguyễn-era grandeur with a warm imperial glow",
    regionLabel: "Central Vietnam",
    accent: "#c08a42",
    previewImage: "/concepts/thai-hoa-palace-scene.webp",
  },
  {
    id: "an_dinh_palace",
    name: "An Dinh Palace",
    shortDescription: "A refined palace portrait inspired by Huế's royal residence",
    regionLabel: "Central Vietnam",
    accent: "#b77452",
    previewImage: "/concepts/an-dinh-palace-scene.webp",
  },
  {
    id: "independence_palace",
    name: "Independence Palace",
    shortDescription: "Southern heritage elegance against a landmark palace setting",
    regionLabel: "Southern Vietnam",
    accent: "#b45b39",
    previewImage: "/concepts/independence-palace-scene.webp",
  },
  {
    id: "gia_long_palace",
    name: "Gia Long Palace",
    shortDescription: "A dignified southern palace portrait with timeless character",
    regionLabel: "Southern Vietnam",
    accent: "#8f4d39",
    previewImage: "/concepts/gia-long-palace-scene.webp",
  },
];

export const SCENARIO_IDS = new Set(SCENARIOS.map((scenario) => scenario.id));

export function getScenario(scenarioId) {
  return SCENARIOS.find((scenario) => scenario.id === scenarioId) || null;
}
