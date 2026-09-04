export const SCENARIOS = [
  {
    id: "imperial_hue",
    name: "Imperial Hue",
    shortDescription: "Refined imperial clothing in a Hue palace",
    clothing: "Silk, brocade, and graceful imperial details",
    setting: "A warm, elegant Hue palace",
    accent: "#dca96b",
    previewImage: "/concepts/imperial-hue.png",
  },
  {
    id: "temple_aodai",
    name: "Timeless Ao Dai",
    shortDescription: "Elegant áo dài at the Temple of Literature",
    clothing: "Tailored áo dài with subtle embroidery",
    setting: "Historic courtyards in Hanoi",
    accent: "#83c9bd",
    previewImage: "/concepts/timeless-ao-dai.png",
  },
  {
    id: "hoian_heritage",
    name: "Hoi An Heritage",
    shortDescription: "Traditional clothing among Hoi An lanterns",
    clothing: "Woven Vietnamese textiles and tasteful details",
    setting: "Lantern-lit Hoi An at blue hour",
    accent: "#ef9e72",
    previewImage: "/concepts/hoian-heritage.png",
  },
];

export const SCENARIO_IDS = new Set(SCENARIOS.map((scenario) => scenario.id));

export function getScenario(scenarioId) {
  return SCENARIOS.find((scenario) => scenario.id === scenarioId) || null;
}
