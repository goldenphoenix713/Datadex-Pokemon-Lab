from app import app
import time
import pytest

pytestmark = pytest.mark.slow


def test_001_initial_load(dash_duo):
    """Verify the app loads with default selections and proper visibility."""
    dash_duo.start_server(app)

    # Wait for initial focus (ensures callbacks finished)
    dash_duo.wait_for_text_to_equal("#pokemon-name-display", "Bulbasaur", timeout=15)

    # Now check title (DMC apps might update title during callback)
    assert dash_duo.driver.title == "Data-Dex: Ultimate Stat Lab"

    # Check that the focus-selector is visible
    focus_selector = dash_duo.find_element("#focus-selector")
    assert focus_selector.is_displayed()


def test_002_auto_focus_addition(dash_duo):
    """Verify that adding a new Pokemon auto-focuses it."""
    dash_duo.start_server(app)

    # Use wait_for_element to ensure the page is ready
    selector = dash_duo.wait_for_element("#pokemon-selector", timeout=15)
    dash_duo.driver.execute_script("arguments[0].click();", selector)
    time.sleep(1.5)

    # In Mantine 7, the input might be nested or have a specific class
    selector_input = dash_duo.find_element("#pokemon-selector input")
    selector_input.send_keys("Squirtle")
    time.sleep(2)

    # Wait for options to appear in the portal
    dash_duo.wait_for_element("[role='option']", timeout=10)
    options = dash_duo.find_elements("[role='option']")

    target = None
    for opt in options:
        if "Squirtle" in opt.text:
            target = opt
            break

    assert target is not None, "Squirtle option not found in dropdown."
    dash_duo.driver.execute_script("arguments[0].click();", target)

    # Verify focus switched to Squirtle
    dash_duo.wait_for_text_to_equal("#pokemon-name-display", "Squirtle", timeout=15)

    # Verify dropdown also shows Squirtle (value might be in data-value attribute in newer Mantine)
    focus_sel = dash_duo.find_element("#focus-selector")
    # Check text content or value attribute
    assert (
        "Squirtle" in focus_sel.get_attribute("value") or "Squirtle" in focus_sel.text
    )


def test_003_evolution_chain_click(dash_duo):
    """Verify that clicking an evolution link updates focus and syncs dropdown."""
    dash_duo.start_server(app)

    # Ensure Bulbasaur is displayed
    dash_duo.wait_for_text_to_equal("#pokemon-name-display", "Bulbasaur", timeout=15)

    # Find Ivysaur in the evolution chain
    dash_duo.wait_for_element(".evolution-node", timeout=15)
    evo_nodes = dash_duo.find_elements(".evolution-node")

    ivysaur_node = None
    for node in evo_nodes:
        # Use child text or ID parsing
        if "Ivysaur" in node.text or (
            node.get_attribute("id") and "Ivysaur" in node.get_attribute("id")
        ):
            ivysaur_node = node
            break

    assert ivysaur_node is not None, "Ivysaur node not found in lineage"

    # Use JS click to avoid ElementClickInterceptedException
    dash_duo.driver.execute_script("arguments[0].click();", ivysaur_node)

    # Verify focus switch
    dash_duo.wait_for_text_to_equal("#pokemon-name-display", "Ivysaur", timeout=15)


def test_004_filter_toggles(dash_duo):
    """Verify that toggling Mega filters updates the Evolution Lineage."""
    dash_duo.start_server(app)

    # Select Charizard
    selector = dash_duo.wait_for_element("#pokemon-selector", timeout=15)
    dash_duo.driver.execute_script("arguments[0].click();", selector)
    time.sleep(1.5)

    selector_input = dash_duo.find_element("#pokemon-selector input")
    selector_input.send_keys("Charizard")
    time.sleep(2)

    option = dash_duo.wait_for_element("[role='option']", timeout=10)
    dash_duo.driver.execute_script("arguments[0].click();", option)

    dash_duo.wait_for_text_to_equal("#pokemon-name-display", "Charizard", timeout=15)

    # Check for Mega Charizard Y
    dash_duo.wait_for_element("#evolution-chain-display", timeout=10)
    content = dash_duo.find_element("#evolution-chain-display").get_attribute(
        "innerHTML"
    )
    assert "Mega Charizard Y" in content

    # Toggle Mega OFF
    mega_toggle = dash_duo.find_element("#mega-toggle")
    dash_duo.driver.execute_script("arguments[0].click();", mega_toggle)
    time.sleep(2)

    # Verify Mega is gone
    content_updated = dash_duo.find_element("#evolution-chain-display").get_attribute(
        "innerHTML"
    )
    assert "Mega Charizard Y" not in content_updated
