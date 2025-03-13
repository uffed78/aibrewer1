/**
 * Enkel mobilmenyfunktionalitet utan sidoeffekter
 */
document.addEventListener('DOMContentLoaded', function() {
    console.log('Simple Mobile: Initializing');
    
    // Skapa hamburger-knappen
    const hamburger = document.createElement('button');
    hamburger.className = 'hamburger-button';
    hamburger.setAttribute('aria-label', 'Meny');
    hamburger.innerHTML = `
        <span></span>
        <span></span>
        <span></span>
    `;
    
    // Lägg till hamburgerknappen
    document.body.appendChild(hamburger);
    
    // Hitta sidebaren
    const sidebar = document.querySelector('.sidebar');
    
    // Skapa overlay
    const overlay = document.createElement('div');
    overlay.className = 'mobile-overlay';
    document.body.appendChild(overlay);
    
    // Toggle för menyn
    hamburger.addEventListener('click', function() {
        hamburger.classList.toggle('active');
        sidebar.classList.toggle('active');
        overlay.classList.toggle('active');
        
        // Förhindra scrollning av bakgrunden när menyn är öppen
        if (sidebar.classList.contains('active')) {
            document.body.style.overflow = 'hidden';
        } else {
            document.body.style.overflow = '';
        }
    });
    
    // Stäng menyn när man klickar på overlay
    overlay.addEventListener('click', function() {
        hamburger.classList.remove('active');
        sidebar.classList.remove('active');
        overlay.classList.remove('active');
        document.body.style.overflow = '';
    });
    
    // Lägg till click handlers på alla meny-knappar för att stänga menyn efter klick på mobil
    const menuButtons = sidebar.querySelectorAll('button');
    menuButtons.forEach(button => {
        // Bevara existerande click handlers genom att använda addEventListener
        const originalClickEvent = button.onclick;
        button.addEventListener('click', function(event) {
            // Stäng menyn bara på mobil
            if (window.innerWidth <= 768) {
                hamburger.classList.remove('active');
                sidebar.classList.remove('active');
                overlay.classList.remove('active');
                document.body.style.overflow = '';
            }
        });
    });
    
    console.log('Simple Mobile: Initialized successfully');
});
