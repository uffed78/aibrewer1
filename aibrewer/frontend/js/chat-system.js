/**
 * Chat System Module
 * Handles chat interaction with the AI assistant
 */
const ChatSystem = (() => {
    // Private variables
    let chatDisplay;
    let chatInput;
    let sendChatBtn;
    
    // Initialize module
    function init() {
        console.log('💬 Initializing Chat System...');
        
        // Cache DOM elements
        chatDisplay = document.getElementById('chatDisplay');
        chatInput = document.getElementById('chatInput');
        sendChatBtn = document.getElementById('sendChatBtn');
        
        // Setup event listeners
        setupEventListeners();
        
        console.log('💬 Chat System initialized');
    }
    
    // Set up event listeners for chat
    function setupEventListeners() {
        if (sendChatBtn) {
            sendChatBtn.addEventListener('click', sendMessage);
        }
        
        if (chatInput) {
            chatInput.addEventListener('keypress', e => {
                if (e.key === 'Enter') {
                    sendMessage();
                }
            });
        }
    }
    
    // Send user message to AI
    async function sendMessage() {
        if (!chatInput) return;
        
        const message = chatInput.value.trim();
        if (!message) return;
        
        // Clear input and add message to display
        chatInput.value = '';
        addMessage('Du', message);
        
        // Add message to history
        APP_STATE.chatHistory.push({ role: "user", content: message });
        
        // Check if we have recipe data to include in the context
        const draftDisplay = document.getElementById('draftDisplay');
        let recipe = null;
        
        if (draftDisplay && draftDisplay.dataset.draft) {
            try {
                recipe = JSON.parse(draftDisplay.dataset.draft);
                
                // Add recipe data to chat context if not already added
                if (!APP_STATE.chatHistory.some(msg => msg.role === "system" && msg.content.includes("aktuella receptet"))) {
                    APP_STATE.chatHistory.push({
                        role: "system",
                        content: `Det aktuella receptet: ${JSON.stringify(recipe, null, 2)}`
                    });
                }
            } catch (error) {
                console.error("❌ Could not parse recipe data:", error);
            }
        }
        
        // Add inventory data to chat context if available and not already added
        if (APP_STATE.inventoryData && 
            !APP_STATE.chatHistory.some(msg => msg.role === "system" && msg.content.includes("tillgängliga ingredienser"))) {
            
            // Create a summary of available ingredients
            const inventorySummary = {
                fermentables: APP_STATE.inventoryData.fermentables?.map(item => ({
                    name: item.name,
                    amount: `${item.inventory} kg`,
                    color: item.color || "N/A"
                })) || [],
                hops: APP_STATE.inventoryData.hops?.map(item => ({
                    name: item.name,
                    amount: `${item.inventory} g`,
                    alpha: item.alpha || "N/A"
                })) || [],
                yeasts: APP_STATE.inventoryData.yeasts?.map(item => ({
                    name: item.name,
                    amount: `${item.inventory} pkg`
                })) || []
            };
            
            APP_STATE.chatHistory.push({
                role: "system",
                content: `Tillgängliga ingredienser i användarens inventory: ${JSON.stringify(inventorySummary, null, 2)}`
            });
        }
        
        // Show loading indicator
        const loadingId = addMessage('Assistent', '...');
        
        // Send message to API
        try {
            const response = await ApiClient.discuss({
                messages: APP_STATE.chatHistory,
                recipe: recipe,
                inventory: APP_STATE.inventoryData,
                personality: APP_STATE.currentPersonality
            });
            
            // Remove loading indicator and show response
            document.getElementById(loadingId)?.remove();
            
            // Add AI response to chat history and display
            APP_STATE.chatHistory.push({ role: "assistant", content: response.response });
            addMessage('Assistent', response.response);
        } catch (error) {
            // Show error message
            document.getElementById(loadingId).innerHTML = `<strong>Assistent:</strong> Ett fel uppstod: ${error.message}`;
        }
    }
    
    // Add a message to the chat display
    function addMessage(sender, text) {
        if (!chatDisplay) return;
        
        const messageDiv = document.createElement('div');
        const messageId = 'chat-msg-' + Date.now();
        messageDiv.id = messageId;
        messageDiv.className = 'chat-message ' + 
            (sender === 'Du' ? 'user-message' : 'assistant-message');
        messageDiv.innerHTML = `<strong>${sender}:</strong> ${text}`;
        
        chatDisplay.appendChild(messageDiv);
        chatDisplay.scrollTop = chatDisplay.scrollHeight;
        
        return messageId;
    }
    
    // Clear chat history and display
    function clearChat() {
        if (chatDisplay) {
            chatDisplay.innerHTML = '';
        }
        
        // Reset chat history to only include the system prompt
        APP_STATE.chatHistory = [
            { role: "system", content: "Du är en AI-assistent som hjälper med ölbryggning. Använd svenska språket i dina svar." }
        ];
        
        // Add welcome message
        addMessage("System", "Chatten har rensats. Ställ en ny fråga!");
    }
    
    // Public API
    return {
        init,
        addMessage,
        sendMessage,
        clearChat
    };
})();
