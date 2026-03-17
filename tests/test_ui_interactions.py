from app import app
import time
import pytest
from selenium.webdriver.common.by import By

pytestmark = pytest.mark.slow


def test_001_initial_load(dash_duo):
    """Verify the app loads with default selections and proper visibility."""
    dash_duo.start_server(app)

    # Wait for initial focus (ensures callbacks finished)
    dash_duo.wait_for_text_to_equal("#pokemon-name-display", "Bulbasaur", timeout=15)

    assert dash_duo.driver.title == "Data-Dex: Ultimate Stat Lab"
    focus_selector = dash_duo.find_element("#focus-selector")
    assert focus_selector.is_displayed()


def select_pokemon(dash_duo, name):
    """Helper to select a specific Pokemon from the searchable focus-selector."""
    # In Mantine 7 / DMC 0.14, the ID is often on the input itself if searchable
    selector_input = dash_duo.wait_for_element("#focus-selector", timeout=15)

    # If it's not the input, find the input inside
    if selector_input.tag_name != "input":
        selector_input = selector_input.find_element(By.TAG_NAME, "input")

    # Clear and type
    dash_duo.driver.execute_script("arguments[0].value = '';", selector_input)
    selector_input.send_keys(name)
    time.sleep(2)

    # Find the EXACT option from the dropdown (portal)
    # Role 'option' is standard for Mantine/Combobox
    dash_duo.wait_for_element("[role='option']", timeout=10)
    options = dash_duo.find_elements(By.CSS_SELECTOR, "[role='option']")
    target = None
    for opt in options:
        if opt.text.strip() == name:
            target = opt
            break

    if not target:
        for opt in options:
            if name in opt.text:
                target = opt
                break

    assert target, f"Could not find option for {name}"
    dash_duo.driver.execute_script("arguments[0].click();", target)
    time.sleep(1.5)


def test_002_focus_switching(dash_duo):
    """Verify that selecting a new Pokemon updates the detail view."""
    dash_duo.start_server(app)
    select_pokemon(dash_duo, "Squirtle")
    dash_duo.wait_for_text_to_equal("#pokemon-name-display", "Squirtle", timeout=15)


def test_003_evolution_chain_click(dash_duo):
    """Verify that clicking an evolution link updates focus and syncs dropdown."""
    dash_duo.start_server(app)
    dash_duo.wait_for_text_to_equal("#pokemon-name-display", "Bulbasaur", timeout=15)

    dash_duo.wait_for_element(".evolution-node", timeout=15)
    evo_nodes = dash_duo.find_elements(By.CLASS_NAME, "evolution-node")

    ivysaur_node = None
    for node in evo_nodes:
        # Dash IDs with dictionaries are stringified and keys are sorted (type, name)
        node_id = node.get_attribute("id")
        if node_id and '"name":"Ivysaur"' in node_id:
            ivysaur_node = node
            break

    assert ivysaur_node, "Ivysaur node not found"
    dash_duo.driver.execute_script("arguments[0].click();", ivysaur_node)
    dash_duo.wait_for_text_to_equal("#pokemon-name-display", "Ivysaur", timeout=15)


def test_004_filter_toggles(dash_duo):
    """Verify that toggling Mega filters updates the Evolution Lineage."""
    dash_duo.start_server(app)
    select_pokemon(dash_duo, "Charizard")
    dash_duo.wait_for_text_to_equal("#pokemon-name-display", "Charizard", timeout=15)

    # Mega Charizard Y
    mega_idx = '{"name":"Mega Charizard Y","type":"evo-link"}'
    # Wait for the element with the exact ID string
    dash_duo.wait_for_element(f"[id='{mega_idx}']", timeout=15)

    # Toggle Mega OFF
    mega_toggle = dash_duo.find_element("#mega-toggle")
    dash_duo.driver.execute_script("arguments[0].click();", mega_toggle)
    time.sleep(2)

    # Verify Mega is gone
    elements = dash_duo.find_elements(By.CSS_SELECTOR, f"[id='{mega_idx}']")
    assert len(elements) == 0, "Mega Charizard Y should be removed from lineage"


def test_005_team_management(dash_duo):
    """Verify adding and removing Pokemon from the team."""
    dash_duo.start_server(app)

    dash_duo.wait_for_text_to_equal("#pokemon-name-display", "Bulbasaur", timeout=15)
    add_btn = dash_duo.wait_for_element("#add-pokemon-btn", timeout=10)

    # Simple retry to ensure button is enabled
    for _ in range(5):
        if not add_btn.get_attribute("disabled"):
            dash_duo.driver.execute_script("arguments[0].click();", add_btn)
            break
        time.sleep(1)

    dash_duo.wait_for_contains_text("#team-list", "Bulbasaur", timeout=20)

    # Add Charmander
    select_pokemon(dash_duo, "Charmander")
    dash_duo.wait_for_text_to_equal("#pokemon-name-display", "Charmander", timeout=15)

    # Click again (add_btn element should still be valid if it wasn't replaced)
    for _ in range(5):
        if not add_btn.get_attribute("disabled"):
            dash_duo.driver.execute_script("arguments[0].click();", add_btn)
            break
        time.sleep(1)

    dash_duo.wait_for_contains_text("#team-list", "Charmander", timeout=15)

    # Remove Bulbasaur
    remove_idx = '{"name":"Bulbasaur","type":"remove-team"}'
    remove_btn = dash_duo.wait_for_element(f"[id='{remove_idx}']", timeout=15)
    dash_duo.driver.execute_script("arguments[0].click();", remove_btn)

    time.sleep(2)
    team_content = dash_duo.find_element("#team-list").text
    assert "Bulbasaur" not in team_content
    assert "Charmander" in team_content
