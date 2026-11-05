# Repository Guidelines

## Project Structure & Module Organization

This repository is a small, dependency-free Trello-style board implemented with browser-native HTML, CSS, and JavaScript. The app entry point is `index.html`; `styles.css` contains layout and responsive styles; `app.js` implements board rendering, card and list actions, drag-and-drop, search, and browser storage. There are currently no asset, source subdirectories, or test directories. Keep new files at the root unless the project grows enough to justify a dedicated directory.

## Build, Test, and Development Commands

There is no build step or package manager configuration. Open `index.html` in a browser for a quick local preview. To serve it over HTTP from the repository root, run:

```sh
python -m http.server 8000
```

Then visit `http://localhost:8000`. Stop the server with Ctrl+C. No automated test or lint command is configured.

## Coding Style & Naming Conventions

Use two spaces for indentation. Keep browser logic in `app.js`, markup in `index.html`, and presentation in `styles.css`. Use `camelCase` for JavaScript variables and functions, descriptive kebab-case CSS class names, and semantic HTML elements. Escape user-provided text before inserting it into HTML. Preserve the existing lightweight, dependency-free approach unless a change clearly requires additional tooling.

## Testing Guidelines

There is no test framework or coverage requirement. For changes, run the app locally and manually check the relevant flows: create and rename boards or lists, add and edit cards, move cards between and within lists, search, and reload to confirm local storage persistence. Check narrow viewport behavior when changing layout or interactions. Do not claim automated coverage unless a test suite is added and run.

## Commit & Pull Request Guidelines

No Git commit history is available in this checkout, so no established commit convention can be inferred. Use short imperative commit subjects, such as `Add card drag-and-drop reordering`. Pull requests should describe user-visible changes, list manual or automated checks performed, link relevant issues when applicable, and include screenshots for visual changes.

## Security & Configuration

Board data is stored in browser `localStorage` under the `flowboard-v1` key. Do not store secrets there. Keep rendering of user-entered board, list, and card content escaped, and avoid introducing remote services or dependencies without documenting the need.
