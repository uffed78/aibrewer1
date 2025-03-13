/**
 * Ingredient Selection System
 * Allows users to select multiple ingredients with a visual interface
 */
document.addEventListener('DOMContentLoaded', function() {
    console.log('Ingredient selection system loaded');
    
    const SELECTED_INGREDIENTS_KEY = 'aibrewerSelectedIngredients';
    const ingredientBtn = document.getElementById('selectIngredientsBtn');
    
    // Lägg till denna variabel i början av filen, efter 'use strict'
    let lastSelectedIngredients = []; // Global variabel för att spara valda ingredienser

    // Create the ingredient selection modal
    async function createIngredientModal() {
        // Check if user is logged in
        if (!currentUser) {
            alert("Du måste konfigurera en Brewfather-profil först.");
            document.getElementById('settingsModal').style.display = 'block';
            return;
        }

        // Fetch inventory data if not already loaded
        if (!window.inventoryData) {
            try {
                const response = await fetch(`${baseUrl}/get-inventory`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ 
                        apiId: currentUser.apiId,
                        apiKey: currentUser.apiKey
                    })
                });
                
                const data = await response.json();
                if (data.error) {
                    throw new Error(data.error);
                }
                window.inventoryData = data;
            } catch (error) {
                alert(`Kunde inte hämta inventory: ${error.message}`);
                return;
            }
        }

        let modal = document.getElementById('ingredientModal');
        if (!modal) {
            modal = document.createElement('div');
            modal.id = 'ingredientModal';
            modal.className = 'modal ingredient-modal';
            
            const modalContent = document.createElement('div');
            modalContent.className = 'modal-content ingredient-modal-content';
            
            const closeBtn = document.createElement('span');
            closeBtn.className = 'close-button';
            closeBtn.innerHTML = '&times;';
            closeBtn.onclick = () => modal.style.display = 'none';
            
            const heading = document.createElement('h2');
            heading.textContent = 'Välj från ditt Inventory';
            
            // Create category tabs
            const categoryTabs = document.createElement('div');
            categoryTabs.className = 'category-tabs';
            
            // Create container for ingredients
            const ingredientsContainer = document.createElement('div');
            ingredientsContainer.className = 'ingredients-container';
            
            // Define categories with icons
            const categories = {
                fermentables: { name: "Malt", icon: "🌾" },
                hops: { name: "Humle", icon: "🌿" },
                yeasts: { name: "Jäst", icon: "🧫" }
            };
            
            // Create tabs and ingredient groups
            Object.entries(categories).forEach(([categoryId, category], index) => {
                // Create tab
                const tab = document.createElement('div');
                tab.className = 'category-tab';
                if (index === 0) tab.classList.add('active');
                tab.innerHTML = `
                    <span class="category-icon">${category.icon}</span>
                    <span>${category.name}</span>
                `;
                
                tab.addEventListener('click', () => {
                    document.querySelectorAll('.category-tab').forEach(t => t.classList.remove('active'));
                    tab.classList.add('active');
                    document.querySelectorAll('.ingredient-group').forEach(g => g.style.display = 'none');
                    document.querySelector(`.ingredient-group[data-category="${categoryId}"]`).style.display = 'grid';
                });
                
                categoryTabs.appendChild(tab);
                
                // Create ingredient group
                const group = document.createElement('div');
                group.className = 'ingredient-group';
                group.dataset.category = categoryId;
                group.style.display = index === 0 ? 'grid' : 'none';
                
                // Add ingredients from inventory
                if (window.inventoryData && window.inventoryData[categoryId]) {
                    window.inventoryData[categoryId].forEach(item => {
                        const card = document.createElement('div');
                        card.className = 'ingredient-card';
                        card.dataset.id = `${categoryId}:${item.name}`;
                        
                        // Format amount based on category
                        let amountText = '';
                        if (item.inventory !== undefined) {
                            if (categoryId === 'fermentables') amountText = `${item.inventory.toFixed(2)} kg`;
                            else if (categoryId === 'hops') amountText = `${item.inventory.toFixed(2)} g`;
                            else if (categoryId === 'yeasts') amountText = `${item.inventory} pkg`;
                        }

                        // Add extra info based on category
                        let extraInfo = '';
                        if (categoryId === 'fermentables' && item.color) {
                            extraInfo = `${item.color} EBC`;
                        } else if (categoryId === 'hops' && item.alpha) {
                            extraInfo = `${item.alpha}% α`;
                        }
                        
                        card.innerHTML = `
                            <div class="ingredient-icon">${category.icon}</div>
                            <div class="ingredient-info">
                                <div class="ingredient-name">${item.name}</div>
                                <div class="ingredient-description">
                                    ${amountText}${extraInfo ? ` • ${extraInfo}` : ''}
                                </div>
                            </div>
                            <div class="ingredient-select">
                                <span class="select-indicator">✓</span>
                            </div>
                        `;
                        
                        card.addEventListener('click', () => {
                            card.classList.toggle('selected');
                            updateSelectionCounter();
                        });
                        
                        group.appendChild(card);
                    });
                }
                
                ingredientsContainer.appendChild(group);
            });
            
            // Add search functionality
            const searchBox = document.createElement('div');
            searchBox.className = 'search-box';
            searchBox.innerHTML = `
                <input type="text" placeholder="Sök ingredienser..." id="ingredientSearch">
            `;
            
            // Add selection controls
            const selectionInfo = document.createElement('div');
            selectionInfo.className = 'selection-info';
            selectionInfo.innerHTML = `
                <span class="selection-counter">Valda ingredienser: <span id="selectedCount">0</span></span>
                <div class="selection-actions">
                    <button id="cancelSelection" class="btn btn-secondary">Avbryt</button>
                    <button id="confirmSelection" class="btn btn-primary">Använd valda</button>
                </div>
            `;
            
            // Add event listeners
            searchBox.querySelector('#ingredientSearch').addEventListener('input', (e) => {
                const searchTerm = e.target.value.toLowerCase();
                document.querySelectorAll('.ingredient-card').forEach(card => {
                    const name = card.querySelector('.ingredient-name').textContent.toLowerCase();
                    card.style.display = name.includes(searchTerm) ? '' : 'none';
                });
            });
            
            selectionInfo.querySelector('#cancelSelection').addEventListener('click', () => {
                modal.style.display = 'none';
            });
            
            selectionInfo.querySelector('#confirmSelection').addEventListener('click', async () => {
                const selectedIngredients = Array.from(document.querySelectorAll('.ingredient-card.selected')).map(card => {
                    const [category, name] = card.dataset.id.split(':');
                    return { category, name };
                });
                
                // Spara valda ingredienser i window.lastSelectedIngredients
                window.lastSelectedIngredients = selectedIngredients;
                
                // Skicka direkt till GPT för stilförslag
                try {
                    const response = await fetch(`${baseUrl}/suggest-styles`, {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({
                            ingredients: selectedIngredients,
                            profile: "Grainfather G30",
                            personality: window.currentPersonality
                        })
                    });
                    const data = await response.json();
                    
                    // Visa stilförslagen genom att anropa den globala funktionen
                    window.displayStyleSuggestions(data.styles);
                    
                    // Visa stilförslag-sektionen
                    document.getElementById('styleSuggestionsSection').classList.remove('hidden');
                    
                    // Stäng ingredient-selection modal
                    modal.style.display = 'none';
                } catch (error) {
                    console.error('Fel vid stilförslag:', error);
                    alert('Ett fel uppstod när stilförslag skulle hämtas');
                }
            });
            
            modalContent.appendChild(closeBtn);
            modalContent.appendChild(heading);
            modalContent.appendChild(searchBox);
            modalContent.appendChild(categoryTabs);
            modalContent.appendChild(ingredientsContainer);
            modalContent.appendChild(selectionInfo);
            
            modal.appendChild(modalContent);
            document.body.appendChild(modal);
        }
        
        return modal;
    }
    
    // Update selection counter
    function updateSelectionCounter() {
        const count = document.querySelectorAll('.ingredient-card.selected').length;
        const counter = document.getElementById('selectedCount');
        if (counter) counter.textContent = count;
    }
    
    // Add click handler to the ingredient selection button
    if (ingredientBtn) {
        ingredientBtn.addEventListener('click', async () => {
            const modal = await createIngredientModal();
            if (modal) modal.style.display = 'block';
        });
    }
    
    console.log('Ingredient selection system initialized');
});

/**
 * Ingredient Selection Module
 * Provides an enhanced UI for selecting brewing ingredients
 */
const IngredientSelector = (() => {
    // Private variables
    let selectedIngredients = [];
    let allIngredients = {
        fermentables: [],
        hops: [],
        yeasts: []
    };
    let activeCategory = 'fermentables';
    let modal = null;
    
    // Initialize the module
    function init(inventoryData) {
        console.log('🧪 Initializing Ingredient Selector...');
        createModal();
        
        if (inventoryData) {
            loadIngredients(inventoryData);
        }
        
        console.log('🧪 Ingredient Selector initialized');
    }
    
    // Create the modal structure
    function createModal() {
        // Remove any existing modal
        if (document.getElementById('ingredientSelectorModal')) {
            document.getElementById('ingredientSelectorModal').remove();
        }
        
        modal = document.createElement('div');
        modal.id = 'ingredientSelectorModal';
        modal.className = 'ingredient-modal';
        
        modal.innerHTML = `
            <div class="ingredient-modal-content">
                <span class="close-button">&times;</span>
                <h2>Select Ingredients</h2>
                
                <div class="category-tabs">
                    <div class="category-tab active" data-category="fermentables">
                        <span class="category-icon">🌾</span> Malts
                    </div>
                    <div class="category-tab" data-category="hops">
                        <span class="category-icon">🌿</span> Hops
                    </div>
                    <div class="category-tab" data-category="yeasts">
                        <span class="category-icon">🔬</span> Yeasts
                    </div>
                </div>
                
                <div class="search-box">
                    <input type="text" placeholder="Search ingredients..." id="ingredientSearch">
                </div>
                
                <div class="ingredients-container">
                    <div class="ingredient-group" id="ingredientGroup"></div>
                </div>
                
                <div class="selection-info">
                    <div class="selection-counter">
                        <span id="selectedCount">0</span> ingredients selected
                    </div>
                    <div class="selection-actions">
                        <button class="btn btn-secondary" id="cancelSelection">Cancel</button>
                        <button class="btn btn-primary" id="confirmSelection">Continue</button>
                    </div>
                </div>
            </div>
        `;
        
        document.body.appendChild(modal);
        
        // Set up event listeners
        modal.querySelector('.close-button').addEventListener('click', closeModal);
        modal.querySelector('#cancelSelection').addEventListener('click', closeModal);
        modal.querySelector('#confirmSelection').addEventListener('click', confirmSelection);
        
        // Category tabs
        modal.querySelectorAll('.category-tab').forEach(tab => {
            tab.addEventListener('click', () => {
                setActiveCategory(tab.dataset.category);
            });
        });
        
        // Search functionality
        modal.querySelector('#ingredientSearch').addEventListener('input', filterIngredients);
    }
    
    // Load ingredients from inventory data
    function loadIngredients(data) {
        allIngredients = {
            fermentables: data.fermentables || [],
            hops: data.hops || [],
            yeasts: data.yeasts || []
        };
        
        // Set all ingredients as initially selected
        selectedIngredients = [];
        
        // Add all fermentables
        allIngredients.fermentables.forEach(item => {
            selectedIngredients.push({
                category: 'fermentables',
                name: item.name,
                id: item._id
            });
        });
        
        // Add all hops
        allIngredients.hops.forEach(item => {
            selectedIngredients.push({
                category: 'hops',
                name: item.name,
                id: item._id
            });
        });
        
        // Add all yeasts
        allIngredients.yeasts.forEach(item => {
            selectedIngredients.push({
                category: 'yeasts',
                name: item.name,
                id: item._id
            });
        });
        
        // Update the counter
        updateSelectionCounter();
        
        // Render the initial category
        renderIngredients(activeCategory);
    }
    
    // Set active category and render ingredients
    function setActiveCategory(category) {
        activeCategory = category;
        
        // Update active tab styling
        modal.querySelectorAll('.category-tab').forEach(tab => {
            tab.classList.toggle('active', tab.dataset.category === category);
        });
        
        // Render ingredients for this category
        renderIngredients(category);
    }
    
    // Render ingredients for selected category
    function renderIngredients(category) {
        const container = modal.querySelector('#ingredientGroup');
        container.innerHTML = '';
        
        if (!allIngredients[category] || allIngredients[category].length === 0) {
            container.innerHTML = '<p>No ingredients found in this category.</p>';
            return;
        }
        
        // Add Select/Deselect All button
        const selectAllContainer = document.createElement('div');
        selectAllContainer.className = 'select-all-container';
        
        const selectAllBtn = document.createElement('button');
        selectAllBtn.className = 'btn btn-secondary select-all-btn';
        selectAllBtn.innerHTML = 'Markera/Avmarkera alla';
        selectAllBtn.onclick = () => toggleAllInCategory(category);
        
        selectAllContainer.appendChild(selectAllBtn);
        container.appendChild(selectAllContainer);
        
        // Continue with existing ingredient rendering...
        allIngredients[category].forEach(item => {
            const isSelected = selectedIngredients.some(
                selected => selected.name === item.name && selected.category === category
            );
            
            // Get appropriate icon
            const icon = getCategoryIcon(category);
            
            // Format amount text
            let amountText = 'Unknown amount';
            if (item.inventory !== undefined) {
                if (category === 'fermentables') {
                    amountText = `${Number(item.inventory).toFixed(2)} kg`;
                } else if (category === 'hops') {
                    amountText = `${Number(item.inventory).toFixed(2)} g`;
                } else if (category === 'yeasts') {
                    amountText = `${item.inventory} pkg`;
                }
            }
            
            // Create ingredient card
            const card = document.createElement('div');
            card.className = `ingredient-card ${isSelected ? 'selected' : ''}`;
            card.setAttribute('data-name', item.name);
            card.setAttribute('data-category', category);
            card.setAttribute('data-id', item._id || '');
            
            card.innerHTML = `
                <div class="ingredient-icon">${icon}</div>
                <div class="ingredient-info">
                    <div class="ingredient-name">${item.name}</div>
                    <div class="ingredient-description">${amountText}</div>
                </div>
                <div class="ingredient-select">
                    <span class="select-indicator">✓</span>
                </div>
            `;
            
            // Add click handler
            card.addEventListener('click', () => toggleIngredient(card));
            
            container.appendChild(card);
        });
    }

    function toggleAllInCategory(category) {
        const cards = modal.querySelectorAll(`.ingredient-card[data-category="${category}"]`);
        const allSelected = Array.from(cards).every(card => card.classList.contains('selected'));
        
        cards.forEach(card => {
            if (allSelected) {
                // Deselect all
                card.classList.remove('selected');
                const existingIndex = selectedIngredients.findIndex(
                    item => item.name === card.dataset.name && item.category === category
                );
                if (existingIndex >= 0) {
                    selectedIngredients.splice(existingIndex, 1);
                }
            } else {
                // Select all
                card.classList.add('selected');
                if (!selectedIngredients.some(item => item.name === card.dataset.name && item.category === category)) {
                    selectedIngredients.push({
                        name: card.dataset.name,
                        category: category,
                        id: card.dataset.id
                    });
                }
            }
        });
        
        updateSelectionCounter();
    }
    
    // Get icon for category
    function getCategoryIcon(category) {
        switch (category) {
            case 'fermentables': return '🌾';
            case 'hops': return '🌿';
            case 'yeasts': return '🔬';
            default: return '📦';
        }
    }
    
    // Toggle ingredient selection
    function toggleIngredient(card) {
        const name = card.dataset.name;
        const category = card.dataset.category;
        const id = card.dataset.id;
        
        // Check if already selected
        const existingIndex = selectedIngredients.findIndex(
            item => item.name === name && item.category === category
        );
        
        if (existingIndex >= 0) {
            // Remove from selection
            selectedIngredients.splice(existingIndex, 1);
            card.classList.remove('selected');
        } else {
            // Add to selection
            selectedIngredients.push({
                name,
                category,
                id
            });
            card.classList.add('selected');
        }
        
        // Update counter
        updateSelectionCounter();
    }
    
    // Update the selection counter
    function updateSelectionCounter() {
        const counter = modal.querySelector('#selectedCount');
        if (counter) {
            counter.textContent = selectedIngredients.length;
        }
    }
    
    // Filter ingredients based on search input
    function filterIngredients() {
        const searchTerm = modal.querySelector('#ingredientSearch').value.toLowerCase();
        const cards = modal.querySelectorAll('.ingredient-card');
        
        cards.forEach(card => {
            const name = card.dataset.name.toLowerCase();
            if (name.includes(searchTerm)) {
                card.style.display = '';
            } else {
                card.style.display = 'none';
            }
        });
    }
    
    // Show the ingredient selector modal
    function showModal(inventoryData) {
        if (!modal) {
            createModal();
        }
        
        if (inventoryData) {
            loadIngredients(inventoryData);
        }
        
        modal.style.display = 'block';
    }
    
    // Close the modal
    function closeModal() {
        if (modal) {
            modal.style.display = 'none';
        }
    }
    
    // Confirm selection and dispatch event
    function confirmSelection() {
        // Dispatch event with selected ingredients
        document.dispatchEvent(new CustomEvent('ingredientsSelected', {
            detail: { ingredients: selectedIngredients }
        }));
        
        // Close modal
        closeModal();
    }
    
    // Public API
    return {
        init,
        showModal,
        closeModal
    };
})();

// Auto-initialize if InventoryManager is available
document.addEventListener('DOMContentLoaded', () => {
    // Listen for events from InventoryManager
    document.addEventListener('inventoryLoaded', (event) => {
        if (event.detail && event.detail.inventoryData) {
            IngredientSelector.init(event.detail.inventoryData);
        }
    });
});
