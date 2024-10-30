let piechartType = "nationwide";
let latestAlert = null;
let latestRegionAlert = null;
const nationwideAlertsElem = document.getElementById("nationwide");
const regionAlertsElem = document.getElementById("regionwide");
const alertType = {
	p1: "alert-danger",
	p2: "alert-p2",
	p3: "alert-warning",
	"non-priority": "alert-dark",
};
const priorities = ["p1", "p2", "p3", "non-priority"];
const selectedPriorities = new Set(priorities);

var socket = io();

socket.on("connect", () => {
	socket.emit("piechart-type", "nationwide");
	socket.emit("filter", [
		regionSelectElem.value,
		Array.from(selectedPriorities),
	]);
});

socket.on("nationwide", (alert) => {
	const alertItem = document.createElement("div");
	alertItem.classList.add("alert", alertType[alert["priority"]]);
	alertItem.innerText = alert["description"];
	nationwideAlertsElem.insertBefore(alertItem, latestAlert);
	latestAlert = alertItem;
});

socket.on("region", (alert) => {
	const alertItem = document.createElement("div");
	alertItem.classList.add("alert", alertType[alert["priority"]]);
	alertItem.innerText = alert["description"];
	regionAlertsElem.insertBefore(alertItem, latestRegionAlert);
	latestRegionAlert = alertItem;
});

socket.on("filtered_region", (alertList) => {
	alertList = Array.from(alertList);
	regionAlertsElem.textContent = "";
	latestRegionAlert = null;
	alertList.forEach((alert) => {
		const alertItem = document.createElement("div");
		alertItem.classList.add("alert", alertType[alert["priority"]]);
		alertItem.innerText = alert["description"];
		regionAlertsElem.insertBefore(alertItem, latestRegionAlert);
		latestRegionAlert = alertItem;
	});
});

priorities.forEach(function (priority) {
	document.getElementById(priority).addEventListener("click", function (e) {
		e.stopPropagation();
	});

	document.getElementById(priority).addEventListener("click", function () {
		this.checked
			? selectedPriorities.add(priority)
			: selectedPriorities.delete(priority);
	});

	document
		.getElementById(`filter-${priority}`)
		.addEventListener("click", function () {
			let priorityElem = document.getElementById(priority);
			!priorityElem.checked
				? selectedPriorities.add(priority)
				: selectedPriorities.delete(priority);

			priorityElem.checked = !document.getElementById(priority).checked;
		});
});

let piechartRegionBtn = document.getElementById("piechart-region");
let piechartNationwideBtn = document.getElementById("piechart-nationwide");

piechartNationwideBtn.addEventListener("click", function () {
	if (piechartType === "nationwide") return;

	piechartType = "nationwide";
	socket.emit("piechart-type", "nationwide");
	piechartRegionBtn.classList.remove("active");
	piechartNationwideBtn.classList.add("active");
});
piechartRegionBtn.addEventListener("click", function () {
	if (piechartType === "region") return;

	piechartType = "region";
	socket.emit("piechart-type", "region");
	piechartRegionBtn.classList.add("active");
	piechartNationwideBtn.classList.remove("active");
});

let regionSelectElem = document.getElementById("region-select");
regionSelectElem.addEventListener("change", function () {
	socket.emit("filter", [
		regionSelectElem.value,
		Array.from(selectedPriorities),
	]);

	piechartRegionBtn.innerText = regionSelectElem.value;
	piechartRegionBtn.classList.remove("disabled");
});

document.getElementById("apply-filters").addEventListener("click", function () {
	socket.emit("filter", [
		document.getElementById("region-select").value,
		Array.from(selectedPriorities),
	]);
});
