# Flowboard — End-to-End (E2E) Test Cases Specification

This document provides a comprehensive end-to-end (E2E) test specification for the Flowboard Trello clone. It covers user journeys, interface interactions, drag-and-drop mechanics, data validation, persistence, responsiveness, and security sanitization.

---

## 1. Test Suite Overview

| Category | Details |
|---|---|
| **Application** | Flowboard (Trello Clone) |
| **Architecture** | Client-side Single Page Application (HTML5, Vanilla JS, CSS3, `localStorage`) |
| **Test Framework** | Pytest (`pytest 9.1.1`) + Playwright (`playwright 1.62.0`) |
| **Target Browsers** | Chromium / Google Chrome / Microsoft Edge |
| **Storage Key** | `flowboard-v1` in `window.localStorage` |

---

## 2. Test Execution Quick Start

### Automated Execution
```sh
# Run the complete automated test suite
python -m pytest test_e2e.py -v

# Run a specific test module or case
python -m pytest test_e2e.py -k "test_tc01" -v

# Run directly via Python runner
python test_e2e.py
```

### Manual Preview
```sh
python -m http.server 8000
# Open http://localhost:8000 in your browser
```

---

## 3. Test Cases Specification

### Module 1: Board Lifecycle Management

#### TC-E2E-01 — Initial Board Render & Default Seed State
- **Priority**: P0 (Blocker)
- **Objective**: Ensure the default board "Product launch" loads with full metadata and 4 seeded lists.
- **Preconditions**: `localStorage` is clear.
- **Steps**:
  1. Navigate to the application root (`/index.html`).
  2. Inspect document title, board title, breadcrumbs, and board description.
  3. Inspect board lists and task cards.
- **Expected Results**:
  - Document title contains `Flowboard`.
  - `#boardTitle` and `#crumbBoard` display `"Product launch"`.
  - 4 default lists are rendered: `"Ideas"`, `"To do"`, `"In progress"`, `"Done"`.
  - Exactly 10 default cards are rendered across the lists.

#### TC-E2E-02 — Create New Board
- **Priority**: P0 (Blocker)
- **Objective**: Verify user can create a new board with custom name.
- **Steps**:
  1. Click `#addBoard` button in sidebar.
  2. Verify `#boardDialog` modal opens.
  3. Enter `"Mobile App Redesign"` into `#newBoardName`.
  4. Submit modal form (`Create board`).
- **Expected Results**:
  - `#boardDialog` closes.
  - Active board title switches to `"Mobile App Redesign"`.
  - 3 default lists ("To do", "In progress", "Done") are initialized with 0 cards.
  - `#boardNav` lists both `"Product launch"` and `"Mobile App Redesign"`.

#### TC-E2E-03 — Switch Active Board
- **Priority**: P1 (Critical)
- **Objective**: Verify user can switch between existing boards from sidebar navigation.
- **Steps**:
  1. Create a second board `"Marketing Strategy"`.
  2. Click on `"Product launch"` item in `#boardNav`.
  3. Verify board title and cards belong to `"Product launch"`.
  4. Click on `"Marketing Strategy"` item in `#boardNav`.
- **Expected Results**:
  - Canvas updates dynamically without page reload.
  - Active class updates on the corresponding `#boardNav button`.

#### TC-E2E-04 — Rename Board
- **Priority**: P1 (Critical)
- **Objective**: Verify active board can be renamed via the board menu prompt.
- **Steps**:
  1. Click `#boardMenu` button ("···").
  2. Accept browser prompt with `"Global Brand Relaunch"`.
- **Expected Results**:
  - `#boardTitle` updates to `"Global Brand Relaunch"`.
  - `#crumbBoard` updates to `"Global Brand Relaunch"`.
  - `#boardNav` item text updates to `"Global Brand Relaunch"`.

#### TC-E2E-05 — Single Board Deletion Guard
- **Priority**: P1 (Critical)
- **Objective**: Prevent deletion when only one board exists to prevent empty broken state.
- **Steps**:
  1. Ensure only 1 board exists.
  2. Click `#boardMenu`.
  3. Enter `"DELETE"` in the browser prompt.
- **Expected Results**:
  - Board is NOT deleted.
  - Toast message appears: `"Keep at least one board"`.
  - Nav and board canvas remain unchanged.

#### TC-E2E-06 — Delete Board with Multiple Boards
- **Priority**: P1 (Critical)
- **Objective**: Verify deleting a board succeeds when at least one other board exists.
- **Steps**:
  1. Create a second board `"Temporary Board"`.
  2. While on `"Temporary Board"`, click `#boardMenu` and enter `"DELETE"`.
- **Expected Results**:
  - `"Temporary Board"` is removed from `#boardNav`.
  - Application switches to the remaining board.

#### TC-E2E-07 — Favorite Board Star Toggle
- **Priority**: P2 (Normal)
- **Objective**: Verify favoriting a board toggles star state visually.
- **Steps**:
  1. Click `.star-button`.
  2. Observe star text and class.
  3. Click `.star-button` again.
- **Expected Results**:
  - First click changes text from `☆` to `★` and adds `.is-favorite`.
  - Second click reverts text to `☆` and removes `.is-favorite`.

---

### Module 2: List Lifecycle Management

#### TC-E2E-08 — Add New List
- **Priority**: P0 (Blocker)
- **Objective**: Add a new custom column list to the board.
- **Steps**:
  1. Click `#addListCanvas` ("＋ Add another list").
  2. Enter `"Blocked"` into `#listName`.
  3. Submit `#listForm`.
- **Expected Results**:
  - New column `section.list-column` appears at the end of the canvas.
  - Column header displays title `"Blocked"` and badge count `"0"`.

#### TC-E2E-09 — Rename Existing List
- **Priority**: P1 (Critical)
- **Objective**: Rename an existing list column via list menu prompt.
- **Steps**:
  1. Click options button `[data-list-menu]` on "Ideas" column.
  2. Enter `"Backlog & Brainstorming"` in the prompt.
- **Expected Results**:
  - List column heading updates immediately to `"Backlog & Brainstorming"`.

#### TC-E2E-10 — List Card Count Synchronization
- **Priority**: P2 (Normal)
- **Objective**: Verify column card count indicator correctly tallies cards.
- **Steps**:
  1. Check `.list-count` text in each column.
  2. Count actual `.task-card` child elements in `.card-stack`.
- **Expected Results**:
  - `.list-count` matches `.card-stack > .task-card` count at all times.

---

### Module 3: Card Lifecycle Management

#### TC-E2E-11 — Create Card with Full Metadata
- **Priority**: P0 (Blocker)
- **Objective**: Create a new task card with title, description, label, and due date.
- **Steps**:
  1. Click `"＋ Add a card"` on "Ideas" list (`[data-add-card="ideas"]`).
  2. Fill title: `"Implement SSO Integration"`.
  3. Fill description: `"Support OAuth 2.0 with Google and GitHub."`.
  4. Select label: `"Development"` (`blue`).
  5. Select due date: `"2026-12-15"`.
  6. Click `#saveCard`.
- **Expected Results**:
  - Card appears in "Ideas" list.
  - Card displays title, description, label pill, and due date indicator.
  - "Ideas" list count increments.

#### TC-E2E-12 — Create Card Validation (Empty Title Guard)
- **Priority**: P2 (Normal)
- **Objective**: Prevent card creation with empty title.
- **Steps**:
  1. Click `"＋ Add a card"`.
  2. Leave `#cardName` blank.
  3. Click `#saveCard`.
- **Expected Results**:
  - Form validation prevents submission (`required` field).
  - Dialog remains open; no blank card is created.

#### TC-E2E-13 — Edit Existing Card
- **Priority**: P0 (Blocker)
- **Objective**: Open an existing card, modify properties, and persist updates.
- **Steps**:
  1. Click on card `"Research competitor products"`.
  2. Change title to `"Research top 5 competitors thoroughly"`.
  3. Change description to `"Updated market positioning analysis."`.
  4. Change label to `"Design"` (`mint`).
  5. Click `#saveCard`.
- **Expected Results**:
  - Modal closes.
  - Card DOM updates with new title, description, and mint label class.

#### TC-E2E-14 — Delete Card
- **Priority**: P0 (Blocker)
- **Objective**: Delete an existing card from within the details modal.
- **Steps**:
  1. Click on card `"Define our product vision"`.
  2. Click `#deleteCard` ("Delete card").
- **Expected Results**:
  - Modal closes.
  - Card is removed from the DOM and list count decrements.
  - Toast message appears: `"Card deleted"`.

#### TC-E2E-15 — Dismiss Modal Without Saving
- **Priority**: P2 (Normal)
- **Objective**: Verify closing the modal without saving discards draft changes.
- **Steps**:
  1. Click on card `"Create moodboard"`.
  2. Type draft changes into `#cardName`.
  3. Click close button `.close-modal` ("×").
- **Expected Results**:
  - Original title `"Create moodboard"` remains unchanged.

---

### Module 4: Drag and Drop & Card Reordering

#### TC-E2E-16 — Move Card Across Different Lists
- **Priority**: P0 (Blocker)
- **Objective**: Drag a card from one column and drop it into a different column.
- **Steps**:
  1. Drag card `"Research competitor products"` from "Ideas" list.
  2. Drop onto the "Done" list column.
- **Expected Results**:
  - Card is removed from "Ideas" and appended to "Done".
  - "Ideas" card count drops from 3 to 2.
  - "Done" card count increases from 2 to 3.

#### TC-E2E-17 — Reorder Cards Within the Same List
- **Priority**: P1 (Critical)
- **Objective**: Change card order within the same column by dragging.
- **Steps**:
  1. Record order of cards in "Ideas" list: `[c1, c2, c3]`.
  2. Drag bottom card `c3` ("Create moodboard") and drop above `c1`.
- **Expected Results**:
  - New card order is `[c3, c1, c2]`.
  - DOM order and internal model order match.

---

### Module 5: Search & Filtering

#### TC-E2E-18 — Real-time Search Filtering & Clear
- **Priority**: P1 (Critical)
- **Objective**: Filter board cards using the top search bar.
- **Steps**:
  1. Type `"competitor"` into `#searchInput`.
  2. Observe matching cards and non-matching cards.
  3. Clear `#searchInput`.
- **Expected Results**:
  - Only `"Research competitor products"` remains visible; others are marked `hidden`.
  - Clearing input restores all 10 cards to visible state.

#### TC-E2E-19 — Filter Toolbar Button Prompt
- **Priority**: P2 (Normal)
- **Objective**: Use the filter toolbar button to initiate a title search.
- **Steps**:
  1. Click `#filterButton`.
  2. Accept prompt with query `"landing"`.
- **Expected Results**:
  - `#searchInput` value becomes `"landing"`.
  - Only `"Design landing page"` card is visible.

#### TC-E2E-20 — Keyboard Shortcut (Cmd+K / Ctrl+K)
- **Priority**: P2 (Normal)
- **Objective**: Pressing keyboard shortcut focuses the search bar.
- **Steps**:
  1. Click outside input.
  2. Press `Control+k` (or `Meta+k`).
- **Expected Results**:
  - `#searchInput` receives active focus (`document.activeElement`).

---

### Module 6: Persistence & Fault Tolerance

#### TC-E2E-21 — LocalStorage Persistence After Browser Reload
- **Priority**: P0 (Blocker)
- **Objective**: Verify board mutations persist across full page reloads.
- **Steps**:
  1. Add a new card `"Persisted Card Across Reload"`.
  2. Trigger hard page reload (`page.reload()`).
  3. Wait for `#boardCanvas` to re-render.
- **Expected Results**:
  - `"Persisted Card Across Reload"` is preserved and visible.
  - `localStorage['flowboard-v1']` contains the new card.

#### TC-E2E-22 — Corrupted Storage Recovery
- **Priority**: P2 (Normal)
- **Objective**: Ensure the app gracefully resets to seed data if localStorage is corrupted.
- **Steps**:
  1. Set `localStorage['flowboard-v1']` to invalid non-JSON string (`'{invalid-json--broken'`).
  2. Reload page.
- **Expected Results**:
  - App catches JSON parse error gracefully.
  - Default "Product launch" board and 10 seed cards are rendered without throwing uncaught exceptions.

---

### Module 7: Responsive Navigation & Interaction

#### TC-E2E-23 — Mobile Drawer Navigation & Escape Key
- **Priority**: P1 (Critical)
- **Objective**: Open/close sidebar on mobile viewport and verify Escape dismissal.
- **Steps**:
  1. Resize viewport to 375 × 812 (mobile portrait).
  2. Click mobile hamburger button `#mobileMenu`.
  3. Verify `#sidebar` has `.open` class.
  4. Press `Escape` key on keyboard.
- **Expected Results**:
  - Sidebar opens with `.open` class.
  - Pressing `Escape` removes `.open` class and collapses drawer.

---

### Module 8: Security & XSS Sanitization

#### TC-E2E-24 — User Input Sanitization (XSS Prevention)
- **Priority**: P0 (Blocker)
- **Objective**: Verify HTML tags and script injections are escaped via `safe()`.
- **Steps**:
  1. Create a card with title `<b id="xss">Injected Bold</b><script>window.__xss = true;</script>`.
  2. Enter description `<img src=x onerror="window.__xss=true" />`.
  3. Click `#saveCard`.
- **Expected Results**:
  - `window.__xss` remains `undefined` / `false`.
  - No element with `#xss` is created in DOM.
  - HTML entities are escaped and rendered as text literals.

---

### Module 9: Secondary UI Actions & Feedback

#### TC-E2E-25 — Placeholder Feature Toast Notifications
- **Priority**: P3 (Low)
- **Objective**: Verify clicking stub features shows informative toast messages.
- **Steps**:
  1. Click `#upgradeButton` ("Explore plans").
  2. Click `.member-add` ("Invite member").
  3. Click `"Table"` view tab.
- **Expected Results**:
  - Toast displays `"Plan options are coming soon"`.
  - Toast displays `"Invite link copied"`.
  - Toast displays `"Table view is coming soon"`.

---

## 4. Test Matrix & Traceability

| ID | Test Scenario | Module | Priority | Automated Test Method |
|---|---|---|---|---|
| TC-E2E-01 | Initial Board & Lists Render | Board | P0 | `test_tc01_initial_board_renders` |
| TC-E2E-02 | Create New Board | Board | P0 | `test_tc02_create_new_board` |
| TC-E2E-03 | Switch Active Boards | Board | P1 | `test_tc03_switch_boards` |
| TC-E2E-04 | Rename Board via Dialog | Board | P1 | `test_tc04_rename_board` |
| TC-E2E-05 | Single Board Deletion Guard | Board | P1 | `test_tc05_single_board_deletion_guard` |
| TC-E2E-06 | Delete Board with Multi Boards | Board | P1 | `test_tc06_delete_board_with_multiple_boards` |
| TC-E2E-07 | Favorite Board Star Toggle | Board | P2 | `test_tc07_favorite_board_toggle` |
| TC-E2E-08 | Create New List | List | P0 | `test_tc08_create_new_list` |
| TC-E2E-09 | Rename List | List | P1 | `test_tc09_rename_list` |
| TC-E2E-10 | List Card Count Synchronization | List | P2 | `test_tc10_list_card_count_accurate` |
| TC-E2E-11 | Create Card with Full Details | Card | P0 | `test_tc11_create_card_with_full_details` |
| TC-E2E-12 | Create Card Validation | Card | P2 | `test_tc12_create_card_validation` |
| TC-E2E-13 | Edit Existing Card | Card | P0 | `test_tc13_edit_existing_card` |
| TC-E2E-14 | Delete Card & Toast | Card | P0 | `test_tc14_delete_card_and_toast` |
| TC-E2E-15 | Cancel Card Modal | Card | P2 | `test_tc15_cancel_card_modal_without_saving` |
| TC-E2E-16 | Move Card Between Lists | Drag & Drop | P0 | `test_tc16_move_card_across_lists` |
| TC-E2E-17 | Reorder Cards in Same List | Drag & Drop | P1 | `test_tc17_reorder_cards_within_same_list` |
| TC-E2E-18 | Search Filter & Clear | Search | P1 | `test_tc18_search_filter_and_clear` |
| TC-E2E-19 | Filter Toolbar Button Prompt | Search | P2 | `test_tc19_filter_button_prompt` |
| TC-E2E-20 | Keyboard Shortcut (Cmd+K / Ctrl+K) | Search | P2 | `test_tc20_keyboard_shortcut_cmd_k_focuses_search` |
| TC-E2E-21 | LocalStorage Persistence on Reload | Persistence | P0 | `test_tc21_persistence_after_page_reload` |
| TC-E2E-22 | Corrupted Storage Fallback | Persistence | P2 | `test_tc22_corrupted_local_storage_recovery` |
| TC-E2E-23 | Mobile Drawer & Escape Key | Responsive | P1 | `test_tc23_mobile_viewport_and_sidebar_toggle` |
| TC-E2E-24 | XSS Sanitization & Escaping | Security | P0 | `test_tc24_xss_prevention` |
| TC-E2E-25 | Placeholder Feature Toasts | UI Feedback | P3 | `test_tc25_placeholder_feature_toasts` |
