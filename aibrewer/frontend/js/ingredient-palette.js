/**
 * Brygg-paletten: Visuell ingrediensväljare för AIBrewer
 * En modern, interaktiv väljare för ingredienser baserad på kategori och egenskaper
 */
document.addEventListener('DOMContentLoaded', function() {
    console.log('Ingredient palette loaded');

    // Konstanter och selectors
    const PALETTE_STORAGE_KEY = 'ingredient_palette_settings';
    const inventoryDisplay = document.getElementById('inventoryDisplay');
    
    // Globala variabler för ingrediensdata
    let allIngredients = {
        fermentables: [],
        hops: [],
        yeasts: []
    };
    
    let selectedIngredients = [];
    
    // Skapa standardgränssnittet för ingrediensväljaren
    function initIngredientPalette() {
        // Skapa grunden för palette UI om den inte finns
        if (!document.getElementById('ingredient-palette')) {
            // Skapa en container som ersätter default inventory display
            const paletteContainer = document.createElement('div');
            paletteContainer.id = 'ingredient-palette';
            paletteContainer.className = 'ingredient-palette';
            
            // Skapa flikar för kategorier
            const tabsContainer = document.createElement('div');
            tabsContainer.className = 'palette-tabs';
            
            // Definiera kategoriflikar
            const categories = [
                { id: 'fermentables', name: 'Malt', icon: '🌾' },
                { id: 'hops', name: 'Humle', icon: '🌿' },
                { id: 'yeasts', name: 'Jäst', icon: '🧫' }
            ];
            
            // Skapa flikarna
            categories.forEach(category => {
                const tab = document.createElement('div');
                tab.className = 'palette-tab';
                tab.dataset.category = category.id;
                tab.innerHTML = `
                    <span class="tab-icon">${category.icon}</span>
                    <span class="tab-name">${category.name}</span>
                `;
                
                tab.addEventListener('click', () => {
                    // Aktivera fliken och visa dess innehåll
                    document.querySelectorAll('.palette-tab').forEach(t => t.classList.remove('active'));
                    tab.classList.add('active');
                    showCategoryContent(category.id);
                });
                
                tabsContainer.appendChild(tab);
            });
            
            // Skapa sökfältet
            const searchContainer = document.createElement('div');
            searchContainer.className = 'palette-search';
            searchContainer.innerHTML = `
                <input type="text" id="ingredient-search" placeholder="Sök ingredienser...">
                <div class="search-icon">🔍</div>
            `;
            
            // Skapa filter-sektion
            const filtersContainer = document.createElement('div');
            filtersContainer.className = 'palette-filters';
            filtersContainer.innerHTML = `
                <div class="filter-title">Filter</div>
                <div id="active-filters" class="active-filters"></div>
            `;
            
            // Skapa innehållssektion
            const contentContainer = document.createElement('div');
            contentContainer.className = 'palette-content';
            contentContainer.id = 'palette-content';
            
            // Skapa urvalsvyn
            const selectionContainer = document.createElement('div');
            selectionContainer.className = 'palette-selection';
            selectionContainer.innerHTML = `
                <h3>Valda ingredienser</h3>
                <div id="selected-ingredients" class="selected-ingredients"></div>
            `;
            
            // Sätt samman alla delar
            paletteContainer.appendChild(tabsContainer);
            paletteContainer.appendChild(searchContainer);
            paletteContainer.appendChild(filtersContainer);
            paletteContainer.appendChild(contentContainer);
            paletteContainer.appendChild(selectionContainer);
            
            // Ersätt standardvyn med vår palette
            if (inventoryDisplay) {
                inventoryDisplay.innerHTML = '';
                inventoryDisplay.appendChild(paletteContainer);
            }
            
            // Initiera sökfunktionen
            document.getElementById('ingredient-search').addEventListener('input', filterIngredients);
            
            // Aktivera första fliken som standard
            tabsContainer.querySelector('.palette-tab').classList.add('active');
            showCategoryContent(categories[0].id);
        }
    }
    
    // Visa ingredienser för en specifik kategori
    function showCategoryContent(categoryId) {
        const contentContainer = document.getElementById('palette-content');
        contentContainer.innerHTML = '';
        
        // Om vi inte har data, visa en laddningsmeddelande
        if (!allIngredients[categoryId] || allIngredients[categoryId].length === 0) {
            contentContainer.innerHTML = '<div class="loading-message">Ingen data tillgänglig. Hämta inventory först.</div>';
            return;
        }
        
        // Sortera ingredienser - malt efter färg, humle efter alfa, jäst efter typ
        const sortedIngredients = [...allIngredients[categoryId]];
        if (categoryId === 'fermentables') {
            sortedIngredients.sort((a, b) => (a.color || 0) - (b.color || 0));
        } else if (categoryId === 'hops') {
            sortedIngredients.sort((a, b) => (b.alpha || 0) - (a.alpha || 0));
        } else if (categoryId === 'yeasts') {
            sortedIngredients.sort((a, b) => (a.name || '').localeCompare(b.name || ''));
        }
        
        // Skapa filter-alternativ baserat på kategori
        updateCategoryFilters(categoryId, sortedIngredients);
        
        // Skapa kort för varje ingrediens
        const grid = document.createElement('div');
        grid.className = 'ingredient-grid';
        
        sortedIngredients.forEach(ingredient => {
            const card = createIngredientCard(ingredient, categoryId);
            grid.appendChild(card);
        });
        
        contentContainer.appendChild(grid);
    }
    
    // Skapa ett ingredienskort
    function createIngredientCard(ingredient, categoryId) {
        const card = document.createElement('div');
        card.className = 'ingredient-card';
        card.dataset.name = ingredient.name;
        card.dataset.category = categoryId;
        
        // Kolla om ingrediensen redan är vald
        const isSelected = selectedIngredients.some(i => 
            i.name === ingredient.name && i.category === categoryId);
        
        if (isSelected) {
            card.classList.add('selected');
        }
        
        // Skapa visuella indikatorer baserat på kategori
        let colorIndicator = '';
        let details = '';
        
        if (categoryId === 'fermentables') {
            const color = ingredient.color || 0;
            // Skapa en färgrepresentation baserad på SRM
            const srmColor = getSrmColorStyle(color);
            colorIndicator = `<div class="color-indicator" style="background-color: ${srmColor}"></div>`;
            details = `<div class="ingredient-details">
                <span class="detail-label">Färg:</span> <span class="detail-value">${color} SRM</span>
                <span class="detail-label">Lager:</span> <span class="detail-value">${ingredient.inventory ? ingredient.inventory.toFixed(2) : 0} kg</span>
            </div>`;
        } else if (categoryId === 'hops') {
            const alpha = ingredient.alpha || 0;
            // Skapa en färgrepresentation baserad på alfa
            const alphaIntensity = Math.min(100, Math.max(20, alpha * 5));
            colorIndicator = `<div class="alpha-indicator" style="background-color: hsl(120, ${alphaIntensity}%, 40%)"></div>`;
            details = `<div class="ingredient-details">
                <span class="detail-label">Alfa:</span> <span class="detail-value">${alpha}%</span>
                <span class="detail-label">Lager:</span> <span class="detail-value">${ingredient.inventory ? ingredient.inventory.toFixed(0) : 0} g</span>
            </div>`;
        } else if (categoryId === 'yeasts') {
            details = `<div class="ingredient-details">
                <span class="detail-label">Typ:</span> <span class="detail-value">${ingredient.type || 'Okänd'}</span>
                <span class="detail-label">Lager:</span> <span class="detail-value">${ingredient.inventory || 0} pkg</span>
            </div>`;
        }
        
        // Skapa lagerstatus-indikator
        let inventoryLevel = '';
        if (ingredient.inventory) {
            let levelClass = 'low';
            if (categoryId === 'fermentables' && ingredient.inventory > 2) levelClass = 'good';
            else if (categoryId === 'hops' && ingredient.inventory > 50) levelClass = 'good';
            else if (categoryId === 'yeasts' && ingredient.inventory > 1) levelClass = 'good';
            
            inventoryLevel = `<div class="inventory-level ${levelClass}"></div>`;
        }
        
        // Sätt ihop kortet
        card.innerHTML = `
            ${colorIndicator}
            <div class="ingredient-name">${ingredient.name}</div>
            ${details}
            ${inventoryLevel}
            <button class="select-btn">${isSelected ? 'Avmarkera' : 'Välj'}</button>
        `;
        
        // Lägg till klickhändelse för val av ingrediens
        card.querySelector('.select-btn').addEventListener('click', (e) => {
            e.stopPropagation(); // Förhindra att kortets klickhändelse aktiveras
            toggleIngredientSelection(ingredient.name, categoryId, card);
        });
        
        // Hela kortet kan också klickas för att välja
        card.addEventListener('click', () => {
            toggleIngredientSelection(ingredient.name, categoryId, card);
        });
        
        return card;
    }
    
    // Växla val av ingrediens
    function toggleIngredientSelection(name, category, cardElement) {
        // Kolla om ingrediensen redan är vald
        const existingIndex = selectedIngredients.findIndex(i => 
            i.name === name && i.category === category);
        
        if (existingIndex >= 0) {
            // Ta bort från valda ingredienser
            selectedIngredients.splice(existingIndex, 1);
            cardElement.classList.remove('selected');
            cardElement.querySelector('.select-btn').textContent = 'Välj';
        } else {
            // Lägg till i valda ingredienser
            selectedIngredients.push({ name, category });
            cardElement.classList.add('selected');
            cardElement.querySelector('.select-btn').textContent = 'Avmarkera';
        }
        
        // Uppdatera listan med valda ingredienser
        updateSelectedIngredientsList();
    }
    
    // Uppdatera listan med valda ingredienser
    function updateSelectedIngredientsList() {
        const container = document.getElementById('selected-ingredients');
        if (!container) return;
        
        container.innerHTML = '';
        
        if (selectedIngredients.length === 0) {
            container.innerHTML = '<div class="no-selection">Inga ingredienser valda</div>';
            return;
        }
        
        // Gruppera valda ingredienser efter kategori
        const groupedByCategory = {
            fermentables: selectedIngredients.filter(i => i.category === 'fermentables'),
            hops: selectedIngredients.filter(i => i.category === 'hops'),
            yeasts: selectedIngredients.filter(i => i.category === 'yeasts')
        };
        
        // Skapa kategorigrupper
        Object.entries(groupedByCategory).forEach(([category, items]) => {
            if (items.length === 0) return;
            
            const categoryName = category === 'fermentables' ? 'Malt' : 
                               category === 'hops' ? 'Humle' : 'Jäst';
            
            const categoryGroup = document.createElement('div');
            categoryGroup.className = 'selection-category';
            categoryGroup.innerHTML = `<div class="category-title">${categoryName}</div>`;
            
            // Lista varje vald ingrediens
            items.forEach(item => {
                const ingredient = allIngredients[category].find(i => i.name === item.name) || {};
                const ingredientItem = document.createElement('div');
                ingredientItem.className = 'selected-item';
                
                let inventoryText = '';
                if (category === 'fermentables') {
                    inventoryText = `${ingredient.inventory ? ingredient.inventory.toFixed(2) : 0} kg`;
                } else if (category === 'hops') {
                    inventoryText = `${ingredient.inventory ? ingredient.inventory.toFixed(0) : 0} g`;
                } else {
                    inventoryText = `${ingredient.inventory || 0} pkg`;
                }
                
                ingredientItem.innerHTML = `
                    <span class="item-name">${item.name}</span>
                    <span class="item-inventory">${inventoryText}</span>
                    <button class="remove-btn">✕</button>
                `;
                
                // Ta bort ingrediensen från listan
                ingredientItem.querySelector('.remove-btn').addEventListener('click', () => {
                    toggleIngredientSelection(item.name, category, 
                        document.querySelector(`.ingredient-card[data-name="${item.name}"][data-category="${category}"]`));
                });
                
                categoryGroup.appendChild(ingredientItem);
            });
            
            container.appendChild(categoryGroup);
        });
        
        // Lägg till knapp för att bekräfta val
        const confirmButton = document.createElement('button');
        confirmButton.className = 'confirm-selection-btn';
        confirmButton.textContent = 'Bekräfta val';
        confirmButton.addEventListener('click', () => {
            confirmIngredientSelection();
        });
        container.appendChild(confirmButton);
    }
    
    // Bekräfta val och uppdatera de vanliga checkboxarna i den dolda originalvyn
    function confirmIngredientSelection() {
        // Hitta alla checkboxes i den ursprungliga vyn och uppdatera dem
        const checkboxes = document.querySelectorAll('.ingredientCheckbox');
        
        checkboxes.forEach(checkbox => {
            const name = checkbox.getAttribute('data-name');
            const category = checkbox.getAttribute('data-category');
            
            // Kolla om denna ingrediens är vald i vår nya vy
            const isSelected = selectedIngredients.some(i => 
                i.name === name && i.category === category);
                
            // Uppdatera checkboxen
            checkbox.checked = isSelected;
        });
        
        // Visa bekräftelsemeddelande
        showNotification('Ingrediensval uppdaterat!');
    }
    
    // Filtrera ingredienser baserat på sökterm
    function filterIngredients() {
        const searchTerm = document.getElementById('ingredient-search').value.toLowerCase();
        const activeCategory = document.querySelector('.palette-tab.active').dataset.category;
        
        // Hitta alla kort
        const cards = document.querySelectorAll(`.ingredient-card[data-category="${activeCategory}"]`);
        
        // Filtrera baserat på sökterm
        cards.forEach(card => {
            const name = card.dataset.name.toLowerCase();
            if (name.includes(searchTerm)) {
                card.style.display = '';
            } else {
                card.style.display = 'none';
            }
        });
    }
    
    // Uppdatera filtermöjligheter baserat på kategori
    function updateCategoryFilters(categoryId, ingredients) {
        const filtersContainer = document.querySelector('.active-filters');
        filtersContainer.innerHTML = '';
        
        // Skapa kategorispecifika filter
        if (categoryId === 'fermentables') {
            // Skapa filter för malt baserat på färg och typ
            const colorFilters = [
                { name: 'Ljusa (<5 SRM)', filter: item => (item.color || 0) < 5 },
                { name: 'Medium (5-15 SRM)', filter: item => (item.color || 0) >= 5 && (item.color || 0) < 15 },
                { name: 'Mörka (>15 SRM)', filter: item => (item.color || 0) >= 15 }
            ];
            
            colorFilters.forEach(filter => {
                const btn = document.createElement('button');
                btn.className = 'filter-btn';
                btn.textContent = filter.name;
                btn.addEventListener('click', () => {
                    applyFilter(categoryId, filter.filter);
                });
                filtersContainer.appendChild(btn);
            });
        } else if (categoryId === 'hops') {
            // Skapa filter för humle baserat på alfa
            const alphaFilters = [
                { name: 'Låg alfa (<5%)', filter: item => (item.alpha || 0) < 5 },
                { name: 'Medium alfa (5-10%)', filter: item => (item.alpha || 0) >= 5 && (item.alpha || 0) < 10 },
                { name: 'Hög alfa (>10%)', filter: item => (item.alpha || 0) >= 10 }
            ];
            
            alphaFilters.forEach(filter => {
                const btn = document.createElement('button');
                btn.className = 'filter-btn';
                btn.textContent = filter.name;
                btn.addEventListener('click', () => {
                    applyFilter(categoryId, filter.filter);
                });
                filtersContainer.appendChild(btn);
            });
        }
        
        // Lägg till filter för lager
        const inventoryFilter = document.createElement('button');
        inventoryFilter.className = 'filter-btn';
        inventoryFilter.textContent = 'Finns i lager';
        inventoryFilter.addEventListener('click', () => {
            applyFilter(categoryId, item => item.inventory && item.inventory > 0);
        });
        filtersContainer.appendChild(inventoryFilter);
        
        // Lägg till reset-knapp
        const resetBtn = document.createElement('button');
        resetBtn.className = 'filter-btn reset';
        resetBtn.textContent = 'Visa alla';
        resetBtn.addEventListener('click', () => {
            // Återställ alla filter
            document.querySelectorAll(`.ingredient-card[data-category="${categoryId}"]`).forEach(card => {
                card.style.display = '';
            });
        });
        filtersContainer.appendChild(resetBtn);
    }
    
    // Tillämpa filter på ingredienser
    function applyFilter(categoryId, filterFunction) {
        const cards = document.querySelectorAll(`.ingredient-card[data-category="${categoryId}"]`);
        
        cards.forEach(card => {
            const name = card.dataset.name;
            const ingredient = allIngredients[categoryId].find(i => i.name === name);
            
            if (ingredient && filterFunction(ingredient)) {
                card.style.display = '';
            } else {
                card.style.display = 'none';
            }
        });
    }
    
    // Helper-funktion för att konvertera SRM till färg (CSS)
    function getSrmColorStyle(srm) {
        // SRM till ungefärlig färg (förenklade värden)
        const srmMap = [
            {srm: 0, color: '#FFE699'},
            {srm: 1, color: '#FFD878'},
            {srm: 2, color: '#FFCA5A'},
            {srm: 3, color: '#FFBF42'},
            {srm: 4, color: '#FBB123'},
            {srm: 5, color: '#F8A600'},
            {srm: 6, color: '#F39C00'},
            {srm: 7, color: '#EA8F00'},
            {srm: 8, color: '#E58500'},
            {srm: 9, color: '#DE7C00'},
            {srm: 10, color: '#D77200'},
            {srm: 11, color: '#CF6900'},
            {srm: 12, color: '#CB6200'},
            {srm: 13, color: '#C35900'},
            {srm: 14, color: '#BB5100'},
            {srm: 15, color: '#B54C00'},
            {srm: 16, color: '#B04500'},
            {srm: 17, color: '#A63E00'},
            {srm: 18, color: '#A13700'},
            {srm: 19, color: '#9B3200'},
            {srm: 20, color: '#952D00'},
            {srm: 21, color: '#8E2900'},
            {srm: 22, color: '#882300'},
            {srm: 23, color: '#821E00'},
            {srm: 24, color: '#7B1A00'},
            {srm: 25, color: '#771900'},
            {srm: 26, color: '#701400'},
            {srm: 27, color: '#6A0E00'},
            {srm: 28, color: '#660D00'},
            {srm: 29, color: '#5E0B00'},
            {srm: 30, color: '#5A0A02'},
            {srm: 31, color: '#600903'},
            {srm: 32, color: '#520907'},
            {srm: 33, color: '#4C0505'},
            {srm: 34, color: '#470606'},
            {srm: 35, color: '#440607'},
            {srm: 36, color: '#3F0708'},
            {srm: 37, color: '#3B0607'},
            {srm: 38, color: '#3A070B'},
            {srm: 39, color: '#36080A'},
            {srm: 40, color: '#2F0A0B'},
            {srm: 41, color: '#2B0C0E'}
        ];
        
        // Hitta närmaste färg
        if (srm <= 0) return srmMap[0].color;
        if (srm >= 41) return srmMap[srmMap.length-1].color;
        
        const lowerBound = Math.floor(srm);
        const upperBound = Math.ceil(srm);
        
        if (lowerBound === upperBound) {
            return srmMap[lowerBound].color;
        }
        
        const lower = srmMap[lowerBound];
        const upper = srmMap[upperBound];
        
        return lower.color; // För enkelhetens skull, använd bara den lägre färgen
    }
    
    // Visa en notifikation
    function showNotification(message) {
        const notification = document.createElement('div');
        notification.className = 'palette-notification';
        notification.textContent = message;
        document.body.appendChild(notification);
        
        // Animera in
        setTimeout(() => {
            notification.classList.add('visible');
        }, 10);
        
        // Animera ut efter en stund
        setTimeout(() => {
            notification.classList.remove('visible');
            setTimeout(() => {
                document.body.removeChild(notification);
            }, 300);
        }, 2000);
    }
    
    // Lyssna på original-knappen för att hämta inventory
    const originalGetInventoryBtn = document.getElementById('getInventoryBtn');
    if (originalGetInventoryBtn) {
        const originalClickHandler = originalGetInventoryBtn.onclick;
        originalGetInventoryBtn.onclick = async function(e) {
            // Låt originalfunktionen köras först för att hämta data
            if (originalClickHandler) {
                await originalClickHandler.call(this, e);
            }
            
            // Efter att datan har hämtats, lagra den och initiera vår palette
            setTimeout(() => {
                if (window.inventoryData) {
                    allIngredients = window.inventoryData;
                    initIngredientPalette();
                    
                    // Aktivera standardfliken
                    const activeTab = document.querySelector('.palette-tab');
                    if (activeTab) {
                        activeTab.click();
                    }
                }
            }, 500); // Vänta en kort stund för att säkerställa att datan har laddats
        };
    }
    
    // Check if we already have inventory data
    if (window.inventoryData) {
        allIngredients = window.inventoryData;
        initIngredientPalette();
    }
    
    // Exportera funktioner som kan användas av andra skript
    window.ingredientPalette = {
        init: initIngredientPalette,
        getSelectedIngredients: () => selectedIngredients,
        setData: (data) => {
            allIngredients = data;
            initIngredientPalette();
        }
    };
});
