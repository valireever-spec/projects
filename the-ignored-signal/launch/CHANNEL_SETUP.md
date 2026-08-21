# Channel Setup — Launch Runbook

Everything you need to stand up the YouTube channel by hand. I can't create the
account (interactive signup + phone verification + ToS are yours to do), but all
the copy-paste assets below are ready.

---

## 0. Naming decision (do this first)

Your rendered Romanian videos are branded **"Sub Radar"** (the on-screen header).
The original brief used localized names (*Semnalul Ignorat / The Ignored Signal /
…*). Pick one line and stay consistent:

- **Option A — one brand, translated (recommended, matches the videos):**
  Sub Radar → Sous les Radars → Unterm Radar → Sotto i Radar → Under the Radar
- **Option B — the brief's localized names:**
  Semnalul Ignorat / Le Signal Ignoré / Das Überhörte Signal / Il Segnale
  Ignorato / The Ignored Signal

The runbook below assumes **Option A**, Romanian channel first (the one you have
7 finished videos for). Swap names if you choose B.

### Handles & names (Option A)

| Lang | Channel name | @handle | Backup handles |
|------|--------------|---------|----------------|
| RO | Sub Radar | `@SubRadarRO` | `@SubRadar.RO`, `@SubRadarRomania` |
| EN | Under the Radar | `@UnderRadarEU` | `@SubRadarEN` |
| FR | Sous les Radars | `@SousLesRadars` | `@SubRadarFR` |
| DE | Unterm Radar | `@UntermRadarEU` | `@SubRadarDE` |
| IT | Sotto i Radar | `@SottoIRadar` | `@SubRadarIT` |

(Handles must be 3–30 chars, letters/numbers/`.`/`_`/`-`, and unique — have the
backups ready in case the first is taken.)

---

## 1. Anonymity + identity prep (before touching YouTube)

- [ ] **Email:** create a dedicated ProtonMail (or similar) — this is the channel's
  identity, kept separate from personal mail.
- [ ] **Phone for verification:** Google requires a number and increasingly
  **rejects VoIP numbers**. Have a real mobile number you can receive one SMS on.
  (You can remove it from the account afterward in most cases.)
- [ ] **Password manager** entry for the Google account + recovery codes.
- [ ] *(optional)* VPN (e.g. Mullvad) during signup if you want IP separation.

> ⚠️ Reality check: **AdSense payout later needs a real legal payee** (your
> Estonian OÜ). Full anonymity works for the *public* channel, not for getting
> paid. Plan the OÜ before you cross the monetization thresholds.

---

## 2. Create the Google account, then the channel

1. Create the Google account with the ProtonMail as recovery + the phone for
   verification.
2. Go to **youtube.com**, sign in.
3. Recommended: use a **Brand Account** channel (not the personal one) — it lets
   you add managers, run multiple language channels under one login, and transfer
   ownership to the OÜ later.
   - YouTube → click avatar → **Settings** → **Add or manage your channel(s)** →
     **Create a channel** → **Use a custom name** → enter **Sub Radar**.
4. **Set the @handle** (Settings → Channel → Advanced, or the handle field):
   `@SubRadarRO`.

---

## 3. Branding (upload the generated assets)

Files are in `launch/branding/`:

- **Banner / channel art:** `banner_sub_radar_2560x1440.png` — upload under
  Customize channel → Branding → Banner image. (Safe area is the center; the art
  keeps all text there so it shows on phone, desktop, and TV.)
- **Profile picture:** `avatar_sub_radar_800x800.png` → Branding → Picture.
- **Video watermark:** you can reuse the avatar → Branding → Video watermark.

---

## 4. Channel settings (YouTube Studio)

- **Customize channel → Basic info:**
  - Name: **Sub Radar** · Handle: **@SubRadarRO**
  - Description: paste the RO *About* text from §6.
  - Language: Romanian · Country: Romania
  - Links: (optional) other-language channels once they exist.
- **Settings → Channel → Advanced:**
  - Category/keywords: `știri, Europa, Uniunea Europeană, date oficiale, Eurostat,
    fapte, semnale ignorate`
  - Audience: **"No, set this channel as not made for kids."**
- **Settings → Upload defaults:** paste a default description + hashtags (from any
  `_upload.md`) so every upload starts pre-filled.

---

## 5. Uploading each video (repeat per video)

Everything you need per video is in `output/<slug>_upload.md` +
`output/<slug>_thumb.jpg`.

1. **Create → Upload video** → pick `output/<slug>.mp4`.
2. **Title / Description / hashtags:** copy from the video's `_upload.md`
   (YouTube Shorts section).
3. **Thumbnail:** upload `output/<slug>_thumb.jpg`.
4. **Details:**
   - Audience: **not made for kids**
   - Language: Romanian · Category: **News & Politics**
5. **Altered content (REQUIRED):** in the "Altered content" step choose
   **"Yes"** — the narration is an AI-generated voice. This is the disclosure your
   upload sheets remind you about.
6. **Visibility:** Public (or Schedule).

> Shorts note: keep the video ≤ 3 min and include `#Shorts` in the title/description
> (already in the sheets). Your videos are 62 s — good for Shorts *and* over
> TikTok's 60 s monetization floor.

---

## 6. About / channel descriptions (per language)

**RO — Sub Radar**
> Sub Radar — semnale ignorate din Europa, explicate clar și cu sursele pe ecran.
> Povești reale care s-au raportat scurt, apoi au dispărut din știri: date UE,
> rapoarte oficiale, statistici. Fără opinii, fără senzațional — doar fapte, cu
> sursa afișată în fiecare clip.
> Narațiune cu voce generată de AI; imaginile sunt ilustrative.
> Clipuri scurte, de câteva ori pe săptămână.

**EN — Under the Radar**
> Under the Radar — underreported European stories, explained clearly with the
> sources on screen. Real stories that were reported briefly, then dropped from
> the news: EU data, official reports, statistics. No opinion, no hype — just
> facts, with the source shown in every clip.
> AI-generated voice narration; footage is illustrative.
> Short videos, a few times a week.

**FR — Sous les Radars**
> Sous les Radars — des histoires européennes passées sous silence, expliquées
> clairement, sources à l'écran. Des faits qui ont été rapportés brièvement, puis
> oubliés : données de l'UE, rapports officiels, statistiques. Sans opinion, sans
> sensationnalisme — juste les faits, avec la source affichée dans chaque clip.
> Voix off générée par IA ; images d'illustration.
> Des vidéos courtes, plusieurs fois par semaine.

**DE — Unterm Radar**
> Unterm Radar — unterberichtete europäische Geschichten, klar erklärt, mit den
> Quellen im Bild. Fakten, die kurz gemeldet und dann vergessen wurden:
> EU-Daten, offizielle Berichte, Statistiken. Keine Meinung, kein Sensationalismus
> — nur Fakten, mit der Quelle in jedem Clip.
> KI-generierte Stimme; Bildmaterial ist illustrativ.
> Kurze Videos, mehrmals pro Woche.

**IT — Sotto i Radar**
> Sotto i Radar — storie europee ignorate, spiegate con chiarezza e con le fonti
> in sovrimpressione. Fatti riportati brevemente e poi spariti dalle notizie: dati
> UE, rapporti ufficiali, statistiche. Nessuna opinione, nessun sensazionalismo —
> solo fatti, con la fonte mostrata in ogni clip.
> Voce narrante generata dall'IA; immagini illustrative.
> Video brevi, alcune volte a settimana.

---

## 7. TikTok (same idea, briefly)

- Separate account per language; sign up with the ProtonMail + phone.
- Use the **TikTok** section of each `_upload.md` for the caption + hashtags.
- Turn on the **"AI-generated content"** label in the video's settings (the TikTok
  equivalent of YouTube's Altered-content disclosure).
- Your 62 s length clears TikTok's 60 s Creator-Rewards floor.

---

## Quick checklist

- [ ] ProtonMail + phone + password manager ready
- [ ] Google account created (VPN optional)
- [ ] Brand Account channel "Sub Radar" created, `@SubRadarRO` set
- [ ] Banner + avatar uploaded (`launch/branding/`)
- [ ] About text + keywords + "not made for kids" set
- [ ] Upload defaults pre-filled
- [ ] First video uploaded with thumbnail + **Altered content: Yes**
