// Tomato Varieties Database - Frontend JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Initialize the application
    initializeApp();
});

function initializeApp() {
    // Add fade-in animation to main content
    const mainContent = document.querySelector('main');
    if (mainContent) {
        mainContent.classList.add('fade-in');
    }
    
    // Initialize search functionality
    initializeSearch();
    
    // Initialize tooltips if Bootstrap is available
    if (typeof bootstrap !== 'undefined') {
        const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    }
    
    // Add keyboard shortcuts
    initializeKeyboardShortcuts();
    
    // Initialize lazy loading for images
    initializeLazyLoading();
}

function initializeSearch() {
    const searchForms = document.querySelectorAll('form[action="/search"]');
    
    searchForms.forEach(form => {
        const searchInput = form.querySelector('input[name="q"]');
        
        if (searchInput) {
            // Add search suggestions (if we had a suggestions endpoint)
            searchInput.addEventListener('input', debounce(function(e) {
                const query = e.target.value.trim();
                if (query.length >= 2) {
                    // Could implement live search suggestions here
                    console.log('Searching for:', query);
                }
            }, 300));
            
            // Handle form submission
            form.addEventListener('submit', function(e) {
                const query = searchInput.value.trim();
                if (!query) {
                    e.preventDefault();
                    alert('Please enter a search term');
                    searchInput.focus();
                }
            });
        }
    });
}

function initializeKeyboardShortcuts() {
    document.addEventListener('keydown', function(e) {
        // Ctrl/Cmd + K for search
        if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
            e.preventDefault();
            const searchInput = document.querySelector('input[name="q"]');
            if (searchInput) {
                searchInput.focus();
                searchInput.select();
            }
        }
        
        // Escape to clear search
        if (e.key === 'Escape') {
            const searchInput = document.querySelector('input[name="q"]:focus');
            if (searchInput) {
                searchInput.value = '';
                searchInput.blur();
            }
        }
    });
}

function initializeLazyLoading() {
    // Simple lazy loading for images
    const images = document.querySelectorAll('img[data-src]');
    
    if ('IntersectionObserver' in window) {
        const imageObserver = new IntersectionObserver((entries, observer) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const img = entry.target;
                    img.src = img.dataset.src;
                    img.classList.remove('lazy');
                    imageObserver.unobserve(img);
                }
            });
        });
        
        images.forEach(img => imageObserver.observe(img));
    } else {
        // Fallback for older browsers
        images.forEach(img => {
            img.src = img.dataset.src;
        });
    }
}

// Utility Functions

function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

function showLoading(element) {
    if (element) {
        element.classList.add('loading');
    }
}

function hideLoading(element) {
    if (element) {
        element.classList.remove('loading');
    }
}

function showToast(message, type = 'info') {
    // Simple toast notification
    const toast = document.createElement('div');
    toast.className = `alert alert-${type} position-fixed`;
    toast.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
    toast.innerHTML = `
        <div class="d-flex justify-content-between align-items-center">
            <span>${message}</span>
            <button type="button" class="btn-close" onclick="this.parentElement.parentElement.remove()"></button>
        </div>
    `;
    
    document.body.appendChild(toast);
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
        if (toast.parentElement) {
            toast.remove();
        }
    }, 5000);
}

// API Helper Functions

async function apiCall(endpoint, options = {}) {
    try {
        showLoading(document.body);
        
        const response = await fetch(`/api${endpoint}`, {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            },
            ...options
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.error || 'API request failed');
        }
        
        return data;
    } catch (error) {
        console.error('API Error:', error);
        showToast(`Error: ${error.message}`, 'danger');
        throw error;
    } finally {
        hideLoading(document.body);
    }
}

// Global functions for inline event handlers

window.refreshData = async function() {
    try {
        const data = await apiCall('/refresh');
        showToast(`Data refreshed! Found ${data.total_varieties} varieties.`, 'success');
        setTimeout(() => location.reload(), 1500);
    } catch (error) {
        // Error already shown by apiCall
    }
};

window.refreshStats = async function() {
    try {
        const data = await apiCall('/refresh');
        showToast('Statistics refreshed!', 'success');
        setTimeout(() => location.reload(), 1500);
    } catch (error) {
        // Error already shown by apiCall
    }
};

// Search functionality
window.performSearch = async function(query) {
    if (!query.trim()) {
        showToast('Please enter a search term', 'warning');
        return;
    }
    
    try {
        const data = await apiCall(`/search?q=${encodeURIComponent(query)}`);
        
        if (data.total_found === 0) {
            showToast('No varieties found matching your search', 'info');
        } else {
            showToast(`Found ${data.total_found} varieties`, 'success');
        }
        
        return data;
    } catch (error) {
        // Error already shown by apiCall
    }
};

// Console welcome message
console.log(`
🍅 Welcome to Tomato Varieties Database!
🔧 Developer Tools Available:
   - refreshData() - Refresh the database
   - performSearch(query) - Search varieties
   - apiCall(endpoint) - Make API calls
   
📚 Keyboard Shortcuts:
   - Ctrl/Cmd + K - Focus search
   - Escape - Clear search
`);
// Beautiful Loading Overlay Functions for Tomato Database
function showLoadingOverlay(type, text) {
    if (!document.getElementById("loadingOverlay")) {
        const overlay = document.createElement("div");
        overlay.id = "loadingOverlay";
        overlay.className = "loading-overlay";
        overlay.innerHTML = `
            <div id="loaderContent"></div>
            <div class="loading-text" id="loadingText"></div>
        `;
        document.body.appendChild(overlay);
    }
    
    updateLoadingOverlay(type, text);
    document.getElementById("loadingOverlay").classList.add("active");
}

function updateLoadingOverlay(type, text) {
    const content = document.getElementById("loaderContent");
    const textEl = document.getElementById("loadingText");
    
    content.innerHTML = "";
    
    switch(type) {
        case "tomato":
            content.innerHTML = "<div class=\"tomato-spinner\"></div>";
            break;
        case "plant":
        default:  // Make plant the default animation
            content.innerHTML = `
                <div class="plant-loader">
                    <span class="plant-stage">🌱</span>
                    <span class="plant-stage">🌿</span>
                    <span class="plant-stage">🍃</span>
                    <span class="plant-stage">🍅</span>
                </div>
            `;
            break;
        case "ripple":
            content.innerHTML = `
                <div class="water-ripple">
                    <div class="ripple-circle"></div>
                    <div class="ripple-circle"></div>
                    <div class="ripple-circle"></div>
                </div>
            `;
            break;
    }
    
    textEl.textContent = text;
}

function hideLoadingOverlay() {
    const overlay = document.getElementById("loadingOverlay");
    if (overlay) {
        overlay.classList.remove("active");
    }
}


// Global navigation loading with growing plants
document.addEventListener("DOMContentLoaded", function() {
    // Add growing plant loading to all internal navigation links
    const internalLinks = document.querySelectorAll("a[href^=\"/\"]:not([href^=\"//\"]):not([target=\"_blank\"])");
    
    internalLinks.forEach(link => {
        link.addEventListener("click", function(e) {
            const href = this.getAttribute("href");
            
            // Skip if its a hash link or external
            if (href.startsWith("#") || href.includes("://")) {
                return;
            }
            
            // Show appropriate loading message based on destination
            let message = "Growing fresh content...";
            
            if (href === "/" || href.includes("home")) {
                message = "Growing tomato garden...";
            } else if (href.includes("search")) {
                message = "Growing search results...";
            } else if (href.includes("tomato/")) {
                message = "Loading variety details...";
            } else if (href.includes("stats")) {
                message = "Growing statistics...";
            } else if (href.includes("loading-demo")) {
                message = "Growing animation demos...";
            }
            
            if (typeof showLoadingOverlay === "function") {
                showLoadingOverlay("plant", message);
            }
        });
    });
    
    // Add loading to form submissions
    const forms = document.querySelectorAll("form");
    forms.forEach(form => {
        form.addEventListener("submit", function(e) {
            const action = this.getAttribute("action") || "";
            let message = "Processing request...";
            
            if (action.includes("search")) {
                message = "Growing search results...";
            }
            
            if (typeof showLoadingOverlay === "function") {
                showLoadingOverlay("plant", message);
            }
        });
    });
});

// Helper function for quick plant loading
window.showPlantLoading = function(message = "Growing fresh content...") {
    if (typeof showLoadingOverlay === "function") {
        showLoadingOverlay("plant", message);
    }
};

window.hidePlantLoading = function() {
    if (typeof hideLoadingOverlay === "function") {
        hideLoadingOverlay();
    }
};

