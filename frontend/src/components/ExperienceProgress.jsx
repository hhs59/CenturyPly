import { Camera, MapPin, Sparkles, Users } from "lucide-react";

const STEPS = [
  { id: "scenario", label: "Place", icon: MapPin },
  { id: "people", label: "Guests", icon: Users },
  { id: "photo", label: "Photo", icon: Camera },
  { id: "portrait", label: "Portrait", icon: Sparkles },
];

const STEP_INDEX = {
  scenario: 0,
  people: 1,
  camera_loading: 2,
  aligning: 2,
  countdown: 2,
  capture_check: 2,
  camera_error: 2,
  photo_ready: 2,
  generating: 3,
  result: 3,
};

export default function ExperienceProgress({ step }) {
  const activeIndex = STEP_INDEX[step] ?? 0;

  return (
    <nav className="experience-progress" aria-label="Portrait creation progress">
      <ol>
        {STEPS.map(({ id, label, icon: Icon }, index) => {
          const status = index < activeIndex ? "complete" : index === activeIndex ? "current" : "upcoming";
          return (
            <li className={`experience-progress-step experience-progress-${status}`} key={id} aria-current={status === "current" ? "step" : undefined}>
              <span className="experience-progress-icon" aria-hidden="true"><Icon size={15} strokeWidth={2} /></span>
              <span className="experience-progress-label">{label}</span>
            </li>
          );
        })}
      </ol>
    </nav>
  );
}
