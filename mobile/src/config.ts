/**
 * API base URL. Set via the EXPO_PUBLIC_API_URL env var (Expo inlines any
 * EXPO_PUBLIC_* var at build time — see https://docs.expo.dev/guides/environment-variables/).
 *
 * Create a `.env` file (see .env.example) for local dev. Point it at
 * whatever the backend is currently reachable at:
 *   - iOS simulator on the same Mac as the backend: http://127.0.0.1:5000
 *   - Expo Go on a physical device: http://<your-computer's-LAN-IP>:5000
 *   - Deployed backend: https://your-backend-host.example.com
 */
export const API_BASE_URL =
  process.env.EXPO_PUBLIC_API_URL ?? 'http://127.0.0.1:5000';
