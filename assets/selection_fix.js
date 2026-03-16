/**
 * Automatically selects the text in the Pokemon selector input when it gains focus.
 * This emulates the 'selectOnFocus' behavior which is not natively supported in DMC 2.6.0.
 */
document.addEventListener('focusin', function (event) {
    const target = event.target;
    if (target && target.id === 'focus-selector') {
        const selectAll = () => {
            if (target.setSelectionRange) {
                target.setSelectionRange(0, target.value.length);
            } else if (target.select) {
                target.select();
            }
        };

        // Execute immediately and then after small delays to fight internal component logic
        selectAll();
        setTimeout(selectAll, 50);
        setTimeout(selectAll, 150);
    }
}, true);
