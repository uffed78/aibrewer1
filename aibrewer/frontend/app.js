document.addEventListener('DOMContentLoaded', () => {
    const categorySelect = document.getElementById('category');
    const filterBtn = document.getElementById('filter-btn');
    const stylesList = document.getElementById('styles-list');
  
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
  });
  