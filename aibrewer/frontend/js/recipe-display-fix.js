/**
 * Fix för att visa torrhumling (dry hopping) korrekt i receptutkastet
 */

document.addEventListener('DOMContentLoaded', function() {
    console.log('Recipe Display Fix loaded');
    
    // Originella formatHopDisplay-funktionen (om den existerar)
    const originalFormatHopDisplay = window.formatHopDisplay || null;
    
    // Förbättrad funktion för att visa humle med stöd för torrhumling
    window.formatHopDisplay = function(hop) {
        if (!hop) return '';
        
        const name = hop.name || 'Okänd humle';
        const alpha = hop.alpha ? `${hop.alpha}% alpha` : '';
        const time = hop.time || 0;
        
        // Check if this is a dry hop (time = 0)
        if (time === 0) {
            // För torrhumle, visa gram per liter istället för IBU
            const dryHopRate = hop.dry_hop_rate !== undefined ? `${hop.dry_hop_rate} g/L` : 'Torrhumle';
            return `${name} - ${alpha} - ${dryHopRate} - Torrhumle`;
        } else {
            // För kokhumle, visa IBU som tidigare
            const ibu = hop.ibu_contribution !== undefined ? `${hop.ibu_contribution} IBU` : '';
            return `${name} - ${alpha} - ${ibu} - ${time} min koktid`;
        }
    };
    
    // Override RecipeManager.displayDraft function to use our new formatHopDisplay
    if (window.RecipeManager && RecipeManager.displayDraft) {
        const originalDisplayDraft = RecipeManager.displayDraft;
        
        RecipeManager.displayDraft = function(draft) {
            // Uppdatera humleformateringen innan vi visar receptet
            if (draft && draft.hops) {
                for (let i = 0; i < draft.hops.length; i++) {
                    const hop = draft.hops[i];
                    if (hop.time === 0 && hop.dry_hop_rate === undefined) {
                        // Säkerställ att torrhumle har ett dry_hop_rate-värde
                        hop.dry_hop_rate = hop.dry_hop_rate || 2.0; // Standardvärde: 2 g/L
                    }
                }
            }
            
            // Anropa originell metod
            return originalDisplayDraft.call(this, draft);
        };
    }
    
    // Kontrollera om vi redan har ett receptutkast i DOM och uppdatera i så fall visningen
    setTimeout(function() {
        const draftDisplay = document.getElementById('draftDisplay');
        if (draftDisplay && draftDisplay.innerHTML.includes('koktid')) {
            // Leta efter referenser till aktuellt draft
            if (window.RecipeManager && RecipeManager.currentDraft) {
                RecipeManager.displayDraft(RecipeManager.currentDraft);
                console.log('Rerendered existing draft with improved hop formatting');
            }
        }
    }, 500);
});
