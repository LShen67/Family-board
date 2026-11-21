# Family board

A simple always-on kitchen display for an old iPad mini 2. It shows:

- a large digital clock and the date
- an hour-by-hour forecast for the next 8 hours in Westminster, London, with a short tip (umbrella, coat and so on)
- Louis Shen's ECF rapid rating for the last three months
- a darker theme from 7pm to 7am

The page is plain HTML, CSS and older-style JavaScript, so it runs in Safari on iOS 12.5.7, the last version the iPad mini 2 supports.

## Files

| File | What it is |
| --- | --- |
| `index.html` | The board itself (this is the home page of the site) |
| `ecf.json` | Latest ECF rapid ratings, read by the board |
| `scripts/update_ecf.py` | Fetches the ratings from the ECF website |
| `.github/workflows/ecf.yml` | Runs that script every day at 06:17 UTC |
| `README.md` | This file |

## Settings

Open `index.html` and edit the `CONFIG` section near the top of the script:

```js
var CONFIG = {
  place: 'Westminster',   // name shown with the weather
  latitude: 51.4975,      // location for the forecast
  longitude: -0.1357,
  nightFrom: 19,          // dark theme starts (24-hour clock)
  nightUntil: 7           // dark theme ends
};
```

## Publishing with GitHub Pages

1. Upload all three files to the root of this repository.
2. Go to **Settings → Pages**, choose **Deploy from a branch**, select `main` and `/ (root)`, then **Save**.
3. Open the site address shown on that page. Changes can take a few minutes to appear.

## Setting up the iPad

1. Open the site address in Safari and choose **Share → Add to Home Screen**.
2. **Settings → Display & Brightness → Auto-Lock → Never**, and keep the iPad plugged in.
3. **Settings → General → Accessibility → Guided Access**: turn it on, set a passcode, and set its Display Auto-Lock to Never.
4. Open the board from the Home Screen, triple-click the Home button and tap **Start**.

To leave the board, triple-click the Home button and enter the Guided Access passcode.

## How it keeps itself fresh

- The weather updates every 15 minutes, and retries every 5 minutes if the connection drops.
- The chess rating is re-read every 6 hours; GitHub refreshes `ecf.json` from the ECF website once a day.
- The page reloads itself at 3am each day.

## Privacy

On GitHub's free plan this repository is public, so anyone can read these files. Don't add names, addresses or private calendar links.

## Credits

Weather data by [Open-Meteo.com](https://open-meteo.com/), licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).
Chess ratings from the [English Chess Federation](https://rating.englishchess.org.uk/).
Font: [Fredoka](https://fonts.google.com/specimen/Fredoka) from Google Fonts.
