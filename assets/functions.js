function str_feature(feature){
    date = new Date(feature.properties.creation_date);
    return `Vol id : ${feature.properties.id} \n Date : ${date.toLocaleString()}`
}

window.carto = Object.assign({}, window.carto, {  
    rendering: {  
        draw_drop_zone: function (feature, latlng)
        {
            const flag = L.icon({iconUrl: `https://img.icons8.com/stickers/50/region-code.png`, iconSize: [50, 50]});
            return L.marker(latlng, {icon: flag});
        },
        flight_style: function(feature, context){

            last_color = '#99ff99';
            old_color = '#9999FF';

         

            last_flight_style =  {
                color: last_color,
                weight: 5,
                fillOpacity: 0.8,
                opacity:1,
                zIndex: 1
            }


            if (context.props.hideout == undefined){
                return last_flight_style;
            }
            const {selected, show_templates} = context.props.hideout;

            old_flight_opacity = 0.5;
            if (show_templates != undefined && !show_templates){
                old_flight_opacity = 0.0;
            }
            old_flight_style = {
                color: old_color,
                weight: 4,
                opacity: old_flight_opacity,
                fillOpacity: 0.5,
                zIndex: 0,
            }

            style = (feature, context) => {
                if (feature.properties.id == selected){
                    return last_flight_style;
                }else return old_flight_style;
            } ;
            
            const map = context.myRef.current.leafletElement._map;
            
            if (selected == undefined){
                return old_flight_style;
            }

            return style(feature, context);


        },
        flight_init: function(feature, layer, context){
            if (context.props.hideout == undefined){
                return;
            }


            const {selected} = context.props.hideout;

            const map = context.myRef.current.leafletElement._map;

            if (selected == undefined){
                return;
            }
      

        },  
        filter_by_month: function(feature, context){
            const {minMonth , maxMonth} = context.props.hideout;
            month = feature.properties.mois
            //convert month to int
            month = parseInt(month);
            
            is_inside = month >= minMonth && month <= maxMonth;
            
            
            return is_inside;
        }

    },

});

window.dash_clientside = Object.assign({}, window.dash_clientside, {
    system: {
        alert_dialog: function(data){
            if(data['type'] == "error")
                alert(data['message']);
            return data['message'];
        }
    }
});