let piechartType = "nationwide";
let latestAlert = null;
let latestRegionAlert = null;
const nationwideAlertsElem = document.getElementById("nationwide");
const regionAlertsElem = document.getElementById("regionwide");
const alertType = {
	high: "alert-danger",
	medium: "alert-p2",
	low: "alert-warning",
	"non-priority": "alert-dark",
};
const serviceColors = {
	Brandweer: "186, 78, 0",
	Politie: "54, 162, 235",
	Ambulance: "2, 194, 2",
	Other: "128, 128, 128",
};
const priorities = ["high", "medium", "low", "non-priority"];
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
	alertItem.classList.add(
		"flex",
		"flex-col",
		"alert",
		alertType[alert["priority"]]
	);
	let alertTime = document.createElement("b");
	alertTime.innerText =
		alert["created_at"].substring(0, 10) +
		" " +
		alert["created_at"].substring(26, 31) +
		" " +
		alert["created_at"].substring(11, 19);
	alertItem.appendChild(alertTime);
	let alertText = document.createElement("div");
	alertText.innerText = alert["description"];
	alertItem.appendChild(alertText);

	const badge = document.createElement("div");
	badge.innerText = alert["service"];
	badge.classList.add("badge");
	badge.style.backgroundColor = `rgb(${serviceColors[alert["service"]]})`;
	if (!!serviceColors[alert["service"]])
		badge.style.backgroundColor = serviceColors["Other"];
	alertItem.appendChild(badge);
	nationwideAlertsElem.insertBefore(alertItem, latestAlert);
	latestAlert = alertItem;
});

socket.on("region", (alert) => {
	const alertItem = document.createElement("div");
	alertItem.classList.add(
		"flex",
		"flex-col",
		"alert",
		alertType[alert["priority"]]
	);
	let alertTime = document.createElement("b");
	alertTime.innerText =
		alert["created_at"].substring(0, 10) +
		" " +
		alert["created_at"].substring(26, 31) +
		" " +
		alert["created_at"].substring(11, 19);
	alertItem.appendChild(alertTime);
	let alertText = document.createElement("div");
	alertText.innerText = alert["description"];
	alertItem.appendChild(alertText);

	const badge = document.createElement("div");
	badge.innerText = alert["service"];
	badge.classList.add("badge");
	badge.style.backgroundColor = `rgb(${serviceColors[alert["service"]]})`;
	if (!!serviceColors[alert["service"]])
		badge.style.backgroundColor = serviceColors["Other"];
	alertItem.appendChild(badge);
	regionAlertsElem.insertBefore(alertItem, latestRegionAlert);
	latestRegionAlert = alertItem;
});

socket.on("filtered_region", (alertList) => {
	alertList = Array.from(alertList);
	regionAlertsElem.textContent = "";
	latestRegionAlert = null;
	alertList.forEach((alert) => {
		const alertItem = document.createElement("div");
		alertItem.classList.add(
			"flex",
			"flex-col",
			"alert",
			alertType[alert["priority"]]
		);
		let alertTime = document.createElement("b");
		alertTime.innerText =
			alert["created_at"].substring(0, 10) +
			" " +
			alert["created_at"].substring(26, 31) +
			" " +
			alert["created_at"].substring(11, 19);
		alertItem.appendChild(alertTime);
		let alertText = document.createElement("div");
		alertText.innerText = alert["description"];
		alertItem.appendChild(alertText);

		const badge = document.createElement("div");
		badge.innerText = alert["service"];
		badge.classList.add("badge");
		badge.style.backgroundColor = `rgb(${serviceColors[alert["service"]]})`;
		if (!!serviceColors[alert["service"]])
			badge.style.backgroundColor = serviceColors["Other"];
		alertItem.appendChild(badge);
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
