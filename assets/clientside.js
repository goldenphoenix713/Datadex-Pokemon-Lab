window.dash_clientside = Object.assign({}, window.dash_clientside, {
    clientside: {
        TYPE_COLORS: {
            "Normal": "#A8A878", "Fire": "#F08030", "Water": "#6890F0", "Grass": "#78C850",
            "Electric": "#F8D030", "Ice": "#98D8D8", "Fighting": "#C03028", "Poison": "#A040A0",
            "Ground": "#E0C068", "Flying": "#A890F0", "Psychic": "#F85888", "Bug": "#A8B020",
            "Rock": "#B8A038", "Ghost": "#705898", "Dragon": "#7038F8", "Dark": "#705848",
            "Steel": "#B8B8D0", "Fairy": "#EE99AC", "None": "#68A090"
        },

        renderPokemonOption: function (option) {
            const sprites = option.sprites || {};
            const spriteUrl = sprites[option.label] || "";
            return {
                "props": {
                    "children": [
                        {
                            "props": {
                                "src": spriteUrl,
                                "h": 30,
                                "w": 30,
                                "fit": "contain",
                                "mr": "xs"
                            },
                            "type": "Image",
                            "namespace": "dash_mantine_components"
                        },
                        {
                            "props": {
                                "children": option.label
                            },
                            "type": "Text",
                            "namespace": "dash_mantine_components"
                        }
                    ],
                    "align": "center",
                    "wrap": "nowrap"
                },
                "type": "Group",
                "namespace": "dash_mantine_components"
            };
        },

        render_team_list: function (team_names, sprite_map) {
            if (!team_names || team_names.length === 0) {
                return {
                    "props": {
                        "children": "No Pokémon in your comparison yet. Add some from the Detail view!",
                        "c": "dimmed",
                        "size": "sm",
                        "fs": "italic"
                    },
                    "type": "Text",
                    "namespace": "dash_mantine_components"
                };
            }

            const badges = team_names.map(name => {
                const sprite_url = sprite_map ? sprite_map[name] : "";

                return {
                    "props": {
                        "children": [
                            {
                                "props": {
                                    "src": sprite_url,
                                    "h": 40,
                                    "w": 40,
                                    "fit": "contain",
                                    "mr": "xs",
                                    "fallbackSrc": "/assets/sprites/pokeball_placeholder.png"
                                },
                                "type": "Image",
                                "namespace": "dash_mantine_components"
                            },
                            {
                                "props": {
                                    "children": name,
                                    "size": "sm",
                                    "fw": 500,
                                    "style": { "flex": 1 }
                                },
                                "type": "Text",
                                "namespace": "dash_mantine_components"
                            },
                            {
                                "props": {
                                    "id": { "type": "remove-team", "name": name },
                                    "variant": "subtle",
                                    "color": "red",
                                    "size": "sm",
                                    "children": {
                                        "props": {
                                            "icon": "tabler:x"
                                        },
                                        "type": "DashIconify",
                                        "namespace": "dash_iconify"
                                    }
                                },
                                "type": "ActionIcon",
                                "namespace": "dash_mantine_components"
                            }
                        ],
                        "variant": "outline",
                        "color": "gray",
                        "radius": "sm",
                        "h": 40,
                        "p": "xs",
                        "style": { "display": "flex", "alignItems": "center", "minWidth": "160px" }
                    },
                    "type": "Paper",
                    "namespace": "dash_mantine_components"
                };
            });

            return {
                "props": {
                    "gap": "xs",
                    "children": badges
                },
                "type": "Group",
                "namespace": "dash_mantine_components"
            };
        },

        get_filtered_data: function (all_data, regions, show_mega, show_regional, final_only, show_legendary, show_mythical, show_gmax, show_ultra_beasts, selected_types, stat_values, stat_names) {
            if (!all_data) return [];

            const stat_ranges = {};
            if (stat_values && stat_names && stat_values.length === stat_names.length) {
                stat_names.forEach((name, i) => {
                    stat_ranges[name] = stat_values[i];
                });
            }

            return all_data.filter(p => {
                if (regions && regions.length > 0 && !regions.includes(p.Region)) return false;
                if (!show_mega && p.Is_Mega) return false;
                if (!show_regional && p.Is_Regional) return false;
                if (final_only && !p.Is_Final_Evolution) return false;
                if (!show_legendary && p.Is_Legendary) return false;
                if (!show_mythical && p.Is_Mythical) return false;
                if (!show_gmax && p.Is_GMax) return false;
                if (!show_ultra_beasts && p.Is_Ultra_Beast) return false;

                if (selected_types && selected_types.length > 0) {
                    const has_type = selected_types.includes(p["Primary Type"]) || selected_types.includes(p["Secondary Type"]);
                    if (!has_type) return false;
                }

                if (stat_ranges) {
                    for (const [stat, range] of Object.entries(stat_ranges)) {
                        if (p[stat] < range[0] || p[stat] > range[1]) return false;
                    }
                }

                return true;
            });
        },

        update_radar_clientside: function (team_names, name_id_map, all_data) {
            const stats = ["HP", "Attack", "Defense", "Speed", "Special Defense", "Special Attack"];
            const closed_stats = [...stats, stats[0]];

            const base_layout = {
                "uirevision": true,
                "polar": {
                    "radialaxis": { "visible": true, "range": [0, 255], "showticklabels": false, "showline": false, "ticks": "", "gridcolor": "lightgrey" },
                    "angularaxis": { "tickfont": { "size": 14, "color": "white" }, "rotation": 90, "direction": "clockwise" }
                },
                "showlegend": true,
                "legend": {
                    "orientation": "h", "yanchor": "bottom", "y": -0.3, "xanchor": "center", "x": 0.5, "font": { "color": "white" }
                },
                "paper_bgcolor": "rgba(0,0,0,0)",
                "transition": { "duration": 500, "easing": "cubic-in-out" },
                "margin": { "l": 40, "r": 40, "t": 40, "b": 40 }
            };

            if (!team_names || team_names.length === 0) {
                return {
                    "data": [{
                        "type": "scatterpolar",
                        "r": [0, 0, 0, 0, 0, 0, 0],
                        "theta": closed_stats,
                        "fill": "none",
                        "line": { "color": "transparent" },
                        "hoverinfo": "none",
                        "showlegend": false
                    }],
                    "layout": base_layout
                };
            }

            const team_data = team_names.map(name => {
                return all_data.find(p => p.Name === name);
            }).filter(p => p);

            const traces = team_data.map(p => {
                const r_vals = stats.map(s => p[s]);
                r_vals.push(r_vals[0]);

                return {
                    "type": "scatterpolar",
                    "r": r_vals,
                    "theta": closed_stats,
                    "fill": "toself",
                    "name": p.Name,
                    "hoverinfo": "text",
                    "text": closed_stats.map((s, i) => s + ": " + r_vals[i])
                };
            });

            return {
                "data": traces,
                "layout": base_layout
            };
        },

        update_leaderboard_clientside: function (all_data, filter_store, stat_names, stat) {
            const filters = (filter_store && filter_store.filters) || {};
            const toggles = (filter_store && filter_store.toggles) || {};
            const stat_values = stat_names ? stat_names.map(name => filters["stat-" + name] || [0, 255]) : [];

            const filtered = window.dash_clientside.clientside.get_filtered_data(
                all_data,
                filters["region-filter"] || [],
                toggles["mega-toggle"] !== undefined ? toggles["mega-toggle"] : true,
                toggles["regional-toggle"] !== undefined ? toggles["regional-toggle"] : true,
                toggles["final-evolution-toggle"] || false,
                toggles["legendary-toggle"] !== undefined ? toggles["legendary-toggle"] : true,
                toggles["mythical-toggle"] !== undefined ? toggles["mythical-toggle"] : true,
                toggles["gmax-toggle"] || false,
                toggles["ultra-beast-toggle"] !== undefined ? toggles["ultra-beast-toggle"] : true,
                filters["type-filter"] || [],
                stat_values,
                stat_names
            );

            if (filtered.length === 0) {
                return {
                    "data": [],
                    "layout": {
                        "uirevision": true,
                        "paper_bgcolor": "rgba(0,0,0,0)",
                        "plot_bgcolor": "rgba(0,0,0,0)"
                    }
                };
            }

            const type_map = {};
            filtered.forEach(p => {
                const types = [p["Primary Type"]];
                if (p["Secondary Type"] && p["Secondary Type"] !== "None") {
                    types.push(p["Secondary Type"]);
                }
                types.forEach(t => {
                    if (!type_map[t]) type_map[t] = { sum: 0, count: 0 };
                    type_map[t].sum += p[stat];
                    type_map[t].count += 1;
                });
            });

            const averages = Object.keys(type_map).map(t => {
                return { type: t, avg: type_map[t].sum / type_map[t].count };
            }).sort((a, b) => b.avg - a.avg);

            const global_avg = filtered.reduce((acc, p) => acc + p[stat], 0) / filtered.length;
            const colors = averages.map(a => window.dash_clientside.clientside.TYPE_COLORS[a.type] || "#68A090");

            const trace = {
                "type": "bar",
                "x": averages.map(item => item.avg),
                "y": averages.map(item => item.type),
                "orientation": "h",
                "marker": { "color": colors },
                "text": averages.map(item => item.avg.toFixed(1)),
                "textposition": "auto",
                "textfont": { "color": "white" },
                "hovertemplate": "<b>%{y}</b><br>Avg " + stat + ": %{x:.1f}<extra></extra>"
            };

            const layout = {
                "uirevision": true,
                "title": { "text": "Top " + stat + " by Type", "font": { "color": "white" } },
                "xaxis": {
                    "title": { "text": stat, "font": { "color": "white" } },
                    "gridcolor": "rgba(255,255,255,0.1)",
                    "tickfont": { "size": 14, "color": "white" }
                },
                "yaxis": { "autorange": "reversed", "tickfont": { "size": 14, "color": "white" } },
                "paper_bgcolor": "rgba(0,0,0,0)",
                "plot_bgcolor": "rgba(0,0,0,0)",
                "transition": { "duration": 500, "easing": "cubic-in-out" },
                "margin": { "l": 80, "r": 20, "t": 40, "b": 40 },
                "shapes": [{
                    "type": "line",
                    "x0": global_avg, "x1": global_avg, "yref": "paper", "y0": 0, "y1": 1,
                    "line": { "color": "white", "dash": "dot", "width": 2 }
                }],
                "annotations": [{
                    "x": global_avg, "y": 0, "yref": "paper",
                    "text": "Global Avg: " + global_avg.toFixed(1),
                    "showarrow": false, "xanchor": "left", "yanchor": "bottom",
                    "font": { "color": "white", "size": 10 }
                }]
            };

            return { "data": [trace], "layout": layout };
        },

        update_scatter_clientside: function (all_data, filter_store, stat_names, x_stat, y_stat) {
            if (!x_stat || !y_stat) return {
                "data": [],
                "layout": {
                    "uirevision": true,
                    "title": { "text": "Select both axes to explore", "font": { "color": "white" } },
                    "paper_bgcolor": "rgba(0,0,0,0)",
                    "plot_bgcolor": "rgba(0,0,0,0)"
                }
            };

            const filters = (filter_store && filter_store.filters) || {};
            const toggles = (filter_store && filter_store.toggles) || {};
            const stat_values = stat_names ? stat_names.map(name => filters["stat-" + name] || [0, 255]) : [];

            const filtered = window.dash_clientside.clientside.get_filtered_data(
                all_data,
                filters["region-filter"] || [],
                toggles["mega-toggle"] !== undefined ? toggles["mega-toggle"] : true,
                toggles["regional-toggle"] !== undefined ? toggles["regional-toggle"] : true,
                toggles["final-evolution-toggle"] || false,
                toggles["legendary-toggle"] !== undefined ? toggles["legendary-toggle"] : true,
                toggles["mythical-toggle"] !== undefined ? toggles["mythical-toggle"] : true,
                toggles["gmax-toggle"] || false,
                toggles["ultra-beast-toggle"] !== undefined ? toggles["ultra-beast-toggle"] : true,
                filters["type-filter"] || [],
                stat_values,
                stat_names
            );

            if (filtered.length === 0) {
                return {
                    "data": [],
                    "layout": {
                        "uirevision": true,
                        "paper_bgcolor": "rgba(0,0,0,0)",
                        "plot_bgcolor": "rgba(0,0,0,0)"
                    }
                };
            }

            const types = [...new Set(filtered.map(p => p["Primary Type"]))];
            const traces = types.map(t => {
                const sub = filtered.filter(p => p["Primary Type"] === t);
                const color = window.dash_clientside.clientside.TYPE_COLORS[t] || "#68A090";
                return {
                    "type": "scattergl",
                    "x": sub.map(p => p[x_stat]),
                    "y": sub.map(p => p[y_stat]),
                    "mode": "markers",
                    "name": t,
                    "text": sub.map(p => p.Name),
                    "marker": {
                        "size": 10, "opacity": 0.7, "color": color,
                        "line": { "width": 1, "color": "white" }
                    },
                    "hovertemplate": "<b>%{text}</b><br>" + x_stat + ": %{x}<br>" + y_stat + ": %{y}<br>Primary Type: " + t + "<extra></extra>"
                };
            });

            return {
                "data": traces,
                "layout": {
                    "uirevision": true,
                    "template": "plotly_dark",
                    "xaxis": { "title": { "text": x_stat, "font": { "color": "white" } }, "gridcolor": "rgba(255,255,255,0.1)", "autorange": true, "tickfont": { "size": 14, "color": "white" } },
                    "yaxis": { "title": { "text": y_stat, "font": { "color": "white" } }, "gridcolor": "rgba(255,255,255,0.1)", "autorange": true, "tickfont": { "size": 14, "color": "white" } },
                    "legend": { "orientation": "h", "y": -0.2, "font": { "color": "white" }, "title": { "text": "Type", "font": { "color": "white" } } },
                    "paper_bgcolor": "rgba(0,0,0,0)",
                    "plot_bgcolor": "rgba(0,0,0,0)",
                    "transition": { "duration": 500, "easing": "cubic-in-out" },
                    "margin": { "l": 40, "r": 40, "t": 40, "b": 40 }
                }
            };
        },

        sync_filters_clientside: function (triggered_value, filter_store) {
            const ctx = window.dash_clientside.callback_context;
            if (!ctx || !ctx.triggered || ctx.triggered.length === 0) {
                return window.dash_clientside.no_update;
            }

            const trigger = ctx.triggered[0];
            const trigger_id = JSON.parse(trigger.prop_id.split('.')[0]);
            const filter_id = trigger_id.id;
            const value = trigger.value;

            // Deep copy and update store
            const new_store = JSON.parse(JSON.stringify(filter_store));
            new_store.filters[filter_id] = value;
            new_store.last_updated_id = filter_id;
            new_store.last_updated_value = value;
            new_store.modified = Date.now();

            // Return [sync_value, new_store]
            // This works for both Navbar -> Drawer and Drawer -> Navbar sync
            return [value, new_store];
        },

        sync_toggles_clientside: function (triggered_value, filter_store) {
            const ctx = window.dash_clientside.callback_context;
            if (!ctx || !ctx.triggered || ctx.triggered.length === 0) {
                return window.dash_clientside.no_update;
            }

            const trigger = ctx.triggered[0];
            const trigger_id = JSON.parse(trigger.prop_id.split('.')[0]);
            const toggle_id = trigger_id.id;
            const value = trigger.value;

            // Deep copy and update store
            const new_store = JSON.parse(JSON.stringify(filter_store));
            new_store.toggles[toggle_id] = value;
            new_store.last_updated_id = toggle_id;
            new_store.last_updated_value = value;
            new_store.modified = Date.now();

            return [value, new_store];
        },

        reset_filters_clientside: function (_n_clicks_nav, _n_clicks_drawer) {
            const stat_options = ["HP", "Attack", "Defense", "Speed", "Special Defense", "Special Attack"];
            const filters = {
                "region-filter": [],
                "type-filter": [],
                "sort-order": "number",
                "trainer-height": 4.5,
                "trainer-weight": 150
            };
            stat_options.forEach(stat => {
                filters[`stat-${stat}`] = [0, 255];
            });

            const toggles = {
                "mega-toggle": true,
                "regional-toggle": true,
                "final-evolution-toggle": false,
                "legendary-toggle": true,
                "mythical-toggle": true,
                "gmax-toggle": false,
                "ultra-beast-toggle": true
            };

            const store_defaults = {
                "filters": filters,
                "toggles": toggles,
                "modified": Date.now(),
                "last_updated_id": null,
                "last_updated_value": null
            };

            const filter_values = [
                filters["region-filter"],
                filters["type-filter"],
                filters["sort-order"],
                filters["trainer-height"],
                filters["trainer-weight"],
                ...stat_options.map(s => filters[`stat-${s}`])
            ];

            const toggle_values = [
                toggles["mega-toggle"],
                toggles["regional-toggle"],
                toggles["final-evolution-toggle"],
                toggles["legendary-toggle"],
                toggles["mythical-toggle"],
                toggles["gmax-toggle"],
                toggles["ultra-beast-toggle"]
            ];

            const group_defaults = [...filter_values, ...toggle_values];
            return [...group_defaults, ...group_defaults, store_defaults];
        },

        // Update team store in the browser — no server round-trip needed.
        // Reads window.dash_clientside.callback_context.triggered to determine the action.
        update_team: function (add_clicks, clear_clicks, remove_clicks, focus_pokemon, current_team) {
            const ctx = window.dash_clientside.callback_context;
            if (!ctx || !ctx.triggered || ctx.triggered.length === 0) {
                return window.dash_clientside.no_update;
            }

            const prop_id = ctx.triggered[0].prop_id || "";

            // Clear team
            if (prop_id === "clear-team-btn.n_clicks") {
                return [];
            }

            // Add Pokémon
            if (prop_id === "add-pokemon-btn.n_clicks") {
                if (!focus_pokemon) return window.dash_clientside.no_update;
                const team = current_team ? [...current_team] : [];
                if (!team.includes(focus_pokemon) && team.length < 6) {
                    team.push(focus_pokemon);
                }
                return team;
            }

            // Remove individual Pokémon (pattern-matched id)
            if (prop_id.includes("remove-team")) {
                try {
                    // prop_id format: '{"name":"Pikachu","type":"remove-team"}.n_clicks'
                    const id_str = prop_id.replace(".n_clicks", "");
                    const id_obj = JSON.parse(id_str);
                    const name = id_obj.name;
                    const team = current_team ? [...current_team] : [];
                    return team.filter(p => p !== name);
                } catch (e) {
                    return window.dash_clientside.no_update;
                }
            }

            return window.dash_clientside.no_update;
        }
    }
});
