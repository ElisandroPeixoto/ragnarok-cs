import { useEffect, useState } from "react";
import { assetUrl } from "../api.js";

// Plays one clip of a sprite sheet made by tools/ro_to_sheet.py: the sheet is a grid of frame_w x frame_h cells,
// one row per clip; the frames advance at the clip's fps (looping clips restart, the others hold the last frame).
export default function SpritePreview({ sheet, clip, scale = 1, className = "" }) {
  const clipData = sheet?.clips?.[clip] ?? Object.values(sheet?.clips ?? {})[0];
  const [frame, setFrame] = useState(0);

  useEffect(() => {
    setFrame(0);
    if (!clipData || clipData.frames <= 1) return undefined;
    const timer = setInterval(() => {
      setFrame((current) => {
        if (current + 1 < clipData.frames) return current + 1;
        return clipData.loop === false ? current : 0;
      });
    }, 1000 / (clipData.fps || 8));
    return () => clearInterval(timer);
  }, [sheet, clip]);  // eslint-disable-line react-hooks/exhaustive-deps

  if (!sheet || !clipData) {
    return <div className={`sprite-missing ${className}`}>no sheet</div>;
  }
  const width = sheet.frame_w * scale;
  const height = sheet.frame_h * scale;
  return (
    <div
      className={`sprite ${className}`}
      style={{
        width,
        height,
        backgroundImage: `url(${assetUrl(sheet.src)})`,
        backgroundSize: `${sheet.cols * width}px ${sheet.rows * height}px`,
        backgroundPosition: `-${frame * width}px -${clipData.row * height}px`,
      }}
    />
  );
}

// The clip that best shows a sheet standing still: the front pose for players, idle facing the viewer for monsters
export function defaultClip(sheet) {
  const clips = sheet?.clips ?? {};
  return ["stand_s", "idle_sw", "idle_se"].find((name) => name in clips) ?? Object.keys(clips)[0];
}
