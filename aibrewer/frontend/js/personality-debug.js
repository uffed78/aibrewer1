/**
 * Personality Debugging and Fix Script
 * This adds better personality selection support to the frontend
 */
document.addEventListener('DOMContentLoaded', function() {
    console.log('Personality debug script loaded');
    
    // Constants & selectors
    const PERSONALITY_STORAGE_KEY = 'aibrewerPersonality';
    const brewerBtn = document.getElementById('brewerPersonalityBtn');
    const brewerIcon = document.getElementById('currentBrewerIcon');
    const brewerName = document.getElementById('currentBrewerName');
    
    // Fetch available personalities
    async function fetchPersonalities() {
        try {
            const response = await fetch('/function_a_v2/personalities');
            const data = await response.json();
            console.log('Available personalities:', data);
            return data;
        } catch (error) {
            console.error('Failed to fetch personalities:', error);
            return {};
        }
    }

    // Create the personality selection modal
    async function createPersonalityModal() {
        const personalities = await fetchPersonalities();
        if (!Object.keys(personalities).length) return;
        
        // Create modal if it doesn't exist
        let modal = document.getElementById('personalityModal');
        if (!modal) {
            modal = document.createElement('div');
            modal.id = 'personalityModal';
            modal.className = 'modal';
            modal.style.display = 'none';
            modal.style.position = 'fixed';
            modal.style.zIndex = '1000';
            modal.style.left = '0';
            modal.style.top = '0';
            modal.style.width = '100%';
            modal.style.height = '100%';
            modal.style.backgroundColor = 'rgba(0,0,0,0.4)';
            
            const modalContent = document.createElement('div');
            modalContent.className = 'modal-content';
            modalContent.style.backgroundColor = '#fefefe';
            modalContent.style.margin = '15% auto';
            modalContent.style.padding = '20px';
            modalContent.style.border = '1px solid #888';
            modalContent.style.width = '50%';
            modalContent.style.borderRadius = '5px';
            
            const closeBtn = document.createElement('span');
            closeBtn.className = 'close-button';
            closeBtn.innerHTML = '&times;';
            closeBtn.style.color = '#aaa';
            closeBtn.style.float = 'right';
            closeBtn.style.fontSize = '28px';
            closeBtn.style.fontWeight = 'bold';
            closeBtn.style.cursor = 'pointer';
            closeBtn.onclick = () => modal.style.display = 'none';
            
            const heading = document.createElement('h2');
            heading.textContent = 'Välj Bryggarpersonlighet';
            
            const personalitiesList = document.createElement('div');
            personalitiesList.className = 'personalities-list';
            personalitiesList.style.marginTop = '20px';
            personalitiesList.style.display = 'flex';
            personalitiesList.style.flexDirection = 'column';
            personalitiesList.style.gap = '10px';
            
            // Add each personality as a selectable option
            Object.entries(personalities).forEach(([id, personality]) => {
                const option = document.createElement('div');
                option.className = 'personality-option';
                option.dataset.personalityId = id;
                option.style.padding = '10px';
                option.style.border = '1px solid #ddd';
                option.style.borderRadius = '5px';
                option.style.cursor = 'pointer';
                option.style.display = 'flex';
                option.style.alignItems = 'center';
                option.style.gap = '10px';
                
                option.innerHTML = `
                    <span class="personality-icon">${personality.icon}</span>
                    <div>
                        <strong>${personality.name}</strong>
                        <p style="margin: 5px 0 0 0; font-size: 0.9em;">${personality.description}</p>
                    </div>
                `;
                
                option.addEventListener('click', () => {
                    selectPersonality(id, personality);
                    modal.style.display = 'none';
                });
                
                personalitiesList.appendChild(option);
            });
            
            modalContent.appendChild(closeBtn);
            modalContent.appendChild(heading);
            modalContent.appendChild(personalitiesList);
            modal.appendChild(modalContent);
            document.body.appendChild(modal);
        }
        
        return modal;
    }
    
    // Select a personality
    function selectPersonality(id, personality) {
        console.log(`Selecting personality: ${id} - ${personality.name}`);
        
        // Update UI
        brewerIcon.textContent = personality.icon;
        brewerName.textContent = personality.name;
        
        // Store selection
        localStorage.setItem(PERSONALITY_STORAGE_KEY, id);
        
        // Announce to the console for debugging
        console.log(`Personality set to: ${id}`);
        
        // Test the selection immediately
        testPersonalitySelection();
    }
    
    // Test if personality is being correctly sent
    async function testPersonalitySelection() {
        try {
            const personalityId = localStorage.getItem(PERSONALITY_STORAGE_KEY) || 'traditionalist';
            console.log('Testing personality selection with ID:', personalityId);
            
            const response = await fetch('/function_a_v2/debug-request', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    personality: personalityId,
                    test: true
                })
            });
            
            const data = await response.json();
            console.log('Debug request response:', data);
        } catch (error) {
            console.error('Failed to test personality selection:', error);
        }
    }
    
    // Initialize personality from storage
    async function initializePersonality() {
        const personalities = await fetchPersonalities();
        const savedPersonalityId = localStorage.getItem(PERSONALITY_STORAGE_KEY) || 'traditionalist';
        
        console.log('Initializing with saved personality ID:', savedPersonalityId);
        
        if (personalities[savedPersonalityId]) {
            const personality = personalities[savedPersonalityId];
            brewerIcon.textContent = personality.icon;
            brewerName.textContent = personality.name;
        }
    }
    
    // Patch the fetch function to include personality in requests
    const originalFetch = window.fetch;
    window.fetch = function(url, options = {}) {
        // Only modify API calls to our backend
        if (typeof url === 'string' && url.includes('/function_a_v2/')) {
            options = options || {};
            options.headers = options.headers || {};
            
            // If it's a JSON request
            if (options.method === 'POST' && 
                (!options.headers['Content-Type'] || options.headers['Content-Type'].includes('application/json'))) {
                
                try {
                    // Get the current body and parse it if it's a string
                    let body = options.body;
                    let jsonBody = {};
                    
                    if (typeof body === 'string') {
                        try {
                            jsonBody = JSON.parse(body);
                        } catch (e) {
                            console.warn('Could not parse request body as JSON');
                        }
                    } else if (body && typeof body === 'object') {
                        jsonBody = body;
                    }
                    
                    // Add personality to the request
                    const personalityId = localStorage.getItem(PERSONALITY_STORAGE_KEY) || 'traditionalist';
                    jsonBody.personality = personalityId;
                    
                    console.log(`Adding personality ${personalityId} to request:`, url);
                    
                    // Update the options body
                    options.body = JSON.stringify(jsonBody);
                    options.headers['Content-Type'] = 'application/json';
                } catch (error) {
                    console.error('Error patching fetch request:', error);
                }
            }
        }
        
        // Call the original fetch with possibly modified options
        return originalFetch.call(this, url, options);
    };
    
    // Set up event listeners
    if (brewerBtn) {
        brewerBtn.addEventListener('click', async () => {
            const modal = await createPersonalityModal();
            modal.style.display = 'block';
        });
    }
    
    // Initialize the personality system
    initializePersonality();
    
    // Log success
    console.log('Personality system initialized successfully');
});
