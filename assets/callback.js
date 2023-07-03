window.dash_clientside = Object.assign({}, window.dash_clientside, {
    clientside: {
        save_and_redirect: function(nclick) {
            //Make a post request to the server
            var xhr = new XMLHttpRequest();
            xhr.open("POST", "https://www.demarches-simplifiees.fr/api/public/v1/demarches/77818/dossiers");
            xhr.setRequestHeader('Content-Type', 'application/json');

            //Set body of the request
            var body = {
                "champ_Q2hhbXAtMzQyNDI1NA==" : "ceci"
            };
            xhr.send(JSON.stringify(body));
            
            //get the response
            xhr.onload = function() {
                if (xhr.status != 200) { // analyze HTTP status of the response
                    alert(`Error ${xhr.status}: ${xhr.statusText}`); // e.g. 404: Not Found
                } else { // show the result
                    alert(`Done, got ${xhr.response.length} bytes`);
                    console.log(xhr.response);
                }
            };
            return "Vous allez être redirigé"
        }
    }
});