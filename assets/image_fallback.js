// Global event listener for image loading errors
document.addEventListener('error', function (event) {
    if (event.target.tagName.toLowerCase() !== 'img') return;

    // Check for artwork vs sprites
    if (event.target.classList.contains('pokemon-artwork')) {
        if (!event.target.src.includes('missing_artwork.png')) {
            console.log('Falling back to full artwork missing placeholder');
            event.target.src = '/assets/images/missing_artwork.png';
        }
    } else if (event.target.classList.contains('pokemon-sprite') || event.target.closest('.custom-dropdown')) {
        // Fallback for small sprites - revert to original pokeball placeholder
        if (!event.target.src.includes('pokeball_placeholder.png')) {
            console.log('Falling back to pokeball sprite placeholder');
            event.target.src = '/assets/sprites/pokeball_placeholder.png';
        }
    }
}, true);

// Unified state management for the artwork loading indicator
function updateLoaderState(img) {
    const container = img.closest('.artwork-container');
    if (!container) return;

    const isPlaceholder = img.src.indexOf('loading_artwork.png') !== -1;

    if (isPlaceholder) {
        container.classList.add('is-loading');
        console.log('Loader state: ACTIVE (placeholder)');
    } else if (img.complete && img.naturalWidth > 0) {
        // Image is already loaded and has valid dimensions
        container.classList.remove('is-loading');
        console.log('Loader state: HIDDEN (complete)');
    } else {
        // Image is still loading
        container.classList.add('is-loading');
        console.log('Loader state: ACTIVE (fetching)');
    }
}

// Safety fallback: Periodically ensure completed images don't show loaders
setInterval(() => {
    document.querySelectorAll('.pokemon-artwork').forEach(img => {
        if (img.complete && img.naturalWidth > 0 && img.src.indexOf('loading_artwork.png') === -1) {
            img.closest('.artwork-container')?.classList.remove('is-loading');
        }
    });
}, 500);

// Global event listeners for image lifecycle
document.addEventListener('load', function (event) {
    if (event.target && event.target.classList && event.target.classList.contains('pokemon-artwork')) {
        updateLoaderState(event.target);
    }
}, true);

document.addEventListener('error', function (event) {
    if (event.target && event.target.classList && event.target.classList.contains('pokemon-artwork')) {
        updateLoaderState(event.target);
    }
}, true);

// Monitor for new artwork images or src changes
const artworkObserver = new MutationObserver((mutations) => {
    mutations.forEach((mutation) => {
        if (mutation.type === 'attributes' && mutation.attributeName === 'src') {
            if (mutation.target.classList.contains('pokemon-artwork')) {
                updateLoaderState(mutation.target);
            }
        } else if (mutation.type === 'childList') {
            mutation.addedNodes.forEach(node => {
                if (node.nodeType === 1) { // Element
                    if (node.classList.contains('pokemon-artwork')) {
                        updateLoaderState(node);
                    }
                    const nested = node.querySelectorAll('.pokemon-artwork');
                    nested.forEach(updateLoaderState);
                }
            });
        }
    });
});

artworkObserver.observe(document.body, {
    attributes: true,
    childList: true,
    subtree: true,
    attributeFilter: ['src']
});

// Initial check
document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('.pokemon-artwork').forEach(updateLoaderState);
});
