// DOM elements
const chatMessages = document.getElementById('chatMessages');
const userInput = document.getElementById('userInput');
const sendButton = document.getElementById('sendButton');
const moviesGrid = document.getElementById('moviesGrid');
const searchInput = document.getElementById('searchInput');
const searchButton = document.getElementById('searchButton');
const loginBtn = document.getElementById('loginBtn');
const logoutBtn = document.getElementById('logoutBtn'); 
const loginModal = document.getElementById('loginModal');
const profileModal = document.getElementById('profileModal');
const submitLogin = document.getElementById('submitLogin');
const showProfileSetup = document.getElementById('showProfileSetup');
const saveProfile = document.getElementById('saveProfile');
const userProfile = document.getElementById('userProfile');
const userName = document.getElementById('userName');
const userAvatar = document.getElementById('userAvatar');
const profilePageBtn = document.getElementById('profilePageBtn'); 

// user data
let currentUser = null;
let userPreferences = {
    genres: [],
    age: 0
};

let movies = []
let ratings = []

function logout() {
    currentUser = null;
    userPreferences = { genres: [], age: 0 };

    // Clear localStorage
    localStorage.removeItem('currentUser');
    localStorage.removeItem('userPreferences');

    // Update UI
    loginBtn.style.display = 'block';
    profileBtn.style.display = 'none';
    logoutBtn.style.display = 'none';
    userProfile.style.display = 'none';

    // Reset movies to default view
    movies = []
    ratings = []
    renderMovies(movies, false);

    // Logout message
    addMessage("You've been logged out. Feel free to login again for personalized recommendations!", false);
}

function shouldLogout(status) {
    if (status != 401) return false
    logout()
    console.log("Unauthorized token, please relog...")
    return true
}

// Check if user is logged in
async function checkLoginStatus() {
    const savedUser = localStorage.getItem('currentUser');
    if (savedUser) {
        currentUser = JSON.parse(savedUser);
        userPreferences = JSON.parse(localStorage.getItem('userPreferences')) || userPreferences;
        updateUIForLoggedInUser();
        renderMovies(getRecommendedMovies());
        await fetchData()
    }
}

// Update UI when user logs in
function updateUIForLoggedInUser() {
    loginBtn.style.display = 'none';
    // REMOVE THIS LINE: profileBtn.style.display = 'block';
    profilePageBtn.style.display = 'block';
    logoutBtn.style.display = 'block';
    userProfile.style.display = 'flex';
    userName.textContent = currentUser.fullName || currentUser.username;
    userAvatar.textContent = (currentUser.fullName || currentUser.username).charAt(0).toUpperCase();
}

// Get user rating stars HTML
function getUserRatingStars(movieId) {
    const userRating = getUserRating(movieId);
    let starsHtml = '<div class="rating-stars">';
    
    for (let i = 1; i <= 5; i++) {
        const isActive = i <= userRating ? 'active' : '';
        starsHtml += `<span class="star ${isActive}" data-rating="${i}">★</span>`;
    }
    
    starsHtml += '</div>';
    return starsHtml;
}

// Get user rating for a movie
function getUserRating(movieId) {
    if (!currentUser) return 0;
    return ratings[movieId]
}

// Add event listeners to rating stars
function addRatingEventListeners() {
    const stars = document.querySelectorAll('.star');
    stars.forEach(star => {
        star.addEventListener('click', handleStarClick);
    });
}

// Handle star click event
function handleStarClick(event) {
    if (!currentUser) {
        addMessage("Please log in to rate movies!", false);
        return;
    }
    
    const star = event.target;
    const rating = parseInt(star.getAttribute('data-rating'));
    const movieId = star.closest('.user-rating').getAttribute('data-movie-id');
    
    // Update the stars visually
    const stars = star.parentElement.querySelectorAll('.star');
    stars.forEach((s, index) => {
        if (index < rating) {
            s.classList.add('active');
        } else {
            s.classList.remove('active');
        }
    });
    
    // Optional: Send rating to backend
    sendRatingToBackend(movieId, rating);
}
async function fetchMovieData() {
    if (!currentUser) return;
    
    try {
        const response = await fetch('/user/fetchmovies', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                jwt: currentUser.jwt,
            })
        });

        if (shouldLogout(response.status)) return
        
        const data = await response.json();
        if (data.success) {
            console.log('Successfully fetched movie data', data);
            movies = data.response.movieData
        }
        else {
            console.log('Failed to fetch movie data:', data.error)
        }
    } catch (error) {
        console.error('Failed to fetch movie data:', error);
    }
}

async function fetchRatingsData() {
    if (!currentUser) return;
    
    try {
        const response = await fetch('/user/fetchratings', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                jwt: currentUser.jwt,
            })
        });

        if (shouldLogout(response.status)) return
        
        const data = await response.json();
        if (data.success) {
            console.log('Successfully fetched ratings data', data);
            ratingsData = []
            data.response.ratingsData.forEach(element => {
                ratingsData[element.movieId] = element.rating
            })
            ratings = ratingsData
        }
        else {
            console.log('Failed to fetch ratings data:', data.error)
        }
    } catch (error) {
        console.error('Failed to fetch ratings data:', error);
    }
}

async function fetchData() {
    await fetchMovieData()
    await fetchRatingsData()
    renderMovies(movies, false)
}

// Send rating to backend (optional)
async function sendRatingToBackend(movieId, rating) {
    if (!currentUser) return;
    
    try {
        const response = await fetch('/user/ratemovie', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                jwt: currentUser.jwt,
                movieId: movieId,
                rating: rating
            })
        });
        if (shouldLogout(response.status)) return
        
        const data = await response.json();
        if (data.success) {
            console.log('Rating saved to backend');
            ratings[movieId] = rating
        }
        else {
            console.log('Failed to save rating to backend:', data.error)
        }
    } catch (error) {
        console.error('Failed to save rating to backend:', error);
    }
}

// Render movies to the grid
function renderMovies(movieList, showMatchScore = true) {
    moviesGrid.innerHTML = '';
    console.log(typeof(movieList))
    Object.values(movieList).forEach(movie => {
        const movieCard = document.createElement('div');
        movieCard.className = 'movie-card';

        let matchScore = 0;
        if (currentUser && showMatchScore) {
            matchScore = calculateMatchScore(movie);
        }

        movieCard.innerHTML = `
            ${matchScore > 80 ? '<div class="recommendation-tag">AI PICK</div>' : ''}
            ${showMatchScore && matchScore > 0 ? `<div class="match-score">${matchScore}%</div>` : ''}
            <img src="${movie.poster}" alt="${movie.title}" class="movie-poster">
            <div class="movie-info">
                <div class="movie-title">${movie.title}</div>
                <div class="movie-year">${movie.year} • Rating: ${movie.rating == "N/A" ? movie.rating : movie.rating + ("/10")}</div>
                <div class="movie-genres">
                    ${movie.genres.map(genre => `<span class="genre-tag">${genre}</span>`).join('')}
                </div>
                <div class="user-rating" data-movie-id="${movie.id}">
                    <div class="rating-label">Your Rating:</div>
                    ${getUserRatingStars(movie.id)}
                </div>
            </div>
        `;
        moviesGrid.appendChild(movieCard);
    });
    
    // Add event listeners for rating stars
    addRatingEventListeners();
}

// Calculate match score for recommendations
function calculateMatchScore(movie) {
    let score = 0;

    // Genre match - more weight since we only have genres now
    const genreMatches = movie.genres.filter(genre =>
        userPreferences.genres.includes(genre)
    ).length;
    score += (genreMatches / movie.genres.length) * 70;

    // Age suitability
    if (userPreferences.age >= (movie.ageSuitability || 13)) {
        score += 30;
    }

    return Math.max(0, Math.min(100, Math.round(score)));
}

// Get recommended movies
function getRecommendedMovies() {
    if (!currentUser) {
        return movies.sort((a, b) => b.rating - a.rating);
    }

    return movies
        .map(movie => ({
            ...movie,
            matchScore: calculateMatchScore(movie)
        }))
        .sort((a, b) => b.matchScore - a.matchScore);
}

// chat functionality
function addMessage(message, isUser) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${isUser ? 'user-message' : 'ai-message'}`;
    messageDiv.textContent = message;
    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// Enhanced AI response with OpenAI
async function getAIResponse(userMessage) {
    try {
        const response = await fetch('/chat/ask', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ message: userMessage, jwt: currentUser.jwt || null})
        });

        if (shouldLogout(response.status))
        {
            addMessage("You must be logged in to ask for recommendations.", false)
            return
        }
        const data = await response.json();
        
        if (data.success) {
            return data.response;
        } else {
            console.error('OpenAI API error:', data.error);
            // Fallback to basic response if OpenAI fails
            return getBasicAIResponse(userMessage);
        }
    } catch (error) {
        console.error('Network error:', error);
        // Fallback to basic response if network fails
        return getBasicAIResponse(userMessage);
    }
}

// Basic AI response as fallback
function getBasicAIResponse(userMessage) {
    const lowerMessage = userMessage.toLowerCase();

    if (currentUser) {
        if (lowerMessage.includes('recommend') || lowerMessage.includes('suggest')) {
            const topMovies = getRecommendedMovies().slice(0, 3);
            return {ai_response: `Based on your profile, I recommend: "${topMovies[0].title}", "${topMovies[1].title}", and "${topMovies[2].title}".`};
        }
    }

    if (lowerMessage.includes('action')) {
        return {ai_response: "For action movies, check out 'The Dark Knight' or 'Inception'."};
    } else if (lowerMessage.includes('drama')) {
        return {ai_response: "For drama, I recommend 'The Shawshank Redemption'."};
    } else if (lowerMessage.includes('comedy')) {
        return {ai_response: "For comedy films, you might enjoy light-hearted movies with humorous plots."};
    } else if (lowerMessage.includes('sci-fi') || lowerMessage.includes('science fiction')) {
        return {ai_response: "For science fiction, I recommend 'Inception' or 'The Matrix'."};
    } else {
        return {ai_response: "I can help you find great movies. Tell me what genres you like or what mood you're in!"};
    }
}

// Enhanced send message function with OpenAI
async function sendMessage() {
    const message = userInput.value.trim();
    if (message) {
        addMessage(message, true);
        userInput.value = '';
        
        // Show typing indicator
        const typingIndicator = document.createElement('div');
        typingIndicator.className = 'message ai-message typing-indicator';
        typingIndicator.innerHTML = '<div class="typing-dots"><span></span><span></span><span></span></div>';
        chatMessages.appendChild(typingIndicator);
        chatMessages.scrollTop = chatMessages.scrollHeight;

        try {
            const aiResponse = await getAIResponse(message);
            addMessage(aiResponse.ai_response, false);
        } catch (error) {
            console.error('Error getting AI response:', error);
            addMessage("Sorry, I encountered an error. Please try again.", false);
        } finally {
            // Remove typing indicator
            chatMessages.removeChild(typingIndicator);
        }
    }
}

// Login functionality with Flask backend
submitLogin.addEventListener('click', async () => {
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;

    if (username && password) {
        try {
            const response = await fetch('/user/login', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ username, password })
            });

            if (shouldLogout(response.status)) return
            const data = await response.json();

            if (data.success) {
                // For demo, we'll still use localStorage
                currentUser = { username, fullName: username, jwt: data.response.jwt };
                localStorage.setItem('currentUser', JSON.stringify(currentUser));

                loginModal.style.display = 'none';
                updateUIForLoggedInUser();
                renderMovies(getRecommendedMovies());

                // Reset form
                document.getElementById('username').value = '';
                document.getElementById('password').value = '';

                // Welcome message
                addMessage(`Welcome, ${username}! I'm ready to help you find great movies.`, false);
                await fetchData()
            } else {
                alert('Login failed: ' + data.message);
            }
        } catch (error) {
            console.error('Login error:', error);
            alert('Login failed. Please try again.');
        }
    } else {
        alert('Please enter both username and password');
    }
});

// Show profile setup
showProfileSetup.addEventListener('click', (e) => {
    e.preventDefault();
    loginModal.style.display = 'none';
    profileModal.style.display = 'flex';
});

// Save profile - update this section
saveProfile.addEventListener('click', async () => {
    const fullName = document.getElementById('fullName').value;
    const email = document.getElementById('email').value;
    const password = document.getElementById('profilePassword').value;
    const confirmPassword = document.getElementById('confirmPassword').value;
    const age = parseInt(document.getElementById('age').value);

    // Get selected genres
    const genreCheckboxes = document.querySelectorAll('.checkbox-group input[type="checkbox"]:checked');
    const genres = Array.from(genreCheckboxes).map(cb => cb.value);

    // Validation
    if (!fullName || !email || !password || !confirmPassword || !age || genres.length === 0) {
        alert('Please complete all fields and select at least one genre');
        return;
    }

    if (password !== confirmPassword) {
        alert('Passwords do not match');
        return;
    }

    if (password.length < 6) {
        alert('Password must be at least 6 characters long');
        return;
    }

    try {
        const response = await fetch('/user/register', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                username: email, // Using email as username
                password: password,
                age: age,
                genres: genres
            })
        });

        if (shouldLogout(response.status)) return
        const data = await response.json();

        if (data.success) {
            // Create user locally
            currentUser = { 
                username: email,
                fullName: fullName,
                email: email,
                jwt: data.response.jwt  // Add JWT token
            };

            userPreferences = { genres, age };

            // Save to localStorage
            localStorage.setItem('currentUser', JSON.stringify(currentUser));
            localStorage.setItem('userPreferences', JSON.stringify(userPreferences));

            // Update UI
            updateUIForLoggedInUser(); // This will show My Profile button
            profileModal.style.display = 'none';

            // Reset form
            document.getElementById('fullName').value = '';
            document.getElementById('email').value = '';
            document.getElementById('profilePassword').value = '';
            document.getElementById('confirmPassword').value = '';
            document.getElementById('age').value = '';
            document.querySelectorAll('.checkbox-group input[type="checkbox"]').forEach(cb => {
                cb.checked = false;
            });

            // Show personalized recommendations
            renderMovies(getRecommendedMovies());

            // Welcome message
            addMessage(`Welcome, ${fullName}! I've learned your preferences for ${genres.join(', ')} movies. Ask me for personalized recommendations!`, false);
            await fetchData()
        } else {
            alert('Registration failed: ' + data.error);
        }
    } catch (error) {
        console.error('Registration error:', error);
        alert('Registration failed. Please try again.');
    }
});

logoutBtn.addEventListener('click', () => {
    // Call Flask logout endpoint
    fetch('/user/logout')
        .then(() => logout())
        .catch(error => {
            console.error('Logout error:', error);
        });
});

// Modal controls
loginBtn.addEventListener('click', () => {
    loginModal.style.display = 'flex';
});

// Close modals when clicking outside
window.addEventListener('click', (e) => {
    if (e.target === loginModal) {
        loginModal.style.display = 'none';
    }
    if (e.target === profileModal) {
        profileModal.style.display = 'none';
    }
});

// Search functionality
searchButton.addEventListener('click', () => {
    const searchTerm = searchInput.value.toLowerCase();
    if (searchTerm) {
        const filteredMovies = movies.filter(movie =>
            movie.title.toLowerCase().includes(searchTerm) ||
            movie.genres.some(genre => genre.toLowerCase().includes(searchTerm))
        );
        renderMovies(filteredMovies, false);
    } else {
        renderMovies(getRecommendedMovies());
    }
});

searchInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        searchButton.click();
    }
});

// chat event listeners
sendButton.addEventListener('click', sendMessage);
userInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        sendMessage();
    }
});

// Auto-generate recommendations when user logs in with preferences
function generateAutoRecommendations() {
    if (currentUser && userPreferences.genres.length > 0) {
        const autoMessage = `Suggest 3 specific movie recommendations based on my preferences for ${userPreferences.genres.join(', ')} genres.`;
        setTimeout(() => {
            sendButton.disabled = true;
            addMessage("Let me suggest some movies based on your profile...", false);
            
            // Simulate AI thinking for auto-recommendations
            setTimeout(async () => {
                try {
                    const aiResponse = await getAIResponse(autoMessage);
                    addMessage(aiResponse, false);
                } catch (error) {
                    console.error('Auto-recommendation error:', error);
                    addMessage("Based on your profile, I recommend checking out popular movies in your preferred genres!", false);
                } finally {
                    sendButton.disabled = false;
                }
            }, 1500);
        }, 2000);
    }
}

// Initialize the app
function initApp() {
    // Initial movie render
    renderMovies(movies, false);

    // Check login status
    checkLoginStatus();

    // Add initial AI message
    setTimeout(() => {
        if (!currentUser) {
            addMessage("You can ask me for movie recommendations by genre, or login for personalized suggestions!", false);
        } else {
            // Generate auto-recommendations for returning users
            generateAutoRecommendations();
        }
    }, 1000);
}

// Start the app
initApp();