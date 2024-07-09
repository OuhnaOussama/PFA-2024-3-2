// Sélectionnez les éléments nécessaires
const navMenu = document.getElementById('nav');
const toggleButton = document.getElementById('menu');

// Fonction pour ouvrir/fermer le menu
function toggleMenu() {
  navMenu.classList.toggle('hidden');
}

// Ajoutez un écouteur d'événement sur le bouton de menu
toggleButton.addEventListener('click', toggleMenu);

// Fermez le menu lorsque l'utilisateur clique en dehors du menu
window.addEventListener('click', function(event) {
  if (!navMenu.contains(event.target) && !toggleButton.contains(event.target)) {
    navMenu.classList.add('hidden');
  }
});