async function fetchInventory() {
    const response = await fetch('http://localhost:5000/function_a_v2/get-inventory');
    const data = await response.json();
    const inventoryContainer = document.getElementById('inventory');
    inventoryContainer.innerHTML = '';

    // Kategorisera och visa inventariet
    for (const [category, items] of Object.entries(data)) {
        const categoryDiv = document.createElement('div');
        categoryDiv.className = 'bg-white p-4 rounded shadow';
        categoryDiv.innerHTML = `<h3 class="font-bold mb-2">${category}</h3><ul>`;
        
        items.forEach(item => {
            categoryDiv.innerHTML += `<li>${item.name} - ${item.amount}</li>`;
        });

        categoryDiv.innerHTML += '</ul>';
        inventoryContainer.appendChild(categoryDiv);
    }
}

async function sendInventoryToGPT() {
    const inventory = JSON.parse(document.getElementById('inventory').textContent || '{}');
    const response = await fetch('http://localhost:5000/function_a_v2/suggest-styles', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ ingredients: inventory })
    });
    const data = await response.json();
    const stylesContainer = document.getElementById('styles');
    stylesContainer.innerHTML = '';

    data.styles.forEach(style => {
        const styleButton = document.createElement('button');
        styleButton.className = 'bg-yellow-500 text-white px-4 py-2 rounded mr-2 mb-2';
        styleButton.textContent = style;
        styleButton.onclick = () => selectStyle(style);
        stylesContainer.appendChild(styleButton);
    });
}

async function selectStyle(style) {
    const response = await fetch('http://localhost:5000/function_a_v2/generate-draft', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ style, ingredients: JSON.parse(document.getElementById('inventory').textContent) })
    });
    const data = await response.json();
    const recipeContainer = document.getElementById('recipe');
    recipeContainer.innerHTML = `<pre>${JSON.stringify(data.draft, null, 2)}</pre>`;
}

async function discussRecipe() {
    const message = document.getElementById('message').value;
    const response = await fetch('http://localhost:5000/function_a_v2/discuss', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            messages: [{ role: 'user', content: message }],
            recipe: JSON.parse(document.getElementById('recipe').textContent)
        })
    });
    const data = await response.json();
    document.getElementById('discussion').textContent = data.response;
}

async function fetchBeerXML() {
    const draft = JSON.parse(document.getElementById('recipe').textContent);
    const response = await fetch('/function_a_v2/generate-xml', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ draft, calculated: {}, profile: "Grainfather G30" })
    });
    const blob = await response.blob();
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${draft.name || 'recipe'}.xml`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    window.URL.revokeObjectURL(url);
    document.getElementById('beerxml').textContent = "BeerXML har laddats ner!";
}