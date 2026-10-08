# App Store Connect metadata — draft

Fill in the `[FILL IN]` items in App Store Connect when you create the app
record (requires an active Apple Developer Program membership).

## Basics

- **App name** (30 char max, must be unique on the Store): `Muster` or `Muster – PST Training Log` — check availability in App Store Connect first, "Muster" alone is a common word and may be taken.
- **Subtitle** (30 char max): `PST/PFT training tracker`
- **Bundle ID**: must match `app.json`'s `ios.bundleIdentifier` in the mobile app — currently the placeholder `com.yourorg.muster`, change both together.
- **Primary category**: Health & Fitness
- **Secondary category** (optional): Sports
- **Age rating**: 4+ — no objectionable content in this version (no user-generated public content, no violence, no mature themes).

## Why category matters here

The app tracks push-ups, sit-ups, pull-ups, run, and swim times against
selection-style physical standards. Keep the store listing framed as
**fitness/training tracking** (what it actually is) rather than anything
tactical or military-operational — that keeps it in Health & Fitness review
lane rather than raising unrelated review flags. The standards data itself
(rep counts, times) is not sensitive or restricted content.

## Description (draft — 4000 char max, this is well under)

> Muster is a straightforward training log for tracking push-ups, sit-ups,
> pull-ups, a 1.5-mile run, and a 500m swim against selection-style
> physical standards.
>
> Log a result and instantly see where it falls — below standard, passing,
> competitive, or max — with your progress visualized against the actual
> standard line, not just a raw number.
>
> • Track 5 core events with real minimum/competitive/max standards
> • See your most recent result for each event at a glance
> • Full history of every entry, with notes
> • Your data is yours — delete your account and everything with it, anytime
>
> No ads. No social feed. No distractions — just your numbers against the standard.

*(Rewrite this once you've decided on final branding/positioning — this is a functional draft, not final marketing copy.)*

## Keywords (100 char max, comma-separated, no spaces needed)

`PST,PFT,fitness,training log,pushups,situps,pullups,swim,run,selection,workout tracker`

## What's New (for the first version)

`Initial release.`

## Support & marketing URLs (both required)

- **Support URL**: `[FILL IN — even a simple page with your support email/FAQ works]`
- **Marketing URL** (optional): `[FILL IN or leave blank]`
- **Privacy Policy URL** (required): `[FILL IN — see privacy-policy.md, must be hosted and live before submission]`

## App Privacy ("nutrition label") — Data Collection

App Store Connect asks you to declare, per data type, whether it's collected and how it's used. Based on what the app in `backend/` and `mobile/` actually does right now:

| Data type | Collected? | Linked to identity? | Used for tracking? | Purpose |
|---|---|---|---|---|
| Email Address | Yes | Yes | No | App functionality (account) |
| User ID / Username | Yes | Yes | No | App functionality (account) |
| Other User Content (workout entries, notes) | Yes | Yes | No | App functionality |
| Precise/Coarse Location | No | — | — | — |
| Contacts, Photos, Identifiers, Usage Data, Diagnostics | No (none of this is collected in the current build) | — | — | — |

"Used for tracking" is **No** across the board — this app has no ad
network or cross-app tracking SDK. If you later add analytics, crash
reporting (Sentry, etc.), or ads, update this table and the corresponding
declaration in App Store Connect before that build ships — Apple checks
this against actual app behavior.

## Account deletion (Guideline 5.1.1(v))

Already implemented: **Settings → Delete account** in the app calls
`DELETE /api/auth/account`, which permanently deletes the user and cascades
to their log entries. No separate web flow or support request needed —
this is required for approval since the app supports account creation.

## Screenshots

You'll need screenshots for at least the largest required iPhone size
(check current requirements in App Store Connect when you set this up —
Apple's required device sizes change periodically). Capture from a real
build (simulator or device), not mockups:
1. Dashboard with a few logged results (shows the tier/progress concept)
2. Log entry screen
3. History list
4. (Optional) Settings screen showing account deletion — good to have but not required
