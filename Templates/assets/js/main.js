const $ = document.querySelector.bind(document);
const $$ = document.querySelectorAll.bind(document);
const waypoints = [];
const markers = [];
let alt_wp = [];
const labels = "1234567890";
const wp = $('#display-wp');
const waypointRef = firebase.database().ref('/location/waypoints'); 
let altitude = [0];
let map;
let flightPath;
let currentHomeMarker;
function initMap() {
    map = new google.maps.Map($("#map"), {
        zoom: 18,
        center: { lat: 10.0122436, lng: 105.7500644 },
        fullscreenControl: false,
        mapTypeId: "satellite",
        mapTypeControlOptions: {
            style: google.maps.MapTypeControlStyle.HORIZONTAL_BAR, 
            position: google.maps.ControlPosition.TOP_RIGHT 
        }
    });
    const ref = firebase.database().ref('/location/Home');
    ref.on('value', snapshot => {
        const position = snapshot.val();
        if (currentHomeMarker) {
            currentHomeMarker.setMap(null);
        }
        const Home = new google.maps.Marker({
            position: position,
            label: "H",
            map: map,
        });
        currentHomeMarker = Home;
        $('#home-position').value = position.lat + "," + position.lng;
        waypoints[0] = position;
        markers[0] = Home;
    });
    
    flightPath = new google.maps.Polyline({
        path: waypoints,
        geodesic: true,
        strokeColor: "green",
        strokeOpacity: 1.0,
        strokeWeight: 3,
        // editable: true, 
        map: map
    });
    $('#edit').addEventListener("click", () => {
        app.handleEdit();
        map.addListener("click", app.addWaypoint);
        alt_wp = [];
        app.removeWaypointsToFirebase();
    });
    $('#save').addEventListener("click", () => {
        google.maps.event.clearListeners(map, 'click');
        app.pushWaypointsToFirebase();
    });
}

const app = {
    params: [
        {
            "node_name": "#speed",
            "path": "/parameters/speed",
            "measure": "m/s"
        },
        {
            "node_name": "#mode",
            "path": "/parameters/mode",
            "measure": ""
        },
        {
            "node_name": "#altitude",
            "path": "/parameters/altitude",
            "measure": "meters"
        },
        {
            "node_name": "#battery",
            "path": "/parameters/battery",
            "measure": "%"
        },
        {
            "node_name": "#heading",
            "path": "/parameters/target/compass",
            "measure": " deg"
        },
    ],

    setTabActive() {
        const tabs = $$('.tab-item')
        const contents = $$('.tabs-content')
        var height = $('.tracking').offsetHeight + 40;
        tabs.forEach((tab, index) => {
            tab.addEventListener('click', () => {
                $('.tab-item.active').classList.remove('active');
                tabs[index].classList.toggle('active');
                contents[index].classList.remove('hidden');
                if (index == 0)
                    $('.mission').classList.add('hidden');
                else {
                    $('.tracking').classList.add('hidden');
                    $('.mission').style.height = height + 'px';
                }
            });
        });
    },

    getParameterToFireBase(params) {
        params.forEach(param => {
            const ref = firebase.database().ref(param.path);
            ref.on('value', snapshot => {
                const value = snapshot.val();
                $(param.node_name).innerHTML = value + param.measure;
            });
        });
    },

    updateTarget() {
        let targetMarker;
        const ref = firebase.database().ref('/parameters/target');
        ref.on('value', snapshot => {
            const position = snapshot.val();
            
            if (targetMarker) {
                targetMarker.setMap(null);
            }
            const targetIcon = {
                path: google.maps.SymbolPath.FORWARD_CLOSED_ARROW,
                fillColor: "#2d92f0",
                fillOpacity: 1,
                strokeWeight: 0,
                rotation: position.compass,
                scale: 6,
                anchor: new google.maps.Point(0, 2.6)
            };
            targetMarker = new google.maps.Marker({
                position: position,
                map: map,
                icon: targetIcon
            });
            $('#target').innerHTML = position.lat + ',\n' + position.lng;
        });
    },

    handleSearch() {
        const searchInput = $('#searchInput');
        searchInput.addEventListener("keypress", function (e) {
            if (e.key === "Enter") {
                const [lat, lng] = searchInput.value.split(',').map(coord => parseFloat(coord.trim()));
                console.log(lat, lng);
                searchInput.value = "";
            }
        });
    },

    removeWaypoints(tag, index) {
        tag.addEventListener('click', (e) => {
            if (e.target.closest(".icon")) {
                wp.removeChild(tag);
                waypoints.splice(index, 1);
                markers[index].setMap(null);
                markers.splice(index, 1);
                flightPath.setPath(waypoints);
                this.totalDistance();
            }
        })
    },

    renderWaypoint(marker) {
        const waypoint = document.createElement("div");
        const latLngValue = marker.getPosition().toString().replace(/[()]/g, '');
        const waypointHTML = `<div class="form-input">
            <div class="title position-relative">
                <span class="form-label">Waypoint ${marker.label}</span>
                <i class="icon bi bi-x-circle-fill position-absolute top-0  end-0  me-1"></i>
            </div>
            <div class="input mt-1 d-flex" id="input-position">
                <span class="input-name">Position</span>
                <input class="ms-3 me-3" id="waypoint${marker.label}-position" type="text" placeholder="lat,lng" value="${latLngValue}" readonly>
            </div>
            <div class="input mt-1 d-flex" id="input-altitude">
                <span class="input-name">Altitude</span>
                <input class="ms-3 me-5" id="waypoint-alt" type="number" placeholder="alt" value="10" readonly>
                <span class="measure me-5">Meters</span>
            </div>
        </div>`;
        waypoint.innerHTML = waypointHTML;
        wp.appendChild(waypoint);
        markers.push(marker);
        this.removeWaypoints(waypoint, marker.label);
        this.handleEdit();
    },

    totalDistance() {
        let totalDistance = 0;
        for (let i = 0; i < waypoints.length - 1; i++) {
            const distance = google.maps.geometry.spherical.computeDistanceBetween(waypoints[i], waypoints[i + 1]);
            totalDistance += distance;
        }
        $('.distance-value').innerHTML = totalDistance.toFixed(2) + ' m';
    },

    addWaypoint(event) {
       
        const waypoint = {
            lat: event.latLng.lat(),
            lng: event.latLng.lng()
        };
        waypoints.push(waypoint);
        flightPath.setPath(waypoints);
        const labelIndex = waypoints.length - 1;
        
        const marker = new google.maps.Marker({
            position: event.latLng,
            label: `${labelIndex}`,
            map: map,
            // draggable: true, 
        });
        app.totalDistance();
        app.renderWaypoint(marker);
        // google.maps.event.addListener(marker, 'dragend', app.updateWaypoint.bind(this, marker, waypoints.indexOf(event.latLng)));
    },

    // updateWaypoint(marker, index) {
    //     waypoints[index] = marker.getPosition();
    //     flightPath.setPath(waypoints);
    //     app.totalDistance();
    // },
    pushWaypointsToFirebase() {
        const altHomeref = firebase.database().ref('/location/Home/altitude');
        const wpToUpload = {};
        alt_wp.push($("#home-alt").value);
        $$("#waypoint-alt").forEach((alt) => {
            alt_wp.push(alt.value);
        });
        waypoints.forEach((waypoint, index) => {
            if (index === 0) {
                altHomeref.set(parseInt(alt_wp[index], 10));
            }
            else {
                wpToUpload[`waypoint${index}`] = {
                    lat: waypoint.lat,
                    lng: waypoint.lng,
                    altitude: parseInt(alt_wp[index], 10)
                };
            }
        });

        waypointRef.set(wpToUpload)
            .then(() => {
                console.log('Send Data Succesed');
            })
            .catch((error) => {
                console.error(error);
            });
    },
    removeWaypointsToFirebase() {
        waypointRef.remove()
            .then(() => {
                console.log('Data Deleted');
            })
            .catch((error) => {
                console.error(error);
            });
    },

    handleEdit() {
        const inputTags = $$('.form-input input');
        inputTags.forEach(input => {
            input.style.border = '1px solid #fff';
            input.removeAttribute('readonly');
        });
        this.handleSave(inputTags);
    },

    handleSave(inputTags) {
        $('#save').addEventListener("click", () => {
            inputTags.forEach(input => {
                input.style.border = 'none';
                input.setAttribute('readonly', 'true');
            });
        });
    },
    handleIconbar() {
        const icons = $$(".icons img");
        const cornerImage = $(".corner-image");
        const invertFilter = "invert(88%) sepia(30%) saturate(1211%) hue-rotate(78deg) brightness(96%)";
        const invertFilterAlt = "invert(93%) sepia(100%) saturate(26%) hue-rotate(30deg) brightness(106%) contrast(107%)";
        const popupBox = $(".popup_box");
        const noBtn = $(".btn1");
        const yesBtn = $(".btn2");
        const txt = $(".txt");

        const handleIconClick = function (id) {
            switch (id) {
                case "view":
                    const icon = this;
                    icon.style.filter = icon.style.filter === invertFilter ? invertFilterAlt : invertFilter;
                    cornerImage.classList.toggle("hidden");
                    break;
                case "land":
                    lockIcons();
                    showPopupBox(this, invertFilter, invertFilterAlt, id, "The UAV will LAND immediately!");
                    break;
                case "flight":
                    lockIcons();
                    showPopupBox(this, invertFilter, invertFilterAlt, id, "The UAV will TAKEOFF immediately!");
                    break;
                case "home":
                    lockIcons();
                    showPopupBox(this, invertFilter, invertFilter, id, "The UAV will RETURN HOME immediately!");
                    break;
                default:
                    break;
            }
        };

        icons.forEach(icon => {
            icon.addEventListener("click", handleIconClick.bind(icon, icon.parentNode.id));
        });

        const updateFilter = function (element, filter) {
            element.style.filter = filter;
        };

        const updateState = function (snapshot, element, _filter) {
            const state = snapshot.val();
            updateFilter(element, state ? invertFilter : invertFilterAlt);
        };

        const lockIcons = function () {
            icons.forEach(icon => {
                icon.style.pointerEvents = "none";
            });
        };

        const unlockIcons = function () {
            icons.forEach(icon => {
                icon.style.pointerEvents = "auto";
            });
        };

        const handleStateChange = function (snapshot) {
            const state = snapshot.val();
            if (state === false) {
                firebase.database().ref('/status/RTL').set(false);
                firebase.database().ref('/status/enable').set(false);
                icons.forEach(icon => {
                    updateFilter(icon, invertFilterAlt);
                });
                lockIcons();
                cornerImage.classList.add("hidden");
            } else {
                unlockIcons();
            }
        };

        const showPopupBox = function (element, filter, altFilter, id, text) {
            txt.textContent = text
            popupBox.classList.remove("hidden");
            yesBtn.addEventListener("click", () => {
                element.style.filter = filter;
                if (id == "land") {
                    $("#home img").style.filter = altFilter;
                    $("#flight img").style.filter = altFilter;
                    firebase.database().ref('/status/RTL').set(false);
                    firebase.database().ref('/status/enable').set(false);
                } else if (id == "flight") {
                    $("#land img").style.filter = altFilter;
                    firebase.database().ref('/status/RTL').set(false);
                    firebase.database().ref('/status/enable').set(true);
                } else if (id == "home") {
                    $("#flight img").style.filter = filter;
                    firebase.database().ref('/status/enable').set(true);
                    firebase.database().ref('/status/RTL').set(true);
                }
                popupBox.classList.add("hidden");
                unlockIcons();
            });
            noBtn.addEventListener("click", () => {
                popupBox.classList.add("hidden");
                unlockIcons();
            });
        };

        firebase.database().ref('/status/state').on('value', function (snapshot) {
            updateState(snapshot, $("#state img"));
            handleStateChange(snapshot);
        });

        firebase.database().ref('/status/RTL').on('value', function (snapshot) {
            updateState(snapshot, $("#home img"), invertFilterAlt);
        });

        firebase.database().ref('/status/enable').on('value', function (snapshot) {
            const enable = snapshot.val();
            updateFilter($("#flight img"), enable ? invertFilter : invertFilterAlt);
            updateFilter($("#land img"), enable ? invertFilterAlt : invertFilter);
        });
        
        firebase.database().ref('/images').on('value', function (snapshot) {
            const url = snapshot.val();
            cornerImage.style.backgroundImage = `url(${url})`;
        });
    },
    init() {
        window.initMap = initMap;
        this.getParameterToFireBase(this.params);
        this.updateTarget();
        this.setTabActive();
        this.handleSearch();
        this.handleIconbar();
    }
};
app.init();
