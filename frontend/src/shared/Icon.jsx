const PATHS = {
  home: "M3 11l9-8 9 8 M5 10v10a1 1 0 001 1h4v-6h4v6h4a1 1 0 001-1V10",
  card: "M2 6h20v12H2z M2 10h20",
  badge: "M3 5h18v14H3z M8 12a2 2 0 104 0 2 2 0 00-4 0z M14 10h4 M14 14h3",
  repeat: "M17 2l4 4-4 4 M21 6H8a4 4 0 00-4 4v1 M7 22l-4-4 4-4 M3 18h13a4 4 0 004-4v-1",
  receipt: "M6 2h12v20l-3-2-3 2-3-2-3 2V2z M9 7h6 M9 11h6 M9 15h4",
  search: "M11 4a7 7 0 100 14 7 7 0 000-14z M21 21l-4.35-4.35",
  help: "M12 22a10 10 0 100-20 10 10 0 000 20z M9.5 9a2.5 2.5 0 015 .5c0 1.5-2 1.5-2.5 3 M12 17h.01",
  play: "M6 4l14 8-14 8V4z",
  book: "M4 4a2 2 0 012-2h13v18H6a2 2 0 00-2 2V4z M20 17H6a2 2 0 00-2 2",
  bookOpen: "M12 6a5 5 0 00-5-2H2v14h5a5 5 0 015 2 5 5 0 015-2h5V4h-5a5 5 0 00-5 2z M12 6v14",
  alertTriangle: "M12 3l10 18H2L12 3z M12 10v4 M12 17h.01",
  tool: "M14 6l4 4-7 7-4-4z M17 3l4 4-2 2-4-4z M3 21l4-4",
  message: "M21 12a8 8 0 01-8 8H7l-4 3 1-5A8 8 0 1121 12z",
  x: "M18 6L6 18 M6 6l12 12",
  checkCircle: "M12 22a10 10 0 100-20 10 10 0 000 20z M8 12l3 3 5-6",
  alertCircle: "M12 22a10 10 0 100-20 10 10 0 000 20z M12 8v4 M12 16h.01",
  clipboard: "M9 3h6v2H9z M6 5h12v16H6z M9 10h6 M9 14h6",
  star: "M12 2l3 7h7l-5.5 4.5L18 21l-6-4.5L6 21l1.5-7.5L2 9h7z",
  cart: "M3 3h2l2.6 12.4a2 2 0 002 1.6h8.8a2 2 0 002-1.6L21 8H6",
  package: "M3 8l9-5 9 5v8l-9 5-9-5V8z M3 8l9 5 9-5 M12 13v8",
  columns: "M4 4h6v16H4z M14 4h6v10h-6z",
  plus: "M12 5v14 M5 12h14",
  calendar: "M4 5h16v16H4z M4 9h16 M8 3v4 M16 3v4",
  pill: "M4.5 12.5l7-7a4.95 4.95 0 117 7l-7 7a4.95 4.95 0 01-7-7z M8.5 8.5l7 7",
  stethoscope: "M6 3v6a4 4 0 008 0V3 M14 13a5 5 0 01-10 0 M18 13a2 2 0 11-4 0 2 2 0 014 0z",
  link: "M9 15l6-6 M8 12l-3.5 3.5a3.5 3.5 0 105 5L13 17 M11 7l3.5-3.5a3.5 3.5 0 115 5L16 12",
  refresh: "M3 12a9 9 0 0115.5-6.5L21 8 M21 12a9 9 0 01-15.5 6.5L3 16 M17 5v4h-4 M7 19v-4h4",
  arrowLeft: "M19 12H5 M12 19l-7-7 7-7",
};

export default function Icon({ name, size = 18, strokeWidth = 1.75, className = "" }) {
  const d = PATHS[name];
  if (!d) return null;
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth={strokeWidth}
      strokeLinecap="round"
      strokeLinejoin="round"
      className={className}
    >
      <path d={d} />
    </svg>
  );
}
