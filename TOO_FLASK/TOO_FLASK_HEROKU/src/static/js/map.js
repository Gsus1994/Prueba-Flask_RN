document.addEventListener("DOMContentLoaded", function() {
    // Inicialización del mapa
    var map = L.map('map').setView([40.416775, -3.70379], 6);  // Centrado en España, con un nivel de zoom que muestra todo el país

    L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
        maxZoom: 19,
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
    }).addTo(map);

    // Variables para almacenar elementos dibujados en el mapa
    let markers = [];
    let polylines = [];
    let legend;

    // Función para limpiar el mapa
    function clearMap() {
        markers.forEach(marker => map.removeLayer(marker));
        markers = [];
        
        polylines.forEach(polyline => map.removeLayer(polyline));
        polylines = [];
        
        if (legend) {
            map.removeControl(legend);
            legend = null;
        }
    }

    // Función para dibujar coordenadas en el mapa
    function drawCoordinates(coords, color, firstCoordColor) {
        var formattedCoords = coords.map(coord => {
            return Array.isArray(coord) ? coord : [coord.latitude, coord.longitude];
        });

        var validCoords = formattedCoords.filter(coord => {
            const isValid = coord && typeof coord[0] === 'number' && typeof coord[1] === 'number';
            return isValid;
        });

        if (validCoords.length === 0) {
            return;
        }

        validCoords.forEach((coord, index) => {
            var markerColor = index === 0 ? firstCoordColor : color;
            let marker = L.marker(coord, {
                icon: L.icon({
                    iconUrl: `http://maps.google.com/mapfiles/ms/icons/${markerColor}-dot.png`
                })
            }).addTo(map);
            markers.push(marker);
        });

        if (validCoords.length > 1) {
            let polyline = L.polyline(validCoords, {color: color}).addTo(map);
            polylines.push(polyline);
        }
    }

    // Función para buscar acuerdos
    function searchAgreements() {
        var dni = document.getElementById('dni-input').value;

        // Validar y formatear el DNI para que acepte solo 8 números y una letra en mayúscula
        dni = dni.replace(/[^0-9A-Za-z]/g, ''); // Eliminar cualquier carácter que no sea un número o letra
        
        if (dni.length <= 8) {
            dni = dni.replace(/[^0-9]/g, ''); // Solo permitir números en los primeros 8 caracteres
        } else if (dni.length === 9) {
            dni = dni.slice(0, 8) + dni[8].toUpperCase().replace(/[^A-Za-z]/g, ''); // Permitir solo una letra en la novena posición y convertirla en mayúscula
        } else {
            dni = dni.slice(0, 9); // Limitar el valor a 9 caracteres
        }

        // Establecer el valor formateado en el campo input
        document.getElementById('dni-input').value = dni;

        // Validar el formato del DNI, que debe ser 8 números y 1 letra
        var dniPattern = /^\d{8}[A-Z]$/;
        if (!dni) {
            alert('Por favor, introduzca un DNI');
            return;
        } else if (!dniPattern.test(dni)) {
            alert('Por favor, introduzca un DNI correcto');
            return;
        }

        fetch('/rooms/obtener_acuerdos', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json; charset=utf-8',
                'Authorization': 'Bearer ' + localStorage.getItem('token')
            },
            body: JSON.stringify({ dni: dni })
        })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                alert(data.error);
            } else {
                var agreementsDropdown = document.getElementById('agreements-dropdown');
                agreementsDropdown.innerHTML = '';
        
                data.forEach(agreement => {
                    var option = document.createElement('option');
                    option.value = agreement._id;  
                    option.textContent = `${agreement.nombreUser1} ${agreement.apellidosUser1} y ${agreement.nombreUser2} ${agreement.apellidosUser2} --> ${agreement.fechaCreacionSala}`; 
                    agreementsDropdown.appendChild(option);
                });                
        
                agreementsDropdown.disabled = false;
                document.getElementById('show-itinerary').disabled = false;
            }
        })
        .catch(error => {
            console.error('Error fetching agreements:', error);
            alert('Hubo un error al buscar los acuerdos.');
        });        
    }

    document.getElementById('search-agreements').addEventListener('click', function() {
        searchAgreements();
    });

    document.getElementById('dni-input').addEventListener('keypress', function(event) {
        if (event.key === 'Enter') {
            searchAgreements();
        }
    });

    // Función para mostrar el itinerario
    document.getElementById('show-itinerary').addEventListener('click', function() {
        clearMap();  // Limpiar el mapa antes de dibujar un nuevo itinerario

        var selectedAgreementId = document.getElementById('agreements-dropdown').value;
        var dni = document.getElementById('dni-input').value;

        if (!selectedAgreementId) {
            alert('Por favor, seleccione un acuerdo');
            return;
        }

        // Ocultar el sidebar cuando se muestra el itinerario
        hideSidebar();

        fetch('/rooms/itinerario', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': 'Bearer ' + localStorage.getItem('token')
            },
            body: JSON.stringify({ agreement_id: selectedAgreementId })
        })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                alert(data.error);
            } else {
                var user1Coordinates, user2Coordinates, userColor, accompliceColor, userFirstCoordColor, accompliceFirstCoordColor, name, accompliceName;
                
                if (dni === data.dniUser1) {
                    user1Coordinates = data.CoordenadasUser1;
                    user2Coordinates = data.CoordenadasUser2;
                    userColor = 'blue';  // Azul
                    accompliceColor = 'green';  // Verde
                    userFirstCoordColor = 'red';  // Rojo
                    accompliceFirstCoordColor = 'orange';  // Naranja
                    name = `${data.nombreUser1} ${data.apellidosUser1}`;
                    accompliceName = `${data.nombreUser2} ${data.apellidosUser2}`;
                } else {
                    user1Coordinates = data.CoordenadasUser2;
                    user2Coordinates = data.CoordenadasUser1;
                    userColor = 'green';  // Verde
                    accompliceColor = 'blue';  // Azul
                    userFirstCoordColor = 'orange';  // Naranja
                    accompliceFirstCoordColor = 'red';  // Rojo
                    name = `${data.nombreUser2} ${data.apellidosUser2}`;
                    accompliceName = `${data.nombreUser1} ${data.apellidosUser1}`;
                }

                drawCoordinates(user1Coordinates, userColor, userFirstCoordColor);
                drawCoordinates(user2Coordinates, accompliceColor, accompliceFirstCoordColor);

                var backend_info = `Nombre: ${name}\n DNI: ${dni}\n Color itinerario: ${colorToSpanish(userColor)}\n Color Primera Coordenada: ${colorToSpanish(userFirstCoordColor)}\n\n Acompañante:\n Nombre: ${accompliceName}\n Color itinerario: ${colorToSpanish(accompliceColor)}\n Color Primera Coordenada: ${colorToSpanish(accompliceFirstCoordColor)}`;

                var legend_html = `
                <div style="position: fixed; bottom: 60px; left: 60px; width: 310px; height: 220px; background-color: white; z-index:9999; font-size:14px; border:2px solid grey; border-radius:10px;">
                &nbsp; <b>Información del Usuario</b><br>
                &nbsp; ${backend_info.replace(/\n/g, "<br>&nbsp;")} 
                </div>
                `;

                legend = L.control({position: 'bottomleft'});
                legend.onAdd = function () {
                    var div = L.DomUtil.create('div');
                    div.innerHTML = legend_html;
                    return div;
                };
                legend.addTo(map);
            }
        })
        .catch(error => {
            console.error('Error fetching agreement details:', error);
            alert('Hubo un error al obtener los detalles del acuerdo.');
        });
    });

    // Función para cerrar sesión
    document.getElementById('logout-button').addEventListener('click', function() {
        fetch('/logout', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': 'Bearer ' + localStorage.getItem('token')
            }
        })
        .then(response => {
            if (response.ok) {
                localStorage.clear();
                sessionStorage.clear();
                window.location.href = '/login';
            } else {
                alert('Error al cerrar sesión.');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Hubo un problema al cerrar sesión. Por favor, inténtalo de nuevo.');
        });
    });

    // Función para convertir colores al español
    function colorToSpanish(color) {
        switch(color) {
            case 'blue':return 'azul';
            case 'green':return 'verde';
            case 'red':return 'rojo';
            case 'orange':return 'naranja';
            default:return color;
        }
    }

    // Función para ocultar el sidebar y expandir el mapa
    function hideSidebar() {
        document.getElementById('sidebar').classList.add('hidden');
        document.getElementById('map').classList.add('fullscreen');
        document.getElementById('show-sidebar-btn').classList.add('visible');

        map.invalidateSize();  // Ajustar tamaño del mapa después de ocultar el sidebar
    }

    // Función para restaurar el sidebar
    function showSidebar() {
        document.getElementById('sidebar').classList.remove('hidden');
        document.getElementById('map').classList.remove('fullscreen');
        document.getElementById('show-sidebar-btn').classList.remove('visible');

        map.invalidateSize();  // Ajustar tamaño del mapa después de mostrar el sidebar
    }

    // Añadir el evento al botón de mostrar el sidebar
    document.getElementById('show-sidebar-btn').addEventListener('click', showSidebar);
});