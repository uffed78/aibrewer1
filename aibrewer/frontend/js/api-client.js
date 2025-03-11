/**
 * API Client Module
 * Handles all API interactions with the backend
 */
const ApiClient = (() => {
    // Helper function for API requests
    async function apiRequest(endpoint, method = 'GET', data = null) {
        const url = `${APP_CONFIG.baseUrl}/${endpoint}`;
        
        const options = {
            method,
            headers: { 'Content-Type': 'application/json' }
        };
        
        if (data) {
            // Add personality to every request
            if (typeof data === 'object') {
                data.personality = APP_STATE.currentPersonality;
            }
            options.body = JSON.stringify(data);
        }
        
        if (APP_CONFIG.debug) {
            console.log(`🔄 API ${method} request to ${endpoint}`, data);
        }
        
        try {
            const response = await fetch(url, options);
            
            // Get content type to determine how to parse the response
            const contentType = response.headers.get('content-type');
            
            if (APP_CONFIG.debug) {
                console.log(`📥 API response from ${endpoint}:`, {
                    status: response.status,
                    contentType
                });
            }
            
            if (!response.ok) {
                // Try to parse error response
                let errorData;
                try {
                    errorData = await response.json();
                } catch (e) {
                    errorData = { error: `HTTP error ${response.status}` };
                }
                
                throw new Error(errorData.error || `API Error: ${response.status}`);
            }
            
            // Handle different response types
            if (contentType && contentType.includes('application/json')) {
                return await response.json();
            } else if (contentType && contentType.includes('application/xml')) {
                return response.blob();
            } else {
                return response;
            }
        } catch (error) {
            console.error(`❌ API Error in ${endpoint}:`, error);
            throw error;
        }
    }
    
    // Get all personalities
    async function getPersonalities() {
        return await apiRequest('personalities');
    }
    
    // Get user's inventory
    async function getInventory(credentials) {
        return await apiRequest('get-inventory', 'POST', credentials);
    }
    
    // Suggest beer styles based on ingredients
    async function suggestStyles(data) {
        return await apiRequest('suggest-styles', 'POST', data);
    }
    
    // Generate recipe draft
    async function generateDraft(data) {
        return await apiRequest('generate-draft', 'POST', data);
    }
    
    // Generate BeerXML
    async function generateXml(data) {
        // This will return a blob for download
        return await apiRequest('generate-xml', 'POST', data);
    }
    
    // Discuss with AI
    async function discuss(data) {
        return await apiRequest('discuss', 'POST', data);
    }
    
    // Public API
    return {
        getPersonalities,
        getInventory,
        suggestStyles,
        generateDraft,
        generateXml,
        discuss
    };
})();
