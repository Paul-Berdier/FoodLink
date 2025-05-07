document.addEventListener('DOMContentLoaded', function() {
    // Initialise la carte
    const map = L.map('map').setView([43.6045, 1.444], 12); // Coordonnées de Toulouse

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
    }).addTo(map);

    function createMarkerIcon(color, text) {
        return L.divIcon({
            className: `map-marker marker-${text.toLowerCase()}`,
            html: text,
            iconSize: [80, 30],
            iconAnchor: [40, 15]
        });
    }

    const markers = [
        { position: [43.6165, 1.4263], icon: createMarkerIcon('#ffc0cb', 'Leclerc'), name: 'Leclerc' },
        { position: [43.6045, 1.4440], icon: createMarkerIcon('#add8e6', 'La Mie Câline'), name: 'La Mie Câline' },
        { position: [43.6112, 1.4550], icon: createMarkerIcon('#ffff00', 'Carrefour'), name: 'Carrefour' },
        { position: [43.5986, 1.4323], icon: createMarkerIcon('#ffa07a', 'Auchan'), name: 'Auchan' },
        { position: [43.5879, 1.4467], icon: createMarkerIcon('#00ffaa', 'Casino'), name: 'Casino' }
    ];

    markers.forEach(marker => {
        L.marker(marker.position, { icon: marker.icon })
            .addTo(map)
            .bindPopup(`<b>${marker.name}</b><br>Cliquez pour voir les produits disponibles.`);
    });

    const storeItems = document.querySelectorAll('.store-item');

    storeItems.forEach((item, index) => {
        item.addEventListener('click', function() {
            storeItems.forEach(i => i.classList.remove('selected'));
            this.classList.add('selected');

            if (index < markers.length) {
                map.setView(markers[index].position, 14);
                L.popup()
                    .setLatLng(markers[index].position)
                    .setContent(`<b>${this.querySelector('.store-name').textContent}</b><br>Cliquez pour voir les produits disponibles.`)
                    .openOn(map);
            }
        });
    });

    const storeProducts = document.querySelectorAll('.store-products');

    storeProducts.forEach((product, index) => {
        setTimeout(() => {
            product.style.opacity = '0';
            product.style.transform = 'translateY(20px)';
            product.style.transition = 'opacity 0.5s ease, transform 0.5s ease';

            setTimeout(() => {
                product.style.opacity = '1';
                product.style.transform = 'translateY(0)';
            }, 50);
        }, index * 200);
    });

    const filterGroups = document.querySelectorAll('.filter-group');

    filterGroups.forEach(filter => {
        filter.addEventListener('click', function() {
            this.classList.toggle('active');

            alert(`Filtre ${this.querySelector('.filter-label').textContent} sélectionné`);
        });
    });
});