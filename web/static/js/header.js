document.addEventListener('DOMContentLoaded', function() {
    const header = document.querySelector('.top-menu');
    const burgerButton = document.querySelector('.burger-button');
    const mobileMenu = document.querySelector('.mobile-menu');
    const mobileLinks = document.querySelectorAll('.mobile-nav-link');
    const burgerText = document.querySelector('.burger-text');

    // Initialiser l'état du menu mobile
    mobileMenu.style.display = 'none';

    // Fonction pour ajouter/enlever la classe 'scrolled' au header
    function handleScroll() {
        if (window.scrollY > 50) {
            header.classList.add('scrolled');
        } else {
            header.classList.remove('scrolled');
        }
    }

    // Fonction pour ouvrir/fermer le menu mobile
    function toggleMobileMenu() {
        burgerButton.classList.toggle('active');
        
        if (!mobileMenu.classList.contains('open')) {
            // Ouvrir le menu
            mobileMenu.style.display = 'block';
            // Forcer un reflow pour que l'animation fonctionne
            mobileMenu.offsetHeight;
            mobileMenu.classList.add('open');
            
            // Changer le texte en "Fermer"
            burgerText.textContent = 'Fermer';
            
            // Bloquer le scroll
            document.body.classList.add('no-scroll');
        } else {
            // Fermer le menu
            mobileMenu.classList.remove('open');
            
            // Attendre la fin de l'animation avant de cacher
            setTimeout(() => {
                mobileMenu.style.display = 'none';
            }, 300);
            
            // Remettre le texte "Menu"
            burgerText.textContent = 'Menu';
            
            // Débloquer le scroll
            document.body.classList.remove('no-scroll');
        }
    }

    // Écouteur d'événement pour le scroll
    window.addEventListener('scroll', handleScroll);
    
    // Écouteur d'événement pour le bouton burger
    if (burgerButton) {
        burgerButton.addEventListener('click', toggleMobileMenu);
    }
    
    // Fermer le menu après un clic sur un lien
    mobileLinks.forEach(link => {
        link.addEventListener('click', function() {
            if (mobileMenu.classList.contains('open')) {
                toggleMobileMenu();
            }
        });
    });
    
    // Appliquer l'état initial
    handleScroll();
}); 