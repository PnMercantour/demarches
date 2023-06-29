// document.onloadstart = function() {
//     console.log("Settings up map")
var mapsPlaceholder = [];

L.Map.addInitHook(function () {
  mapsPlaceholder.push(this); // Use whatever global scope variable you like.
    let pluginOptions = {
        cropImageByInnerWH: true, // crop blank opacity from image borders
        hidden: false, // hide screen icon
        preventDownload: false, // prevent download on button click
        domtoimageOptions: {}, // see options for dom-to-image
        position: 'topleft', // position of take screen icon
        screenName: 'screen', // string or function
        hideElementsWithSelectors: ['.leaflet-control-container'], // by default hide map controls All els must be child of _map._container
        mimeType: 'image/png', // used if format == image,
        caption: "test", // string or function, added caption to bottom of screen
        captionFontSize: 15,
        captionFont: 'Arial',
        captionColor: 'black',
        captionBgColor: 'white',
        captionOffset: 5,
        // callback for manually edit map if have warn: "May be map size very big on that zoom level, we have error"
        // and screenshot not created
        onPixelDataFail: async function({ node, plugin, error, mapPane, domtoimageOptions }) {
            // Solutions:
            // decrease size of map
            // or decrease zoom level
            // or remove elements with big distanses
            // and after that return image in Promise - plugin._getPixelDataOfNormalMap
            return plugin._getPixelDataOfNormalMap(domtoimageOptions)
        }
        }
        this.simpleMapScreenshoter = L.simpleMapScreenshoter(pluginOptions).addTo(mapsPlaceholder[0])
        let format = 'blob' // 'image' - return base64, 'canvas' - return canvas
        let overridedPluginOptions = {
          mimeType: 'image/jpeg'
        }
      
});
    
console.log("Settings up map")

// }
