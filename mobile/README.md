# Muster (mobile)

Expo/React Native (TypeScript) client for the Muster training-log API in
`../backend`. Screens: login/register/forgot-password, dashboard (progress
per event, matching the original app's min/competitive/max tiers),
log/edit entry, paginated history, and settings (logout + in-app account
deletion, required by App Store review).

Verified in this environment: `npx tsc --noEmit` passes with zero errors,
and `npx expo export --platform ios` bundles all 850 modules successfully.
**Not yet verified**: actually running on a simulator or device, or a real
EAS build — this container has no Xcode/iOS simulator, and Android
emulation wasn't attempted. Do that before trusting the UI looks right.

## Local dev

```bash
npm install
cp .env.example .env   # point EXPO_PUBLIC_API_URL at your running backend
npm start
```

Then either:
- press `i` for iOS simulator (needs a Mac with Xcode), or
- press `a` for Android emulator, or
- scan the QR code with the **Expo Go** app on your phone (fastest way to
  see this running with no Mac at all — just make sure `EXPO_PUBLIC_API_URL`
  is reachable from your phone, e.g. your computer's LAN IP, not `127.0.0.1`).

## Getting to an actual App Store build without a Mac

You don't strictly need a Mac for this. [EAS Build](https://docs.expo.dev/build/introduction/)
compiles the iOS binary in Expo's cloud:

```bash
npm install -g eas-cli
eas login
eas build:configure
eas build --platform ios
```

That produces a signed `.ipa`. From there:

```bash
eas submit --platform ios
```

submits it to App Store Connect directly — no Xcode required. You still need:
- an Apple Developer Program account ($99/yr) — `eas build` will walk you
  through connecting it and can manage certificates/provisioning for you.
- to change `app.json`'s `ios.bundleIdentifier` (currently the placeholder
  `com.yourorg.muster`) to your own reverse-DNS identifier before your
  first build.

## Before this goes to production

- [ ] Change `ios.bundleIdentifier` / `android.package` in `app.json` from the placeholder.
- [ ] Point `EXPO_PUBLIC_API_URL` at the deployed backend (HTTPS).
- [ ] Replace the default Expo icon/splash assets in `assets/` with real branding — App Store submission requires a real app icon.
- [ ] Consider moving the refresh token from AsyncStorage to `expo-secure-store` (iOS Keychain) — see the note in `src/api/tokenStorage.ts`.
- [ ] Actually run this on a simulator/device and a real EAS build before submitting — see "Verified" note above.
