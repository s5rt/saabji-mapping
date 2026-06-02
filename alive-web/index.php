<!DOCTYPE html>
<html lang="en">

<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Tree Survey</title>
    <style>
        * {
            box-sizing: border-box;
            font-family: Arial, sans-serif;
        }

        body {
            margin: 0;
            padding: 12px;
            background: #fff;
            color: #000;
        }

        .container {
            max-width: 600px;
            margin: auto;
        }

        h2 {
            text-align: center;
            margin-bottom: 16px;
        }

        label {
            display: block;
            margin-top: 12px;
            margin-bottom: 4px;
            font-weight: 600;
        }

        input,
        select {
            width: 100%;
            padding: 12px;
            border: 1px solid #000;
            border-radius: 4px;
            font-size: 16px;
        }

        button {
            width: 100%;
            margin-top: 20px;
            padding: 14px;
            border: none;
            background: #000;
            color: #fff;
            font-size: 16px;
            cursor: pointer;
        }

        .gps {
            border: 1px solid #000;
            padding: 8px;
            margin-bottom: 12px;
            font-size: 13px;
        }

        .status {
            margin-top: 12px;
            text-align: center;
            font-weight: bold;
        }
    </style>
</head>

<body>
    <div class="container">
        <h2>Tree Inventory Form</h2>
        <div class="gps" id="gpsStatus">
            Waiting for GPS...
        </div>
        <form id="treeForm">
            <label>Tree ID *</label>
            <input type="text" id="tree_id" required>
            <label>Common Name</label>
            <input type="text" id="common_name">
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
            <input type="text" id="remarks">
            <button type="submit">Save Record</button>
        </form>
        <div class="status" id="status"></div>
    </div>
    <script>
        let latitude = "";
        let longitude = "";
        const heightSelect = document.getElementById("height_m");
        for (let i = 5; i <= 25.0001; i += 0.5) {
            const option = document.createElement("option");
            option.value = i.toFixed(1);
            option.textContent = i.toFixed(1);
            heightSelect.appendChild(option);
        }
        heightSelect.value = "20.0";
        const widthSelect = document.getElementById("width_m");
        for (let i = 0.5; i <= 10.0001; i += 0.1) {
            const option = document.createElement("option");
            option.value = i.toFixed(1);
            option.textContent = i.toFixed(1);
            widthSelect.appendChild(option);
        }
        widthSelect.value = "5.0";
        function getLocation() {
            if (!navigator.geolocation) {
                document.getElementById("gpsStatus").textContent =
                    "Geolocation not supported";
                return;
            }
            navigator.geolocation.getCurrentPosition(
                function (position) {
                    latitude = position.coords.latitude;
                    longitude = position.coords.longitude;
                    document.getElementById("gpsStatus").innerHTML =
                        "Lat: " + latitude.toFixed(6) +
                        "<br>Lon: " + longitude.toFixed(6);
                },
                function (error) {
                    document.getElementById("gpsStatus").textContent =
                        "GPS Error: " + error.message;
                },
                {
                    enableHighAccuracy: true,
                    timeout: 10000,
                    maximumAge: 0
                }
            );
        }
        getLocation();
        document.getElementById("treeForm").addEventListener(
            "submit",
            async function (e) {
                e.preventDefault();
                const status = document.getElementById("status");
                status.textContent = "Saving...";
                const payload = {
                    latitude,
                    longitude,
                    tree_id: document.getElementById("tree_id").value.trim(),
                    common_name: document.getElementById("common_name").value.trim(),
                    condition: document.getElementById("condition").value,
                    growth_stage: document.getElementById("growth_stage").value,
                    height_m: document.getElementById("height_m").value,
                    width_m: document.getElementById("width_m").value,
                    remarks: document.getElementById("remarks").value.trim()
                };
                try {
                    const response = await fetch("save.php", {
                        method: "POST",
                        headers: {
                            "Content-Type": "application/json"
                        },
                        body: JSON.stringify(payload)
                    });
                    const result = await response.json();
                    if (result.status !== "success") {
                        throw new Error(result.message || "Save failed");
                    }
                    status.textContent = "Saved. FID: " + result.fid;
                    document.getElementById("treeForm").reset();
                    document.getElementById("condition").value = "good";
                    document.getElementById("growth_stage").value = "young";
                    document.getElementById("height_m").value = "5.0";
                    document.getElementById("width_m").value = "0.5";
                    getLocation();
                } catch (error) {
                    status.textContent = error.message;
                }
            }
        );
    </script>
</body>

</html>