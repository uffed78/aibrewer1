/**
 * User Manager Module
 * Handles user profiles, authentication and Brewfather API integration
 */
const UserManager = (() => {
    // Private variables
    let settingsForm;
    let settingsModal;
    let settingsBtn;
    let userProfilesList;
    
    // Initialize module
    function init() {
        console.log('🔑 Initializing User Manager...');
        
        // Cache DOM elements
        settingsForm = document.getElementById('settingsForm');
        settingsModal = document.getElementById('settingsModal');
        settingsBtn = document.getElementById('settingsBtn');
        userProfilesList = document.getElementById('userProfilesList');
        
        // Setup event listeners
        setupEventListeners();
        
        // Load saved profiles
        loadSavedProfiles();
        
        console.log('🔑 User Manager initialized');
    }
    
    // Set up event listeners for user management
    function setupEventListeners() {
        // Settings button
        if (settingsBtn) {
            settingsBtn.addEventListener('click', () => {
                settingsModal.style.display = 'block';
            });
        }
        
        // Settings form submission
        if (settingsForm) {
            settingsForm.addEventListener('submit', handleSettingsSubmit);
        }
        
        // Modal close button
        const closeButton = settingsModal ? settingsModal.querySelector('.close') : null;
        if (closeButton) {
            closeButton.addEventListener('click', () => {
                settingsModal.style.display = 'none';
            });
        }
        
        // Close modal when clicking outside
        window.addEventListener('click', function(event) {
            if (event.target === settingsModal) {
                settingsModal.style.display = 'none';
            }
        });
    }
    
    // Handle settings form submission
    function handleSettingsSubmit(e) {
        e.preventDefault();
        
        const username = document.getElementById('username').value.trim();
        const apiId = document.getElementById('apiId').value.trim();
        const apiKey = document.getElementById('apiKey').value.trim();
        
        // Retrieve saved profiles
        let profiles = JSON.parse(localStorage.getItem('brewfatherProfiles')) || [];
        
        // Check if the user already exists
        const existingIndex = profiles.findIndex(p => p.username === username);
        
        if (existingIndex >= 0) {
            profiles[existingIndex] = { username, apiId, apiKey };
        } else {
            profiles.push({ username, apiId, apiKey });
        }
        
        // Save to localStorage
        localStorage.setItem('brewfatherProfiles', JSON.stringify(profiles));
        localStorage.setItem('lastUsedProfile', username);
        
        // Update current user
        APP_STATE.currentUser = { username, apiId, apiKey };
        
        // Update UI
        updateUserProfilesList(profiles);
        updateCurrentUserDisplay();
        
        // Close modal
        settingsModal.style.display = 'none';
        
        alert(`Inställningar sparade för ${username}`);
    }
    
    // Load saved profiles from localStorage
    function loadSavedProfiles() {
        let savedProfiles = JSON.parse(localStorage.getItem('brewfatherProfiles')) || [];
        let lastUsedProfile = localStorage.getItem('lastUsedProfile');
        
        if (lastUsedProfile) {
            APP_STATE.currentUser = savedProfiles.find(p => p.username === lastUsedProfile);
        }
        
        // Display current user if any
        if (APP_STATE.currentUser) {
            document.getElementById('username').value = APP_STATE.currentUser.username;
            document.getElementById('apiId').value = APP_STATE.currentUser.apiId;
            document.getElementById('apiKey').value = APP_STATE.currentUser.apiKey;
            updateCurrentUserDisplay();
        }
        
        // Display all saved profiles
        updateUserProfilesList(savedProfiles);
    }
    
    // Update the list of user profiles in UI
    function updateUserProfilesList(profiles) {
        if (!userProfilesList) return;
        
        userProfilesList.innerHTML = '';
        
        if (profiles.length === 0) {
            userProfilesList.innerHTML = '<p>Inga profiler sparade ännu.</p>';
            return;
        }
        
        profiles.forEach(profile => {
            const profileDiv = document.createElement('div');
            profileDiv.className = 'user-profile';
            
            profileDiv.innerHTML = `
                <span>${profile.username}</span>
                <button class="use-profile" data-username="${profile.username}">Använd</button>
                <button class="delete-profile" data-username="${profile.username}">Ta bort</button>
            `;
            
            userProfilesList.appendChild(profileDiv);
        });
        
        // Add event handlers to the buttons
        document.querySelectorAll('.use-profile').forEach(button => {
            button.addEventListener('click', function() {
                const username = this.getAttribute('data-username');
                selectUserProfile(username, profiles);
            });
        });
        
        document.querySelectorAll('.delete-profile').forEach(button => {
            button.addEventListener('click', function() {
                const username = this.getAttribute('data-username');
                deleteUserProfile(username, profiles);
            });
        });
    }
    
    // Select a user profile
    function selectUserProfile(username, profiles) {
        const profile = profiles.find(p => p.username === username);
        
        if (profile) {
            document.getElementById('username').value = profile.username;
            document.getElementById('apiId').value = profile.apiId;
            document.getElementById('apiKey').value = profile.apiKey;
            
            // Update current user and save to localStorage
            APP_STATE.currentUser = profile;
            localStorage.setItem('lastUsedProfile', username);
            updateCurrentUserDisplay();
        }
    }
    
    // Delete a user profile
    function deleteUserProfile(username, profiles) {
        if (confirm(`Är du säker på att du vill ta bort profilen för ${username}?`)) {
            const updatedProfiles = profiles.filter(p => p.username !== username);
            localStorage.setItem('brewfatherProfiles', JSON.stringify(updatedProfiles));
            
            // If the deleted profile was the active one, reset currentUser
            if (APP_STATE.currentUser && APP_STATE.currentUser.username === username) {
                APP_STATE.currentUser = null;
                localStorage.removeItem('lastUsedProfile');
                document.getElementById('username').value = '';
                document.getElementById('apiId').value = '';
                document.getElementById('apiKey').value = '';
                updateCurrentUserDisplay();
            }
            
            updateUserProfilesList(updatedProfiles);
        }
    }
    
    // Update the display of the current user
    function updateCurrentUserDisplay() {
        const displayElement = document.getElementById('currentUserDisplay');
        if (!displayElement) return;
        
        if (APP_STATE.currentUser) {
            displayElement.innerHTML = `<div class="current-user">Inloggad som: <strong>${APP_STATE.currentUser.username}</strong></div>`;
        } else {
            displayElement.innerHTML = '<div class="current-user">Ingen användare vald</div>';
        }
    }
    
    // Check if user is authenticated
    function isAuthenticated() {
        return !!APP_STATE.currentUser;
    }
    
    // Get user API credentials
    function getApiCredentials() {
        if (!isAuthenticated()) {
            return null;
        }
        
        return {
            apiId: APP_STATE.currentUser.apiId,
            apiKey: APP_STATE.currentUser.apiKey
        };
    }
    
    // Show settings modal
    function showSettings() {
        if (settingsModal) {
            settingsModal.style.display = 'block';
        }
    }
    
    // Public API
    return {
        init,
        isAuthenticated,
        getApiCredentials,
        showSettings,
        updateCurrentUserDisplay
    };
})();
