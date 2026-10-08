import AsyncStorage from '@react-native-async-storage/async-storage';

/**
 * AsyncStorage is unencrypted on-device storage. That's an acceptable
 * tradeoff for a fitness-log app's short-lived access token, but before
 * shipping, consider moving the refresh token (which is long-lived, 30
 * days) to expo-secure-store (backed by iOS Keychain) instead. Swapping
 * this module's implementation is a one-file change — nothing else in the
 * app talks to AsyncStorage directly.
 */
const ACCESS_TOKEN_KEY = 'muster.access_token';
const REFRESH_TOKEN_KEY = 'muster.refresh_token';

export async function saveTokens(accessToken: string, refreshToken: string) {
  await AsyncStorage.setMany({
    [ACCESS_TOKEN_KEY]: accessToken,
    [REFRESH_TOKEN_KEY]: refreshToken,
  });
}

export async function getAccessToken() {
  return AsyncStorage.getItem(ACCESS_TOKEN_KEY);
}

export async function getRefreshToken() {
  return AsyncStorage.getItem(REFRESH_TOKEN_KEY);
}

export async function setAccessToken(accessToken: string) {
  await AsyncStorage.setItem(ACCESS_TOKEN_KEY, accessToken);
}

export async function clearTokens() {
  await AsyncStorage.removeMany([ACCESS_TOKEN_KEY, REFRESH_TOKEN_KEY]);
}
