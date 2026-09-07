function FaceGuideOverlay({ faces, width, height }) {
  if (!width || !height) {
    return null;
  }

  return (
    <svg
      className="face-guide-overlay"
      viewBox={`0 0 ${width} ${height}`}
      preserveAspectRatio="xMidYMid slice"
      aria-hidden="true"
    >
      <g className="face-guide-overlay-mirror">
        {faces.map((face, index) => {
          const mirroredX = width - face.x - face.width;
          return (
            <g key={`${face.x}-${face.y}-${index}`}>
              <rect
                className="face-guide-box"
                x={mirroredX}
                y={face.y}
                width={face.width}
                height={face.height}
                rx={Math.max(8, face.width * 0.08)}
              />
              <text className="face-guide-label" x={mirroredX + 8} y={face.y + 22}>
                {index + 1}
              </text>
            </g>
          );
        })}
      </g>
    </svg>
  );
}

export default FaceGuideOverlay;
