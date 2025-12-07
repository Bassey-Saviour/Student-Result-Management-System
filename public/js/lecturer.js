// Lecturer Grade Upload Page JavaScript
(function () {
	"use strict";

	// Helper function to convert score to grade
	function scoreToGrade(score) {
		const s = parseInt(score) || 0;
		if (s >= 80) return "A";
		if (s >= 60) return "B";
		if (s >= 50) return "C";
		if (s >= 45) return "D";
		if (s >= 40) return "E";
		return "F";
	}

	// Lecturer login and course loading
	const loginForm = document.getElementById("login-form");
	const uploadSection = document.getElementById("upload-section");
	const courseSelect = document.getElementById("courseSelect");
	const courseSelectForm = document.getElementById("course-select-form");
	const studentsTableSection = document.getElementById(
		"students-table-section"
	);
	const courseTitle = document.getElementById("course-title");
	const tbody = document.getElementById("students-table-body");
	const loginError = document.getElementById("login-error");
	const uploadError = document.getElementById("upload-error");
	const uploadStatus = document.getElementById("upload-status");
	const submitScoresBtn = document.getElementById("submit-scores-btn");
	let currentCourseId = null;
	let studentsData = [];

	loginForm.addEventListener("submit", async function (e) {
		e.preventDefault();
		const username = document.getElementById("lecturerUsername").value.trim();
		const password = document.getElementById("lecturerPassword").value;
		if (!username || !password) return;

		// Clear previous errors
		loginError.style.display = "none";
		loginError.textContent = "";

		try {
			const params = new URLSearchParams();
			params.append("username", username);
			params.append("password", password);

			const resp = await fetch("/cgi-bin/lecturer_courses.py", {
				method: "POST",
				credentials: "same-origin",
				body: params,
			});

			const data = await resp.json();

			if (!resp.ok) {
				const errorMsg = data.error || `Server error (${resp.status})`;
				loginError.textContent = "Error: " + errorMsg;
				loginError.style.display = "block";
				return;
			}

			if (data.error) {
				loginError.textContent = "Error: " + data.error;
				loginError.style.display = "block";
				return;
			}

			if (!data.courses || data.courses.length === 0) {
				loginError.textContent = "No courses found for this lecturer";
				loginError.style.display = "block";
				return;
			}

			// Populate course dropdown
			courseSelect.innerHTML = '<option value="">Select course</option>';
			data.courses.forEach((course) => {
				const option = document.createElement("option");
				option.value = course.course_id;
				option.textContent = course.course_code + " - " + course.course_title;
				courseSelect.appendChild(option);
			});

			// Hide login form after successful authentication
			document.getElementById("lecturer-login").style.display = "none";
			uploadSection.classList.remove("hidden");
		} catch (err) {
			loginError.textContent = "Failed to load courses: " + err.message;
			loginError.style.display = "block";
		}
	});

	// Handle course selection
	courseSelect.addEventListener("change", async function () {
		const courseId = this.value;
		if (!courseId) {
			studentsTableSection.classList.add("hidden");
			return;
		}

		currentCourseId = courseId;
		uploadError.style.display = "none";
		uploadError.textContent = "";

		try {
			const resp = await fetch(
				"/cgi-bin/get_course_students.py?course_id=" +
					encodeURIComponent(courseId),
				{
					method: "GET",
					credentials: "same-origin",
				}
			);

			const data = await resp.json();

			if (!resp.ok) {
				const errorMsg = data.error || `Server error (${resp.status})`;
				uploadError.textContent = "Error: " + errorMsg;
				uploadError.style.display = "block";
				return;
			}

			if (data.error) {
				uploadError.textContent = "Error: " + data.error;
				uploadError.style.display = "block";
				return;
			}

			// Set course title
			courseTitle.textContent = data.course_code + " - " + data.course_title;

			// Store students data and render table
			studentsData = data.students || [];
			tbody.innerHTML = "";

			if (studentsData.length === 0) {
				tbody.innerHTML =
					'<tr><td colspan="5" style="text-align: center;">No students found</td></tr>';
			} else {
				studentsData.forEach((student, idx) => {
					const tr = document.createElement("tr");
					const scoreInput = document.createElement("input");
					scoreInput.type = "number";
					scoreInput.min = "0";
					scoreInput.max = "100";
					scoreInput.value = student.score || "";
					scoreInput.dataset.studentIdx = idx;
					scoreInput.dataset.studentId = student.student_id;
					scoreInput.class = "score-input";

					const gradeCell = document.createElement("td");
					gradeCell.className = "grade-cell";
					gradeCell.textContent = student.grade || "";
					gradeCell.dataset.studentIdx = idx;

					// Auto-update grade on score input
					scoreInput.addEventListener("input", function () {
						const grade = this.value ? scoreToGrade(this.value) : "";
						gradeCell.textContent = grade;
					});

					const scoreTd = document.createElement("td");
					scoreTd.appendChild(scoreInput);

					tr.innerHTML = `
            <td>${student.matric_no}</td>
            <td>${student.first_name}</td>
            <td>${student.last_name}</td>
          `;
					tr.appendChild(scoreTd);
					tr.appendChild(gradeCell);
					tbody.appendChild(tr);
				});
			}

			studentsTableSection.classList.remove("hidden");
		} catch (err) {
			uploadError.textContent = "Failed to load students: " + err.message;
			uploadError.style.display = "block";
		}
	});

	// Handle submit all scores
	submitScoresBtn.addEventListener("click", async function () {
		uploadError.style.display = "none";
		uploadError.textContent = "";

		// Collect all scores
		const scoreInputs = tbody.querySelectorAll('input[type="number"]');
		const updates = [];

		scoreInputs.forEach((input) => {
			const studentId = input.dataset.studentId;
			const score = input.value.trim();

			if (score === "") {
				return; // Skip empty scores
			}

			try {
				const scoreVal = parseInt(score);
				if (scoreVal < 0 || scoreVal > 100) {
					throw new Error("Score must be between 0 and 100");
				}
				updates.push({
					course_id: currentCourseId,
					student_id: studentId,
					score: scoreVal,
				});
			} catch (e) {
				uploadError.textContent = "Error: " + e.message;
				uploadError.style.display = "block";
				throw e;
			}
		});

		if (updates.length === 0) {
			uploadError.textContent = "Error: No scores to submit";
			uploadError.style.display = "block";
			return;
		}

		try {
			// Submit each score
			for (const update of updates) {
				const params = new URLSearchParams();
				params.append("course_id", currentCourseId);
				params.append("student_id", update.student_id);
				params.append("score", update.score);

				const resp = await fetch("/cgi-bin/upload_results_by_student.py", {
					method: "POST",
					credentials: "same-origin",
					body: params,
				});

				if (!resp.ok) throw new Error("Failed to upload result");
				const data = await resp.json();
				if (data.error) throw new Error(data.error);
			}

			// Show success
			uploadStatus.style.display = "block";
			setTimeout(() => {
				uploadStatus.style.display = "none";
				courseSelect.value = "";
				studentsTableSection.classList.add("hidden");
			}, 3000);
		} catch (err) {
			uploadError.textContent = "Failed to upload results: " + err.message;
			uploadError.style.display = "block";
		}
	});
})();
