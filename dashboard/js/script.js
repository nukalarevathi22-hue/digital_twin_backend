async function loadSimulationData() {
  const response = await fetch("/api/patient/sample_patient/latest-results");
  const data = await response.json();

  const pressures = data.nodes.map(node => node.pressure);
  const labels = data.nodes.map(node => "Node " + node.id);

  const ctx = document.getElementById("pressureChart").getContext("2d");
  new Chart(ctx, {
    type: "bar",
    data: {
      labels,
      datasets: [{
        label: "Node Pressure",
        data: pressures,
        borderWidth: 1
      }]
    },
    options: { responsive: true }
  });
}

loadSimulationData();
