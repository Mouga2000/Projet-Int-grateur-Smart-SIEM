// src/components/investigation/PivotButton.tsx
import { useNavigate } from "react-router-dom";

type PivotType = "ip" | "user" | "host" | "alert";

interface PivotButtonProps {
  type: PivotType;
  value: string;
}

const LABELS: Record<PivotType, string> = {
  ip:    "Pivoter sur IP",
  user:  "Pivoter sur utilisateur",
  host:  "Pivoter sur hôte",
  alert: "Voir l'alerte liée",
};

const PivotButton = ({ type, value }: PivotButtonProps) => {
  const navigate = useNavigate();

  const handlePivot = () => {
    if (type === "alert") {
      navigate(`/alerts/${value}`);
    } else {
      navigate(`/investigation?pivot=${type}&value=${encodeURIComponent(value)}`);
    }
  };

  return (
    <button
      onClick={handlePivot}
      className="inline-flex items-center gap-1 text-xs text-cyan-400 hover:text-cyan-300 transition-colors"
    >
      <span>→</span>
      <span>{LABELS[type]}</span>
      <span className="font-mono text-gray-500">({value})</span>
    </button>
  );
};

export default PivotButton;