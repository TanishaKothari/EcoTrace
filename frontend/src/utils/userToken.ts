/**
 * User token management for anonymous users
 */

const USER_TOKEN_KEY = 'ecotrace-user-token';

export async function getUserToken(): Promise<string> {
  // Check if we're in browser environment
  if (typeof window === 'undefined') {
    return await generateToken();
  }

  let token = localStorage.getItem(USER_TOKEN_KEY);
  if (!token) {
    token = await generateToken();
    localStorage.setItem(USER_TOKEN_KEY, token);
  }
  return token;
}

export async function generateToken(): Promise<string> {
  // Request a secure token from the backend
  try {
    const response = await fetch('http://localhost:8000/auth/token', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      }
    });

    if (response.ok) {
      const data = await response.json();
      return data.token;
    }
  } catch (error) {
    console.warn('Failed to get token from backend, using fallback');
  }

  // Fallback: generate a simple token (backend will replace with secure one)
  const timestamp = Date.now();
  const random = Math.random().toString(36).substr(2, 9);
  return `temp_${timestamp}_${random}`;
}

export function clearUserToken(): void {
  if (typeof window !== 'undefined') {
    localStorage.removeItem(USER_TOKEN_KEY);
  }
}

export async function getAuthHeaders(): Promise<Record<string, string>> {
  return {
    'Content-Type': 'application/json',
    'X-User-Token': await getUserToken()
  };
}
