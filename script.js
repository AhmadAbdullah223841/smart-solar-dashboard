async function loadWeather() {

    try {

        const response = await fetch("/api/weather");

        const data = await response.json();

        if (data.error) {
            throw new Error(data.error);
        }


        document.getElementById("temperature").textContent =
            data.temperature;

        document.getElementById("radiation").textContent =
            data.radiation;

        document.getElementById("cloud").textContent =
            data.cloud;

        document.getElementById("humidity").textContent =
            data.humidity;

        // API gives wind speed in km/h
        document.getElementById("wind").textContent =
            data.wind;

        document.getElementById("power").textContent =
            data.estimated_power;


        let status = "";

        if (data.radiation >= 700) {

            status = "🟢 HIGH";

        } else if (data.radiation >= 300) {

            status = "🟡 MEDIUM";

        } else {

            status = "🔴 LOW";

        }


        document.getElementById("status").textContent =
            status;


        document.getElementById("updated").textContent =
            "Last update: " + data.time;


    } catch (error) {

        console.error(error);

        document.getElementById("status").textContent =
            "⚠️ Data unavailable";

    }

}


// প্রথমবার data load
loadWeather();


// প্রতি 60 second পরপর নতুন data
setInterval(loadWeather, 60000);