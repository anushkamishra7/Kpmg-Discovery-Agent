import { ExternalLink, ImageOff } from 'lucide-react';
import type { ImageSearchResponse } from '../api';

function scoreTone(score: number) {
  if (score >= 0.28) return 'text-green-700 bg-green-50 border-green-200';
  if (score >= 0.22) return 'text-amber-700 bg-amber-50 border-amber-200';
  return 'text-red-700 bg-red-50 border-red-200';
}

export function ResultsGrid({ data }: { data: ImageSearchResponse }) {
  if (data.results.length === 0) {
    return (
      <div className="mx-auto mt-10 max-w-md rounded-2xl border border-studio-200 bg-white/80 px-6 py-8 text-center text-sm text-studio-900/60 backdrop-blur-sm">
        No assets matched your query. Try broadening the search or lowering the similarity threshold.
      </div>
    );
  }

  return (
    <div className="relative z-20 mx-auto mt-10 w-full max-w-5xl px-4">
      <div className="mb-3 flex items-baseline justify-between px-1 text-xs text-studio-900/50">
        <span>
          <strong className="text-studio-900">{data.count}</strong> assets found
        </span>
        <span>{data.latency_ms}ms</span>
      </div>
      <div className="grid grid-cols-2 gap-3 sm:grid-cols-3 md:grid-cols-4">
        {data.results.map((r) => {
          const filename = (r.metadata?.filename as string) ?? r.asset_path.split('/').pop() ?? r.asset_path;
          const imgUrl = `${r.asset_url}/jcr:content/renditions/original`;
          return (
            <a
              key={r.asset_path}
              href={r.asset_url}
              target="_blank"
              rel="noreferrer"
              className="group overflow-hidden rounded-xl border border-studio-200/70 bg-white/85 shadow-sm backdrop-blur-sm transition-all duration-200 hover:-translate-y-1 hover:shadow-lg"
            >
              <div className="relative flex aspect-[3/2] items-center justify-center bg-studio-100">
                <img
                  src={imgUrl}
                  alt={filename}
                  loading="lazy"
                  className="h-full w-full object-cover transition-transform duration-300 group-hover:scale-105"
                  onError={(e) => {
                    e.currentTarget.style.display = 'none';
                    e.currentTarget.nextElementSibling?.classList.remove('hidden');
                  }}
                />
                <div className="hidden flex-col items-center gap-1 text-studio-900/30">
                  <ImageOff className="h-5 w-5" />
                </div>
                <span
                  className={`absolute right-2 top-2 rounded-md border px-1.5 py-0.5 text-[0.62rem] font-bold backdrop-blur-sm ${scoreTone(r.score)}`}
                >
                  {r.score.toFixed(3)}
                </span>
              </div>
              <div className="p-2.5">
                <p className="line-clamp-2 text-xs font-semibold text-studio-900">{filename}</p>
                <span className="mt-1 inline-flex items-center gap-1 text-[0.68rem] font-medium text-ember-600">
                  Open in AEM <ExternalLink className="h-2.5 w-2.5" />
                </span>
              </div>
            </a>
          );
        })}
      </div>
    </div>
  );
}
