function BrandLogos() {
  return (
    <div className="flex items-center gap-3">
      <svg width="56" height="29" viewBox="0 0 186 96" xmlns="http://www.w3.org/2000/svg" aria-label="KPMG">
        <g fill="none" stroke="#00338D" strokeWidth="3.2" strokeLinejoin="miter">
          <path d="M18,3 L42,3 L36,40 L12,40 Z" />
          <path d="M50,3 L74,3 L68,40 L44,40 Z" />
          <path d="M82,3 L106,3 L100,40 L76,40 Z" />
          <path d="M114,3 L138,3 L132,40 L108,40 Z" />
        </g>
        <text
          x="3"
          y="80"
          fill="#00338D"
          fontFamily="-apple-system,'Helvetica Neue','Arial Black',sans-serif"
          fontWeight="900"
          fontSize="44"
          letterSpacing="3"
        >
          KPMG
        </text>
      </svg>
      <div className="h-5 w-px bg-studio-900/15" />
      <svg width="118" height="30" viewBox="0 0 230 60" xmlns="http://www.w3.org/2000/svg" aria-label="Asian Paints">
        <text
          x="0"
          y="42"
          fill="#ED1C24"
          fontFamily="-apple-system,'Helvetica Neue',sans-serif"
          fontWeight="800"
          fontSize="34"
        >
          asianpaints
        </text>
      </svg>
    </div>
  );
}

export function Header() {
  return (
    <header className="relative z-30 mx-3 mt-3 flex items-center justify-between rounded-2xl border border-white/40 bg-white/70 px-6 py-3 shadow-lg backdrop-blur-md md:mx-6 md:mt-4 md:px-8">
      <BrandLogos />
      <a
        href="/docs"
        className="rounded-full bg-studio-900 px-5 py-2 text-[0.8rem] font-semibold text-studio-50 transition-colors duration-200 hover:bg-ember-600"
      >
        View API Docs
      </a>
    </header>
  );
}
