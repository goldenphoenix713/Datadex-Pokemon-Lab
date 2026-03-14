
> Dash Mantine Components v2.6.0 Documentation for MultiSelect
> See complete docs at <https://www.dash-mantine-components.com/assets/llms.txt>  
> All relative links in this file should be resolved against <https://www.dash-mantine-components.com>

## MultiSelect  

MultiSelect enables users to select multiple options in a dropdown.  
Category: Combobox  

### Made with Combobox

`MultiSelect` is built on top of [Combobox](https://mantine.dev/core/combobox/) and covers common use cases. If you need more advanced behavior or want to extend
its functionality, you can create your own custom `MultiSelect` component. See this [GitHub repository](https://github.com/AnnMarieW/dmc_custom_components) for custom DMC component examples.

### Simple Example

MultiSelect component allows user to pick any number of option from the given data.
If you would like users to be able to enter custom values, see `TagsInput`.

```python
import dash_mantine_components as dmc
from dash import Output, Input, html, callback

component = html.Div(
    [
        dmc.MultiSelect(
            label="Select your favorite libraries",
            placeholder="Select all you like!",
            id="framework-multi-select",
            value=["pd", "torch"],
            data=[
                {"value": "pd", "label": "Pandas"},
                {"value": "np", "label": "NumPy"},
                {"value": "tf", "label": "TensorFlow"},
                {"value": "torch", "label": "PyTorch"},
            ],
            w=400,
            mb=10,
        ),
        dmc.Text(id="multi-selected-value"),
    ]
)


@callback(
    Output("multi-selected-value", "children"), Input("framework-multi-select", "value")
)
def select_value(value):
    return ", ".join(value)
```

### Data Format

The data can be provided as either:

* an array of strings - use when label and value are same.
* an array of dicts with `label` and `value` properties.
* an array of dict with `group` and `items` as keys where items are one of the previous two types.

```python
data = ["Pandas", "NumPy", "TensorFlow", "PyTorch"]

# or

data = [
    {"value": "Pandas", "label": "Pandas"},
    {"value": "NumPy", "label": "NumPy"},
    {"value": "TensorFlow", "label": "TensorFlow"},
    {"value": "PyTorch", "label": "PyTorch"},
]

# or

data = [
    {"group": "Data Analysis", "items": ["Pandas", "NumPy"]},
    {"group": "Deep Learning", "items": ["TensorFlow", "Pytorch"]}
]

# or

data = [
    {
        "group": "Data Analysis",
        "items": [
            {"value": "Pandas", "label": "Pandas"},
            {"value": "NumPy", "label": "NumPy"},
        ],
    },
    {
        "group": "Deep Learning",
        "items": [
            {"value": "TensorFlow", "label": "TensorFlow"},
            {"value": "PyTorch", "label": "PyTorch"},
        ],
    },
]
```

### Clearable

Set `clearable` prop to display the clear button in the right section. The button is not displayed when:

* The component does not have a value
* The component is disabled
* The component is read only

```python
import dash_mantine_components as dmc

component = dmc.MultiSelect(
    label="Select your favorite library",
    placeholder="Select all you like!",
    value=["Pandas", "TensorFlow"],
    data=["Pandas", "NumPy", "TensorFlow", "PyTorch"],
    clearable=True,
    w=400,
    mb=180,
)
```

### Searchable

Set `searchable` prop to allow filtering options by user input.

```python
import dash_mantine_components as dmc

component = dmc.MultiSelect(
    label="Pick your favorite libraries",
    data=["Pandas", "NumPy", "TensorFlow", "PyTorch"],
    searchable=True,
    w=400,
)
```

### Nothing Found

Set the `nothingFoundMessage` prop to display a given message when no options match the search query or there is
no data available. If the `nothingFoundMessage` prop is not set, the `MultiSelect` dropdown will be hidden.

```python
import dash_mantine_components as dmc

component = dmc.MultiSelect(
    label="Pick your favorite libraries",
    data=["Pandas", "NumPy", "TensorFlow", "PyTorch"],
    searchable=True,
    nothingFoundMessage="Nothing found...",
    w=400,
)
```

### Clear search on change

Set the `clearSearchOnChange=False` to enable selecting multiple items using the same search query.

```python
import dash_mantine_components as dmc

component = dmc.MultiSelect(
    data=["aa", "ab", "ac", "ba", "bb", "bc"],
    value=["aa"],
    searchable=True,
    clearSearchOnChange=False
)
```

### Checked option icon

Set `checkIconPosition` prop to `left` or `right` to control position of check icon in active option.
To remove the check icon, set `withCheckIcon=False`.

```python
import dash_mantine_components as dmc

component = dmc.MultiSelect(
    label="Control check icon",
    data=["Pandas", "NumPy", "TensorFlow", "PyTorch"],
    value=["Pandas", "NumPy"],
    checkIconPosition="right",
    dropdownOpened=True,
    w=400,
    pb=150,
    id="multi-select-check-icon",
    comboboxProps={"withinPortal": False}

)
```

### Max Selected Values

You can limit the number of selected values with `maxValues` prop. This will not allow adding more values
once the limit is reached.

```python
import dash_mantine_components as dmc

component = dmc.MultiSelect(
    label="Select your favorite",
    description="You can select a maximum of 3 frameworks.",
    data=["Pandas", "NumPy", "TensorFlow", "PyTorch"],
    maxValues=3,
    w=400,
)
```

### Hide selected options

To remove selected options from the list of available options, set `hidePickedOptions` prop:

```python
import dash_mantine_components as dmc

component = dmc.MultiSelect(
    label="Select your favorite libraries",
    placeholder="Select all you like!",
    hidePickedOptions=True,
    value=["Pandas", "TensorFlow"],
    data=["Pandas", "NumPy", "TensorFlow", "PyTorch"],
    w=400,
    mb=140,
    dropdownOpened=True,
    comboboxProps={"withinPortal":False}
)
```

### Large Data Sets

The best strategy for large data sets is to limit the number of options that are rendered at the same time. You can
do it with limit prop.

Example of `MultiSelect` with 100 000 options, 10 options are rendered at the same time:

```python
import dash_mantine_components as dmc

component = dmc.MultiSelect(
    label="100,000 options",
    data=[f"Option {i}" for i in range(100000)],
    placeholder="use limit to optimize performance",
    limit=10,
    searchable=True,
    w=400,
)
```

### renderOption

`renderOption` function allows you to customize option rendering.

Note: This example uses custom JavaScript defined in the assets folder. Learn more in the "Functions As Props" section of this document.

```python
import dash_mantine_components as dmc

users_data = {
    "Emily Johnson": {
        "image": "https://raw.githubusercontent.com/mantinedev/mantine/master/.demo/avatars/avatar-7.png",
        "email": "emily92@gmail.com",
    },
    "Ava Rodriguez": {
        "image": "https://raw.githubusercontent.com/mantinedev/mantine/master/.demo/avatars/avatar-8.png",
        "email": "ava_rose@gmail.com",
    },
    "Olivia Chen": {
        "image": "https://raw.githubusercontent.com/mantinedev/mantine/master/.demo/avatars/avatar-4.png",
        "email": "livvy_globe@gmail.com",
    },
    "Ethan Barnes": {
        "image": "https://raw.githubusercontent.com/mantinedev/mantine/master/.demo/avatars/avatar-1.png",
        "email": "ethan_explorer@gmail.com",
    },
    "Mason Taylor": {
        "image": "https://raw.githubusercontent.com/mantinedev/mantine/master/.demo/avatars/avatar-2.png",
        "email": "mason_musician@gmail.com",
    },
}

component = dmc.MultiSelect(
    data=list(users_data.keys()),
    label="Employees of the month",
    placeholder="Search for employee",
    maxDropdownHeight=300,
    searchable=True,
    hidePickedOptions=True,
    renderOption={
        "function": "renderUserOption",
        "options": {"users": users_data},
    },
)
```

```javascript
var dmcfuncs = window.dashMantineFunctions = window.dashMantineFunctions || {};
var dmc = window.dash_mantine_components;

dmcfuncs.renderUserOption = function ({ option }, { users }) {
  const user = users[option.value];

  return React.createElement(
    dmc.Group,
    { gap: "sm" },
    React.createElement(dmc.Avatar, {
      key: "avatar",
      src: user.image,
      size: 36,
      radius: "xl",
    }),
    React.createElement(
      "div",
      { key: "text-block" },
      React.createElement(dmc.Text, { size: "sm", key: "name" }, option.value),
      React.createElement(dmc.Text, {
        size: "xs",
        opacity: 0.5,
        key: "email",
        children: user.email,
      })
    )
  );
};
```

### Options filtering

By default, `MultiSelect` filters options by checking if the option label contains input value. You can change this behavior
with `filter`. The filter function receives an object with the following properties as a single argument:

* `options` – array of options or options groups, all options are in `{ value: string; label: string; disabled?: boolean }` format
* `search` – current search query
* `limit` – value of limit prop passed to `Select`

Note: This example uses custom JavaScript defined in the assets folder. Learn more in the "Functions As Props" section of this document.

Example of a custom filter function that matches options by words instead of letters sequence:

```python
import dash_mantine_components as dmc

component = dmc.MultiSelect(
    label="Your country",
    placeholder="Pick value",
    searchable=True,
    data=[
        "Great Britain",
        "Canada",
        "United States",
    ],
    filter={"function": "filterCountries"},
)
```

```javascript
var dmcfuncs = window.dashMantineFunctions = window.dashMantineFunctions || {};

dmcfuncs.filterCountries = function ({ options, search }) {
  const queryWords = search.toLowerCase().trim().split(" ");
  return options.filter((option) => {
    const words = option.label.toLowerCase().trim().split(" ");
    return queryWords.every((word) =>
      words.some((labelWord) => labelWord.includes(word))
    );
  });
};
```

### Sort options

By default, options are sorted by their position in the data array. You can change this behavior with `filter` function:

Note: This example uses custom JavaScript defined in the assets folder. Learn more in the "Functions As Props" section of this document.

```python
import dash_mantine_components as dmc

component = dmc.MultiSelect(
    label="Your favorite Python library",
    placeholder="Pick value",
    searchable=True,
    nothingFoundMessage="Nothing found...",
    data=[
        "4 – NumPy",
        "1 – Pandas",
        "3 – Scikit-learn",
        "2 – Plotly",
    ],
    filter={"function": "filterPythonLibs"},
)
```

```javascript
var dmcfuncs = window.dashMantineFunctions = window.dashMantineFunctions || {};

dmcfuncs.filterPythonLibs = function ({ options, search }) {
  const query = search.toLowerCase().trim();
  const result = options.filter((option) =>
    option.label.toLowerCase().trim().includes(query)
  );
  result.sort((a, b) => a.label.localeCompare(b.label));
  return result;
};
```

### Scrollable dropdown

By default, the options list is wrapped with `ScrollArea.Autosize`. You can control dropdown max-height with
`maxDropdownHeight` prop if you do not change the default settings.

If you want to use native scrollbars, set `withScrollArea=False`. Note that in this case, you will need to change
dropdown styles with `Styles API`.

```python
import dash_mantine_components as dmc

component = dmc.Paper(
    [
        dmc.MultiSelect(
            label="Scrollable dropdown",
            data=[f"Option {i}" for i in range(100)],
            placeholder="Pick value",
            maxDropdownHeight=300,
            w=400,
        ),
        dmc.MultiSelect(
            label="With native scroll",
            data=[f"Option {i}" for i in range(100)],
            placeholder="Pick value",
            withScrollArea=False,
            styles={"dropdown": {"maxHeight": 200, "overflowY": "auto"}},
            w=400,
            mt="md",
        ),
    ]
)
```

### Grouping

```python
import dash_mantine_components as dmc

component = dmc.MultiSelect(
    data=[
        {
            "group": "Data Analysis",
            "items": [
                {"value": "Pandas", "label": "Pandas"},
                {"value": "NumPy", "label": "NumPy"},
            ],
        },
        {
            "group": "Deep Learning",
            "items": [
                {"value": "TensorFlow", "label": "TensorFlow"},
                {"value": "PyTorch", "label": "PyTorch"},
            ],
        },
    ],
    w=400,
)
```

### Combobox props

You can override `Combobox` props with `comboboxProps`. It is useful when you need to change some of the props that are
not exposed by `MultiSelect`, for example `withinPortal`:

```python
dmc.MultiSelect(comboboxProps={"withinPortal": False})
```

### Change dropdown z-index

```python
dmc.MultiSelect(comboboxProps={"zIndex": 1000})
```

### Inside Popover

To use MultiSelect inside popover, you need to set `withinPortal=False`:

```python
import dash_mantine_components as dmc

component = dmc.Popover(
    width=300,
    position="bottom",
    withArrow=True,
    shadow="md",
    children=[
        dmc.PopoverTarget(dmc.Button("Toggle Popover")),
        dmc.PopoverDropdown(
            dmc.MultiSelect(
                label="Your favorite libraries",
                placeholder="Pick values",
                data=["Pandas", "NumPy", "TensorFlow", "PyTorch"],
                comboboxProps={"withinPortal": False},
            )
        ),
    ],
)
```

### Dropdown open in a callback

```python
import dash_mantine_components as dmc
from dash import Output, Input, html, callback

component = html.Div(
    [
        dmc.Button("Toggle dropdown", id="btn-multi-select-opened", n_clicks=0),
        dmc.MultiSelect(
            label="Select your favorite libraries",
            placeholder="Select all you like!",
            id="multi-select-opened",
            value=["pd", "torch"],
            data=[
                {"value": "pd", "label": "Pandas"},
                {"value": "np", "label": "NumPy"},
                {"value": "tf", "label": "TensorFlow"},
                {"value": "torch", "label": "PyTorch"},
            ],
            comboboxProps={"position": "bottom", "middlewares": {"flip": False, "shift": False}},
            w=400,
            mb=10,
        ),
    ]
)


@callback(
    Output("multi-select-opened", "dropdownOpened"),
    Input("btn-multi-select-opened", "n_clicks"),
)
def select_value(n):
    if n % 2 == 0:
        return False
    return True
```

### Dropdown position

By default, the dropdown is displayed below the input if there is enough space; otherwise it is displayed above the
input. You can change this behavior by setting `position` and `middlewares` props, which are passed down to the
underlying `Popover` component.

Example of dropdown that is always displayed above the input:

```python
import dash_mantine_components as dmc

component = dmc.MultiSelect(
    label="Your favorite libraries",
    placeholder="Pick values",
    data=["Pandas", "NumPy", "TensorFlow", "PyTorch"],
    comboboxProps={"position": "top", "middlewares": {"flip": False, "shift": False}},
)
```

### Dropdown width

To change dropdown width, set `width` prop in `comboboxProps`. By default, dropdown width is equal to the input width.

```python
import dash_mantine_components as dmc

component = dmc.MultiSelect(
    label="Your favorite libraries",
    placeholder="Pick values",
    data=["Pandas", "NumPy", "TensorFlow", "PyTorch"],
    comboboxProps={"position": "bottom-start", "width": 200},
)
```

### Dropdown offset

To change dropdown offset, set `offset` prop in `comboboxProps`:  

```python
import dash_mantine_components as dmc

component = dmc.MultiSelect(
    label="Your favorite libraries",
    placeholder="Pick values",
    data=["Pandas", "NumPy", "TensorFlow", "PyTorch"],
    comboboxProps={
        "position": "bottom",
        "middlewares": {"flip": False, "shift": False},
        "offset": 0,
    },
)
```

### Dropdown animation

By default, dropdown animations are disabled. To enable them, you can set `transitionProps`, which will be passed
down to the underlying `Transition` component.

```python
import dash_mantine_components as dmc

component = dmc.MultiSelect(
    label="Your favorite libraries",
    placeholder="Pick values",
    data=["Pandas", "NumPy", "TensorFlow", "PyTorch"],
    comboboxProps={"transitionProps": {"transition": "pop", "duration": 200}},
)
```

### Dropdown padding

```python
import dash_mantine_components as dmc

component = dmc.Paper(
    [
        dmc.MultiSelect(
            label="Zero padding",
            data=["Pandas", "NumPy", "TensorFlow", "PyTorch"],
            placeholder="Pick value",
            comboboxProps={"dropdownPadding": 0},
            w=400,
        ),
        dmc.MultiSelect(
            label="10px padding",
            data=["Pandas", "NumPy", "TensorFlow", "PyTorch"],
            placeholder="Pick value",
            comboboxProps={"dropdownPadding": 10},
            w=400,
            mt="md",
        ),
    ]
)
```

### Dropdown shadow

```python
import dash_mantine_components as dmc

component = dmc.MultiSelect(
    label="Your favorite libraries",
    placeholder="Pick values",
    data=["Pandas", "NumPy", "TensorFlow", "PyTorch"],
    comboboxProps={"shadow": "md"},
)
```

### Left and right sections

`MultiSelect` supports `leftSection` and `rightSection` props. These sections are rendered with absolute position
inside the input wrapper. You can use them to display icons, input controls or any other elements.

You can use the following props to control sections styles and content:

* `rightSection`/`leftSection` – component to render on the corresponding side of input
* `rightSectionWidth`/`leftSectionWidth` – controls width of the right section and padding on the corresponding side of the input. By default, it is controlled by component size prop.
* `rightSectionPointerEvents`/`leftSectionPointerEvents` – controls pointer-events property of the section. If you want to render a non-interactive element, set it to none to pass clicks through to the input.

```python
import dash_mantine_components as dmc
from dash_iconify import DashIconify

component = dmc.Paper(
    [
        dmc.MultiSelect(
            label="Your favorite libraries",
            data=["Pandas", "NumPy", "TensorFlow", "PyTorch"],
            placeholder="Pick values",
            leftSectionPointerEvents="none",
            leftSection=DashIconify(icon="bi-book"),
            w=400,
        ),
        dmc.MultiSelect(
            label="Your favorite libraries",
            data=["Pandas", "NumPy", "TensorFlow", "PyTorch"],
            placeholder="Pick values",
            rightSectionPointerEvents="none",
            rightSection=DashIconify(icon="bi-book"),
            w=400,
            mt="md",
        ),
    ]
)
```

### Invalid State And Error

You can let the user know if the selected value is invalid. In the example below, you will get an error message if you
select less than 2 currency pairs.

```python
import dash_mantine_components as dmc
from dash import Output, Input, callback

component = dmc.MultiSelect(
    data=["USDINR", "EURUSD", "USDTWD", "USDJPY"],
    id="multi-select-error",
    value=["USDJPY"],
    w=400,
)


@callback(Output("multi-select-error", "error"), Input("multi-select-error", "value"))
def select_value(value):
    return "Select at least 2." if len(value) < 2 else ""
```

### Input Props

`MultiSelect` component supports `Input` and Input Wrapper components features and all input element props.
`MultiSelect` documentation does not include all features supported by the component – see Input documentation to learn about all available features.

### Removing placeholder after values selected

`MultiSelect` component uses placeholder to indicate that there are values available for selection. It is different
from `Select` component where placeholder is removed when value is selected – user can select only one value.

You can use CSS to remove the placeholder in the `MultiSelect` component when values are selected:

```python
import dash_mantine_components as dmc
from dash_iconify import DashIconify

component = dmc.Paper(
    [
        dmc.MultiSelect(
            label="Default Placeholder",
            data=["Pandas", "NumPy", "TensorFlow", "PyTorch"],
            placeholder="Pick values",
            value=["Pandas"],
            w=400,
        ),
        dmc.MultiSelect(
            label="Placeholder removed when values are selected",
            data=["Pandas", "NumPy", "TensorFlow", "PyTorch"],
            placeholder="Pick values",
            value=["Pandas"],
            className="dmc-docs-demo",
            w=400,
            mt="md",
        ),
    ]
)
```

```css
.dmc-docs-demo .mantine-MultiSelect-inputField {
  &:not(:only-child)::placeholder {
    color: transparent;
  }
}
```

### Dash 4 dcc.Dropdown

The Dash 4 [dcc.Dropdown](https://dash.plotly.com/dash-core-components/dropdown) supports some features that are not
available in DMC.  For example, virtualization, which renders only the visible options instead of the entire list. This improves performance and responsiveness when working
with large data sets. It also includes a search input and Select all / Deselect all buttons inside the dropdown menu.
When `multi=True`, it displays a count of selected items, preventing the input from resizing as selections grow.

The `dmc.InputWrapper` can be used to add elements like `label`, `description`, and `error` to the `dcc.Dropdown`,
making it consistent with the other DMC inputs. The `htmlFor` prop links the label to the component for focus and accessibility.

To style the `dcc.Dropdown` with a Mantine theme see the   [Dash 4 components](/dash4-components) section.

```python
from dash import dcc
import dash_mantine_components as dmc

component = dmc.InputWrapper(
    dcc.Dropdown([f"option {i}" for i in range(100)],  value=["option 1", "option 2", "option 3"], multi=True, id="dcc4-dropdown"),
    label="dcc.Dropdown with a dmc.InputWrapper",
    htmlFor="dcc4-dropdown",
    className="dmc"  # styles with Mantine theme
)
```

### Styles API

This component supports Styles API. With Styles API, you can customize styles of any inner element. See the Styling and Theming sections of these docs for more information.

| Name        | Static selector                  | Description                                      |
|:------------|:---------------------------------|:-------------------------------------------------|
| wrapper     | .mantine-MultiSelect-wrapper     | Root element of the Input                        |
| input       | .mantine-MultiSelect-input       | Input element                                    |
| section     | .mantine-MultiSelect-section     | Left and right sections                          |
| root        | .mantine-MultiSelect-root        | Root element                                     |
| label       | .mantine-MultiSelect-label       | Label element                                    |
| required    | .mantine-MultiSelect-required    | Required asterisk element, rendered inside label |
| description | .mantine-MultiSelect-description | Description element                              |
| error       | .mantine-MultiSelect-error       | Error element                                    |
| dropdown    | .mantine-MultiSelect-dropdown    | Dropdown root element                            |
| options     | .mantine-MultiSelect-options     | Options wrapper                                  |
| option      | .mantine-MultiSelect-option      | Option                                           |
| empty       | .mantine-MultiSelect-empty       | Nothing found message                            |
| group       | .mantine-MultiSelect-group       | Options group wrapper                            |
| groupLabel  | .mantine-MultiSelect-groupLabel  | Options group label                              |
| pill        | .mantine-MultiSelect-pill        | Value pill                                       |
| inputField  | .mantine-MultiSelect-inputField  | Input field                                      |
| pillsList   | .mantine-MultiSelect-pillsList   | List of pills, also contains input field         |

### Keyword Arguments

#### MultiSelect

* id (string; optional):
    Unique ID to identify this component in Dash callbacks.

* aria-* (string; optional):
    Wild card aria attributes.

* attributes (boolean | number | string | dict | list; optional):
    Passes attributes to inner elements of a component.  See Styles
    API docs.

* checkIconPosition (a value equal to: 'left', 'right'; optional):
    Position of the check icon relative to the option label, `'left'`
    by default.

* className (string; optional):
    Class added to the root element, if applicable.

* classNames (dict; optional):
    Adds custom CSS class names to inner elements of a component.  See
    Styles API docs.

* clearButtonProps (dict; optional):
    Props passed down to the clear button.

    `clearButtonProps` is a dict with keys:

* clearSearchOnChange (boolean; optional):
    Clear search value when item is selected. Default True.

* clearable (boolean; optional):
    Determines whether the clear button should be displayed in the
    right section when the component has value, `False` by default.

* comboboxProps (dict; optional):
    Props passed down to `Combobox` component.

    `comboboxProps` is a dict with keys:

* darkHidden (boolean; optional):
    Determines whether component should be hidden in dark color scheme
    with `display: none`.

* data (list of strings; optional):
    Data used to generate options.

* data-* (string; optional):
    Wild card data attributes.

* debounce (number | boolean; default False):
    (boolean | number; default False): If True, changes to input will
    be sent back to the Dash server only on enter or when losing
    focus. If it's False, it will send the value back on every change.
    If a number, it will not send anything back to the Dash server
    until the user has stopped typing for that number of milliseconds.

* description (a list of or a singular dash component, string or number; optional):
    Contents of `Input.Description` component. If not set, description
    is not rendered.

* descriptionProps (dict with strings as keys and values of type boolean | number | string | dict | list; optional):
    Props passed down to the `Input.Description` component.

* disabled (boolean; optional):
    Sets `disabled` attribute on the `input` element.

* dropdownOpened (boolean; optional):
    Controlled dropdown opened state.

* error (a list of or a singular dash component, string or number; optional):
    Contents of `Input.Error` component. If not set, error is not
    rendered.

* errorProps (dict with strings as keys and values of type boolean | number | string | dict | list; optional):
    Props passed down to the `Input.Error` component.

* filter (boolean | number | string | dict | list; optional):
    A Function based on which items are filtered and sorted. See
    <https://www.dash-mantine-components.com/functions-as-props>.

* hiddenFrom (string; optional):
    Breakpoint above which the component is hidden with `display:
    none`.

* hiddenInputProps (dict; optional):
    Props passed down to the hidden input.

* hiddenInputValuesDivider (string; optional):
    Divider used to separate values in the hidden input `value`
    attribute, `','` by default.

* hidePickedOptions (boolean; optional):
    Determines whether picked options should be removed from the
    options list, `False` by default.

* inputProps (dict with strings as keys and values of type boolean | number | string | dict | list; optional):
    Props passed down to the `Input` component.

* inputWrapperOrder (list of a value equal to: 'label', 'description', 'error', 'input's; optional):
    Controls order of the elements, `['label', 'description', 'input',
    'error']` by default.

* label (a list of or a singular dash component, string or number; optional):
    Contents of `Input.Label` component. If not set, label is not
    rendered.

* labelProps (dict with strings as keys and values of type boolean | number | string | dict | list; optional):
    Props passed down to the `Input.Label` component.

* leftSection (a list of or a singular dash component, string or number; optional):
    Content section rendered on the left side of the input.

* leftSectionPointerEvents (a value equal to: 'auto', '-moz-initial', 'inherit', 'initial', 'revert', 'revert-layer', 'unset', 'none', 'all', 'fill', 'painted', 'stroke', 'visible', 'visibleFill', 'visiblePainted', 'visibleStroke'; optional):
    Sets `pointer-events` styles on the `leftSection` element,
    `'none'` by default.

* leftSectionProps (dict; optional):
    Props passed down to the `leftSection` element.

* leftSectionWidth (string | number; optional):
    Left section width, used to set `width` of the section and input
    `padding-left`, by default equals to the input height.

* lightHidden (boolean; optional):
    Determines whether component should be hidden in light color
    scheme with `display: none`.

* limit (number; optional):
    Maximum number of options displayed at a time, `Infinity` by
    default.

* loading_state (dict; optional):
    Object that holds the loading state object coming from
    dash-renderer. For use with dash<3.

    `loading_state` is a dict with keys:

* maxDropdownHeight (string | number; optional):
    `max-height` of the dropdown, only applicable when
    `withScrollArea` prop is `True`, `250` by default.

* maxValues (number; optional):
    Maximum number of values, `Infinity` by default.

* mod (string | dict | list of string | dicts; optional):
    Element modifiers transformed into `data-` attributes. For
    example: "xl" or {"data-size": "xl"}. Can also be a list of
    strings or dicts for multiple modifiers. Falsy values are removed.

* n_blur (number; default 0):
    An integer that represents the number of times that this element
    has lost focus.

* n_submit (number; default 0):
    An integer that represents the number of times that this element
    has been submitted.

* name (string; optional):
    Name prop.

* nothingFoundMessage (a list of or a singular dash component, string or number; optional):
    Message displayed when no option matched current search query,
    only applicable when `searchable` prop is set.

* openOnFocus (boolean; optional):
    If set, the dropdown opens when the input receives focus default
    `True`.

* persisted_props (list of strings; optional):
    Properties whose user interactions will persist after refreshing
    the component or the page. Since only `value` is allowed this prop
    can normally be ignored.

* persistence (string | number | boolean; optional):
    Used to allow user interactions in this component to be persisted
    when the component - or the page - is refreshed. If `persisted` is
    truthy and hasn't changed from its previous value, a `value` that
    the user has changed while using the app will keep that change, as
    long as the new `value` also matches what was given originally.
    Used in conjunction with `persistence_type`. Note:  The component
    must have an `id` for persistence to work.

* persistence_type (a value equal to: 'local', 'session', 'memory'; optional):
    Where persisted user changes will be stored: memory: only kept in
    memory, reset on page refresh. local: window.localStorage, data is
    kept after the browser quit. session: window.sessionStorage, data
    is cleared once the browser quit.

* placeholder (string; optional):
    Placeholder.

* pointer (boolean; optional):
    Determines whether the input should have `cursor: pointer` style,
    `False` by default.

* radius (number; optional):
    Key of `theme.radius` or any valid CSS value to set
    `border-radius`, numbers are converted to rem,
    `theme.defaultRadius` by default.

* readOnly (boolean; optional):
    Readonly.

* renderOption (boolean | number | string | dict | list; optional):
    A function to render content of the option, replaces the default
    content of the option.  See
    <https://www.dash-mantine-components.com/functions-as-props>.

* required (boolean; optional):
    Adds required attribute to the input and a red asterisk on the
    right side of label, `False` by default.

* rightSection (a list of or a singular dash component, string or number; optional):
    Content section rendered on the right side of the input.

* rightSectionPointerEvents (a value equal to: 'auto', '-moz-initial', 'inherit', 'initial', 'revert', 'revert-layer', 'unset', 'none', 'all', 'fill', 'painted', 'stroke', 'visible', 'visibleFill', 'visiblePainted', 'visibleStroke'; optional):
    Sets `pointer-events` styles on the `rightSection` element,
    `'none'` by default.

* rightSectionProps (dict; optional):
    Props passed down to the `rightSection` element.

* rightSectionWidth (string | number; optional):
    Right section width, used to set `width` of the section and input
    `padding-right`, by default equals to the input height.

* scrollAreaProps (dict; optional):
    Props passed down to the underlying `ScrollArea` component in the
    dropdown.

    `scrollAreaProps` is a dict with keys:

* searchValue (string; optional):
    Controlled search value.

* searchable (boolean; optional):
    Determines whether the select should be searchable, `False` by
    default.

* selectFirstOptionOnChange (boolean; optional):
    Determines whether the first option should be selected when value
    changes, `False` by default.

* selectFirstOptionOnDropdownOpen (boolean; optional):
    If set, the first option is selected when dropdown opens, `False`
    by default.

* size (optional):
    Controls input `height` and horizontal `padding`, `'sm'` by
    default.

* styles (boolean | number | string | dict | list; optional):
    Adds inline styles directly to inner elements of a component.  See
    Styles API docs.

* tabIndex (number; optional):
    tab-index.

* value (list of strings; optional):
    Controlled component value.

* variant (string; optional):
    variant.

* visibleFrom (string; optional):
    Breakpoint below which the component is hidden with `display:
    none`.

* withAlignedLabels (boolean; optional):
    If set, unchecked labels are aligned with the checked one
    @,default,`False`.

* withAsterisk (boolean; optional):
    Determines whether the required asterisk should be displayed.
    Overrides `required` prop. Does not add required attribute to the
    input. `False` by default.

* withCheckIcon (boolean; optional):
    Determines whether check icon should be displayed near the
    selected option label, `True` by default.

* withErrorStyles (boolean; optional):
    Determines whether the input should have red border and red text
    color when the `error` prop is set, `True` by default.

* withScrollArea (boolean; optional):
    Determines whether the options should be wrapped with
    `ScrollArea.AutoSize`, `True` by default.

* wrapperProps (dict with strings as keys and values of type boolean | number | string | dict | list; optional):
    Props passed down to the root element.
