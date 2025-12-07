// Student Results Page JavaScript
(function () {
	"use strict";

	// Fetch student results from API and render the table
	const form = document.getElementById("student-form");
	const resultsSection = document.getElementById("results-section");
	const tbody = document.getElementById("results-table-body");
	const gpaEl = document.getElementById("gpa-value");
	const errorMessage = document.getElementById("error-message");

	form.addEventListener("submit", async function (e) {
		e.preventDefault();
		const matric = document.getElementById("matricNo").value.trim();
		const password = document.getElementById("password").value;
		if (!matric || !password) return;

		// Clear previous errors
		errorMessage.style.display = "none";
		errorMessage.textContent = "";

		try {
			const params = new URLSearchParams();
			params.append("matricNo", matric);
			params.append("password", password);

			const resp = await fetch("/cgi-bin/student_results.py", {
				method: "POST",
				credentials: "same-origin",
				body: params,
			});

			const data = await resp.json();

			if (!resp.ok) {
				const errorMsg = data.error || `Server error (${resp.status})`;
				errorMessage.textContent = "Error: " + errorMsg;
				errorMessage.style.display = "block";
				resultsSection.classList.add("hidden");
				return;
			}

			if (data.error) {
				errorMessage.textContent = "Error: " + data.error;
				errorMessage.style.display = "block";
				resultsSection.classList.add("hidden");
				return;
			}

			// populate table
			tbody.innerHTML = "";
			if (!data.results || data.results.length === 0) {
				tbody.innerHTML =
					'<tr><td colspan="5">No results found for ' + matric + "</td></tr>";
				gpaEl.textContent = "-";
			} else {
				data.results.forEach((r) => {
					const tr = document.createElement("tr");
					tr.innerHTML = `
            <td>${r.course_code || ""}</td>
            <td>${r.course_title || ""}</td>
            <td>${r.credit_units || ""}</td>
            <td>${r.score || ""}</td>
            <td>${r.grade || ""}</td>
          `;
					tbody.appendChild(tr);
				});
				gpaEl.textContent = data.gpa !== null ? data.gpa : "-";
			}
			// Hide login form after successful authentication
			form.style.display = "none";
			resultsSection.classList.remove("hidden");
		} catch (err) {
			errorMessage.textContent = "Failed to load results: " + err.message;
			errorMessage.style.display = "block";
		}
	});
})();
