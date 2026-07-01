import { useState, type FormEvent } from 'react';
import { Search, ArrowRight, Loader2 } from 'lucide-react';
import { WALL_PRESETS, type WallStyleKey } from '../three/wallPresets';

const QUICK_TAGS = Object.values(WALL_PRESETS);

interface SearchDockProps {
  wallStyle: WallStyleKey;
  onWallStyleChange: (key: WallStyleKey) => void;
  onSearch: (query: string) => void;
  isLoading: boolean;
}

export function SearchDock({ wallStyle, onWallStyleChange, onSearch, isLoading }: SearchDockProps) {
  const [query, setQuery] = useState('');

  function handleSubmit(e: FormEvent) {
    e.preventDefault();
    if (query.trim()) onSearch(query.trim());
  }

  return (
    <div className="w-full max-w-xl rounded-3xl border border-white/30 bg-white/40 p-5 shadow-[0_32px_64px_-15px_rgba(0,0,0,0.15)] backdrop-blur-xl">
      <form onSubmit={handleSubmit} className="flex flex-col gap-3 sm:flex-row sm:items-center">
        <div className="relative flex-1">
          <Search className="pointer-events-none absolute left-4 top-1/2 h-4 w-4 -translate-y-1/2 text-studio-900/40" />
          <input
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Find the right asset in seconds..."
            className="w-full rounded-2xl border border-studio-200/70 bg-white/80 py-3 pl-10 pr-4 text-sm text-studio-900 placeholder:text-studio-900/40 outline-none transition-colors focus:border-ember-500"
          />
        </div>
        <button
          type="submit"
          disabled={isLoading}
          className="flex items-center justify-center gap-1.5 rounded-2xl bg-ember-500 px-5 py-3 text-sm font-semibold text-white transition-colors hover:bg-ember-600 disabled:opacity-60"
        >
          {isLoading ? <Loader2 className="h-4 w-4 animate-spin" /> : <ArrowRight className="h-4 w-4" />}
          Search
        </button>
      </form>

      <div className="mt-4 flex flex-wrap gap-2">
        {QUICK_TAGS.map((tag) => {
          const active = tag.key === wallStyle;
          return (
            <button
              key={tag.key}
              type="button"
              onClick={() => onWallStyleChange(tag.key)}
              className={`rounded-full border px-3.5 py-1.5 text-xs font-medium transition-colors duration-200 ${
                active
                  ? 'border-ember-500 bg-ember-500/10 text-ember-600'
                  : 'border-studio-200 bg-white/60 text-studio-900/60 hover:border-ember-500/50 hover:text-ember-600'
              }`}
            >
              {tag.label}
            </button>
          );
        })}
      </div>
    </div>
  );
}
