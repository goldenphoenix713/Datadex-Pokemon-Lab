from app import app
import time


def test_001_initial_load(dash_duo):
    """Verify the app loads with default selections and proper visibility."""
    dash_duo.start_server(app)

    # 1. Check title
    assert dash_duo.driver.title == "Data-Dex: Ultimate Stat Lab"

    # 2. Check initial focus (Bulbasaur)
    dash_duo.wait_for_text_to_equal("#pokemon-name-display", "Bulbasaur", timeout=10)

    # 3. Check that the focus-selector is visible
    focus_selector = dash_duo.find_element("#focus-selector")
    assert focus_selector.is_displayed()


def test_002_auto_focus_addition(dash_duo):
    """Verify that adding a new Pokemon auto-focuses it."""
    dash_duo.start_server(app)

    # Use JS to focus and click the dropdown to ensure options appear
    selector = dash_duo.find_element("#pokemon-selector")
    dash_duo.driver.execute_script("arguments[0].click();", selector)
    time.sleep(1)

    # Type into input
    selector_input = dash_duo.find_element("#pokemon-selector input")
    selector_input.send_keys("Squirtle")
    time.sleep(1)

    # Find Squirtle in options using multiple potential classes
    # Dash-Mantine combined with Dcc can be tricky
    options = (
        dash_duo.find_elements(".dash-dropdown-option")
        or dash_duo.find_elements(".Select-option")
        or dash_duo.find_elements("[role='option']")
    )

    target = None
    for opt in options:
        if "Squirtle" in opt.text:
            target = opt
            break

    if not target:
        # Debug: list all roles on page if fails
        all_options = dash_duo.find_elements("[role='option']")
        assert target is not None, (
            f"Squirtle option not found. Roles found: {[o.text for o in all_options]}"
        )

    dash_duo.driver.execute_script("arguments[0].click();", target)

    # Verify focus switched to Squirtle
    dash_duo.wait_for_text_to_equal("#pokemon-name-display", "Squirtle", timeout=10)

    # Verify dropdown also shows Squirtle
    focus_sel = dash_duo.find_element("#focus-selector")
    assert "Squirtle" in focus_sel.get_attribute("value")


def test_003_evolution_chain_click(dash_duo):
    """Verify that clicking an evolution link updates focus and syncs dropdown."""
    dash_duo.start_server(app)

    # Ensure Bulbasaur is displayed
    dash_duo.wait_for_text_to_equal("#pokemon-name-display", "Bulbasaur", timeout=10)

    # Find Ivysaur in the evolution chain
    dash_duo.wait_for_element(".evolution-node", timeout=10)
    evo_nodes = dash_duo.find_elements(".evolution-node")

    ivysaur_node = None
    for node in evo_nodes:
        # Use ID parsing for reliable discovery
        node_id = node.get_attribute("id")
        if node_id and "Ivysaur" in node_id:
            ivysaur_node = node
            break

    assert ivysaur_node is not None, f"Ivysaur node not found in lineage"

    # Use JS click to avoid ElementClickInterceptedException from tooltips/overlays
    dash_duo.driver.execute_script("arguments[0].click();", ivysaur_node)

    # Verify focus switch
    dash_duo.wait_for_text_to_equal("#pokemon-name-display", "Ivysaur", timeout=10)

    # Verify dropdown update
    focus_sel = dash_duo.find_element("#focus-selector")
    assert "Ivysaur" in focus_sel.get_attribute("value")


def test_004_filter_toggles(dash_duo):
    """Verify that toggling Mega filters updates the Evolution Lineage."""
    dash_duo.start_server(app)

    # Select Charizard
    selector = dash_duo.find_element("#pokemon-selector")
    dash_duo.driver.execute_script("arguments[0].click();", selector)
    time.sleep(1)

    selector_input = dash_duo.find_element("#pokemon-selector input")
    selector_input.send_keys("Charizard")
    time.sleep(1)

    # Click first option
    option = dash_duo.wait_for_element(
        ".dash-dropdown-option, .Select-option, [role='option']"
    )
    dash_duo.driver.execute_script("arguments[0].click();", option)

    dash_duo.wait_for_text_to_equal("#pokemon-name-display", "Charizard", timeout=10)

    # Check for Mega Charizard Y
    dash_duo.wait_for_element("#evolution-chain-display")
    content = dash_duo.find_element("#evolution-chain-display").get_attribute(
        "innerHTML"
    )
    assert "Mega Charizard Y" in content

    # Toggle Mega OFF
    mega_toggle = dash_duo.find_element("#mega-toggle")
    dash_duo.driver.execute_script("arguments[0].click();", mega_toggle)
    time.sleep(1)

    # Verify Mega is gone
    content_updated = dash_duo.find_element("#evolution-chain-display").get_attribute(
        "innerHTML"
    )
    assert "Mega Charizard Y" not in content_updated
