document
  .getElementById("urlForm")
  .addEventListener("submit", async function (e) {
    e.preventDefault();

    const url = document.getElementById("urlInput").value;

    const response = await fetch("/predict", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ url: url }),
    });

    const data = await response.json();

    document.getElementById("verdict").textContent = data.verdict;
    document.getElementById("probability").textContent =
      data.probability.toFixed(2);

    const reasonsList = document.getElementById("reasonsList");
    reasonsList.innerHTML = "";
    data.reasons.forEach((reason) => {
      const li = document.createElement("li");
      li.textContent = reason;
      reasonsList.appendChild(li);
    });

    document.getElementById("result").classList.remove("hidden");
  });
