// backend/static/appLogic.cjs

// ---------------- STATE HELPERS ----------------
function resetState() {
  currentUser = null;
  userPreferences = { genres: [], age: 0 };
  movies = [];
  ratings = {};
}

// ---------------- LOGIC FUNCTIONS ----------------
function shouldLogout(status) {
  return status == 401
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

function getUserRating(movieId) {
  if (!currentUser) return 0;
  return ratings[movieId] || 0;
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

// ---------------- EXPORTS (COMMONJS ONLY) ----------------
module.exports = {
  shouldLogout,
  calculateMatchScore,
  getUserRating,
  getRecommendedMovies,
  getBasicAIResponse,
  resetState,
};
