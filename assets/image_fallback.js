// Global event listener for image loading errors
document.addEventListener('error', function (event) {
    if (event.target.tagName.toLowerCase() !== 'img') return;

    // Check for artwork vs sprites
    if (event.target.classList.contains('pokemon-artwork')) {
        if (!event.target.src.includes('placeholder.png')) {
            console.log('Falling back to full artwork placeholder');
            event.target.src = '/assets/images/placeholder.png';
        }
    } else if (event.target.classList.contains('pokemon-sprite') || event.target.closest('.custom-dropdown')) {
        // Fallback for small sprites
        if (!event.target.src.includes('pokeball_placeholder.png')) {
            console.log('Falling back to small pokeball placeholder');
            event.target.src = '/assets/images/pokeball_placeholder.png';
        }
    }
}, true);
