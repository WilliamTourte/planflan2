function initMap() {
    // Default location (center of the map)
    const defaultLocation = { lat: 51.505, lng: -0.09 }; // London

    // Create a map centered at the default location
    const map = new google.maps.Map(document.getElementById("map"), {
        zoom: 13,
        center: defaultLocation,
    });

    // Try HTML5 Geolocation to get user's location
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(
            (position) => {
                const userLocation = {
                    lat: position.coords.latitude,
                    lng: position.coords.longitude,
                };

                // Center the map to user's location
                map.setCenter(userLocation);

                // Place a marker at user's location
                new google.maps.Marker({
                    position: userLocation,
                    map: map,
                    title: "You are here!",
                });
            },
            () => {
                // Handle location access denied
                console.error("Geolocation permission denied");
            }
        );
    } else {
        console.error("Browser doesn't support Geolocation");
    }
}
