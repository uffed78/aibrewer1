/**
 * User Manager Module
 * Handles user authentication and settings
 */
const UserManager = (() => {
    // Private variables
    let settingsBtn;
    let settingsModal;
    let closeBtn;
    let settingsForm;
    let userProfilesList;
    let currentUserDisplay;
    let currentUser = null;
    
    // Local storage keys
    const USERS_KEY = 'aibrewer_users';
    const CURRENT_USER_KEY = 'aibrewer_current_user';
    
    // Initialize module
    function init() {
        console.log('👤 Initializing User Manager...');
        
        // Cache DOM elements
        settingsBtn = document.getElementById('settingsBtn');
        settingsModal = document.getElementById('settingsModal');
        closeBtn = settingsModal ? settingsModal.querySelector('.close') : null;
        settingsForm = document.getElementById('settingsForm');
        userProfilesList = document.getElementById('userProfilesList');
        currentUserDisplay = document.getElementById('currentUserDisplay');
        
        // Setup event listeners
        setupEventListeners();
        
        // Load current user
        loadCurrentUser();
        
        // Display users list
        displayUsersList();
        
        // Update current user display
        updateCurrentUserDisplay();
        
        console.log('👤 User Manager initialized');
    }
    
    // Set up event listeners
    function setupEventListeners() {
        // Settings button click
        if (settingsBtn) {
            settingsBtn.addEventListener('click', showSettings);
            console.log('👤 Settings button listener added');
        } else {
            console.warn('👤 Settings button not found');
        }
        
        // Close button click
        if (closeBtn) {
            closeBtn.addEventListener('click', hideSettings);
        }
        
        // Settings form submit
        if (settingsForm) {
            settingsForm.addEventListener('submit', saveSettings);
        }
        
        // Close modal when clicking outside
        window.addEventListener('click', function(event) {
            if (event.target === settingsModal) {
                hideSettings();
            }
        });
    }
    
    // Show settings modal
    function showSettings() {
        console.log('👤 Showing settings modal');
        if (settingsModal) {
            settingsModal.style.display = 'block';
            
            // Pre-fill form with current user data if available
            if (currentUser) {
                const usernameInput = document.getElementById('username');
                const apiIdInput = document.getElementById('apiId');
                const apiKeyInput = document.getElementById('apiKey');
                
                if (usernameInput) usernameInput.value = currentUser.username || '';
                if (apiIdInput) apiIdInput.value = currentUser.apiId || '';
                if (apiKeyInput) apiKeyInput.value = currentUser.apiKey || '';
            }
        }
    }
    
    // Hide settings modal
    function hideSettings() {
        if (settingsModal) {
            settingsModal.style.display = 'none';
        }
    }
    
    // Save settings from form
    function saveSettings(event) {
        event.preventDefault();
        
        const username = document.getElementById('username').value.trim();
        const apiId = document.getElementById('apiId').value.trim();
        const apiKey = document.getElementById('apiKey').value.trim();
        
        if (!username || !apiId || !apiKey) {
            alert('Alla fält måste fyllas i.');
            return;
        }
        
        // Create user object
        const user = {
            username,
            apiId,
            apiKey,
            timestamp: new Date().toISOString()
        };
        
        // Save user
        saveUser(user);
        
        // Set as current user
        setCurrentUser(user);
        
        // Update display
        updateCurrentUserDisplay();
        displayUsersList();
        
        // Close modal
        hideSettings();
        
        // Show success message
        alert(`Profil sparad för ${username}`);
    }
    
    // Save user to local storage
    function saveUser(user) {
        const users = getUsers();
        
        // Check if user already exists
        const existingIndex = users.findIndex(u => u.username === user.username);
        if (existingIndex >= 0) {
            // Update existing user
            users[existingIndex] = user;
        } else {
            // Add new user
            users.push(user);
        }
        
        // Save to local storage
        localStorage.setItem(USERS_KEY, JSON.stringify(users));
    }
    
    // Get all users from local storage
    function getUsers() {
        const usersString = localStorage.getItem(USERS_KEY);
        return usersString ? JSON.parse(usersString) : [];
    }
    
    // Set current user
    function setCurrentUser(user) {
        currentUser = user;
        localStorage.setItem(CURRENT_USER_KEY, JSON.stringify(user));
    }
    
    // Load current user from local storage
    function loadCurrentUser() {
        const userString = localStorage.getItem(CURRENT_USER_KEY);
        if (userString) {
            try {
                currentUser = JSON.parse(userString);
            } catch (e) {
                console.error('Error parsing current user:', e);
                currentUser = null;
            }
        }
    }
    
    // Display users list
    function displayUsersList() {
        if (!userProfilesList) return;
        
        const users = getUsers();
        
        userProfilesList.innerHTML = '';
        
        if (users.length === 0) {
            userProfilesList.innerHTML = '<p>Inga sparade profiler.</p>';
            return;
        }
        
        users.forEach(user => {
            const userDiv = document.createElement('div');
            userDiv.className = 'user-profile';
            
            const isActive = currentUser && currentUser.username === user.username;
            if (isActive) {
                userDiv.classList.add('active');
            }
            
            userDiv.innerHTML = `
                <div class="user-profile-name">${user.username}</div>
                <div class="user-profile-actions">
                    <button class="select-btn">${isActive ? 'Aktiv' : 'Välj'}</button>
                    <button class="delete-btn">Ta bort</button>
                </div>
            `;
            
            // Add select event
            const selectBtn = userDiv.querySelector('.select-btn');
            selectBtn.addEventListener('click', () => {
                setCurrentUser(user);
                updateCurrentUserDisplay();
                displayUsersList();
            });
            
            // Add delete event
            const deleteBtn = userDiv.querySelector('.delete-btn');
            deleteBtn.addEventListener('click', () => {
                if (confirm(`Är du säker på att du vill ta bort profilen för ${user.username}?`)) {
                    deleteUser(user.username);
                    displayUsersList();
                    updateCurrentUserDisplay();
                }
            });
            
            userProfilesList.appendChild(userDiv);
        });
    }
    
    // Delete user
    function deleteUser(username) {
        let users = getUsers();
        users = users.filter(u => u.username !== username);
        localStorage.setItem(USERS_KEY, JSON.stringify(users));
        
        // Check if current user is deleted
        if (currentUser && currentUser.username === username) {
            currentUser = users.length > 0 ? users[0] : null;
            if (currentUser) {
                localStorage.setItem(CURRENT_USER_KEY, JSON.stringify(currentUser));
            } else {
                localStorage.removeItem(CURRENT_USER_KEY);
            }
        }
    }
    
    // Update current user display
    function updateCurrentUserDisplay() {
        if (!currentUserDisplay) return;
        
        if (currentUser) {
            currentUserDisplay.innerHTML = `
                <div class="current-user-info">
                    <p><strong>Aktiv profil:</strong> ${currentUser.username}</p>
                    <p><small>API ID: ${currentUser.apiId}</small></p>
                </div>
            `;
        } else {
            currentUserDisplay.innerHTML = '<p>Ingen aktiv profil vald.</p>';
        }
    }
    
    // Check if user is authenticated
    function isAuthenticated() {
        return !!currentUser && !!currentUser.apiId && !!currentUser.apiKey;
    }
    
    // Get API credentials
    function getApiCredentials() {
        if (!isAuthenticated()) {
            return null;
        }
        
        return {
            apiId: currentUser.apiId,
            apiKey: currentUser.apiKey
        };
    }
    
    // Public API
    return {
        init,
        showSettings,
        hideSettings,
        isAuthenticated,
        getApiCredentials,
        setCurrentUser
    };
})();

// Initialize the module when DOM is ready
document.addEventListener('DOMContentLoaded', UserManager.init);
