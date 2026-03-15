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
            fallbackSrc: "/assets/images/pokeball_placeholder.png",
            className: "pokemon-sprite"
        }),
        React.createElement(
            "div",
            { key: "text-block-" + option.value },
            React.createElement(dmc.Text, { size: "sm", key: "name-" + option.value }, option.label)
        )
    );
};
