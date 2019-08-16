var map = L.map('map');

L.tileLayer('http://{s}.tile.osm.org/{z}/{x}/{y}.png', {
	attribution: '&copy; <a href="http://osm.org/copyright">OpenStreetMap</a> contributors'
}).addTo(map);

var routingControl = L.Routing.control({
	waypoints: [
		L.latLng(27.71, 85.32),
		L.latLng(27.69, 85.30)
	],              	 	
	geocoder: L.Control.Geocoder.nominatim(),
	router: L.Routing.graphHopper('2d58e52c-f0d0-4063-83ed-65c8c748d953'),
	routeWhileDragging: false
}).addTo(map);

var router = routingControl.getRouter();
router.on('response',function(e){
  console.log('This request consumed ' + e.credits + ' credit(s)');
  console.log('You have ' + e.remaining + ' left');
});
