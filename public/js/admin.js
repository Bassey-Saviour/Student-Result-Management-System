// Admin Dashboard Page JavaScript
(function () {
	"use strict";

	// Configuration
	const CGI_SCRIPT_URL = "/api/get_all_data";
	const CGI_SCRIPT_URL2 = "/api/add_data";

	// Admin authentication
	const adminLoginForm = document.getElementById("admin-login-form");
	const adminLoginSection = document.getElementById("admin-login");
	const adminDashboard = document.getElementById("admin-dashboard");
	const adminLoginError = document.getElementById("admin-login-error");

	adminLoginForm.addEventListener("submit", async function (e) {
		e.preventDefault();
		const username = document.getElementById("adminUsername").value.trim();
		const password = document.getElementById("adminPassword").value;
		if (!username || !password) return;

		// Clear previous errors
		adminLoginError.style.display = "none";
		adminLoginError.textContent = "";

		try {
			const resp = await fetch("/api/admin_login", {
				method: "POST",
				credentials: "same-origin",
				headers: { "Content-Type": "application/json" },
				body: JSON.stringify({
					username: username,
					password: password,
				}),
			});

			const data = await resp.json();

			if (!resp.ok) {
				const errorMsg = data.error || `Server error (${resp.status})`;
				adminLoginError.textContent = "Error: " + errorMsg;
				adminLoginError.style.display = "block";
				return;
			}

			if (data.error) {
				adminLoginError.textContent = "Error: " + data.error;
				adminLoginError.style.display = "block";
				return;
			}

			// Login successful
			adminLoginSection.style.display = "none";
			adminDashboard.classList.remove("hidden");

			// Load all data
			loadAllData();
		} catch (err) {
			adminLoginError.textContent = "Failed to login: " + err.message;
			adminLoginError.style.display = "block";
		}
	});

	// Tab switching logic
	const tabs = document.querySelectorAll('[role="tab"]');
	const tabContents = document.querySelectorAll('[role="tabpanel"]');

	tabs.forEach((tab) => {
		tab.addEventListener("click", () => {
			tabs.forEach((t) => {
				t.classList.remove("active");
				t.setAttribute("aria-selected", "false");
			});
			tab.classList.add("active");
			tab.setAttribute("aria-selected", "true");

			tabContents.forEach((content) => {
				content.classList.remove("active");
			});
			const selectedPanel = document.getElementById(
				tab.getAttribute("aria-controls")
			);
			selectedPanel.classList.add("active");
		});
	});

	// Function to fetch data from API
	async function fetchData(action) {
		try {
			const response = await fetch(`${CGI_SCRIPT_URL}?action=${action}`);

			// Log response status
			console.log("Response status:", response.status);

			if (!response.ok) {
				throw new Error(`HTTP error! status: ${response.status}`);
			}

			// Get response text first
			const text = await response.text();
			console.log("Response text:", text.substring(0, 200)); // Log first 200 chars

			// Try to parse as JSON
			if (!text || text.trim() === "") {
				throw new Error("Empty response from server");
			}

			const data = JSON.parse(text);
			return data;
		} catch (error) {
			console.error("Error fetching data:", error);
			console.error("Full error:", error.message);
			return null;
		}
	}

	// Modal confirmation helper
	function showConfirmModal(title, message) {
		return new Promise((resolve) => {
			const overlay = document.createElement("div");
			overlay.className = "modal-overlay";
			overlay.innerHTML = `
	        <div class="modal-card" role="dialog" aria-modal="true" aria-label="${title}">
	          <h3>${title}</h3>
	          <p>${message}</p>
	          <div class="modal-actions">
	            <button type="button" class="btn-secondary" data-action="cancel">Cancel</button>
	            <button type="button" class="btn-primary" data-action="confirm">Delete</button>
	          </div>
	        </div>
	      `;

			document.body.appendChild(overlay);

			const cleanup = () => {
				overlay.remove();
			};

			overlay.addEventListener("click", (e) => {
				if (e.target === overlay) {
					cleanup();
					resolve(false);
				}
			});

			overlay
				.querySelector('[data-action="cancel"]')
				.addEventListener("click", () => {
					cleanup();
					resolve(false);
				});

			overlay
				.querySelector('[data-action="confirm"]')
				.addEventListener("click", () => {
					cleanup();
					resolve(true);
				});
		});
	}

	// Function to populate students table
	function populateStudents(students) {
		const tbody = document.getElementById("students-tbody");
		const table = document.getElementById("students-table");
		const loading = document.getElementById("students-loading");

		if (!students || students.length === 0) {
			loading.textContent = "No students found.";
			return;
		}

		tbody.innerHTML = "";
		students.forEach((student) => {
			const row = tbody.insertRow();
			row.innerHTML = `
        <td>${student.matric_no}</td>
        <td>${student.first_name}</td>
        <td>${student.last_name}</td>
        <td>${student.email}</td>
        <td>${student.department_code}</td>
        <td>
          <button class="btn-delete" data-type="student" data-id="${student.student_id}" data-name="${student.first_name} ${student.last_name}">
            <img src="/images/icons8-delete.svg"/>
          </button>
        </td>
      `;
		});

		// Add delete event listeners
		const deleteButtons = tbody.querySelectorAll(".btn-delete");
		deleteButtons.forEach((btn) => {
			btn.addEventListener("click", handleDelete);
		});

		loading.style.display = "none";
		table.style.display = "table";
	}

	// Function to populate lecturers table
	function populateLecturers(lecturers) {
		const tbody = document.getElementById("lecturers-tbody");
		const table = document.getElementById("lecturers-table");
		const loading = document.getElementById("lecturers-loading");

		if (!lecturers || lecturers.length === 0) {
			loading.textContent = "No lecturers found.";
			return;
		}

		tbody.innerHTML = "";
		lecturers.forEach((lecturer) => {
			const row = tbody.insertRow();
			row.innerHTML = `
      <td>${lecturer.first_name}</td>
        <td>${lecturer.last_name}</td>
      <td>${lecturer.email}</td>
        <td>${lecturer.department_code}</td>
        <td>
          <button class="btn-delete" data-type="lecturer" data-id="${lecturer.lecturer_id}" data-name="${lecturer.first_name} ${lecturer.last_name}">
            <img src="/images/icons8-delete.svg"/>
          </button>
        </td>
      `;
		});

		// Add delete event listeners
		const deleteButtons = tbody.querySelectorAll(".btn-delete");
		deleteButtons.forEach((btn) => {
			btn.addEventListener("click", handleDelete);
		});

		loading.style.display = "none";
		table.style.display = "table";
	}

	// Function to populate courses table
	function populateCourses(courses) {
		const tbody = document.getElementById("courses-tbody");
		const table = document.getElementById("courses-table");
		const loading = document.getElementById("courses-loading");

		if (!courses || courses.length === 0) {
			loading.textContent = "No courses found.";
			return;
		}

		tbody.innerHTML = "";
		courses.forEach((course) => {
			const row = tbody.insertRow();
			row.innerHTML = `
        <td>${course.course_code}</td>
        <td>${course.course_title}</td>
        <td>${course.credit_units}</td>
        <td>${course.department_code}</td>
        <td>${course.lecturer_name}</td>
        <td>
          <button class="btn-delete" data-type="course" data-id="${course.course_id}" data-name="${course.course_code}">
            <img src="/images/icons8-delete.svg"/>
          </button>
        </td>
      `;
		});

		// Add delete event listeners
		const deleteButtons = tbody.querySelectorAll(".btn-delete");
		deleteButtons.forEach((btn) => {
			btn.addEventListener("click", handleDelete);
		});

		loading.style.display = "none";
		table.style.display = "table";
	}

	// Load all data after admin login
	async function loadAllData() {
		const data = await fetchData("get_all");

		if (data) {
			if (data.students) {
				populateStudents(data.students);
			}
			if (data.lecturers) {
				populateLecturers(data.lecturers);
			}
			if (data.courses) {
				populateCourses(data.courses);
			}
		} else {
			document.getElementById("students-loading").textContent =
				"Error loading data. Please check your configuration.";
			document.getElementById("lecturers-loading").textContent =
				"Error loading data. Please check your configuration.";
			document.getElementById("courses-loading").textContent =
				"Error loading data. Please check your configuration.";
		}
	}

	// Function to submit form data
	async function submitFormData(action, formData) {
		try {
			const payload = {
				action: action,
				...formData,
			};

			const response = await fetch(CGI_SCRIPT_URL2, {
				method: "POST",
				headers: {
					"Content-Type": "application/json",
				},
				body: JSON.stringify(payload),
			});

			if (!response.ok) {
				throw new Error(`HTTP error! status: ${response.status}`);
			}

			const data = await response.json();
			return data;
		} catch (error) {
			console.error("Error submitting form:", error);
			return { success: false, message: error.message };
		}
	}

	// Function to show message
	// Function to show message in a modal (for delete feedback)
	// Function to show inline message (for add forms)
	function showMessage(elementId, message, isSuccess) {
		const msgElement = document.getElementById(elementId);
		msgElement.textContent = message;
		msgElement.style.display = "block";
		msgElement.style.color = isSuccess ? "green" : "red";
		msgElement.style.fontWeight = "bold";
		// Hide message after 5 seconds
		setTimeout(() => {
			msgElement.style.display = "none";
		}, 5000);
	}
	function showMessageModal(message, isSuccess) {
		const overlay = document.createElement("div");
		overlay.className = "modal-overlay";
		overlay.innerHTML = `
			<div class="modal-card" role="dialog" aria-modal="true" aria-label="Message">
				<h3 style="color: ${isSuccess ? "green" : "red"};">${
			isSuccess ? "Success" : "Error"
		}</h3>
				<p>${message}</p>
				<div class="modal-actions">
					<button type="button" class="btn-primary" data-action="close">OK</button>
				</div>
			</div>
		`;
		document.body.appendChild(overlay);
		const closeBtn = overlay.querySelector('[data-action="close"]');
		closeBtn.addEventListener("click", () => {
			overlay.remove();
		});
		// Auto-close after 5 seconds
		setTimeout(() => {
			if (document.body.contains(overlay)) overlay.remove();
		}, 5000);
	}

	// Student form submission
	document
		.getElementById("student-form")
		.addEventListener("submit", async function (e) {
			e.preventDefault();

			const formData = {
				matric_no: document.getElementById("studMatric").value,
				first_name: document.getElementById("studFirstName").value,
				last_name: document.getElementById("studLastName").value,
				email: document.getElementById("studEmail").value,
				level: document.getElementById("studLevel").value,
				department_code: document.getElementById("studDept").value,
				password: document.getElementById("studPword").value,
			};

			const result = await submitFormData("add_student", formData);

			if (result.success) {
				showMessage("student-message", result.message, true);
				this.reset();
				// Refresh the students table
				const data = await fetchData("get_students");
				if (data && data.students) {
					populateStudents(data.students);
				}
			} else {
				showMessage("student-message", "Error: " + result.message, false);
			}
		});

	// Lecturer form submission
	document
		.getElementById("lecturer-form")
		.addEventListener("submit", async function (e) {
			e.preventDefault();

			const formData = {
				email: document.getElementById("lectEmail").value,
				first_name: document.getElementById("lectFirstName").value,
				last_name: document.getElementById("lectLastName").value,
				department_code: document.getElementById("lectDept").value,
				password: document.getElementById("lectPword").value,
			};

			const result = await submitFormData("add_lecturer", formData);

			if (result.success) {
				showMessage("lecturer-message", result.message, true);
				this.reset();
				// Refresh the lecturers table
				const data = await fetchData("get_lecturers");
				if (data && data.lecturers) {
					populateLecturers(data.lecturers);
				}
			} else {
				showMessage("lecturer-message", "Error: " + result.message, false);
			}
		});

	// Course form submission
	document
		.getElementById("course-form")
		.addEventListener("submit", async function (e) {
			e.preventDefault();

			const formData = {
				course_code: document.getElementById("courseCode").value,
				course_title: document.getElementById("courseTitle").value,
				credit_units: document.getElementById("courseUnits").value,
				department_code: document.getElementById("courseDept").value,
				lecturer_name: document.getElementById("courseLecturer").value,
			};

			const result = await submitFormData("add_course", formData);

			if (result.success) {
				showMessage("course-message", result.message, true);
				this.reset();
				// Refresh the courses table
				const data = await fetchData("get_courses");
				if (data && data.courses) {
					populateCourses(data.courses);
				}
			} else {
				showMessage("course-message", "Error: " + result.message, false);
			}
		});

	// Handle delete button clicks
	async function handleDelete(event) {
		const button = event.currentTarget || event.target;
		const entityType = button.dataset.type;
		const entityId = button.dataset.id;
		const entityName = button.dataset.name;

		// Confirm deletion using modal
		const confirmed = await showConfirmModal(
			"Confirm delete",
			`Are you sure you want to delete ${entityType} "${entityName}"? This action cannot be undone.`
		);

		if (!confirmed) return;

		try {
			const response = await fetch("/api/delete_data", {
				method: "POST",
				headers: {
					"Content-Type": "application/json",
				},
				body: JSON.stringify({
					type: entityType,
					id: entityId,
				}),
			});

			const result = await response.json();

			// Show feedback in a modal
			if (result.success) {
				showMessageModal(result.message, true);
				// Refresh the appropriate table
				if (entityType === "student") {
					const data = await fetchData("get_students");
					if (data && data.students) {
						populateStudents(data.students);
					}
				} else if (entityType === "lecturer") {
					const data = await fetchData("get_lecturers");
					if (data && data.lecturers) {
						populateLecturers(data.lecturers);
					}
				} else if (entityType === "course") {
					const data = await fetchData("get_courses");
					if (data && data.courses) {
						populateCourses(data.courses);
					}
				}
			} else {
				showMessageModal("Error: " + (result.error || "Delete failed"), false);
			}
		} catch (error) {
			console.error("Delete error:", error);
			showMessageModal("Failed to delete: " + error.message, false);
		}
	}
})();
