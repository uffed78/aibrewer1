/**
 * Recipe Manager Module
 * Handles recipe generation, display, and manipulation
 */
const RecipeManager = (() => {
    // Private variables
    let draftSection;
    let draftDisplay;
    let generateXmlBtn;
    let updateRecipeBtn;
    let styleSuggestionsSection;
    let customStyleBtn;
    let customStyleInput;
    
    // Initialize module
    function init() {
        console.log('🍺 Initializing Recipe Manager...');
        
        // Cache DOM elements
        draftSection = document.getElementById('draftSection');
        draftDisplay = document.getElementById('draftDisplay');
        generateXmlBtn = document.getElementById('generateXmlBtn');
        styleSuggestionsSection = document.getElementById('styleSuggestionsSection');
        customStyleBtn = document.getElementById('customStyleBtn');
        customStyleInput = document.getElementById('customStyle');
        
        // Setup event listeners
        setupEventListeners();
        
        console.log('🍺 Recipe Manager initialized');
    }
    
    // Set up event listeners for recipe management
    function setupEventListeners() {
        // Generate XML button
        if (generateXmlBtn) {
            generateXmlBtn.addEventListener('click', generateXml);
        }
        
        // Custom style button
        if (customStyleBtn && customStyleInput) {
            customStyleBtn.addEventListener('click', () => {
                const customStyle = customStyleInput.value.trim();
                if (customStyle) {
                    generateDraft(customStyle);
                }
            });
        }
    }
    
    // Display beer style suggestions 
    function displayStyleSuggestions(responseText) {
        console.log("💡 Displaying GPT's style suggestions");

        if (!styleSuggestionsSection) {
            console.error("❌ Could not find styleSuggestionsSection element");
            return;
        }

        styleSuggestionsSection.classList.remove('hidden');
        const suggestionsDiv = document.getElementById('styleSuggestions');
        if (!suggestionsDiv) return;
        
        suggestionsDiv.innerHTML = '';

        // Show GPT's complete answer so the user can read reasoning
        const explanation = document.createElement('p');
        explanation.innerHTML = `<strong>GPT:s förslag och resonemang:</strong><br>${responseText.replace(/\n/g, "<br>")}`;
        suggestionsDiv.appendChild(explanation);

        // Extract style names (looking for lines starting with numbers)
        const styleMatches = responseText.match(/\d+\.\s([^\n]+)/g);

        if (styleMatches) {
            styleMatches.forEach(match => {
                const styleName = match.replace(/^\d+\.\s/, "").trim();
                const btn = document.createElement('button');
                btn.textContent = styleName;
                btn.style.margin = "5px";
                btn.addEventListener('click', () => {
                    generateDraft(styleName);
                });
                suggestionsDiv.appendChild(btn);
            });
        } else {
            console.warn("⚠️ Could not extract style names automatically.");
        }
    }
    
    // Generate recipe draft based on style and ingredients
    async function generateDraft(style) {
        console.log(`🍺 Generating recipe for style: "${style}"`);
        
        // Check if we have ingredients selected
        const ingredients = APP_STATE.lastSelectedIngredients;
        if (!ingredients || ingredients.length === 0) {
            alert("Inga ingredienser valda. Vänligen välj ingredienser först.");
            return;
        }
        
        // Check if user is authenticated
        if (!UserManager.isAuthenticated()) {
            alert("Du måste konfigurera en Brewfather-profil först. Klicka på 'Inställningar'.");
            UserManager.showSettings();
            return;
        }
        
        // Show draft section and loading indicator
        if (draftSection) {
            draftSection.classList.remove('hidden');
        }
        
        if (draftDisplay) {
            draftDisplay.innerHTML = '<div style="text-align: center; padding: 20px;"><b>Genererar receptutkast...</b><br>Detta kan ta upp till 30 sekunder.</div>';
        }
        
        try {
            const credentials = UserManager.getApiCredentials();
            
            // Call API to generate draft
            const data = await ApiClient.generateDraft({ 
                style,
                ingredients,
                profile: "Grainfather G30",
                apiId: credentials.apiId,
                apiKey: credentials.apiKey,
                inventory_data: APP_STATE.inventoryData
            });
            
            // Display the draft
            displayDraft(data.draft);
            
        } catch (error) {
            console.error('❌ Error generating draft:', error);
            
            if (draftDisplay) {
                draftDisplay.innerHTML = `<div style="color: red; padding: 10px; border: 1px solid red; margin: 10px 0;">
                    <b>Fel vid generering av recept:</b><br>${error.message}<br><br>
                    <button id="retryDraftBtn">Försök igen</button>
                </div>`;
                
                // Add retry button functionality
                setTimeout(() => {
                    const retryBtn = document.getElementById('retryDraftBtn');
                    if (retryBtn) {
                        retryBtn.addEventListener('click', () => generateDraft(style));
                    }
                }, 100);
            }
        }
    }
    
    // Display recipe draft
    function displayDraft(draft) {
        console.log("📃 Displaying recipe draft:", draft.name);
        
        if (!draftDisplay) return;

        // Store the complete JSON data as a data attribute
        draftDisplay.dataset.draft = JSON.stringify(draft);
        
        // Format the recipe display
        draftDisplay.innerHTML = `
            <h2>${draft.name || "Namnlöst recept"}</h2>
            <p><strong>OG:</strong> ${draft.target_og || draft.og || "?"} | 
            <strong>IBU:</strong> ${draft.ibu || "?"} | 
            <strong>EBC:</strong> ${draft.ebc || "?"} | 
            <strong>ABV:</strong> ${draft.abv || "Beräknas senare"}</p>
            <h3>Maltsammansättning</h3>
            <ul>${Object.entries(draft.fermentables).map(([name, values]) => {
                    const percent = values[0];
                    const metadata = draft.fermentables_metadata[name] || {};
                    return `<li><strong>${name}</strong> (${percent}%) - Färg: ${metadata.srm_color ? metadata.srm_color.toFixed(1) : "?"} SRM - Leverantör: ${metadata.supplier || "Okänd"}</li>`;
                }).join('')}</ul>
            <h3>Humle</h3>
            <ul>${(draft.hops || []).map(hop => `<li>${formatHopDisplay(hop)}</li>`).join('')}</ul>
            <h3>Jäst</h3>
            <p><strong>${draft.yeast?.type}</strong> - ${draft.yeast?.amount} paket</p>
            
            <!-- Recipe action buttons -->
            <div class="recipe-actions">
                <button id="updateRecipeBtn" class="action-button">Uppdatera recept baserat på chatt</button>
            </div>
        `;
        
        // Add event listener to the update button
        setTimeout(() => {
            updateRecipeBtn = document.getElementById('updateRecipeBtn');
            if (updateRecipeBtn) {
                updateRecipeBtn.addEventListener('click', updateRecipeFromChat);
            }
        }, 100);
    }
    
    // Generate BeerXML from current recipe
    async function generateXml() {
        console.log("📄 Attempting to generate BeerXML...");
        
        // Check if user is authenticated
        if (!UserManager.isAuthenticated()) {
            alert("Du måste konfigurera en Brewfather-profil först.");
            UserManager.showSettings();
            return;
        }
        
        // Get the current recipe draft
        if (!draftDisplay || !draftDisplay.dataset.draft) {
            alert("❌ Inget receptutkast att generera BeerXML från.");
            return;
        }
        
        let draft;
        try {
            draft = JSON.parse(draftDisplay.dataset.draft);
        } catch (error) {
            console.error("❌ Error parsing draft as JSON:", error);
            alert("Ett fel uppstod när receptet skulle läsas. Försök skapa ett nytt recept.");
            return;
        }
        
        // Show loading indicator
        const btn = generateXmlBtn;
        const originalText = btn.textContent;
        btn.textContent = "Genererar...";
        btn.disabled = true;
        
        try {
            const credentials = UserManager.getApiCredentials();
            
            // Create request payload
            const payload = {
                draft: draft,
                profile: "Grainfather G30",
                apiId: credentials.apiId,
                apiKey: credentials.apiKey,
                selectedIngredients: APP_STATE.lastSelectedIngredients
            };
            
            // Call API to generate XML
            const blob = await ApiClient.generateXml(payload);
            
            // Download the file
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `${draft.name || 'recipe'}.xml`;
            a.style.display = 'none';
            document.body.appendChild(a);
            a.click();
            
            // Clean up
            setTimeout(() => {
                document.body.removeChild(a);
                window.URL.revokeObjectURL(url);
            }, 100);
            
        } catch (error) {
            console.error('❌ Error generating BeerXML:', error);
            alert(`Ett fel uppstod: ${error.message}`);
        } finally {
            // Reset button state
            btn.textContent = originalText;
            btn.disabled = false;
        }
    }
    
    // Update recipe based on chat
    async function updateRecipeFromChat() {
        console.log("🔄 Attempting to update recipe from chat...");
        
        // Get current draft
        if (!draftDisplay || !draftDisplay.dataset.draft) {
            alert("❌ Inget receptutkast att uppdatera.");
            return;
        }
        
        let draft;
        try {
            draft = JSON.parse(draftDisplay.dataset.draft);
        } catch (error) {
            console.error("❌ Error parsing draft as JSON:", error);
            return;
        }
        
        // Add notification to chat
        ChatSystem.addMessage("System", "Uppdaterar recept baserat på chatt...");
        
        try {
            // Use the discuss API endpoint to get an updated recipe
            const response = await ApiClient.discuss({
                messages: [
                    ...APP_STATE.chatHistory,
                    { 
                        role: "user", 
                        content: "Baserat på vår diskussion ovan, uppdatera receptet och ge mig ett nytt komplett recept i JSON-format som följer exakt samma format som det nuvarande receptet. Ändra bara de delar vi diskuterat." 
                    }
                ],
                recipe: draft
            });
            
            // Try to extract JSON from the response
            const jsonMatch = response.response.match(/```json\s*([\s\S]*?)\s*```/) || 
                              response.response.match(/```\s*([\s\S]*?)\s*```/) ||
                              response.response.match(/{[\s\S]*}/);
            
            if (jsonMatch) {
                try {
                    // Parse the JSON string
                    const newRecipeData = JSON.parse(jsonMatch[1] || jsonMatch[0]);
                    
                    // Update the recipe display
                    displayDraft(newRecipeData);
                    
                    // Add confirmation message
                    ChatSystem.addMessage("System", "✅ Receptet har uppdaterats baserat på diskussionen.");
                    
                    // Update chat history
                    APP_STATE.chatHistory.push({ role: "user", content: "Uppdatera receptet baserat på vår diskussion." });
                    APP_STATE.chatHistory.push({ role: "assistant", content: response.response });
                    APP_STATE.chatHistory.push({ role: "system", content: "Receptet har uppdaterats." });
                    
                } catch (jsonError) {
                    console.error("❌ Could not parse GPT response as JSON:", jsonError);
                    ChatSystem.addMessage("System", "❌ Kunde inte uppdatera receptet automatiskt. GPT:s svar hade inte rätt format.");
                }
            } else {
                ChatSystem.addMessage("System", "❌ Kunde inte hitta JSON-data i GPT:s svar för att uppdatera receptet.");
                console.error("No JSON format found in GPT response:", response.response);
            }
        } catch (error) {
            console.error('❌ Error updating recipe:', error);
            ChatSystem.addMessage("System", "❌ Ett fel uppstod: " + error.message);
        }
    }
    
    // Get current recipe
    function getCurrentRecipe() {
        if (!draftDisplay || !draftDisplay.dataset.draft) {
            return null;
        }
        
        try {
            return JSON.parse(draftDisplay.dataset.draft);
        } catch (error) {
            console.error("❌ Error parsing draft as JSON:", error);
            return null;
        }
    }
    
    /**
     * Formaterar visningen av humle
     */
    function formatHopDisplay(hop) {
        if (!hop) return '';
        
        // Grunddata
        const name = hop.name || 'Okänd humle';
        const alpha = hop.alpha ? `${hop.alpha}% alpha` : '';
        const time = hop.time || 0;
        
        // För torrhumle (time = 0), visa g/L istället för IBU
        if (time === 0) {
            // För torrhumle, använd dry_hop_rate som direkt kommer från backend
            const dryHopRate = hop.dry_hop_rate !== undefined ? `${hop.dry_hop_rate} g/L` : '';
            return `<strong>${name}</strong> - ${alpha} - ${dryHopRate} - Torrhumle`;
        } else {
            // För kokhumle, visa IBU som tidigare
            const ibu = hop.ibu_contribution !== undefined ? `${hop.ibu_contribution} IBU` : '';
            return `<strong>${name}</strong> - ${alpha} - ${ibu} - ${time} min koktid`;
        }
    }
    
    // Public API
    return {
        init,
        generateDraft,
        displayDraft,
        displayStyleSuggestions,
        getCurrentRecipe,
        generateXml,
        updateRecipeFromChat
    };
})();
