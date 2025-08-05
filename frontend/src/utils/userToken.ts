/**
 * User token management for anonymous and authenticated users
 */

const USER_TOKEN_KEY = 'ecotrace-user-token';
const USER_INFO_KEY = 'ecotrace-user-info';

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

export function setUserToken(token: string): void {
  if (typeof window !== 'undefined') {
    localStorage.setItem(USER_TOKEN_KEY, token);
  }
}

export function clearUserToken(): void {
  if (typeof window !== 'undefined') {
    localStorage.removeItem(USER_TOKEN_KEY);
    localStorage.removeItem(USER_INFO_KEY);
  }
}

export interface UserInfo {
  id: string;
  email: string;
  name?: string;
  is_anonymous: boolean;
  created_at: string;
  email_verified: boolean;
}

export function setUserInfo(userInfo: UserInfo): void {
  if (typeof window !== 'undefined') {
    localStorage.setItem(USER_INFO_KEY, JSON.stringify(userInfo));

    // Dispatch custom event to notify components of login
    window.dispatchEvent(new CustomEvent('userLogin', { detail: userInfo }));
  }
}

export function getUserInfo(): UserInfo | null {
  if (typeof window === 'undefined') {
    return null;
  }

  const userInfoStr = localStorage.getItem(USER_INFO_KEY);
  if (!userInfoStr) {
    return null;
  }

  try {
    return JSON.parse(userInfoStr);
  } catch {
    return null;
  }
}

export function isAuthenticated(): boolean {
  const userInfo = getUserInfo();
  return userInfo !== null && !userInfo.is_anonymous;
}

export async function registerUser(email: string, password: string, name?: string) {
  const response = await fetch('http://localhost:8000/auth/register', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ email, password, name }),
  });

  const data = await response.json();

  if (data.success && data.token && data.user) {
    localStorage.setItem(USER_TOKEN_KEY, data.token);
    setUserInfo(data.user);
  }

  return data;
}

export async function loginUser(email: string, password: string) {
  const response = await fetch('http://localhost:8000/auth/login', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ email, password }),
  });

  const data = await response.json();

  if (data.success && data.token && data.user) {
    localStorage.setItem(USER_TOKEN_KEY, data.token);
    setUserInfo(data.user);
  }

  return data;
}

export function logoutUser(): void {
  clearUserToken();

  // Dispatch custom event to notify components of logout
  if (typeof window !== 'undefined') {
    window.dispatchEvent(new CustomEvent('userLogout'));
  }
}

export async function getAuthHeaders(): Promise<Record<string, string>> {
  return {
    'Content-Type': 'application/json',
    'X-User-Token': await getUserToken()
  };
}
