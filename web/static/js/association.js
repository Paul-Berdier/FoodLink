document.addEventListener('DOMContentLoaded', function() {
    // Initialisation de la carte
    const map = L.map('map').setView([43.6047, 1.4442], 13); // Coordonnées de Toulouse

    // Ajout de la couche OpenStreetMap
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors'
    }).addTo(map);

    // Liste des commerces avec leurs coordonnées
    const commerces = [
        {
            name: "Carrefour",
            lat: 43.6047,
            lng: 1.4442,
            address: "2 ALL. ÉMILE ZOLA, 31750 BLAGNAC"
        },
        {
            name: "Leclerc",
            lat: 43.6147,
            lng: 1.4542,
            address: "2 ALL. ÉMILE ZOLA, 31750 BLAGNAC"
        },
        {
            name: "Auchan",
            lat: 43.5947,
            lng: 1.4342,
            address: "ZAC DES, RUE ANNA POLITKOVSKAÏA, 31000 TOULOUSE"
        }
    ];

    // Ajouter les marqueurs pour chaque commerce
    commerces.forEach(commerce => {
        const marker = L.marker([commerce.lat, commerce.lng])
            .addTo(map)
            .bindPopup(`
                <strong>${commerce.name}</strong><br>
                ${commerce.address}
            `);

        // Ajouter un gestionnaire d'événements pour le clic sur les éléments de la liste
        const storeItems = document.querySelectorAll('.store-item');
        storeItems.forEach(item => {
            if (item.querySelector('.store-name').textContent === commerce.name) {
                item.addEventListener('click', () => {
                    map.setView([commerce.lat, commerce.lng], 15);
                    marker.openPopup();
                });
            }
        });
    });

    // Gestionnaire pour les filtres
    const filterGroups = document.querySelectorAll('.filter-group');
    filterGroups.forEach(group => {
        group.addEventListener('click', function() {
            this.classList.toggle('active');
        });
    });

    // Gestionnaire pour la recherche
    const searchInput = document.querySelector('.search-input');
    const searchButton = document.querySelector('.search-button');
    
    function performSearch() {
        const searchTerm = searchInput.value.toLowerCase();
        const storeItems = document.querySelectorAll('.store-item');
        
        storeItems.forEach(item => {
            const storeName = item.querySelector('.store-name').textContent.toLowerCase();
            if (storeName.includes(searchTerm)) {
                item.style.display = 'flex';
            } else {
                item.style.display = 'none';
            }
        });
    }

    searchButton.addEventListener('click', performSearch);
    searchInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            performSearch();
        }
    });
});