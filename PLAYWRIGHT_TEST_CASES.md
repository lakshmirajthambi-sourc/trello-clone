# Playwright end-to-end cases

These cases cover the app's browser flows.

> **Automated Test Suite**: A fully automated test suite implementing all end-to-end test cases is available in `test_e2e.py` and documented in `E2E_TEST_CASES.md`. You can run the entire automated suite with:
> ```sh
> python -m pytest test_e2e.py -v
> ```

## Start the app (for interactive CLI or browser runs)

From the repository root, start the static server:

```sh
python -m http.server 8000
```

In another terminal, start a Playwright CLI session:

```sh
playwright-cli open http://localhost:8000
playwright-cli snapshot
```

Use fresh element refs from `snapshot` whenever you choose ref-based targets. The commands below use Playwright locator expressions and CSS selectors so they do not depend on ref numbers.

## TC-01 — Initial board renders

**Steps**

```sh
playwright-cli open http://localhost:8000
playwright-cli snapshot
```

**Expected**

- Page title is `Flowboard — organize anything`.
- The `Product launch` board is active and four lists appear: Ideas, To do, In progress, Done.
- The initial cards, including `Research competitor products` and `Write launch announcement`, are visible.

## TC-02 — Create, edit, and delete a card

**Steps**

```sh
playwright-cli click "getByRole('button', { name: 'Add a card' }).first()"
playwright-cli fill "#cardName" "CLI test card"
playwright-cli fill "#cardDescription" "Created by the Playwright CLI"
playwright-cli select "#cardLabel" "blue"
playwright-cli click "#saveCard"
playwright-cli snapshot
playwright-cli click "getByText('CLI test card')"
playwright-cli fill "#cardName" "CLI test card edited"
playwright-cli click "#saveCard"
playwright-cli snapshot
playwright-cli click "getByText('CLI test card edited')"
playwright-cli click "#deleteCard"
playwright-cli snapshot
```

**Expected**

- The new card appears in Ideas with its description and Development label.
- Editing changes the title.
- Deleting removes the card and shows the delete confirmation toast.

## TC-03 — Create and rename a list

**Steps**

```sh
playwright-cli click "#addListCanvas"
playwright-cli fill "#listName" "CLI test list"
playwright-cli click "getByRole('button', { name: 'Create list' })"
playwright-cli snapshot
playwright-cli click "[data-list='l<generated-id>'] [data-list-menu]"
```

When the browser prompt opens, run:

```sh
playwright-cli dialog-accept "CLI renamed list"
playwright-cli snapshot
```

Replace `l<generated-id>` with the actual new list id, or click the options button within the `CLI test list` column using the latest snapshot ref.

**Expected**

- The new list appears with no cards.
- After accepting the prompt, its heading reads `CLI renamed list`.

## TC-04 — Create and rename a board

**Steps**

```sh
playwright-cli click "#addBoard"
playwright-cli fill "#newBoardName" "CLI test board"
playwright-cli click "getByRole('button', { name: 'Create board' })"
playwright-cli snapshot
playwright-cli click "#boardMenu"
playwright-cli dialog-accept "CLI renamed board"
playwright-cli snapshot
```

**Expected**

- The new board becomes active and is added to the board navigation.
- It contains the default To do, In progress, and Done lists.
- The board title and breadcrumb update to `CLI renamed board`.

## TC-05 — Search and clear search

**Steps**

```sh
playwright-cli fill "#searchInput" "competitor"
playwright-cli snapshot
playwright-cli fill "#searchInput" ""
playwright-cli snapshot
```

**Expected**

- While searching, `Research competitor products` remains visible and unrelated cards are hidden.
- Clearing the search restores the full board.

## TC-06 — Move a card between lists

**Steps**

```sh
playwright-cli drag "getByText('Define our product vision')" "[data-list='todo']"
playwright-cli snapshot
```

**Expected**

- `Define our product vision` is removed from Ideas and appears in To do.
- The list card counts update.

## TC-07 — Reorder cards within a list

**Steps**

```sh
playwright-cli drag "getByText('Create moodboard')" "[data-list='ideas']"
playwright-cli snapshot
```

Drop the card at the intended position if the CLI's locator drop point places it elsewhere.

**Expected**

- The card stays in Ideas and its position changes.
- Reloading keeps the new order.

## TC-08 — Changes persist after reload

Run after creating a card, list, or board in another case:

```sh
playwright-cli reload
playwright-cli snapshot
```

**Expected**

- The saved changes remain visible after reload.

## TC-09 — Narrow viewport navigation

**Steps**

```sh
playwright-cli resize 375 812
playwright-cli snapshot
playwright-cli click "#mobileMenu"
playwright-cli snapshot
playwright-cli press Escape
playwright-cli snapshot
```

**Expected**

- The page remains usable at 375 × 812.
- The menu button opens the sidebar; Escape closes it.

## TC-10 — Board deletion guard and removal

Run after creating a second board so the initial board is retained:

```sh
playwright-cli click "#boardMenu"
playwright-cli dialog-accept "DELETE"
playwright-cli snapshot
```

**Expected**

- The deleted board disappears from navigation and another board becomes active.
- With only one board remaining, repeating the delete action shows `Keep at least one board` and preserves that board.

## Cleanup

Remove the test board/list/card through the UI, or clear the Playwright browser session's data before the next run:

```sh
playwright-cli delete-data
playwright-cli close
```

