import axios, { AxiosInstance } from "axios";
import { tokenStorage } from "./token-storage";

// Backend API Base URL
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

/**
 * Create axios instance with default headers and interceptors
 */
const apiClient: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
});

/**
 * Request interceptor to add Authorization header
 * Automatically includes access token from token storage
 */
apiClient.interceptors.request.use(
  (config) => {
    // Get token from token storage
    const token = tokenStorage.getAccessToken();

    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }

    // Set Content-Type to application/json for non-FormData requests
    // FormData requests should not have Content-Type set - let browser handle it
    if (!(config.data instanceof FormData)) {
      config.headers["Content-Type"] = "application/json";
    }

    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

/**
 * Response interceptor to handle token expiration and refresh
 */
apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    // If 401 and not already retried, attempt to refresh token
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      try {
        const refreshToken = tokenStorage.getRefreshToken();

        if (refreshToken) {
          const response = await axios.post(
            `${API_BASE_URL}/api/auth/refresh-token`,
            { refresh_token: refreshToken }
          );

          const { access_token } = response.data;
          tokenStorage.setTokens(access_token, refreshToken);

          // Retry original request with new token
          originalRequest.headers.Authorization = `Bearer ${access_token}`;
          return apiClient(originalRequest);
        }
      } catch (refreshError) {
        // Refresh failed, redirect to login
        tokenStorage.clearTokens();
        window.location.href = "/auth/login";
        return Promise.reject(refreshError);
      }
    }

    return Promise.reject(error);
  }
);

export default apiClient;

/**
 * AUTHENTICATION API CALLS
 * 
 * Example usage in components:
 * 
 * 1. Register
 * -----
 * const response = await apiClient.post('/api/auth/register', {
 *   username: 'company123',
 *   email: 'company@example.com',
 *   password: 'securePassword123',
 *   company_name: 'My Company',
 *   website_url: 'https://mycompany.com'
 * });
 * 
 * 2. Verify OTP
 * -----
 * const response = await apiClient.post('/api/auth/verify-otp', {
 *   email: 'company@example.com',
 *   otp: '123456'
 * });
 * localStorage.setItem('access_token', response.data.tokens.access_token);
 * localStorage.setItem('refresh_token', response.data.tokens.refresh_token);
 * 
 * 3. Login
 * -----
 * const response = await apiClient.post('/api/auth/login', {
 *   email: 'company@example.com',
 *   password: 'securePassword123'
 * });
 * localStorage.setItem('access_token', response.data.tokens.access_token);
 * localStorage.setItem('refresh_token', response.data.tokens.refresh_token);
 * 
 * 4. Get Current Profile
 * -----
 * const response = await apiClient.get('/api/auth/me');
 * // Returns company details including id, name, subscription tier, etc.
 * 
 * 5. Refresh Token
 * -----
 * const response = await apiClient.post('/api/auth/refresh-token', {
 *   refresh_token: 'your-refresh-token'
 * });
 * localStorage.setItem('access_token', response.data.access_token);
 * 
 * 6. Forgot Password
 * -----
 * const response = await apiClient.post('/api/auth/forgot-password', {
 *   email: 'company@example.com'
 * });
 * 
 * 7. Reset Password
 * -----
 * const response = await apiClient.post('/api/auth/reset-password', {
 *   email: 'company@example.com',
 *   otp: '123456',
 *   new_password: 'newSecurePassword123'
 * });
 */

/**
 * USING WITH REACT QUERY
 * 
 * Example:
 * 
 * const useLogin = () => {
 *   return useMutation({
 *     mutationFn: (data) => apiClient.post('/api/auth/login', data),
 *     onSuccess: (response) => {
 *       const { tokens } = response.data;
 *       localStorage.setItem('access_token', tokens.access_token);
 *       localStorage.setItem('refresh_token', tokens.refresh_token);
 *     },
 *   });
 * };
 * 
 * In component:
 * const { mutate, isPending } = useLogin();
 * const handleLogin = (email, password) => {
 *   mutate({ email, password });
 * };
 */

/**
 * ERROR HANDLING
 * 
 * All API errors follow this format:
 * {
 *   detail: "Error message",
 *   error_code?: "CODE" (optional)
 * }
 * 
 * Example:
 * try {
 *   const response = await apiClient.post('/api/auth/login', data);
 * } catch (error) {
 *   if (error.response?.status === 401) {
 *     console.log(error.response.data.detail); // "Invalid email or password"
 *   }
 * }
 */
