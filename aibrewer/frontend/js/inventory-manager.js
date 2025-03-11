/**
 * Inventory Manager Module
 * Handles ingredient inventory and selection
 */
const InventoryManager = (() => {
    // Private variables
    let selectIngredientsBtn;
    let inventorySection;
    let inventoryDisplay;
    
    // Initialize module
    function init() {
        console.log('📦 Initializing Inventory Manager...');
        
        // Cache DOM elements
        selectIngredientsBtn = document.getElementById('selectIngredientsBtn');
        inventorySection = document.getElementById('inventorySection');
        inventoryDisplay = document.getElementById('inventoryDisplay');
        
        // Setup event listeners
        setupEventListeners();
        
        console.log('📦 Inventory Manager initialized');
    }
    
    // Set up event listeners for inventory management
    function setupEventListeners() {
        // Select ingredients button
        if (selectIngredientsBtn) {
            selectIngredientsBtn.addEventListener('click', fetchInventory);
        }
        
        // Listen for ingredient selection event
        document.addEventListener('ingredientsSelected', handleIngredientSelection);
    }
    
    // Fetch inventory from API
    async function fetchInventory() {
        console.log('📦 Fetching inventory...');
        
        // Check if user is authenticated
        if (!UserManager.isAuthenticated()) {
            alert("Du måste konfigurera en Brewfather-profil först. Klicka på 'Inställningar'.");
            UserManager.showSettings();
            return;
        }
        
        try {
            // Show loading indicator
            inventoryDisplay.innerHTML = '<div style="text-align: center; padding: 20px;"><b>Laddar ingredienser...</b></div>';
            
            // Get credentials and fetch inventory
            const credentials = UserManager.getApiCredentials();
            const data = await ApiClient.getInventory(credentials);
            
            // Store inventory data globally
            APP_STATE.inventoryData = data;
            console.log('📦 Inventory data received:', data);
            
            // Display the inventory in the main UI
            displayInventory(data);
            
            // Dispatch event that inventory was loaded
            document.dispatchEvent(new CustomEvent('inventoryLoaded', {
                detail: { inventoryData: data }
            }));
            
            // Show ingredient selection modal using the enhanced selector
            if (typeof IngredientSelector !== 'undefined') {
                IngredientSelector.showModal(data);
            } else {
                console.error('❌ IngredientSelector module not found. Falling back to simple selection.');
                showSimpleIngredientModal(data);
            }
        } catch (error) {
            console.error('❌ Error fetching inventory:', error);
            inventoryDisplay.innerHTML = `<div class="error-message">
                Ett fel inträffade: ${error.message}
                <button onclick="InventoryManager.fetchInventory()">Försök igen</button>
            </div>`;
        }
    }
    
    // Show a simple ingredient selection modal as fallback
    function showSimpleIngredientModal(data) {
        // Create modal if it doesn't exist
        let modal = document.getElementById('simpleIngredientModal');
        if (!modal) {
            modal = document.createElement('div');
            modal.id = 'simpleIngredientModal';
            modal.className = 'modal';
            modal.style.display = 'none';
            
            const modalContent = document.createElement('div');
            modalContent.className = 'modal-content';
            modalContent.style.width = '80%';
            modalContent.style.maxWidth = '800px';
            
            const closeBtn = document.createElement('span');
            closeBtn.className = 'close';
            closeBtn.innerHTML = '&times;';
            closeBtn.onclick = function() { modal.style.display = 'none'; };
            
            const header = document.createElement('h2');
            header.textContent = 'Välj ingredienser';
            
            const contentInner = document.createElement('div');
            contentInner.className = 'modal-content-inner';
            
            modalContent.appendChild(closeBtn);
            modalContent.appendChild(header);
            modalContent.appendChild(contentInner);
            modal.appendChild(modalContent);
            
            document.body.appendChild(modal);
        }
        
        // Clear previous content
        const content = modal.querySelector('.modal-content-inner');
        content.innerHTML = '';
        
        // Add categories
        ['fermentables', 'hops', 'yeasts'].forEach(category => {
            if (data[category] && data[category].length > 0) {
                const section = document.createElement('div');
                section.classList.add('inventory-category');
                
                // Add header and toggle button
                const header = document.createElement('h3');
                header.textContent = category.charAt(0).toUpperCase() + category.slice(1);
                
                const toggleAllBtn = document.createElement('button');
                toggleAllBtn.textContent = 'Markera alla';
                toggleAllBtn.style.marginLeft = '10px';
                toggleAllBtn.style.fontSize = '12px';
                toggleAllBtn.style.padding = '5px';
                toggleAllBtn.dataset.category = category;
                toggleAllBtn.onclick = () => toggleAllCheckboxes(category);
                
                section.appendChild(header);
                section.appendChild(toggleAllBtn);
                
                // Add ingredients
                data[category].forEach(item => {
                    const div = document.createElement('div');
                    
                    // Format amount text
                    let amountText = 'okänd mängd';
                    if (item.inventory) {
                        if (category === 'fermentables') {
                            amountText = `${item.inventory.toFixed(2)} kg`;
                        } else if (category === 'hops') {
                            amountText = `${item.inventory.toFixed(2)} g`;
                        } else if (category === 'yeasts') {
                            amountText = `${item.inventory} paket`;
                        }
                    }
                    
                    div.innerHTML = `
                        <input type="checkbox" class="ingredientCheckbox" data-category="${category}" data-name="${item.name}" checked>
                        ${item.name} - ${amountText}
                    `;
                    
                    section.appendChild(div);
                });
                
                content.appendChild(section);
            }
        });
        
        // Add confirm button
        const confirmBtn = document.createElement('button');
        confirmBtn.textContent = 'Bekräfta val';
        confirmBtn.className = 'btn btn-primary';
        confirmBtn.style.marginTop = '20px';
        confirmBtn.onclick = confirmSimpleIngredientSelection;
        content.appendChild(confirmBtn);
        
        // Show the modal
        modal.style.display = 'block';
    }
    
    // Toggle all checkboxes in a category (for simple modal)
    function toggleAllCheckboxes(category) {
        const checkboxes = document.querySelectorAll(`.ingredientCheckbox[data-category="${category}"]`);
        let allChecked = Array.from(checkboxes).every(cb => cb.checked);
        
        checkboxes.forEach(cb => {
            cb.checked = !allChecked;
        });
        
        // Update button text
        const button = document.querySelector(`button[data-category="${category}"]`);
        if (button) {
            button.textContent = allChecked ? 'Markera alla' : 'Avmarkera alla';
        }
    }
    
    // Confirm simple ingredient selection (for simple modal)
    function confirmSimpleIngredientSelection() {
        // Get selected ingredients
        const selectedIngredients = getSelectedIngredients();
        
        // Dispatch event
        document.dispatchEvent(new CustomEvent('ingredientsSelected', {
            detail: { ingredients: selectedIngredients }
        }));
        
        // Hide modal
        const modal = document.getElementById('simpleIngredientModal');
        if (modal) {
            modal.style.display = 'none';
        }
    }
    
    // Get selected ingredients (for simple modal)
    function getSelectedIngredients() {
        const checkboxes = document.querySelectorAll('.ingredientCheckbox');
        const selected = [];
        
        checkboxes.forEach(cb => {
            if (cb.checked) {
                selected.push({
                    category: cb.getAttribute('data-category'),
                    name: cb.getAttribute('data-name')
                });
            }
        });
        
        return selected;
    }
    
    // Handle ingredient selection event
    function handleIngredientSelection(event) {
        const ingredients = event.detail.ingredients;
        APP_STATE.lastSelectedIngredients = ingredients;
        console.log('📦 Ingredients selected:', ingredients);
        
        // Request style suggestions
        requestStyleSuggestions(ingredients);
    }
    
    // Request style suggestions from API
    async function requestStyleSuggestions(ingredients) {
        try {
            const response = await ApiClient.suggestStyles({
                ingredients: ingredients,
                profile: "Grainfather G30"
            });
            
            if (response && response.styles) {
                if (typeof RecipeManager !== 'undefined' && RecipeManager.displayStyleSuggestions) {
                    RecipeManager.displayStyleSuggestions(response.styles);
                } else if (window.displayStyleSuggestions) {
                    window.displayStyleSuggestions(response.styles);
                } else {
                    console.error('❌ No styles display function found');
                    alert('Kunde inte visa stilförslag.');
                }
                
                // Show style suggestions section
                const styleSection = document.getElementById('styleSuggestionsSection');
                if (styleSection) {
                    styleSection.classList.remove('hidden');
                }
            } else {
                console.error('❌ No styles in response:', response);
                alert('Kunde inte hämta stilförslag.');
            }
        } catch (error) {
            console.error('❌ Error requesting style suggestions:', error);
            alert(`Ett fel uppstod: ${error.message}`);
        }
    }
    
    // Display inventory in the main UI
    function displayInventory(data) {
        if (!inventoryDisplay) return;
        
        inventoryDisplay.innerHTML = '';
        
        ['fermentables', 'hops', 'yeasts'].forEach(category => {
            if (data[category] && data[category].length > 0) {
                const section = document.createElement('div');
                section.classList.add('inventory-category');
                
                // Add header
                const header = document.createElement('h3');
                header.textContent = category.charAt(0).toUpperCase() + category.slice(1);
                section.appendChild(header);
                
                // Add ingredients
                data[category].forEach(item => {
                    const div = document.createElement('div');
                    
                    // Format amount text
                    let amountText = 'okänd mängd';
                    if (item.inventory) {
                        if (category === 'fermentables') {
                            amountText = `${item.inventory.toFixed(2)} kg`;
                        } else if (category === 'hops') {
                            amountText = `${item.inventory.toFixed(2)} g`;
                        } else if (category === 'yeasts') {
                            amountText = `${item.inventory} paket`;
                        }
                    }
                    
                    div.textContent = `${item.name} - ${amountText}`;
                    section.appendChild(div);
                });
                
                inventoryDisplay.appendChild(section);
            }
        });
    }
    
    // Public API
    return {
        init,
        fetchInventory,
        displayInventory
    };
})();