import { Suspense, useState } from 'react';
import { ShowroomCanvas } from './three/Showroom';
import { DEFAULT_WALL_STYLE, type WallStyleKey } from './three/wallPresets';
import { Header } from './components/Header';
import { Hero } from './components/Hero';
import { SearchDock } from './components/SearchDock';
import { ResultsGrid } from './components/ResultsGrid';
import { searchAssets, type ImageSearchResponse } from './api';

function App() {
  const [wallStyle, setWallStyle] = useState<WallStyleKey>(DEFAULT_WALL_STYLE);
  const [results, setResults] = useState<ImageSearchResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleSearch(query: string) {
    setIsLoading(true);
    setError(null);
    try {
      const data = await searchAssets(query);
      setResults(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Search failed');
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <div className="relative min-h-screen overflow-x-hidden bg-studio-50">
      <div className="fixed inset-0 z-0">
        <Suspense fallback={null}>
          <ShowroomCanvas wallStyle={wallStyle} />
        </Suspense>
      </div>

      <div className="relative flex min-h-screen flex-col">
        <Header />

        <main className="flex flex-1 flex-col items-center px-4 pb-10 pt-16 md:pt-20">
          <Hero>
            <SearchDock
              wallStyle={wallStyle}
              onWallStyleChange={setWallStyle}
              onSearch={handleSearch}
              isLoading={isLoading}
            />
          </Hero>

          {error && (
            <div className="relative z-20 mt-6 max-w-md rounded-xl border border-red-200 bg-red-50/90 px-4 py-3 text-sm text-red-600 backdrop-blur-sm">
              {error}
            </div>
          )}

          {results && !error && <ResultsGrid data={results} />}
        </main>

        </div>
    </div>
  );
}

export default App;
