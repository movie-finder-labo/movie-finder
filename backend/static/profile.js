// DOM elements
const userProfile = document.getElementById('userProfile');
const userName = document.getElementById('userName');
const userAvatar = document.getElementById('userAvatar');
const logoutBtn = document.getElementById('logoutBtn');
const deleteAccountBtn = document.getElementById('deleteAccountBtn');
const deleteModal = document.getElementById('deleteModal');
const cancelDeleteBtn = document.getElementById('cancelDeleteBtn');
const confirmDeleteBtn = document.getElementById('confirmDeleteBtn');
const confirmDeleteInput = document.getElementById('confirmDelete');

// Profile display elements
const profileFullName = document.getElementById('profileFullName');
const profileEmail = document.getElementById('profileEmail');
const profileAge = document.getElementById('profileAge');

// User data
let currentUser = null;
let userPreferences = null;

// Check if user is logged in
function checkLoginStatus() {
    const savedUser = localStorage.getItem('currentUser');
    if (savedUser) {
        currentUser = JSON.parse(savedUser);
        userPreferences = JSON.parse(localStorage.getItem('userPreferences')) || { genres: [], age: 0 };
        updateUIForLoggedInUser();
        loadProfileData();
    } else {
        // Redirect to home if not logged in
        window.location.href = '/';
    }
}

// Update UI when user logs in
function updateUIForLoggedInUser() {
    userName.textContent = currentUser.fullName || currentUser.username || 'User';
    userAvatar.textContent = (currentUser.fullName || currentUser.username || 'U').charAt(0).toUpperCase();
}

// Load profile data
function loadProfileData() {
    // Personal information
    profileFullName.textContent = currentUser.fullName || 'Not set';
    profileEmail.textContent = currentUser.email || currentUser.username || 'Not set';
    profileAge.textContent = userPreferences.age || 'Not set';
}

// Delete account functionality
deleteAccountBtn.addEventListener('click', () => {
    deleteModal.style.display = 'flex';
});

cancelDeleteBtn.addEventListener('click', () => {
    deleteModal.style.display = 'none';
    confirmDeleteInput.value = '';
    confirmDeleteBtn.disabled = true;
});

// Enable delete button only when "DELETE" is typed
confirmDeleteInput.addEventListener('input', () => {
    confirmDeleteBtn.disabled = confirmDeleteInput.value !== 'DELETE';
});

confirmDeleteBtn.addEventListener('click', async () => {
    if (confirmDeleteInput.value === 'DELETE') {
        try {
            // Get JWT token from localStorage if available
            const jwt = localStorage.getItem('jwt') || '';
            
            const response = await fetch('/user/delete', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    jwt: jwt,
                    confirmation: "DELETE"
                })
            });

            const data = await response.json();

            if (data.success) {
                // Clear local storage
                localStorage.removeItem('currentUser');
                localStorage.removeItem('userPreferences');
                localStorage.removeItem('jwt');
                
                // Remove user's ratings
                const userRatings = JSON.parse(localStorage.getItem('userRatings')) || {};
                if (currentUser.username) {
                    delete userRatings[currentUser.username];
                }
                localStorage.setItem('userRatings', JSON.stringify(userRatings));
                
                // Show success message and redirect
                alert('Account deleted successfully');
                window.location.href = '/';
            } else {
                alert('Failed to delete account: ' + data.error);
            }
        } catch (error) {
            console.error('Delete account error:', error);
            alert('Failed to delete account. Please try again.');
        }
    }
});

// Logout functionality
logoutBtn.addEventListener('click', () => {
    fetch('/user/logout')
        .then(() => {
            localStorage.removeItem('currentUser');
            localStorage.removeItem('userPreferences');
            localStorage.removeItem('jwt');
            window.location.href = '/';
        })
        .catch(error => {
            console.error('Logout error:', error);
        });
});

// Close modal when clicking outside
window.addEventListener('click', (e) => {
    if (e.target === deleteModal) {
        deleteModal.style.display = 'none';
        confirmDeleteInput.value = '';
        confirmDeleteBtn.disabled = true;
    }
});

// Initialize the profile page
function initProfilePage() {
    checkLoginStatus();
}

// Start the profile page
initProfilePage();