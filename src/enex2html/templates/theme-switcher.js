/**
 * Theme Switcher for ENEX HTML Archive
 * Handles theme persistence using localStorage
 */

(function() {
    'use strict';

    const STORAGE_KEY = 'enex-theme-preference';
    const THEMES = ['light', 'dark'];

    /**
     * Get the current theme preference
     * @returns {string} The current theme name
     */
    function getCurrentTheme() {
        // First check localStorage for user preference
        const stored = localStorage.getItem(STORAGE_KEY);
        if (stored && THEMES.includes(stored)) {
            return stored;
        }

        // Fall back to default theme from body attribute
        const defaultTheme = document.body.getAttribute('data-default-theme') || 'dark';
        return THEMES.includes(defaultTheme) ? defaultTheme : 'dark';
    }

    /**
     * Apply the theme by updating the CSS link href
     * @param {string} theme - The theme name to apply
     */
    function applyTheme(theme) {
        const link = document.querySelector('link[rel="stylesheet"][href*="themes/"]');
        if (link) {
            // Update the href to point to the selected theme
            link.href = link.href.replace(/themes\/(light|dark)\.css/, `themes/${theme}.css`);
        }
    }

    /**
     * Save theme preference and apply it
     * @param {string} theme - The theme name to save
     */
    function setTheme(theme) {
        if (!THEMES.includes(theme)) {
            console.warn(`Invalid theme: ${theme}`);
            return;
        }

        localStorage.setItem(STORAGE_KEY, theme);
        applyTheme(theme);
        updateToggleButton(theme);
    }

    /**
     * Toggle between light and dark themes
     */
    function toggleTheme() {
        const current = getCurrentTheme();
        const next = current === 'dark' ? 'light' : 'dark';
        setTheme(next);
    }

    /**
     * Update the toggle button text/icon based on current theme
     * @param {string} theme - The current theme name
     */
    function updateToggleButton(theme) {
        const button = document.getElementById('theme-toggle');
        if (button) {
            button.textContent = theme === 'dark' ? '☀️ Light' : '🌙 Dark';
            button.setAttribute('aria-label', `Switch to ${theme === 'dark' ? 'light' : 'dark'} theme`);
        }
    }

    /**
     * Initialize the theme switcher
     */
    function init() {
        // Apply the current theme on page load
        const theme = getCurrentTheme();
        applyTheme(theme);

        // Wait for DOM to be ready before updating button
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', function() {
                updateToggleButton(theme);
            });
        } else {
            updateToggleButton(theme);
        }
    }

    // Expose toggle function globally for button onclick
    window.toggleTheme = toggleTheme;

    // Initialize immediately
    init();
})();