const form = document.querySelector('#upload-form');
const apiInput = document.querySelector('#api-url');
const fileInput = document.querySelector('#files');
const statusEl = document.querySelector('#status');
const tableBody = document.querySelector('#results tbody');

const setStatus = (message, isError = false) => {
  statusEl.textContent = message;
  statusEl.style.color = isError ? '#b91c1c' : '#1f2937';
};

form.addEventListener('submit', async (event) => {
  event.preventDefault();
  tableBody.innerHTML = '';

  if (!fileInput.files || fileInput.files.length === 0) {
    setStatus('Please select at least one file.', true);
    return;
  }

  const formData = new FormData();
  Array.from(fileInput.files).forEach((file) => formData.append('files', file));

  const apiBase = apiInput.value.replace(/\/$/, '');
  setStatus('Analyzing files...');

  try {
    const response = await fetch(`${apiBase}/analyze`, { method: 'POST', body: formData });
    if (!response.ok) throw new Error(await response.text());

    const data = await response.json();
    data.results.forEach((item) => {
      const row = document.createElement('tr');
      row.innerHTML = `<td>${item.filename}</td><td>${item.label}</td><td>${item.score.toFixed(4)}</td><td>${item.chars_analyzed}</td>`;
      tableBody.appendChild(row);
    });

    setStatus(`Done. Model: ${data.model}. Files analyzed: ${data.total_files}.`);
  } catch (error) {
    setStatus(`Error: ${error.message}`, true);
  }
});
