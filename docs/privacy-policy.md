# Muster Privacy Policy

**Effective date:** [FILL IN BEFORE PUBLISHING]
**Last updated:** August 31, 2026

This is a draft written for the current state of the app (account creation,
password auth, and a personal PST/PFT training log). Review it — and have
someone with legal authority to do so approve it — before publishing. Fill
in every `[FILL IN]` placeholder; Apple checks that the linked privacy
policy actually matches what the app collects.

---

## Who this covers

This policy covers the Muster mobile app and its backend, operated by
**[FILL IN: your name or business/legal entity name]** ("we," "us"). Contact:
**[FILL IN: a real support email address]**.

## What we collect

When you create an account:
- **Username** and **email address**
- **Password** — stored as a salted hash (werkzeug/PBKDF2), never in plain text and never visible to us

When you log a workout:
- **Exercise type, value (reps or time), date, and optional notes** you enter

We do not currently collect:
- Location data
- Device identifiers, advertising IDs, or analytics/tracking data
- Payment information (the app has no in-app purchases as of this version)
- Camera, microphone, contacts, or photo library access

*(If you add analytics, crash reporting, ads, or in-app purchase in a
future version, this section and the App Store "nutrition label" both need
to be updated before that version ships — see `app-store-metadata.md`.)*

## How we use it

- Account data (username/email/password) is used only to authenticate you and secure your account.
- Training log data is used only to show your own dashboard, history, and progress against the standards in the app.
- We do not sell your data, and we do not share it with third parties for their own marketing purposes.
- We do not use your data to serve you ads.

## Where it's stored

Your data is stored in a database operated by us at **[FILL IN: your hosting provider, e.g. Render/Fly/AWS, and region]**, transmitted over HTTPS/TLS.

## How long we keep it

We keep your account and training log data for as long as your account exists. You can permanently delete your account and all associated data at any time from **Settings → Delete account** inside the app — this is immediate and cannot be undone, and requires no separate request to us.

## Your choices

- **Delete your account**: in-app, under Settings. This removes your user record and every log entry you've created.
- **Access or correct your data**: contact us at **[FILL IN support email]**.

## Children's privacy

Muster is not directed at children and is not intended for use by anyone under 13 (or the relevant minimum age in your country). We do not knowingly collect data from children. If you believe a child has created an account, contact us at **[FILL IN support email]** and we will delete it.

## Security

Passwords are hashed, not stored in plain text. Data in transit is encrypted via HTTPS. No method of storage or transmission is 100% secure, but we follow standard practices to protect your data.

## Changes to this policy

If this policy changes materially, we'll update the "Last updated" date above and, for significant changes, notify users in-app.

## Contact

**[FILL IN: support email / mailing address if you want one listed]**

---

### Before you publish this

1. Fill in every `[FILL IN]` bracket above.
2. Host this at a stable, public URL (e.g. a page on your own domain) — App Store Connect requires a working privacy policy URL at submission, and it has to stay live for the life of the app.
3. Have someone who can make this call for your business review it — this draft is a starting point, not legal advice.
