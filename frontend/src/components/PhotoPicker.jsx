import { ImagePlus } from "lucide-react";
import { useRef } from "react";

function PhotoPicker({ onFileSelected, buttonClassName = "secondary-button", label = "Choose from gallery", disabled = false }) {
  const inputRef = useRef(null);

  function openPicker() {
    inputRef.current?.click();
  }

  function handleChange(event) {
    const [file] = event.target.files || [];
    event.target.value = "";
    if (file) {
      onFileSelected(file);
    }
  }

  return (
    <>
      <input
        ref={inputRef}
        className="visually-hidden"
        type="file"
        accept="image/jpeg,image/png,image/webp"
        onChange={handleChange}
        tabIndex={-1}
        aria-hidden="true"
      />
      <button className={buttonClassName} type="button" onClick={openPicker} disabled={disabled}>
        <ImagePlus size={19} aria-hidden="true" />
        {label}
      </button>
    </>
  );
}

export default PhotoPicker;
