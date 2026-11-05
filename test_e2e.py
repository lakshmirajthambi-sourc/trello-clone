"""
End-to-End Automated Test Suite for Flowboard (Trello Clone)
Framework: pytest + Playwright (Python)
Usage:
    pytest test_e2e.py
    or
    python test_e2e.py
"""

import http.server
import json
import threading
from typing import Generator
import pytest
from playwright.sync_api import sync_playwright, Page, BrowserContext, Browser, Playwright


class QuietServer(http.server.ThreadingHTTPServer):
    def __init__(self, server_address, RequestHandlerClass):
        super().__init__(server_address, RequestHandlerClass)


class StaticFileHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, format, *args):
        # Suppress standard HTTP request logging in test outputs
        pass


@pytest.fixture(scope="session")
def server_url() -> Generator[str, None, None]:
    """Spins up a lightweight HTTP server serving the current directory on a random port."""
    server = QuietServer(("127.0.0.1", 0), StaticFileHandler)
    port = server.server_port
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    yield f"http://127.0.0.1:{port}"
    server.shutdown()
    server.server_close()


@pytest.fixture(scope="session")
def playwright_instance() -> Generator[Playwright, None, None]:
    with sync_playwright() as p:
        yield p


@pytest.fixture(scope="session")
def browser(playwright_instance: Playwright) -> Generator[Browser, None, None]:
    # Try chrome first, then msedge, then default bundled chromium
    for channel in ["chrome", "msedge", None]:
        try:
            if channel:
                b = playwright_instance.chromium.launch(channel=channel, headless=True)
            else:
                b = playwright_instance.chromium.launch(headless=True)
            yield b
            b.close()
            return
        except Exception:
            continue
    raise RuntimeError("No supported browser could be launched.")


@pytest.fixture
def page(browser: Browser, server_url: str) -> Generator[Page, None, None]:
    context: BrowserContext = browser.new_context()
    pg = context.new_page()
    # Ensure fresh storage before each test
    pg.goto(f"{server_url}/index.html")
    pg.evaluate("() => localStorage.clear()")
    pg.reload()
    pg.wait_for_selector("#boardCanvas")
    yield pg
    context.close()


# =========================================================================
# 1. BOARD LIFECYCLE MANAGEMENT TESTS
# =========================================================================

def test_tc01_initial_board_renders(page: Page):
    """TC-E2E-01: Verify default initial board and elements render correctly."""
    assert "Flowboard" in page.title()
    assert page.locator("#boardTitle").text_content() == "Product launch"
    assert page.locator("#crumbBoard").text_content() == "Product launch"
    assert page.locator("#boardDescription").text_content() == "A little progress each day adds up to big results."
    
    # Verify 4 default lists: Ideas, To do, In progress, Done
    lists = page.locator("section.list-column")
    assert lists.count() == 4
    list_titles = [el.text_content().strip() for el in page.locator(".list-title").all()]
    assert list_titles == ["Ideas", "To do", "In progress", "Done"]

    # Verify initial cards total 10
    cards = page.locator("article.task-card")
    assert cards.count() == 10
    assert page.locator("text=Research competitor products").is_visible()
    assert page.locator("text=Write launch announcement").is_visible()


def test_tc02_create_new_board(page: Page):
    """TC-E2E-02: Create a new board and verify it becomes active with default lists."""
    page.click("#addBoard")
    assert page.locator("#boardDialog").is_visible()
    page.fill("#newBoardName", "Mobile App Redesign")
    page.click('#boardForm button[value="save"]')

    # Modal should close and new board should be active
    assert page.locator("#boardDialog").is_hidden()
    assert page.locator("#boardTitle").text_content() == "Mobile App Redesign"
    assert page.locator("#crumbBoard").text_content() == "Mobile App Redesign"

    # Newly created board has 3 default lists: To do, In progress, Done
    list_titles = [el.text_content().strip() for el in page.locator(".list-title").all()]
    assert list_titles == ["To do", "In progress", "Done"]

    # Board nav should contain both boards
    nav_boards = [el.text_content().strip() for el in page.locator("#boardNav button").all()]
    assert "Product launch" in nav_boards
    assert "Mobile App Redesign" in nav_boards


def test_tc03_switch_boards(page: Page):
    """TC-E2E-03: Create a second board and switch back and forth between boards."""
    page.click("#addBoard")
    page.fill("#newBoardName", "Marketing Strategy")
    page.click('#boardForm button[value="save"]')
    assert page.locator("#boardTitle").text_content() == "Marketing Strategy"

    # Click on the original 'Product launch' board in navigation
    page.locator("#boardNav button:has-text('Product launch')").click()
    assert page.locator("#boardTitle").text_content() == "Product launch"
    assert page.locator("text=Research competitor products").is_visible()

    # Switch back to 'Marketing Strategy'
    page.locator("#boardNav button:has-text('Marketing Strategy')").click()
    assert page.locator("#boardTitle").text_content() == "Marketing Strategy"
    assert page.locator("text=Research competitor products").is_hidden()


def test_tc04_rename_board(page: Page):
    """TC-E2E-04: Rename the active board using the board menu prompt."""
    page.on("dialog", lambda dialog: dialog.accept("Global Brand Relaunch"))
    page.click("#boardMenu")
    
    assert page.locator("#boardTitle").text_content() == "Global Brand Relaunch"
    assert page.locator("#crumbBoard").text_content() == "Global Brand Relaunch"
    assert page.locator("#boardNav button.active").text_content().strip() == "Global Brand Relaunch"


def test_tc05_single_board_deletion_guard(page: Page):
    """TC-E2E-05: Prevent deletion when only one board exists, showing a guard toast."""
    page.on("dialog", lambda dialog: dialog.accept("DELETE"))
    page.click("#boardMenu")

    # Toast should warn user and board must NOT be deleted
    toast = page.locator("#toast")
    assert toast.is_visible()
    assert "Keep at least one board" in toast.text_content()
    assert page.locator("#boardTitle").text_content() == "Product launch"
    assert page.locator("#boardNav button").count() == 1


def test_tc06_delete_board_with_multiple_boards(page: Page):
    """TC-E2E-06: Successfully delete a board when multiple boards exist."""
    # Create second board
    page.click("#addBoard")
    page.fill("#newBoardName", "Temporary Board")
    page.click('#boardForm button[value="save"]')
    assert page.locator("#boardNav button").count() == 2

    # Delete the newly active 'Temporary Board'
    page.on("dialog", lambda dialog: dialog.accept("DELETE"))
    page.click("#boardMenu")

    # Active board falls back to the remaining board
    assert page.locator("#boardNav button").count() == 1
    assert page.locator("#boardTitle").text_content() == "Product launch"


def test_tc07_favorite_board_toggle(page: Page):
    """TC-E2E-07: Toggle board favorite star button."""
    star = page.locator(".star-button")
    assert star.text_content() == "☆"
    assert "is-favorite" not in (star.get_attribute("class") or "")

    star.click()
    assert star.text_content() == "★"
    assert "is-favorite" in (star.get_attribute("class") or "")

    star.click()
    assert star.text_content() == "☆"
    assert "is-favorite" not in (star.get_attribute("class") or "")


# =========================================================================
# 2. LIST LIFECYCLE MANAGEMENT TESTS
# =========================================================================

def test_tc08_create_new_list(page: Page):
    """TC-E2E-08: Add a new list to the current board via the canvas button."""
    page.click("#addListCanvas")
    assert page.locator("#listDialog").is_visible()
    page.fill("#listName", "Blocked")
    page.click('#listForm button[value="save"]')

    assert page.locator("#listDialog").is_hidden()
    new_list = page.locator("section.list-column:has-text('Blocked')")
    assert new_list.is_visible()
    assert new_list.locator(".list-count").text_content() == "0"


def test_tc09_rename_list(page: Page):
    """TC-E2E-09: Rename an existing list via its menu prompt."""
    page.on("dialog", lambda dialog: dialog.accept("Backlog & Brainstorming"))
    page.locator('button[data-list-menu="ideas"]').click()

    assert page.locator("section[data-list='ideas'] .list-title").text_content() == "Backlog & Brainstorming"


def test_tc10_list_card_count_accurate(page: Page):
    """TC-E2E-10: Verify list card counter matches the actual number of cards."""
    ideas_count = int(page.locator("section[data-list='ideas'] .list-count").text_content() or "0")
    actual_cards = page.locator("section[data-list='ideas'] .task-card").count()
    assert ideas_count == actual_cards == 3


# =========================================================================
# 3. CARD LIFECYCLE MANAGEMENT TESTS
# =========================================================================

def test_tc11_create_card_with_full_details(page: Page):
    """TC-E2E-11: Create a card with title, description, label, and due date."""
    page.locator('button[data-add-card="ideas"]').click()
    assert page.locator("#cardDialog").is_visible()
    
    # Fill card details
    page.fill("#cardName", "Implement SSO Integration")
    page.fill("#cardDescription", "Support OAuth 2.0 with Google and GitHub.")
    page.select_option("#cardLabel", "blue")  # Development label
    page.fill("#cardDue", "2026-12-15")
    page.click("#saveCard")

    assert page.locator("#cardDialog").is_hidden()
    card = page.locator("article.task-card:has-text('Implement SSO Integration')")
    assert card.is_visible()
    assert card.locator(".task-desc").text_content() == "Support OAuth 2.0 with Google and GitHub."
    assert card.locator(".task-label.blue").is_visible()
    assert card.locator(".due-pill").is_visible()
    # Verify ideas list card count incremented to 4
    assert page.locator("section[data-list='ideas'] .list-count").text_content() == "4"


def test_tc12_create_card_validation(page: Page):
    """TC-E2E-12: Verify empty title prevents card creation."""
    page.locator('button[data-add-card="ideas"]').click()
    page.fill("#cardName", "")
    page.click("#saveCard")

    # Form required validation keeps the dialog open and cards count intact
    assert page.locator("#cardDialog").is_visible()
    page.locator("#cardDialog .close-modal").click()
    assert page.locator("section[data-list='ideas'] .task-card").count() == 3


def test_tc13_edit_existing_card(page: Page):
    """TC-E2E-13: Open an existing card, modify its details, and verify changes."""
    page.locator("text=Research competitor products").click()
    assert page.locator("#cardDialog").is_visible()
    assert page.locator("#cardName").input_value() == "Research competitor products"

    page.fill("#cardName", "Research top 5 competitors thoroughly")
    page.fill("#cardDescription", "Updated market positioning analysis.")
    page.select_option("#cardLabel", "mint")
    page.click("#saveCard")

    assert page.locator("#cardDialog").is_hidden()
    updated_card = page.locator("article.task-card:has-text('Research top 5 competitors thoroughly')")
    assert updated_card.is_visible()
    assert updated_card.locator(".task-desc").text_content() == "Updated market positioning analysis."
    assert updated_card.locator(".task-label.mint").is_visible()


def test_tc14_delete_card_and_toast(page: Page):
    """TC-E2E-14: Delete a card from the card modal and verify toast notification."""
    initial_count = page.locator("article.task-card").count()
    page.locator("text=Define our product vision").click()
    assert page.locator("#deleteCard").is_visible()

    page.click("#deleteCard")
    assert page.locator("#cardDialog").is_hidden()
    assert page.locator("text=Define our product vision").is_hidden()
    assert page.locator("article.task-card").count() == initial_count - 1

    toast = page.locator("#toast")
    assert toast.is_visible()
    assert "Card deleted" in toast.text_content()


def test_tc15_cancel_card_modal_without_saving(page: Page):
    """TC-E2E-15: Closing or canceling the modal leaves the card unchanged."""
    page.locator("text=Create moodboard").click()
    page.fill("#cardName", "This should NOT be saved")
    page.locator("#cardDialog .close-modal").click()

    assert page.locator("text=Create moodboard").is_visible()
    assert page.locator("text=This should NOT be saved").is_hidden()


# =========================================================================
# 4. DRAG AND DROP & REORDERING TESTS
# =========================================================================

def test_tc16_move_card_across_lists(page: Page):
    """TC-E2E-16: Drag a card from one list to another and verify positions and counts."""
    source_card = page.locator("article.task-card[data-card='c1']")
    target_list = page.locator("section.list-column[data-list='done']")

    assert page.locator("section[data-list='ideas'] .task-card").count() == 3
    assert page.locator("section[data-list='done'] .task-card").count() == 2

    source_card.drag_to(target_list)

    assert page.locator("section[data-list='ideas'] .task-card").count() == 2
    assert page.locator("section[data-list='done'] .task-card").count() == 3
    assert page.locator("section[data-list='done'] [data-card='c1']").is_visible()


def test_tc17_reorder_cards_within_same_list(page: Page):
    """TC-E2E-17: Drag a card within the same list to change its relative order."""
    ideas_list = page.locator("section.list-column[data-list='ideas']")
    card3 = page.locator("article.task-card[data-card='c3']")
    card1 = page.locator("article.task-card[data-card='c1']")

    before_order = ideas_list.locator(".task-card").evaluate_all("els => els.map(e => e.dataset.card)")
    assert before_order == ["c1", "c2", "c3"]

    # Drag card c3 above card c1
    card3.drag_to(card1)

    after_order = ideas_list.locator(".task-card").evaluate_all("els => els.map(e => e.dataset.card)")
    assert after_order == ["c3", "c1", "c2"]


# =========================================================================
# 5. SEARCH & FILTERING TESTS
# =========================================================================

def test_tc18_search_filter_and_clear(page: Page):
    """TC-E2E-18: Type into search input to filter cards, then clear to restore."""
    total_cards = page.locator("article.task-card").count()
    assert total_cards == 10

    # Search for 'competitor'
    page.fill("#searchInput", "competitor")
    visible_cards = [c for c in page.locator("article.task-card").all() if not c.is_hidden()]
    assert len(visible_cards) == 1
    assert "competitor" in visible_cards[0].text_content().lower()

    # Clear search
    page.fill("#searchInput", "")
    all_visible = [c for c in page.locator("article.task-card").all() if not c.is_hidden()]
    assert len(all_visible) == total_cards


def test_tc19_filter_button_prompt(page: Page):
    """TC-E2E-19: Use the filter toolbar button prompt to search cards."""
    page.on("dialog", lambda dialog: dialog.accept("landing"))
    page.click("#filterButton")

    assert page.locator("#searchInput").input_value() == "landing"
    visible_cards = [c for c in page.locator("article.task-card").all() if not c.is_hidden()]
    assert len(visible_cards) == 1
    assert "Design landing page" in visible_cards[0].text_content()


def test_tc20_keyboard_shortcut_cmd_k_focuses_search(page: Page):
    """TC-E2E-20: Pressing Control+K or Meta+K focuses the search input."""
    page.keyboard.press("Control+k")
    is_focused = page.evaluate("() => document.activeElement === document.querySelector('#searchInput')")
    assert is_focused is True


# =========================================================================
# 6. STORAGE PERSISTENCE & FAULT TOLERANCE TESTS
# =========================================================================

def test_tc21_persistence_after_page_reload(page: Page):
    """TC-E2E-21: State persisted to localStorage survives hard browser reloads."""
    # Add a custom card
    page.locator('button[data-add-card="progress"]').click()
    page.fill("#cardName", "Persisted Card Across Reload")
    page.click("#saveCard")

    assert page.locator("text=Persisted Card Across Reload").is_visible()

    # Reload page
    page.reload()
    page.wait_for_selector("#boardCanvas")

    # Card must still be present
    assert page.locator("text=Persisted Card Across Reload").is_visible()
    assert page.locator("section[data-list='progress'] article.task-card:has-text('Persisted Card Across Reload')").is_visible()


def test_tc22_corrupted_local_storage_recovery(page: Page):
    """TC-E2E-22: Gracefully recover to default boards if localStorage contains corrupted data."""
    # Inject corrupted non-JSON data into localStorage
    page.evaluate("() => localStorage.setItem('flowboard-v1', '{invalid-json--broken')")
    page.reload()
    page.wait_for_selector("#boardCanvas")

    # Default board should be loaded without crashing
    assert page.locator("#boardTitle").text_content() == "Product launch"
    assert page.locator("article.task-card").count() == 10


# =========================================================================
# 7. RESPONSIVE NAVIGATION & SHORTCUTS
# =========================================================================

def test_tc23_mobile_viewport_and_sidebar_toggle(page: Page):
    """TC-E2E-23: Mobile menu drawer opens and closes, and Escape key dismisses it."""
    page.set_viewport_size({"width": 375, "height": 812})
    sidebar = page.locator("#sidebar")

    assert "open" not in (sidebar.get_attribute("class") or "")
    
    # Open mobile menu
    page.click("#mobileMenu")
    assert "open" in (sidebar.get_attribute("class") or "")

    # Press Escape to close
    page.keyboard.press("Escape")
    assert "open" not in (sidebar.get_attribute("class") or "")


# =========================================================================
# 8. SECURITY & XSS SANITIZATION
# =========================================================================

def test_tc24_xss_prevention(page: Page):
    """TC-E2E-24: Ensure HTML entities and potential script injections are safely escaped."""
    xss_payload = '<b id="xss">Injected Bold</b><script>window.__xss = true;</script>'
    
    page.locator('button[data-add-card="ideas"]').click()
    page.fill("#cardName", xss_payload)
    page.fill("#cardDescription", "<img src=x onerror=\"window.__xss=true\" />")
    page.click("#saveCard")

    # Verify script was not executed
    has_xss = page.evaluate("() => window.__xss === true")
    assert has_xss is False

    # Verify HTML tags are rendered as plain text strings, not DOM nodes
    assert page.locator("#xss").count() == 0
    assert page.locator("text=<b id=\"xss\">Injected Bold</b>").is_visible()


# =========================================================================
# 9. UI FEEDBACK & PLACEHOLDER TOASTS
# =========================================================================

def test_tc25_placeholder_feature_toasts(page: Page):
    """TC-E2E-25: Clicking placeholder buttons triggers expected informative toast notices."""
    toast = page.locator("#toast")

    # Upgrade plans button
    page.click("#upgradeButton")
    assert toast.is_visible()
    assert "Plan options are coming soon" in toast.text_content()

    # Member add button
    page.click(".member-add")
    assert toast.is_visible()
    assert "Invite link copied" in toast.text_content()

    # Table view tab
    page.locator("button.tab:has-text('Table')").click()
    assert toast.is_visible()
    assert "Table view is coming soon" in toast.text_content()


if __name__ == "__main__":
    pytest.main(["-v", __file__])
