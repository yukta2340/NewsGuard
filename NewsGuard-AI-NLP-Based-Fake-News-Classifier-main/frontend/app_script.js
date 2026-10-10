// frontend/app_script.js - Interactive client-side enhancements for NewsGuard
(function() {
    function initAppEnhancements() {
        // 1. Textarea Keyboard Shortcut (Ctrl+Enter or Cmd+Enter to submit)
        const textareas = window.parent.document.querySelectorAll('textarea');
        textareas.forEach(function(ta) {
            if (!ta.dataset.shortcutAttached) {
                ta.dataset.shortcutAttached = "true";
                ta.addEventListener('keydown', function(e) {
                    if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
                        e.preventDefault();
                        const primaryBtn = window.parent.document.querySelector('button[kind="primary"]');
                        if (primaryBtn) {
                            primaryBtn.click();
                        }
                    }
                });
            }
        });

        // 2. Character counter observer
        const textInputs = window.parent.document.querySelectorAll('textarea[aria-label*="content"]');
        textInputs.forEach(function(ta) {
            const parent = ta.closest('[data-testid="stTextArea"]');
            if (parent && !parent.querySelector('.char-counter-badge')) {
                const badge = document.createElement('div');
                badge.className = 'char-counter-badge';
                badge.style.cssText = 'text-align: right; font-size: 0.76rem; color: #64748b; margin-top: 4px;';
                
                function updateCount() {
                    const len = ta.value ? ta.value.length : 0;
                    const words = ta.value ? ta.value.trim().split(/\s+/).filter(Boolean).length : 0;
                    badge.textContent = words + ' words · ' + len + ' chars (Press Ctrl+Enter to analyze)';
                }
                
                ta.addEventListener('input', updateCount);
                parent.appendChild(badge);
                updateCount();
            }
        });
    }

    // Run on load and periodically to support Streamlit DOM re-renders
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initAppEnhancements);
    } else {
        initAppEnhancements();
    }
    setInterval(initAppEnhancements, 1500);
})();
