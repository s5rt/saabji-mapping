<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no">
    <title>Tree Survey</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }

        body {
            font-family: 'Courier New', monospace;
            background: #f5f5f0;
            color: #111;
            padding: 12px;
            font-size: 15px;
        }

        h2 {
            text-align: center;
            font-size: 17px;
            letter-spacing: 2px;
            text-transform: uppercase;
            margin-bottom: 12px;
            padding-bottom: 8px;
            border-bottom: 2px solid #111;
        }

        /* GPS BLOCK */
        #gpsBlock {
            background: #111;
            color: #f5f5f0;
            padding: 5px 8px 4px;
            margin-bottom: 10px;
            border-radius: 4px;
        }

        /* row 1: coords + button */
        #gpsRow1 {
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 6px;
        }

        #gpsCoords {
            font-size: 11px;
            line-height: 1.4;
            white-space: nowrap;
            flex: 1;
        }

        #btnForceGPS {
            padding: 3px 7px;
            background: transparent;
            border: 1px solid #555;
            color: #ccc;
            font-family: 'Courier New', monospace;
            font-size: 11px;
            cursor: pointer;
            border-radius: 3px;
            white-space: nowrap;
            flex-shrink: 0;
        }
        #btnForceGPS:active { background: #333; }

        /* row 2: status + changed badge + bar */
        #gpsRow2 {
            display: flex;
            align-items: center;
            gap: 6px;
            margin-top: 3px;
        }

        #gpsStatusLine {
            font-size: 10px;
            color: #777;
            white-space: nowrap;
        }

        #locationChanged {
            font-size: 10px;
            font-weight: bold;
            letter-spacing: 0.5px;
            text-transform: uppercase;
            white-space: nowrap;
        }
        .loc-changed  { color: #7fff7f; }
        .loc-same     { color: #666; }
        .loc-first    { color: #ffdd77; }

        /* COUNTDOWN BAR */
        #countdownWrap {
            display: flex;
            align-items: center;
            gap: 4px;
            flex: 1;
        }

        #countdownBar {
            flex: 1;
            height: 3px;
            background: #333;
            border-radius: 2px;
            overflow: hidden;
        }

        #countdownFill {
            height: 100%;
            background: #7fff7f;
            width: 100%;
            transition: width 1s linear;
        }

        #countdownLabel {
            font-size: 10px;
            color: #666;
            white-space: nowrap;
            min-width: 24px;
            text-align: right;
        }

        /* FORM */
        label {
            display: block;
            margin-top: 12px;
            margin-bottom: 3px;
            font-size: 11px;
            letter-spacing: 1.5px;
            text-transform: uppercase;
            font-weight: bold;
            color: #444;
        }

        input, select {
            width: 100%;
            padding: 11px 10px;
            border: 1px solid #bbb;
            border-radius: 4px;
            font-size: 16px;
            font-family: 'Courier New', monospace;
            background: #fff;
            color: #111;
            -webkit-appearance: none;
        }

        input:focus, select:focus {
            outline: none;
            border-color: #111;
        }

        button[type="submit"] {
            width: 100%;
            margin-top: 18px;
            padding: 15px;
            border: none;
            background: #111;
            color: #f5f5f0;
            font-size: 15px;
            font-family: 'Courier New', monospace;
            letter-spacing: 2px;
            text-transform: uppercase;
            cursor: pointer;
            border-radius: 4px;
        }
        button[type="submit"]:active { background: #333; }

        #status {
            margin-top: 12px;
            text-align: center;
            font-size: 13px;
            font-weight: bold;
            min-height: 20px;
            letter-spacing: 1px;
        }
        .status-ok  { color: #2a7a2a; }
        .status-err { color: #cc2222; }
    </style>
</head>
<body>

<h2>Tree Inventory</h2>

<div id="gpsBlock">
    <div id="gpsRow1">
        <div id="gpsCoords">Acquiring GPS…</div>
        <button id="btnForceGPS">⟳ GPS</button>
    </div>
    <div id="gpsRow2">
        <div id="gpsStatusLine">—</div>
        <div id="locationChanged" class="loc-first">PENDING</div>
        <div id="countdownWrap">
            <div id="countdownBar"><div id="countdownFill"></div></div>
            <div id="countdownLabel">30s</div>
        </div>
    </div>
</div>

<form id="treeForm">
    <label>Tree ID *</label>
    <input type="text" id="tree_id" required autocomplete="off">

    <label>Common Name</label>
    <input type="text" id="common_name" autocomplete="off">

    <label>Condition</label>
    <select id="condition">
        <option value="good">Good</option>
        <option value="moderate">Moderate</option>
        <option value="poor">Poor</option>
        <option value="dead">Dead</option>
    </select>

    <label>Growth Stage</label>
    <select id="growth_stage">
        <option value="young">Young</option>
        <option value="mature">Mature</option>
        <option value="old">Old</option>
    </select>

    <label>Height (m)</label>
    <select id="height_m"></select>

    <label>Width (m)</label>
    <select id="width_m"></select>

    <label>Remarks</label>
    <input type="text" id="remarks" autocomplete="off">

    <button type="submit">Save Record</button>
</form>

<div id="status"></div>

<script>
(function () {
    /* ── dropdowns ─────────────────────────────────────── */
    const heightSelect = document.getElementById('height_m');
    for (let i = 5; i <= 25.0001; i += 0.5) {
        const o = document.createElement('option');
        o.value = o.textContent = i.toFixed(1);
        heightSelect.appendChild(o);
    }
    heightSelect.value = '20.0';

    const widthSelect = document.getElementById('width_m');
    for (let i = 0.5; i <= 10.0001; i += 0.1) {
        const o = document.createElement('option');
        o.value = o.textContent = i.toFixed(1);
        widthSelect.appendChild(o);
    }
    widthSelect.value = '5.0';

    /* ── GPS state ─────────────────────────────────────── */
    const REFRESH_SEC   = 30;
    const CACHE_KEY_LAT = 'gps_last_lat';
    const CACHE_KEY_LON = 'gps_last_lon';

    let currentLat = '';
    let currentLon = '';
    let countdownTimer  = null;
    let countdownSeconds = REFRESH_SEC;

    const elCoords   = document.getElementById('gpsCoords');
    const elStatus   = document.getElementById('gpsStatusLine');
    const elChanged  = document.getElementById('locationChanged');
    const elFill     = document.getElementById('countdownFill');
    const elLabel    = document.getElementById('countdownLabel');

    function setStatusLine(msg) { elStatus.textContent = msg; }

    function compareWithCache(lat, lon) {
        const prevLat = localStorage.getItem(CACHE_KEY_LAT);
        const prevLon = localStorage.getItem(CACHE_KEY_LON);

        if (prevLat === null || prevLon === null) {
            elChanged.textContent  = 'FIRST FIX';
            elChanged.className    = 'loc-first';
        } else {
            const dLat = Math.abs(parseFloat(prevLat) - lat);
            const dLon = Math.abs(parseFloat(prevLon) - lon);
            const moved = dLat > 0.000010 || dLon > 0.000010;
            if (moved) {
                elChanged.textContent = '▲ MOVED';
                elChanged.className   = 'loc-changed';
            } else {
                elChanged.textContent = '● SAME';
                elChanged.className   = 'loc-same';
            }
        }

        localStorage.setItem(CACHE_KEY_LAT, lat);
        localStorage.setItem(CACHE_KEY_LON, lon);
    }

    function onGPSSuccess(position) {
        currentLat = position.coords.latitude;
        currentLon = position.coords.longitude;
        const acc  = position.coords.accuracy ? position.coords.accuracy.toFixed(0) + ' m acc' : '';
        elCoords.innerHTML =
            currentLat.toFixed(6) + ', ' + currentLon.toFixed(6) +
            (acc ? ' <span style="color:#555">±' + acc + '</span>' : '');
        setStatusLine('Updated: ' + new Date().toLocaleTimeString());
        compareWithCache(currentLat, currentLon);
    }

    function onGPSError(err) {
        setStatusLine('GPS error: ' + err.message);
        elChanged.textContent = 'NO FIX';
        elChanged.className   = 'loc-first';
    }

    const GEO_OPTS = { enableHighAccuracy: true, timeout: 10000, maximumAge: 0 };

    function fetchGPS() {
        if (!navigator.geolocation) {
            elCoords.textContent = 'Geolocation not supported';
            return;
        }
        setStatusLine('Refreshing…');
        navigator.geolocation.getCurrentPosition(onGPSSuccess, onGPSError, GEO_OPTS);
    }

    /* ── countdown bar ─────────────────────────────────── */
    function startCountdown() {
        clearInterval(countdownTimer);
        countdownSeconds = REFRESH_SEC;
        updateBar();
        countdownTimer = setInterval(function () {
            countdownSeconds--;
            if (countdownSeconds <= 0) {
                countdownSeconds = REFRESH_SEC;
                fetchGPS();
            }
            updateBar();
        }, 1000);
    }

    function updateBar() {
        const pct = (countdownSeconds / REFRESH_SEC) * 100;
        elFill.style.width  = pct + '%';
        elLabel.textContent = countdownSeconds + 's';
    }

    /* ── force refresh button ──────────────────────────── */
    document.getElementById('btnForceGPS').addEventListener('click', function () {
        fetchGPS();
        startCountdown();
    });

    /* ── initial load ──────────────────────────────────── */
    fetchGPS();
    startCountdown();

    /* ── form submit ───────────────────────────────────── */
    document.getElementById('treeForm').addEventListener('submit', async function (e) {
        e.preventDefault();
        const statusEl = document.getElementById('status');
        statusEl.textContent = 'Saving…';
        statusEl.className   = '';

        const payload = {
            latitude:     currentLat,
            longitude:    currentLon,
            tree_id:      document.getElementById('tree_id').value.trim(),
            common_name:  document.getElementById('common_name').value.trim(),
            condition:    document.getElementById('condition').value,
            growth_stage: document.getElementById('growth_stage').value,
            height_m:     document.getElementById('height_m').value,
            width_m:      document.getElementById('width_m').value,
            remarks:      document.getElementById('remarks').value.trim()
        };

        try {
            const response = await fetch('save.php', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });
            const result = await response.json();
            if (result.status !== 'success') throw new Error(result.message || 'Save failed');
            statusEl.textContent = '✓ Saved — FID: ' + result.fid;
            statusEl.className   = 'status-ok';

            document.getElementById('treeForm').reset();
            document.getElementById('condition').value    = 'good';
            document.getElementById('growth_stage').value = 'young';
            document.getElementById('height_m').value     = '20.0';
            document.getElementById('width_m').value      = '5.0';
        } catch (err) {
            statusEl.textContent = '✗ ' + err.message;
            statusEl.className   = 'status-err';
        }
    });
})();
</script>
</body>
</html>
