document.addEventListener('DOMContentLoaded', function() {

    // Mock data
    const featuredBooks = [
      {
        id: 1,
        title: 'The Great Gatsby',
        author: 'F. Scott Fitzgerald',
        price: 12.99,
        coverUrl: 'https://images.unsplash.com/photo-1544947950-fa07a98d237f?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=800&q=80',
        rating: 4.5,
      },
      {
        id: 2,
        title: 'To Kill a Mockingbird',
        author: 'Harper Lee',
        price: 10.99,
        coverUrl: 'https://images.unsplash.com/photo-1541963463532-d68292c34b19?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=800&q=80',
        rating: 4.8,
      },
      {
        id: 3,
        title: '1984',
        author: 'George Orwell',
        price: 9.99,
        coverUrl: 'https://images.unsplash.com/photo-1543002588-bfa74002ed7e?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=800&q=80',
        rating: 4.6,
      },
      {
        id: 4,
        title: 'Pride and Prejudice',
        author: 'Jane Austen',
        price: 8.99,
        coverUrl: 'https://images.unsplash.com/photo-1512820790803-83ca734da794?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=800&q=80',
        rating: 4.7,
      }
    ];
  
    const newReleases = [
      {
        id: 5,
        title: 'The Midnight Library',
        author: 'Matt Haig',
        price: 14.99,
        coverUrl: 'https://images.unsplash.com/photo-1589998059171-988d887df646?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=800&q=80',
        rating: 4.4,
      },
      {
        id: 6,
        title: 'Project Hail Mary',
        author: 'Andy Weir',
        price: 15.99,
        coverUrl: 'https://images.unsplash.com/photo-1531901599143-df5010ab9438?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=800&q=80',
        rating: 4.9,
      },
      {
        id: 7,
        title: 'Klara and the Sun',
        author: 'Kazuo Ishiguro',
        price: 13.99,
        coverUrl: 'https://images.unsplash.com/photo-1589998059171-988d887df646?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=800&q=80',
        rating: 4.3,
      },
      {
        id: 8,
        title: 'The Four Winds',
        author: 'Kristin Hannah',
        price: 12.99,
        coverUrl: 'https://images.unsplash.com/photo-1610882648335-ced8fc8fa6b6?ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D&auto=format&fit=crop&w=800&q=80',
        rating: 4.5,
      }
    ];
  

    const categories = ['Fiction', 'Non-Fiction', 'Mystery', 'Sci-Fi', 'Romance', 'Biography', 'History', 'Self-Help', 'Children', 'Business', 'Cooking', 'Art'];
  

    // DOM elements
    const mobileMenuBtn = document.getElementById('mobile-menu-btn');
    const mobileMenu = document.getElementById('mobile-menu');
    const menuIcon = document.getElementById('menu-icon');
    const closeIcon = document.getElementById('close-icon');
    const featuredBooksContainer = document.getElementById('featured-books');
    const newReleasesContainer = document.getElementById('new-releases-books');
    const categoriesGrid = document.getElementById('categories-grid');


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
  
    // Create category item HTML
    function createCategoryItem(category) {
      return `
        <div class="bg-gray-50 hover:bg-gray-100 rounded-lg p-4 text-center cursor-pointer transition duration-200">
          <p class="font-medium text-gray-800">${category}</p>
        </div>
      `;
    }
  
    // Populate books and categories
    function populateContent() {
      // Featured books
      featuredBooksContainer.innerHTML = featuredBooks.map(book => createBookCard(book)).join('');
      
      // New releases
      newReleasesContainer.innerHTML = newReleases.map(book => createBookCard(book)).join('');
      
      // Categories
      categoriesGrid.innerHTML = categories.map(category => createCategoryItem(category)).join('');
    }
  
    // Event listeners
    mobileMenuBtn.addEventListener('click', toggleMobileMenu);
  
    // Initialize
    populateContent();
    
  });