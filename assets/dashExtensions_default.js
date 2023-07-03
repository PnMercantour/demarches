window.dashExtensions = Object.assign({}, window.dashExtensions, {
    default: {
        function0: function(feature, latlng) {
            const flag = L.icon({
                iconUrl: `https://img.icons8.com/ios/50/circled-h.png`,
                iconSize: [50, 50]
            });
            return L.marker(latlng, {
                icon: flag
            });
        }
    }
});