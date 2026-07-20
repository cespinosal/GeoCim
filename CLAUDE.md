# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

GeoCim is a desktop application for geotechnical/structural engineering: checking and designing shallow and deep
foundations (zapata aislada, torre de telecomunicaciones, pilas con campana, pilote, grupo de pilotes) against
codes such as NMX-C-401 and ACI 318-19. It's a Windows desktop app built by wrapping a single self-contained
HTML/JS application in a thin PySide6 (Qt WebEngine) shell.

**Golden rule (from `Prompt_GeoCim.txt`, the original project brief):** the Python/`ui/` shell is meant to stay a
thin "mask" around the HTML app. Do not restructure `ui/` or the Python↔JS integration without checking with the
user first — the actual calculation/UI logic lives in `GeoCim.html`, not in Python.

## Architecture — two layers

**1. Python shell (`main.py`, `ui/`)** — a PySide6 `QMainWindow` with a `QWebEngineView` that loads `GeoCim.html`
from disk (`ui/ventana_principal.py`). Its only real jobs:
- Show a splash screen (`ui/splash.py`) while the HTML loads, then reveal the main window (`_open_window`).
- Intercept the browser's `downloadRequested` signal to show a native "Save As" dialog when the JS side saves a
  project (JS creates a blob and triggers a download; Python redirects it to a real file path).
- Handle opening `.gcm`/`.json` files passed as argv (double-click file association in Explorer) by injecting
  `loadJsonString(...)` into the page via `runJavaScript`.
- On window close, ask the JS side for the current project JSON (`menuGuardarData()`) and offer to save before
  exiting.
- `ui/tema.py` only styles the native Qt chrome (status bar); it has no influence on the in-page UI.

There is effectively no other Python business logic — no models, no calculation code, no API layer.

**2. The application itself (`GeoCim.html`)** — a single ~4,900-line self-contained HTML file with all CSS and
JS inline, no build step, no framework, no `node_modules`. It embeds Three.js and OrbitControls inline
(`<script id="threejs-src">` / `#threejs-orbitcontrols-src`) so the app works fully offline — do not replace
these with CDN `<script src>` tags. `index.html` is a duplicate of `GeoCim.html` kept for GitHub Pages; when you
edit one, mirror the change into the other (they're expected to be byte-identical).

Inside `GeoCim.html`'s main `<script>` block (starts ~line 1504):
- `state` is the single global mutable object holding the entire app: current module, per-module wizard
  progress (`currentFrame`, `modDone`, `frameStatus`), project metadata, config (calc method, units), and one
  sub-object per foundation type (`zapata`, `pilote`, `pilas`, `torre`, `grupopilotes`) plus `diseno` (structural
  design inputs per module). `profile` is the soil-stratigraphy array; `SOILS`/`HATCH_DEFS` define soil
  presets/patterns. `_DEFAULT_STATE`/`_DEFAULT_PROFILE`/`_DEFAULT_SOILS` are deep clones used to reset
  ("Nuevo proyecto").
- `FRAME_CFG` defines, per module, the ordered list of wizard "frames" (steps) shown in the left sidebar —
  Proyecto → Configuración → Perfil de suelos → Geometría → Cargas → Capacidad → Extracción/Asentamiento →
  Verificación → [structural design frames flagged `estr:true`: Flexión, Cortante, Punzonamiento, Armado,
  Pedestal]. Adding a wizard step means adding an entry here plus a matching render function.
- Module tabs (`data-mod="zapata|torre|pilas|pilote|grupopilotes"`) are switched via `trySetModule` →
  `setModule`, which warns before losing in-progress state on the current module (each module's state is
  otherwise independent).
- Calculation engine: `calcZapata`, `calcPilote`, `calcTorre` (bearing capacity via `bcFactors` — Vesic/
  Meyerhof/Terzaghi Nc/Nq/Nγ), `calcEstrChecks` (ACI 318-19 flexure/shear/punching/rebar), `_calcExtraccionZapata`/
  `_calcExtraccionPilote`/`_calcExtraccionChecks` (uplift), `_calcPedestal`/`_pmCurveAtAngle` (biaxial P-M
  pedestal interaction).
- Rendering pipeline: everything funnels through `renderAll()`, called after essentially every state mutation.
  It calls `renderFrames`, `renderInputs`, `renderLegend`, `renderScaleTag`, `renderWorkflowSteps`, `drawScene`
  (2D SVG cross-section into `#scene`), the relevant `calc*` function, `renderResults`, then `saveState()`. The
  2D/3D toggle (`setView3D`) swaps between the SVG canvas and `#scene3d` (Three.js, set up in `_init3D`/
  `_update3D`). If you add a new input that affects geometry or results, it must flow through `state` and be
  picked up by `renderAll` — there's no separate dispatch/observer system.
- Units: everything is stored in `state` in SI internally. `CF`/`ULBL` hold conversion factors/labels for
  `SI`/`MKS`/`Imp`; use `toD`/`toSI`/`fD`/`uLbl` to convert for display and back to SI on input — never store
  display-unit values in `state`.
- Persistence: `saveState()`/`loadState()` mirror `state`/`profile`/soil overrides to `localStorage`
  (`gcm_st`/`gcm_pr`/`gcm_so`) for session recovery. Explicit project files (`.gcm`, really JSON) are produced by
  `menuGuardarData()` (`{version, state, profile, soils}`) and consumed by `loadJsonString()`. Older `.gcm` files
  may reference a module key that no longer exists (`losa`, since renamed/split into `pilas`/`grupopilotes`) —
  keep `loadJsonString` tolerant of unknown/missing keys when touching it.

## Running

```
pip install -r requirements.txt   # PySide6, pyinstaller
python main.py                    # launch the desktop app
```

There is no test suite, linter, or formatter configured in this repo — verify changes by running the app and
exercising the affected module/frame in the UI.

Since `GeoCim.html` is plain inline JS with no bundler, you can also open it directly in a browser for quick
iteration on UI/calc logic (file-menu save/open won't get the native dialog Python provides, but everything
else — modules, 2D/3D view, calculations, localStorage persistence — works standalone).

## Building the Windows executable

```
python make_assets.py             # regenerate GeoCim.ico / GeoCim.png from the vector icon in ui/splash.py
pyinstaller GeoCim.spec --noconfirm   # or just run build.bat on Windows
```

`GeoCim.spec` is a onedir PyInstaller build (required for QtWebEngine) that bundles `GeoCim.html`, `GeoCim.ico`,
and `GeoCim.png` as data files; output goes to `dist/GeoCim/GeoCim.exe`. Re-run `make_assets.py` only after
changing `draw_icon_badge` in `ui/splash.py` (the icon is generated by Qt painter code, not from an image asset).

## Referencias externas

- Guía práctica de diseño geotécnico y estructural de pilotes rotados (Sismica Institute) — caso de
  referencia/ejemplo para contrastar con el módulo `pilote`/`pilas` (`calcPilote`, `FRAME_CFG.pilote` en
  `GeoCim.html`):
  https://sismica-institute.com/guia-practica-diseno-geotecnico-y-estructural-de-pilotes-rotados/
