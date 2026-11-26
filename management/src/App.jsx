import { useCallback, useEffect, useMemo, useState } from "react";
import { api } from "./api.js";
import Window from "./components/Window.jsx";
import CharactersPage from "./pages/CharactersPage.jsx";
import MonstersPage from "./pages/MonstersPage.jsx";
import ClassesPage from "./pages/ClassesPage.jsx";
import ItemsPage from "./pages/ItemsPage.jsx";
import SpritesPage from "./pages/SpritesPage.jsx";

const PAGES = [
  { id: "characters", label: "Characters", icon: "/assets/icons/profile.png" },
  { id: "monsters", label: "Monsters", icon: "/assets/icons/instances.png" },
  { id: "classes", label: "Classes", icon: "/assets/icons/change_char.png" },
  { id: "items", label: "Items & Drops", icon: "/assets/icons/inventory.png" },
  { id: "sprites", label: "Sprite Sheets", icon: "/assets/icons/wiki.png" },
];

export default function App() {
  const [page, setPage] = useState(() => localStorageGet("rcs-page") ?? "characters");
  const [data, setData] = useState(null);
  const [loadError, setLoadError] = useState(null);
  const [toasts, setToasts] = useState([]);

  const load = useCallback(async () => {
    setLoadError(null);
    try {
      const [options, characters, monsters, jobs, items, spriteList] = await Promise.all([
        api.options(), api.characters(), api.monsters(), api.jobs(), api.items(), api.sprites(),
      ]);
      setData({ options, characters, monsters, jobs, items, spriteList });
    } catch (error) {
      setLoadError(error.message);
    }
  }, []);

  useEffect(() => { load(); }, [load]);
  useEffect(() => { localStorageSet("rcs-page", page); }, [page]);

  const notify = useCallback((message, kind = "success") => {
    const id = Date.now() + Math.random();
    setToasts((list) => [...list, { id, message, kind }]);
    setTimeout(() => setToasts((list) => list.filter((toast) => toast.id !== id)), kind === "error" ? 6000 : 3000);
  }, []);

  // one updater per collection, so each page only touches its own list
  const setter = (key) => (update) => setData((current) => ({
    ...current, [key]: typeof update === "function" ? update(current[key]) : update,
  }));

  // sheet JSONs by "<group>/<name>", for every sprite preview
  const sheets = useMemo(() => Object.fromEntries((data?.spriteList ?? [])
    .map((entry) => [`${entry.group}/${entry.name}`, entry.json])), [data?.spriteList]);

  const counts = data && {
    characters: data.characters.length, monsters: data.monsters.length, classes: data.jobs.length,
    items: data.items.length, sprites: data.spriteList.length,
  };

  function onSpriteUploaded(entry) {
    setData((current) => {
      const others = current.spriteList.filter((s) => !(s.group === entry.group && s.name === entry.name));
      const spriteList = [...others, entry].sort((a, b) => `${a.group}/${a.name}`.localeCompare(`${b.group}/${b.name}`));
      const names = current.options.sheets[entry.group].includes(entry.name)
        ? current.options.sheets[entry.group]
        : [...current.options.sheets[entry.group], entry.name].sort();
      return { ...current, spriteList, options: { ...current.options, sheets: { ...current.options.sheets, [entry.group]: names } } };
    });
  }

  return (
    <div className="app">
      <header className="topbar">
        <img src="/assets/Icon.png" alt="" />
        <div>
          <h1>Ragnarok Chaos Saga</h1>
          <span>Game Management</span>
        </div>
        <button type="button" className="button ghost topbar-reload" onClick={load} title="Reload everything from the backend">
          ↻ Reload
        </button>
      </header>

      <div className="layout">
        <aside>
          <Window icon="/assets/icons/map.png" title="Management" subtitle="Game data">
            <nav className="categories">
              {PAGES.map((entry) => (
                <button key={entry.id} type="button" className={`category ${page === entry.id ? "active" : ""}`}
                        onClick={() => setPage(entry.id)}>
                  <img src={entry.icon} alt="" />
                  <span>{entry.label}</span>
                  <span className="count">{counts ? counts[entry.id] : "–"}</span>
                </button>
              ))}
            </nav>
            <p className="note small">
              Changes are saved straight into the game database. Running <code>seed_data.py</code> again puts back the
              seed's values for monsters, classes, items and drops.
            </p>
          </Window>
        </aside>

        <main>
          {loadError && (
            <Window title="Backend not reachable" subtitle="http://127.0.0.1:8001">
              <p className="note warning">{loadError}</p>
              <p className="note">Start the backend (run-management.ps1 does it for you) and press Reload.</p>
            </Window>
          )}
          {!data && !loadError && <div className="loading">Loading game data…</div>}
          {data && page === "characters" && (
            <CharactersPage characters={data.characters} setCharacters={setter("characters")} options={data.options}
                            sheets={sheets} jobs={data.jobs} notify={notify} />
          )}
          {data && page === "monsters" && (
            <MonstersPage monsters={data.monsters} setMonsters={setter("monsters")} items={data.items}
                          setItems={setter("items")} options={data.options} sheets={sheets} notify={notify} />
          )}
          {data && page === "classes" && (
            <ClassesPage jobs={data.jobs} setJobs={setter("jobs")} characters={data.characters} options={data.options}
                         sheets={sheets} notify={notify} />
          )}
          {data && page === "items" && (
            <ItemsPage items={data.items} setItems={setter("items")} options={data.options} notify={notify} />
          )}
          {data && page === "sprites" && (
            <SpritesPage spriteList={data.spriteList} onUploaded={onSpriteUploaded} monsters={data.monsters}
                         jobs={data.jobs} notify={notify} />
          )}
        </main>
      </div>

      <div className="toasts">
        {toasts.map((toast) => <div key={toast.id} className={`toast ${toast.kind}`}>{toast.message}</div>)}
      </div>
    </div>
  );
}

function localStorageGet(key) {
  try { return window.localStorage.getItem(key); } catch { return null; }
}

function localStorageSet(key, value) {
  try { window.localStorage.setItem(key, value); } catch { /* private mode: the page just isn't remembered */ }
}
