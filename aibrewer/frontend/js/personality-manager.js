/**
 * Personality Manager Module
 * Handles brewer personality selection and management
 */
const PersonalityManager = (() => {
    // Private variables
    let personalityModal;
    let personalityGrid;
    let personalityBadge;
    let brewerPersonalityBtn;
    let currentBrewerIcon;
    let currentBrewerName;
    let badgeIcon;
    let badgeName;
    
    // Initialize module
    function init() {
        console.log('👤 Initializing Personality Manager...');
        
        // Cache DOM elements
        personalityModal = document.getElementById('personalityModal');
        personalityGrid = document.getElementById('personalityGrid');
        personalityBadge = document.getElementById('personalityBadge');
        brewerPersonalityBtn = document.getElementById('brewerPersonalityBtn');
        currentBrewerIcon = document.getElementById('currentBrewerIcon');
        currentBrewerName = document.getElementById('currentBrewerName');
        badgeIcon = document.getElementById('badgeIcon');
        badgeName = document.getElementById('badgeName');
        
        // Setup event listeners
        setupEventListeners();
        
        // Load personalities from API
        loadPersonalities();
        
        console.log('👤 Personality Manager initialized');
    }
    
    // Set up event listeners for personality management
    function setupEventListeners() {
        // Brewer personality button
        if (brewerPersonalityBtn) {
            brewerPersonalityBtn.addEventListener('click', () => {
                if (personalityModal) {
                    personalityModal.style.display = 'block';
                }
            });
        }
        
        // Personality badge
        if (personalityBadge) {
            personalityBadge.addEventListener('click', () => {
                if (personalityModal) {
                    personalityModal.style.display = 'block';
                }
            });
        }
        
        // Close buttons
        document.querySelectorAll('.close').forEach(closeBtn => {
            closeBtn.addEventListener('click', () => {
                if (personalityModal) {
                    personalityModal.style.display = 'none';
                }
            });
        });
        
        // Close modal when clicking outside
        window.addEventListener('click', (event) => {
            if (event.target === personalityModal) {
                personalityModal.style.display = 'none';
            }
        });
    }
    
    // Load available personalities from API
    async function loadPersonalities() {
        try {
            const data = await ApiClient.getPersonalities();
            
            // Store personalities globally
            APP_STATE.allPersonalities = data;
            
            // Generate personality cards
            generatePersonalityCards();
            
            // Update UI with current personality
            updatePersonalityUI();
        } catch (error) {
            console.error('❌ Error fetching personalities:', error);
        }
    }
    
    // Generate personality card elements
    function generatePersonalityCards() {
        if (!personalityGrid) return;
        
        personalityGrid.innerHTML = '';
        
        for (const [id, personality] of Object.entries(APP_STATE.allPersonalities)) {
            const card = document.createElement('div');
            card.className = 'personality-card';
            if (id === APP_STATE.currentPersonality) {
                card.classList.add('selected');
            }
            card.dataset.personality = id;
            
            card.innerHTML = `
                <div class="personality-icon">${personality.icon}</div>
                <h3>${personality.name}</h3>
                <p>${personality.description}</p>
            `;
            
            card.addEventListener('click', () => {
                selectPersonality(id);
            });
            
            personalityGrid.appendChild(card);
        }
    }
    
    // Select a personality
    function selectPersonality(personalityId) {
        APP_STATE.currentPersonality = personalityId;
        
        // Update UI
        document.querySelectorAll('.personality-card').forEach(card => {
            card.classList.toggle('selected', card.dataset.personality === personalityId);
        });
        
        updatePersonalityUI();
        
        // Close modal
        if (personalityModal) {
            personalityModal.style.display = 'none';
        }
        
        // Show notification
        const personality = APP_STATE.allPersonalities[personalityId];
        if (personality) {
            showNotification(`${personality.name} hjälper dig nu med dina bryggningar!`);
        }
        
        // Save selection to localStorage
        localStorage.setItem('aibrewerPersonality', personalityId);
    }
    
    // Update UI with current personality
    function updatePersonalityUI() {
        const personality = APP_STATE.allPersonalities[APP_STATE.currentPersonality];
        if (!personality) return;
        
        // Update sidebar button
        if (currentBrewerIcon) currentBrewerIcon.textContent = personality.icon;
        if (currentBrewerName) currentBrewerName.textContent = personality.name;
        
        // Update badge
        if (badgeIcon) badgeIcon.textContent = personality.icon;
        if (badgeName) badgeName.textContent = personality.name;
    }
    
    // Show notification
    function showNotification(message) {
        const notification = document.createElement('div');
        notification.style.position = 'fixed';
        notification.style.bottom = '80px';
        notification.style.right = '20px';
        notification.style.backgroundColor = '#4CAF50';
        notification.style.color = 'white';
        notification.style.padding = '10px 20px';
        notification.style.borderRadius = '5px';
        notification.style.zIndex = '1000';
        notification.textContent = message;
        
        document.body.appendChild(notification);
        
        // Remove after 3 seconds
        setTimeout(() => {
            notification.style.opacity = '0';
            notification.style.transition = 'opacity 0.5s';
            setTimeout(() => {
                document.body.removeChild(notification);
            }, 500);
        }, 3000);
    }
    
    // Set active personality
    function setPersonality(personalityId) {
        APP_STATE.currentPersonality = personalityId;
        updatePersonalityUI();
    }
    
    // Get current personality
    function getCurrentPersonality() {
        return APP_STATE.currentPersonality;
    }
    
    // Public API
    return {
        init,
        setPersonality,
        getCurrentPersonality,
        loadPersonalities,
        showNotification
    };
})();
