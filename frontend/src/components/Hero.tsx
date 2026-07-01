import { type ReactNode } from 'react';

export function Hero({ children }: { children: ReactNode }) {
  return (
    <div className="relative z-20 mx-auto flex w-full max-w-2xl flex-col items-center gap-6 px-4 text-center">
      <div className="rounded-3xl bg-white/55 px-6 py-5 backdrop-blur-md md:px-10 md:py-7">
        <h1 className="font-display text-4xl font-semibold leading-tight tracking-tight text-studio-900 md:text-5xl">
          Find the right asset in seconds
        </h1>
        <p className="mx-auto mt-3 max-w-md text-sm leading-relaxed text-studio-900/65 md:text-base">
          Search campaign visuals by mood, texture, or theme &mdash; explore the studio wall finish
          alongside it.
        </p>
      </div>
      {children}
    </div>
  );
}
