// DOM elements
const chatMessages = document.getElementById('chatMessages');
const userInput = document.getElementById('userInput');
const sendButton = document.getElementById('sendButton');
const moviesGrid = document.getElementById('moviesGrid');
const searchInput = document.getElementById('searchInput');
const searchButton = document.getElementById('searchButton');
const loginBtn = document.getElementById('loginBtn');
const profileBtn = document.getElementById('profileBtn');
const logoutBtn = document.getElementById('logoutBtn');
const loginModal = document.getElementById('loginModal');
const profileModal = document.getElementById('profileModal');
const submitLogin = document.getElementById('submitLogin');
const showProfileSetup = document.getElementById('showProfileSetup');
const saveProfile = document.getElementById('saveProfile');
const userProfile = document.getElementById('userProfile');
const userName = document.getElementById('userName');
const userAvatar = document.getElementById('userAvatar');

// User data
let currentUser = null;
let userPreferences = {
    genres: [],
    mood: '',
    frequency: '',
    age: 0
};

let movies = []

// Check if user is logged in
function checkLoginStatus() {
    const savedUser = localStorage.getItem('currentUser');
    if (savedUser) {
        currentUser = JSON.parse(savedUser);
        userPreferences = JSON.parse(localStorage.getItem('userPreferences')) || userPreferences;
        updateUIForLoggedInUser();
        renderMovies(getRecommendedMovies());
    }
}

// Update UI when user logs in
function updateUIForLoggedInUser() {
    loginBtn.style.display = 'none';
    profileBtn.style.display = 'block';
    logoutBtn.style.display = 'block';
    userProfile.style.display = 'flex';
    userName.textContent = currentUser.fullName || currentUser.username;
    userAvatar.textContent = (currentUser.fullName || currentUser.username).charAt(0).toUpperCase();
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
            </div>
        `;
        moviesGrid.appendChild(movieCard);
    });
}

// Calculate match score for recommendations
function calculateMatchScore(movie) {
    let score = 0;

    // Genre match
    const genreMatches = movie.genres.filter(genre =>
        userPreferences.genres.includes(genre)
    ).length;
    score += (genreMatches / movie.genres.length) * 40;

    // Mood match
    if (movie.mood === userPreferences.mood) {
        score += 30;
    }

    // Age suitability
    if (userPreferences.age >= movie.ageSuitability) {
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

// Chat functionality
function addMessage(message, isUser, movieData) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${isUser ? 'user-message' : 'ai-message'}`;
    messageDiv.textContent = message;
    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
    if (movieData) {
        movies = movieData
        renderMovies(movies, false)
    }
}

// Enhanced AI response with OpenAI
async function getAIResponse(userMessage) {
    try {
        // Add user context to the message if logged in
        let enhancedMessage = userMessage;
        if (currentUser) {
            enhancedMessage = `User preferences: ${userPreferences.genres.join(', ')} genres, ${userPreferences.mood} mood, age ${userPreferences.age}. Question: ${userMessage}`;
        }

        const response = await fetch('/chat/ask', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ message: enhancedMessage })
        });

        const data = await response.json();
        console.log(data)
        
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
            return `Based on your profile, I recommend: "${topMovies[0].title}", "${topMovies[1].title}", and "${topMovies[2].title}".`;
        }
    }

    if (lowerMessage.includes('action')) {
        return "For action movies, check out 'The Dark Knight' or 'Inception'.";
    } else if (lowerMessage.includes('drama')) {
        return "For drama, I recommend 'The Shawshank Redemption'.";
    } else if (lowerMessage.includes('comedy')) {
        return "For comedy films, you might enjoy light-hearted movies with humorous plots.";
    } else if (lowerMessage.includes('sci-fi') || lowerMessage.includes('science fiction')) {
        return "For science fiction, I recommend 'Inception' or 'The Matrix'.";
    } else {
        return "I can help you find great movies. Tell me what genres you like or what mood you're in!";
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
            addMessage(aiResponse.ai_response, false, aiResponse.data);
        } catch (error) {
            console.error('Error getting AI response:', error);
            addMessage("Sorry, I encountered an error. Please try again.", false);
        } finally {
            // Remove typing indicator
            chatMessages.removeChild(typingIndicator);
        }
    }
}

// Get structured recommendations based on user profile
async function getStructuredRecommendations() {
    if (!currentUser) return null;
    
    const preferences = `User likes ${userPreferences.genres.join(', ')} genres, prefers ${userPreferences.mood} movies, and is ${userPreferences.age} years old.`;
    
    try {
        const response = await fetch('/chat/recommend', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ preferences: preferences })
        });

        const data = await response.json();
        return data.success ? data.recommendations : null;
    } catch (error) {
        console.error('Structured recommendations error:', error);
        return null;
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

            const data = await response.json();

            if (data.success) {
                // For demo, we'll still use localStorage
                currentUser = { username, fullName: username };
                localStorage.setItem('currentUser', JSON.stringify(currentUser));

                loginModal.style.display = 'none';
                updateUIForLoggedInUser();
                renderMovies(getRecommendedMovies());

                // Reset form
                document.getElementById('username').value = '';
                document.getElementById('password').value = '';

                // Welcome message
                addMessage(`Welcome, ${username}! I'm ready to help you find great movies.`, false);
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

// Save profile
saveProfile.addEventListener('click', async () => {
    const fullName = document.getElementById('fullName').value;
    const age = parseInt(document.getElementById('age').value);
    const mood = document.getElementById('mood').value;
    const frequency = document.getElementById('frequency').value;

    // Get selected genres
    const genreCheckboxes = document.querySelectorAll('.checkbox-group input[type="checkbox"]:checked');
    const genres = Array.from(genreCheckboxes).map(cb => cb.value);

    if (fullName && age && genres.length > 0 && mood && frequency) {
        try {
            const response = await fetch('/user/register', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    username: fullName.toLowerCase().replace(/\s+/g, ''),
                    password: 'default123',
                    fullName,
                    age,
                    genres,
                    mood,
                    frequency
                })
            });

            const data = await response.json();

            if (data.success) {
                // Create user locally
                currentUser = { 
                    username: fullName.toLowerCase().replace(/\s+/g, ''),
                    fullName: fullName
                };

                userPreferences = { genres, mood, frequency, age };

                // Save to localStorage
                localStorage.setItem('currentUser', JSON.stringify(currentUser));
                localStorage.setItem('userPreferences', JSON.stringify(userPreferences));

                // Update UI
                updateUIForLoggedInUser();
                profileModal.style.display = 'none';

                // Show personalized recommendations
                renderMovies(getRecommendedMovies());

                // Welcome message with OpenAI
                addMessage(`Welcome, ${fullName}! I've learned your preferences for ${genres.join(', ')} movies with a ${mood} mood. Ask me for personalized recommendations!`, false);
            } else {
                alert('Registration failed: ' + data.message);
            }
        } catch (error) {
            console.error('Registration error:', error);
            alert('Registration failed. Please try again.');
        }
    } else {
        alert('Please complete all fields in the profile');
    }
});

// Logout functionality
logoutBtn.addEventListener('click', () => {
    // Call Flask logout endpoint
    fetch('/user/logout')
        .then(() => {
            currentUser = null;
            userPreferences = { genres: [], mood: '', frequency: '', age: 0 };

            // Clear localStorage
            localStorage.removeItem('currentUser');
            localStorage.removeItem('userPreferences');

            // Update UI
            loginBtn.style.display = 'block';
            profileBtn.style.display = 'none';
            logoutBtn.style.display = 'none';
            userProfile.style.display = 'none';

            // Reset movies to default view
            renderMovies(movies, false);

            // Logout message
            addMessage("You've been logged out. Feel free to login again for personalized recommendations!", false);
        })
        .catch(error => {
            console.error('Logout error:', error);
        });
});

// Modal controls
loginBtn.addEventListener('click', () => {
    loginModal.style.display = 'flex';
});

profileBtn.addEventListener('click', () => {
    // Populate form with current data
    document.getElementById('fullName').value = currentUser.fullName || '';
    document.getElementById('age').value = userPreferences.age || '';
    document.getElementById('mood').value = userPreferences.mood || '';
    document.getElementById('frequency').value = userPreferences.frequency || '';

    // Check genre boxes
    document.querySelectorAll('.checkbox-group input[type="checkbox"]').forEach(cb => {
        cb.checked = userPreferences.genres.includes(cb.value);
    });

    profileModal.style.display = 'flex';
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

// Chat event listeners
sendButton.addEventListener('click', sendMessage);
userInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        sendMessage();
    }
});

// Auto-generate recommendations when user logs in with preferences
function generateAutoRecommendations() {
    if (currentUser && userPreferences.genres.length > 0) {
        const autoMessage = `Suggest 3 specific movie recommendations based on my preferences for ${userPreferences.genres.join(', ')} genres and ${userPreferences.mood} mood.`;
        setTimeout(() => {
            sendButton.disabled = true;
            addMessage("Let me suggest some movies based on your profile...", false);
            
            // Simulate AI thinking for auto-recommendations
            setTimeout(async () => {
                try {
                    const aiResponse = await getAIResponse(autoMessage);
                    addMessage(aiResponse, false, aiResponse.data);
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