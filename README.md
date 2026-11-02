# Arrow Escape v4 — One Board, One Puzzle (Phone-first)

**Complete source update for GitHub Codespaces and GitHub Actions.** Android package ID remains `com.arrowbottles.game`.

## Gameplay changes

- **Unified intertwined campaign:** all 300 layouts are built from one continuous snake/braid of paths spanning former row-band divisions, not six independent blocks. Distant lock dependencies connect different areas of the board. Every level is validated by the same solver rules used by the game.
- **Circular “Orbit Maze”** stages start at level 10 and alternate with woven layouts. Arrows visibly curve around a centre, so their onscreen direction changes as they travel. To preserve fair rules and solvability, the underlying movement/collision logic is still the familiar four-direction logical grid. This is a radial presentation, not a new 3D physics or eight-direction collision engine.
- **12 arrows at level 1, increasing by exactly 4 per level through level 20** (88 arrows). Later levels cap arrow count growth to suit small phone displays and shift difficulty into tighter global dependencies.
- **Puzzle IQ** is a game-only challenge score, not a psychological IQ assessment.
- **Phone-first controls:** tested at 320px and 390px portrait widths; responsive header and bottle shelf, +/−/Fit zoom buttons (at least 44px touch targets), pinch to zoom, drag to pan when zoomed, and hold for 430ms or more to magnify near your finger. All controls also work on tablets.
- Timers, hearts, power-ups, two optional time extensions, daily spins, offline guest gameplay, AdMob bridge and consent logic remain from v3/v2.

## Install via Codespaces

1. In your existing Codespace (on **main**), upload `arrow-escape-v4-mobile-first.zip` into the repository root through Explorer → Upload.
2. In the Codespaces terminal paste:

```bash
unzip -o arrow-escape-v4-mobile-first.zip
cp -a arrow-escape/. ./
rm -rf arrow-escape
rm -f arrow-escape-v4-mobile-first.zip
if [ -d .github/workflows/.github ]; then git rm -r .github/workflows/.github; fi
npm install --no-audit --no-fund
npm test
npm run build:web
```

3. Only if all three commands succeed:

```bash
git add -A
git commit -m "Arrow Escape v4 - unified orbit puzzles mobile-first"
git push origin main
```

4. Open GitHub Actions → **Build Arrow Escape Android**. After a successful job, download the artifact, extract `android/app/build/outputs/apk/debug/app-debug.apk` and install on an Android phone. The artifact contains an AAB too, but Play Store distribution requires signing secrets.

## Verification

- `node --test tests/*.test.js`: **25 passing tests**, including global board continuity, cross-band dependencies, orbit geometry, +4 initial progression, automatic 300-level solver checks and mobile controls.
- Browser smoke tests: narrow 320px portrait and standard 390px portrait; no JavaScript errors; zoom in/out/Fit; automated Level 10 win. Earlier browser checks opened and solved Levels 1, 8, 10 and 20.
- **Not verified here:** native Android Gradle APK/AAB build, actual finger comfort at 88–132 arrows on a small physical phone, live AdMob ad delivery, player median solve times, Google Play signing.
- Production ads remain **off by default**; configure GitHub variable `ADMOB_PRODUCTION=true` after completing AdMob policy/consent checks. The app and banner IDs are preconfigured; rewarded/interstitial units require separate IDs.
- App updates built with a different debug signing key may conflict with an installed older APK. Uninstalling the old APK can delete local progress; back up first if important.

## Maintainer notes

- Core generated dataset: `scripts/v4-campaign.json`; reproducible generator: `scripts/build_v4_levels.py`.
- `scripts/assemble_v4.py` and `scripts/apply_mobile_v4.py` are **one-time patch utilities** provided for transparency; do not rerun against this already-patched `www/index.html`.
- The browser-facing game and independent HTML backup are `www/index.html` and `arrow-bottles-final-index.html`.
- Native dependencies are installed by `npm install` inside Codespaces/GitHub Actions. `package-lock.json` is intentionally not included; existing repos can regenerate it with `npm install`. Run `npm install` before invoking `npm run build:web`.
- Google Play Billing is not integrated. Do not claim the game has working real-money purchases yet.
