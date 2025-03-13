/**
 * AIBrewer Mobile Navigation
 * A clean implementation to avoid conflicts
 */
document.addEventListener('DOMContentLoaded', function() {
    console.log("AIBrewer Mobile: Initializing mobile navigation");
    
    // Add mobile layout class to body
    document.body.classList.add('mobile-layout');
    
    // Find the original sidebar
    const originalSidebar = document.querySelector('.sidebar');
    
    // Add the aibrewer-sidebar class for our CSS
    if (originalSidebar) {
        originalSidebar.classList.add('aibrewer-sidebar');
    }
    
    // Create hamburger button
    const hamburgerBtn = document.createElement('button');
    hamburgerBtn.className = 'mobile-menu-btn';
    hamburgerBtn.innerHTML = `
        <span></span>
        <span></span>
        <span></span>
    `;
    document.body.appendChild(hamburgerBtn);
    
    // Create mobile nav
    const mobileNav = document.createElement('div');
    mobileNav.className = 'mobile-nav';
    
    // Clone buttons from original sidebar
    if (originalSidebar) {
        // Copy the buttons
        const buttons = originalSidebar.querySelectorAll('button');
        buttons.forEach(button => {
            const clonedButton = button.cloneNode(true);
            mobileNav.appendChild(clonedButton);
            
            // Re-add event listeners
            const buttonId = button.id;
            if (buttonId === 'selectIngredientsBtn') {
                clonedButton.addEventListener('click', function() {
                    if (typeof InventoryManager !== 'undefined' && InventoryManager.fetchInventory) {
                        InventoryManager.fetchInventory();
                        closeMobileMenu();
                    }
                });
            } else if (buttonId === 'generateXmlBtn') {
                clonedButton.addEventListener('click', function() {
                    if (typeof RecipeManager !== 'undefined' && RecipeManager.downloadBeerXml) {
                        RecipeManager.downloadBeerXml();
                        closeMobileMenu();
                    }
                });
            } else if (buttonId === 'brewerPersonalityBtn') {
                clonedButton.addEventListener('click', function() {
                    if (typeof PersonalityManager !== 'undefined' && PersonalityManager.showPersonalityModal) {
                        PersonalityManager.showPersonalityModal();
                        closeMobileMenu();
                    }
                });
            }
        });
    }
    
    document.body.appendChild(mobileNav);
    
    // Create overlay
    const overlay = document.createElement('div');
    overlay.className = 'mobile-overlay';
    document.body.appendChild(overlay);
    
    // Function to close mobile menu
    function closeMobileMenu() {
        hamburgerBtn.classList.remove('active');
        mobileNav.classList.remove('active');
        overlay.classList.remove('active');
    }
    
    // Toggle mobile menu
    hamburgerBtn.addEventListener('click', function() {
        hamburgerBtn.classList.toggle('active');
        mobileNav.classList.toggle('active');
        overlay.classList.toggle('active');
    });
    
    // Close menu when clicking overlay
    overlay.addEventListener('click', closeMobileMenu);
    
    console.log("AIBrewer Mobile: Mobile navigation initialized");
});
