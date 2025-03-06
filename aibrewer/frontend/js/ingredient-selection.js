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
