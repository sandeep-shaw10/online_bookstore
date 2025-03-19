document.addEventListener('DOMContentLoaded', function() {

    // DOM elements
    const mobileMenuBtn = document.getElementById('mobile-menu-btn');
    const mobileMenu = document.getElementById('mobile-menu');
    const menuIcon = document.getElementById('menu-icon');
    const closeIcon = document.getElementById('close-icon');
    const featuredBooksContainer = document.getElementById('featured-books');
    const newReleasesContainer = document.getElementById('new-releases-books');


    // Toggle mobile menu
    function toggleMobileMenu() {
      mobileMenu.classList.toggle('hidden');
      menuIcon.classList.toggle('hidden');
      closeIcon.classList.toggle('hidden');
    }

    // Create book card HTML
    function createBookCard(book) {
      return `
        <div class="bg-white rounded-lg shadow-md overflow-hidden transition-transform duration-300 hover:shadow-lg hover:-translate-y-1">
          <div class="h-64 overflow-hidden">
            <img 
              src="${book.coverUrl}" 
              alt="${book.title}" 
              class="w-full h-full object-cover"
            />
          </div>
          <div class="p-4">
            <h3 class="text-lg font-semibold text-gray-900 truncate">${book.title}</h3>
            <p class="text-sm text-gray-600 mb-2">${book.author}</p>
            <div class="flex items-center mb-2">
              <div class="flex items-center">
                <i class="lucide-star h-4 w-4 text-yellow-400">
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-star"><path d="M11.525 2.295a.53.53 0 0 1 .95 0l2.31 4.679a2.123 2.123 0 0 0 1.595 1.16l5.166.756a.53.53 0 0 1 .294.904l-3.736 3.638a2.123 2.123 0 0 0-.611 1.878l.882 5.14a.53.53 0 0 1-.771.56l-4.618-2.428a2.122 2.122 0 0 0-1.973 0L6.396 21.01a.53.53 0 0 1-.77-.56l.881-5.139a2.122 2.122 0 0 0-.611-1.879L2.16 9.795a.53.53 0 0 1 .294-.906l5.165-.755a2.122 2.122 0 0 0 1.597-1.16z"/></svg>
                </i>
                <span class="ml-1 text-sm text-gray-700">${book.rating}</span>
              </div>
              <span class="mx-2 text-gray-300">|</span>
              <span class="text-sm text-gray-700 font-medium">$${book.price.toFixed(2)}</span>
            </div>
            <button class="w-full mt-2 flex items-center justify-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700">
              <i class="lucide-shopping-cart mr-2 h-4 w-4"> </i>
              Add to Cart
            </button>
          </div>
        </div>
      `;
    }
  
    // Populate books and categories
    function populateContent() {
      // Featured books
      featuredBooksContainer.innerHTML = featuredBooks.map(book => createBookCard(book)).join('');
      
      // New releases
      newReleasesContainer.innerHTML = newReleases.map(book => createBookCard(book)).join('');

    }
  
    // Event listeners
    mobileMenuBtn.addEventListener('click', toggleMobileMenu);
  
    // Initialize
    populateContent();
  
    
  });