/**
 * Fix för knappen "Välj Ingredienser"
 * Detta skript säkerställer att ingrediensvalsfunktionen fungerar korrekt
 */

document.addEventListener('DOMContentLoaded', function() {
    console.log('Ingredient Selection Fix loaded');
    
    // Hitta knappen och kontrollera att den finns
    const selectIngredientsBtn = document.getElementById('selectIngredientsBtn');
    
    if (selectIngredientsBtn) {
        console.log('Found select ingredients button, adding event listener');
        
        // Lägg till en ny eventListener på knappen som har högre prioritet
        selectIngredientsBtn.addEventListener('click', function(e) {
            console.log('Select ingredients button clicked');
            
            // Kör inventoryManager.fetchInventory om det finns
            if (typeof InventoryManager !== 'undefined' && 
                typeof InventoryManager.fetchInventory === 'function') {
                console.log('Calling InventoryManager.fetchInventory');
                InventoryManager.fetchInventory();
            } else {
                console.error('InventoryManager.fetchInventory is not available');
            }
            
            // Förhindra att eventet stoppas av andra handlers
            e.stopPropagation();
        }, true); // true = useCapture, vilket gör att denna körs före andra listeners
    } else {
        console.error('Could not find button with ID selectIngredientsBtn');
    }
    
    // Återställ funktionalitet för andra knappar också
    const generateXmlBtn = document.getElementById('generateXmlBtn');
    if (generateXmlBtn) {
        console.log('Found generate XML button, adding event listener');
        generateXmlBtn.addEventListener('click', function(e) {
            if (typeof RecipeManager !== 'undefined' && 
                typeof RecipeManager.downloadBeerXml === 'function') {
                RecipeManager.downloadBeerXml();
            }
            e.stopPropagation();
        }, true);
    }
    
    // Återställ funktionalitet för bryggarpersonlighetsväljaren
    const brewerPersonalityBtn = document.getElementById('brewerPersonalityBtn');
    if (brewerPersonalityBtn) {
        console.log('Found brewer personality button, adding event listener');
        brewerPersonalityBtn.addEventListener('click', function(e) {
            if (typeof PersonalityManager !== 'undefined' && 
                typeof PersonalityManager.showPersonalityModal === 'function') {
                PersonalityManager.showPersonalityModal();
            }
            e.stopPropagation();
        }, true);
    }
    
    // Kontrollera om knapparna finns i mobilmenyn också
    setTimeout(() => {
        const mobileSidebar = document.querySelector('.mobile-sidebar');
        if (mobileSidebar) {
            console.log('Found mobile sidebar, checking for buttons');
            const mobileSelectBtn = mobileSidebar.querySelector('[id*="selectIngredients"]');
            if (mobileSelectBtn) {
                console.log('Found mobile select ingredients button, adding event listener');
                mobileSelectBtn.addEventListener('click', function() {
                    if (typeof InventoryManager !== 'undefined' && 
                        typeof InventoryManager.fetchInventory === 'function') {
                        InventoryManager.fetchInventory();
                    }
                }, true);
            }
        }
    }, 1000); // Vänta en sekund för att säkerställa att mobilmenyn har skapats
});
