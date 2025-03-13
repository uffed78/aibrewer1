document.addEventListener('DOMContentLoaded', function() {
    console.log('Mobile nav script loaded');
    
    const header = document.querySelector('.app-header');
    const sidebar = document.querySelector('.sidebar');
    
    // Skapa hamburger-knappen
    const hamburgerBtn = document.createElement('button');
    hamburgerBtn.className = 'hamburger-btn';
    hamburgerBtn.innerHTML = `
        <span></span>
        <span></span>
        <span></span>
    `;
    
    // Skapa overlay för mobil
    const overlay = document.createElement('div');
    overlay.className = 'mobile-overlay';
    document.body.appendChild(overlay);
    
    // Skapa mobil-sidebar (en kopia av den vanliga sidebaren)
    const mobileSidebar = document.createElement('div');
    mobileSidebar.className = 'mobile-sidebar';
    
    // Kopiera innehållet från den vanliga sidebaren
    if (sidebar) {
        mobileSidebar.innerHTML = sidebar.innerHTML;
        document.body.appendChild(mobileSidebar);
        
        // Återställ eventlisteners för knapparna i mobilmenyn
        const selectIngredientsBtn = mobileSidebar.querySelector('#selectIngredientsBtn');
        const generateXmlBtn = mobileSidebar.querySelector('#generateXmlBtn');
        const brewerPersonalityBtn = mobileSidebar.querySelector('#brewerPersonalityBtn');
        
        if (selectIngredientsBtn) {
            selectIngredientsBtn.id = 'mobileSelectIngredientsBtn';
            selectIngredientsBtn.addEventListener('click', function() {
                if (typeof InventoryManager !== 'undefined' && InventoryManager.fetchInventory) {
                    InventoryManager.fetchInventory();
                    closeMobileMenu();
                }
            });
        }
        
        if (generateXmlBtn) {
            generateXmlBtn.id = 'mobileGenerateXmlBtn';
            generateXmlBtn.addEventListener('click', function() {
                if (typeof RecipeManager !== 'undefined' && RecipeManager.downloadBeerXml) {
                    RecipeManager.downloadBeerXml();
                    closeMobileMenu();
                }
            });
        }
        
        if (brewerPersonalityBtn) {
            brewerPersonalityBtn.id = 'mobileBrewerPersonalityBtn';
            brewerPersonalityBtn.addEventListener('click', function() {
                if (typeof PersonalityManager !== 'undefined' && PersonalityManager.showPersonalityModal) {
                    PersonalityManager.showPersonalityModal();
                    closeMobileMenu();
                }
            });
        }
    }
    
    // Lägg till hamburger-knappen i headern (om den finns)
    if (header) {
        // Lägg till som första barn i header
        if (header.firstChild) {
            header.insertBefore(hamburgerBtn, header.firstChild);
        } else {
            header.appendChild(hamburgerBtn);
        }
    } else {
        console.error('Header element not found');
    }
    
    // Funktion för att stänga mobilmenyn
    function closeMobileMenu() {
        hamburgerBtn.classList.remove('active');
        mobileSidebar.classList.remove('active');
        overlay.classList.remove('active');
    }
    
    // Hantera klick på hamburger-knappen
    hamburgerBtn.addEventListener('click', function() {
        console.log('Hamburger button clicked');
        hamburgerBtn.classList.toggle('active');
        mobileSidebar.classList.toggle('active');
        overlay.classList.toggle('active');
    });
    
    // Stäng menyn när man klickar på overlay
    overlay.addEventListener('click', closeMobileMenu);
    
    console.log('Mobile nav initialization complete');
});
