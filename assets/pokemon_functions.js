var dmcfuncs = window.dashMantineFunctions = window.dashMantineFunctions || {};

dmcfuncs.renderPokemonOption = function ({ option }, { sprites }) {
    const dmc = window.dash_mantine_components;
    if (!dmc) return option.label;

    const spriteUrl = sprites[option.value];

    return React.createElement(
        dmc.Group,
        { gap: "sm", wrap: "nowrap" },
        React.createElement(dmc.Image, {
            key: "sprite-" + option.value,
            src: spriteUrl,
            h: 30,
            w: 30,
            fit: "contain",
            fallbackSrc: "/assets/sprites/pokeball_placeholder.png",
            className: "pokemon-sprite"
        }),
        React.createElement(
            "div",
            { key: "text-block-" + option.value },
            React.createElement(dmc.Text, { size: "sm", key: "name-" + option.value }, option.label)
        )
    );
};

// Clientside callback helper for evolution clicks
window.dash_clientside = window.dash_clientside || {};
window.dash_clientside.clientside = window.dash_clientside.clientside || {};
window.dash_clientside.clientside.handleEvolutionClick = function (evo_clicks) {
    if (!evo_clicks || evo_clicks.length === 0) {
        return window.dash_clientside.no_update;
    }

    // dash_clientside.callback_context.triggered gives us information about what was clicked
    const triggered = window.dash_clientside.callback_context.triggered;
    if (!triggered || triggered.length === 0) {
        return window.dash_clientside.no_update;
    }

    const trigger = triggered[0];
    // Property check for n_clicks > 0
    if (trigger.value > 0) {
        // ID is usually a dictionary for evo-links: {"name": "Bulbasaur", "type": "evo-link"}
        try {
            const id = JSON.parse(trigger.prop_id.split('.')[0]);
            return id.name;
        } catch (e) {
            console.error("Failed to parse trigger ID", e);
        }
    }

    return window.dash_clientside.no_update;
};

window.dash_clientside.clientside.playPokemonCry = function(n_clicks) {
    if (n_clicks > 0) {
        const audioElement = document.getElementById('pokemon-cry-audio');
        if (audioElement) {
            audioElement.currentTime = 0;
            audioElement.play();
        }
    }
    return window.dash_clientside.no_update;
};
