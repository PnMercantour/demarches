function str_feature(feature){
    date = new Date(feature.properties.creation_date);
    return `Vol id : ${feature.properties.id} \n Date : ${date.toLocaleString()}`
}

window.carto = Object.assign({}, window.carto, {  
    rendering: {  
        draw_drop_zone: function (feature, latlng)
        {
            const flag = L.icon({iconUrl: `https://img.icons8.com/ios/50/circled-h.png`, iconSize: [50, 50]});
            return L.marker(latlng, {icon: flag});
        },
        draw_arrow: function(feature, layer, context){
            date = new Date(feature.properties.creation_date);
            last_color = '#99ff99';
            old_color = '#9999FF';

            last_flight_style =  {
                color: last_color,
                weight: 5,
                fillOpacity: 0.8,
                opacity: 0.8
            }
            old_flight_style = {
                    color: old_color,
                    weight: 4,
                    opacity: 0.5,
                    fillOpacity: 0.5,
            }
            hover_style = {
                color: '#ff9999',
                fillOpacity: 0.5,
                weight: 5,
                opacity: 1
            }

            is_last = (feature, context) => {
                get_oldest_feature = context.myRef.current.props.data.features[0];
                return feature.properties.id == get_oldest_feature.properties.id;
            }


            color = (feature, context) => {
                if (is_last(feature, context)){
                    return last_color;
                }else return old_color;
            }
            opacity = (feature, context) => { 
                if (is_last(feature, context)){
                    return 0.8;
                }else return 0.5;
            }
            style = (feature, context) => {
                if (is_last(feature, context)){
                    return last_flight_style;
                }else return old_flight_style;
            } ;
            
            const map = context.myRef.current.leafletElement._map;
            
        

            //bind popup
            layer.bindPopup(str_feature(feature));
            layer.bindTooltip(date.toLocaleString());
            

            //hover style
            layer.on('mouseover', function (e) {
                layer.setStyle(hover_style);
            });
            layer.on('mouseout', function (e) {
                layer.setStyle(style(feature, context));
            });


            //normal style
            layer.setStyle(style(feature, context));



            L.polylineDecorator(layer, {
                  patterns: [
                      {symbol: L.Symbol.arrowHead({pixelSize: 15, pathOptions: style(feature, context)}),
                        repeat: 100
                    }
                  ]
            }).addTo(map);
        },
    }  
});