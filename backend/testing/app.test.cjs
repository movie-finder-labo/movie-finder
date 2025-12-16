/**
 * Unit tests for appLogic.cjs
 * These are true unit tests (logic only, no DOM, no backend)
 */
const appLogic = require('../static/appLogic.cjs');
console.log(appLogic);


const {
  shouldLogout,
  calculateMatchScore,
  getUserRating,
  getRecommendedMovies,
  getBasicAIResponse
} = appLogic;

// ---------------- RESET STATE BEFORE EACH TEST ----------------
beforeEach(() => {
  appLogic.resetState();
});

// ---------------- 1. shouldLogout ----------------
describe('shouldLogout()', () => {
  test('returns true when status is 401', () => {
    expect(shouldLogout(401)).toBe(true);
  });

  test('returns false when status is not 401', () => {
    expect(shouldLogout(200)).toBe(false);
  });
});

// ---------------- 2. calculateMatchScore ----------------
describe('calculateMatchScore()', () => {
  test('returns a score between 0 and 100', () => {
    userPreferences.genres.push('Action');
    userPreferences.age = 18;

    const movie = {
      genres: ['Action', 'Comedy'],
      ageSuitability: 13
    };

    const score = calculateMatchScore(movie);

    expect(score).toBeGreaterThanOrEqual(0);
    expect(score).toBeLessThanOrEqual(100);
  });
});

// ---------------- 3. getUserRating ----------------
describe('getUserRating()', () => {
  test('returns 0 when user is not logged in', () => {
    expect(getUserRating(ratings, 1)).toBe(0);
  });

  test('returns correct rating when user is logged in', () => {
    currentUser = { username: 'testUser' };
    ratings[1] = 4;

    expect(getUserRating(1)).toBe(4);
  });
});

// ---------------- 4. getRecommendedMovies ----------------
describe('getRecommendedMovies()', () => {
  test('sorts movies by rating when user is not logged in', () => {
    movies.push(
      { title: 'Movie A', rating: 6, genres: ['Action'], ageSuitability: 13 },
      { title: 'Movie B', rating: 9, genres: ['Drama'], ageSuitability: 13 }
    );

    const result = getRecommendedMovies();
    expect(result[0].title).toBe('Movie B');
  });
});

// ---------------- 5. getBasicAIResponse ----------------
describe('getBasicAIResponse()', () => {
  test('returns action response when keyword is present', () => {
    const response = getBasicAIResponse('I like action movies');
    expect(response.ai_response.toLowerCase()).toContain('action');
  });

  test('returns default response otherwise', () => {
    const response = getBasicAIResponse('hello');
    expect(response.ai_response).toBeDefined();
  });
});
