/**
 * AIBrewer - Main Application Entry Point
 * This script initializes the application and coordinates between different modules
 */

// Global configuration - fix the baseUrl to use a relative path
const APP_CONFIG = {
    baseUrl: '/function_a_v2',  // Changed from 'http://localhost:5001/function_a_v2'
    debug: true
};

// Global state
const APP_STATE = {
    lastSelectedIngredients: [],
    inventoryData: null,
    chatHistory: [],
    currentUser: null,
    currentPersonality: 'traditionalist',
    allPersonalities: {}
};

// Initialize the application when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    console.log('🍺 AIBrewer application initializing...');
    
    // Define a helper function to safely initialize modules
    function safeInit(module, name) {
        if (!module) {
            console.error(`❌ Module ${name} not loaded`);
            return false;
        }
        
        try {
            if (typeof module.init === 'function') {
                module.init();
                console.log(`✅ ${name} initialized`);
                return true;
            } else {
                console.warn(`⚠️ ${name} has no init method`);
                return false;
            }
        } catch (e) {
            console.error(`❌ Error initializing ${name}:`, e);
            return false;
        }
    }
    
    // Delay initialization slightly to ensure all scripts have loaded
    setTimeout(() => {
        // Initialize modules in order of dependency
        if (typeof UserManager !== 'undefined') safeInit(UserManager, 'UserManager');
        if (typeof ApiClient !== 'undefined') safeInit(ApiClient, 'ApiClient');
        if (typeof InventoryManager !== 'undefined') safeInit(InventoryManager, 'InventoryManager');
        if (typeof ChatSystem !== 'undefined') safeInit(ChatSystem, 'ChatSystem');
        if (typeof PersonalityManager !== 'undefined') safeInit(PersonalityManager, 'PersonalityManager');
        if (typeof RecipeManager !== 'undefined') safeInit(RecipeManager, 'RecipeManager');
        
        // Set up global event listeners
        attachGlobalEventListeners();
        
        // Initialize chat history
        APP_STATE.chatHistory = [
            { role: "system", content: "Du är en AI-assistent som hjälper med ölbryggning. Använd svenska språket i dina svar." }
        ];
        
        // Add welcome message if ChatSystem loaded properly
        if (typeof ChatSystem !== 'undefined' && typeof ChatSystem.addMessage === 'function') {
            ChatSystem.addMessage("System", "Hej! Jag är din bryggassistent. Ställ frågor om receptet, ingredienser eller bryggning!");
        }
        
        // Load user preferences
        loadUserPreferences();
        
        console.log('🍺 AIBrewer application initialized');
    }, 100);
});

// Attach global event listeners
function attachGlobalEventListeners() {
    // Document-level event listeners for custom events
    document.addEventListener('ingredientsSelected', function(event) {
        APP_STATE.lastSelectedIngredients = event.detail.ingredients;
        console.log('🔔 Ingredients selected:', APP_STATE.lastSelectedIngredients);
    });
    
    // Make sure style suggestions handler is available globally
    window.displayStyleSuggestions = function(responseText) {
        if (RecipeManager && RecipeManager.displayStyleSuggestions) {
            RecipeManager.displayStyleSuggestions(responseText);
        } else {
            console.error('❌ RecipeManager.displayStyleSuggestions is not available');
            // Fallback implementation
            const styleSection = document.getElementById('styleSuggestionsSection');
            if (styleSection) {
                styleSection.classList.remove('hidden');
                const suggestionsDiv = document.getElementById('styleSuggestions');
                if (suggestionsDiv) {
                    suggestionsDiv.innerHTML = `<p>${responseText}</p>`;
                }
            }
        }
    };
    
    // Handle general application errors
    window.addEventListener('error', function(event) {
        console.error('❌ Application error:', event.error);
    });
}

// Load user preferences from localStorage
function loadUserPreferences() {
    try {
        // Load saved personality
        const savedPersonality = localStorage.getItem('aibrewerPersonality');
        if (savedPersonality) {
            APP_STATE.currentPersonality = savedPersonality;
            if (PersonalityManager && PersonalityManager.setPersonality) {
                PersonalityManager.setPersonality(savedPersonality);
            }
        }
    } catch (e) {
        console.error('❌ Error loading user preferences:', e);
    }
}

// Fix for generateXmlBtn - make sure it's globally accessible
if (document.getElementById('generateXmlBtn')) {
    document.getElementById('generateXmlBtn').addEventListener('click', function() {
        if (RecipeManager && RecipeManager.generateXml) {
            RecipeManager.generateXml();
        } else {
            console.error('❌ RecipeManager.generateXml is not available');
            alert("The XML generation module is not properly loaded. Please refresh the page and try again.");
        }
    });
}

// Export the globals for use in other modules
window.APP_CONFIG = APP_CONFIG;
window.APP_STATE = APP_STATE;
