document.addEventListener('DOMContentLoaded', () => {
    const categorySelect = document.getElementById('category');
    const filterBtn = document.getElementById('filter-btn');
    const stylesList = document.getElementById('styles-list');
    const recipeList = document.getElementById('recipe-list');
    const chatBox = document.getElementById('chat-box');
    const userInput = document.getElementById('user-input');
    const sendBtn = document.getElementById('send-btn');

    let messages = []; // Håller reda på GPT-konversationen

    // Hämta kategorier och fyll rullistan
    fetch('/styles/categories')
        .then(response => response.json())
        .then(categories => {
            categorySelect.innerHTML = '<option value="">Alla kategorier</option>';
            categories.forEach(category => {
                const option = document.createElement('option');
                option.value = category;
                option.textContent = category;
                categorySelect.appendChild(option);
            });
        });

    // Filtrera ölstilar
    filterBtn.addEventListener('click', () => {
        const category = categorySelect.value;
        const abvMin = document.getElementById('abv-min').value;
        const abvMax = document.getElementById('abv-max').value;

        const queryParams = new URLSearchParams();
        if (category) queryParams.append('category', category);
        if (abvMin) queryParams.append('abv_min', abvMin);
        if (abvMax) queryParams.append('abv_max', abvMax);

        fetch(`/styles/filter?${queryParams.toString()}`)
            .then(response => response.json())
            .then(styles => {
                stylesList.innerHTML = '';
                styles.forEach(style => {
                    const li = document.createElement('li');
                    li.textContent = `${style.name} (${style.category}) - ABV: ${style.abvmin}-${style.abvmax}`;
                    stylesList.appendChild(li);
                });
            });
    });

    // Hämta och visa recept
    fetch('/recipes')
        .then(response => response.json())
        .then(data => {
            if (data && data.length > 0) {
                recipeList.innerHTML = ''; // Rensa listan först
                data.forEach(recipe => {
                    const li = document.createElement('li');
                    li.innerHTML = `
                        <strong>Namn:</strong> ${recipe.name || 'N/A'}<br>
                        <strong>Typ:</strong> ${recipe.type || 'N/A'}<br>
                        <strong>Författare:</strong> ${recipe.author || 'Okänd'}<br>
                        <strong>Stil:</strong> ${recipe.style?.name || 'N/A'}<br>
                        <strong>Utrustning:</strong> ${recipe.equipment?.name || 'N/A'}
                    `;
                    recipeList.appendChild(li);
                });
            } else {
                recipeList.innerHTML = '<p>Inga recept hittades.</p>';
            }
        })
        .catch(error => {
            recipeList.textContent = `Fel vid hämtning av recept: ${error.message}`;
        });

    // GPT-diskussion
    sendBtn.addEventListener('click', () => {
        const userMessage = userInput.value.trim();
        if (!userMessage) return;
    
        const includeInventory = document.getElementById('include-inventory').checked;
        const recipeId = document.getElementById('recipe-id').value;
    
        // Lägg till användarens meddelande
        messages.push({ role: "user", content: userMessage });
    
        // Skicka konversationen till backend
        fetch('/chat-with-gpt', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ messages, include_inventory: includeInventory, recipe_id: recipeId })
        })
            .then(response => response.json())
            .then(data => {
                if (data.response) {
                    messages.push({ role: "assistant", content: data.response });
                    chatBox.innerHTML += `<p><strong>GPT:</strong> ${data.response}</p>`;
                } else {
                    chatBox.innerHTML += `<p><strong>Fel:</strong> ${data.error}</p>`;
                }
            })
            .catch(error => {
                chatBox.innerHTML += `<p><strong>Fel:</strong> ${error.message}</p>`;
            });
    });
    
    
});
