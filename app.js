const results = document.getElementById('results');
const raceNameInput = document.getElementById('raceName');
const entryTableBody = document.getElementById('entryTableBody');
const addRowBtn = document.getElementById('addRowBtn');
const calculateBtn = document.getElementById('calculateBtn');
const saveRaceBtn = document.getElementById('saveRaceBtn');
const exportBtn = document.getElementById('exportBtn');
const saveTemplateBtn = document.getElementById('saveTemplateBtn');
const loadTemplateBtn = document.getElementById('loadTemplateBtn');
const savedTemplates = document.getElementById('savedTemplates');

let competitors = [];
let boatOptions = [];
let savedRaceSheets = [];

function formatTime(totalSeconds) {
  const hours = Math.floor(totalSeconds / 3600);
  const minutes = Math.floor((totalSeconds % 3600) / 60);
  const seconds = Math.round(totalSeconds % 60);
  return `${String(hours).padStart(2, '0')}:${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`;
}

function parseTimeInput(value) {
  const trimmed = String(value).trim();
  if (!trimmed) return 0;
  if (trimmed.includes(':')) {
    const parts = trimmed.split(':').map((part) => Number(part));
    if (parts.length === 2) {
      return parts[0] * 60 + parts[1];
    }
    if (parts.length === 3) {
      return parts[0] * 3600 + parts[1] * 60 + parts[2];
    }
  }
  return Number(trimmed) * 60;
}

function getCorrectedTime(entry) {
  const elapsedSeconds = parseTimeInput(entry.elapsedTime);
  const boat = boatOptions.find((item) => item.name === entry.boatClass);
  const handicap = boat?.handicap || 100;
  return formatTime(Math.round(elapsedSeconds * (handicap / 100)));
}

function getCorrectedSeconds(entry) {
  const elapsedSeconds = parseTimeInput(entry.elapsedTime);
  const boat = boatOptions.find((item) => item.name === entry.boatClass);
  const handicap = boat?.handicap || 100;
  return elapsedSeconds * (handicap / 100);
}

async function loadBoatOptions() {
  const response = await fetch('/api/boat-definitions');
  const boats = await response.json();
  boatOptions = boats;
  loadSavedTemplates();
  if (!competitors.length) {
    addRow();
  }
}

function loadSavedTemplates() {
  const stored = localStorage.getItem('sailing-race-sheets');
  if (stored) {
    savedRaceSheets = JSON.parse(stored);
  }
  renderSavedTemplates();
}

function saveSavedTemplates() {
  localStorage.setItem('sailing-race-sheets', JSON.stringify(savedRaceSheets));
  renderSavedTemplates();
}

function renderSavedTemplates() {
  if (!savedRaceSheets.length) {
    savedTemplates.innerHTML = '<p class="placeholder">No saved race sheets yet.</p>';
    return;
  }

  savedTemplates.innerHTML = savedRaceSheets.map((sheet, index) => `
    <div class="template-chip">
      <span>${sheet.name || 'Untitled race'} · ${sheet.competitors.length} row${sheet.competitors.length === 1 ? '' : 's'}</span>
      <button class="small-btn" data-template-index="${index}">Restore</button>
    </div>
  `).join('');
}

function saveCurrentTableAsTemplate() {
  if (!competitors.length) {
    alert('Add at least one row before saving the table.');
    return;
  }

  const sheetName = prompt('Name this saved race sheet', raceNameInput.value || 'Race sheet');
  if (!sheetName) {
    return;
  }

  savedRaceSheets.push({
    name: sheetName,
    competitors: competitors.map((entry) => ({ ...entry })),
  });
  saveSavedTemplates();
}

function loadTemplateIntoTable() {
  if (!savedRaceSheets.length) {
    alert('No saved race sheets yet.');
    return;
  }

  const sheet = savedRaceSheets[0];
  competitors = sheet.competitors.map((entry) => ({
    ...entry,
    correctedTime: entry.correctedTime || getCorrectedTime(entry),
    difference: entry.difference || '',
  }));
  raceNameInput.value = sheet.name || raceNameInput.value;
  renderEntryTable();
  renderResults();
}

function createRowData() {
  return {
    sailorName: '',
    boatClass: boatOptions[0]?.name || 'Laser',
    sailNumber: '',
    elapsedTime: '35:00',
    correctedTime: '',
    difference: '',
  };
}

function addRow() {
  competitors.push(createRowData());
  renderEntryTable();
}

function removeRow(index) {
  competitors.splice(index, 1);
  if (!competitors.length) {
    addRow();
  }
  renderEntryTable();
}

function updateCompetitor(index, field, value) {
  if (!competitors[index]) return;

  const activeElement = document.activeElement;
  competitors[index][field] = value;

  if (field === 'elapsedTime' || field === 'boatClass') {
    competitors[index].correctedTime = getCorrectedTime(competitors[index]);
  }

  const row = entryTableBody.children[index];
  if (!row) return;

  const correctedCell = row.querySelector('[data-field="correctedTime"]');
  if (correctedCell) {
    correctedCell.value = competitors[index].correctedTime;
  }

  if (activeElement instanceof HTMLElement && activeElement.dataset.index === String(index)) {
    requestAnimationFrame(() => {
      activeElement.focus();
      if (activeElement instanceof HTMLInputElement && 'setSelectionRange' in activeElement) {
        const end = activeElement.value.length;
        activeElement.setSelectionRange(end, end);
      }
    });
  }
}

function renderEntryTable() {
  if (!competitors.length) {
    competitors.push(createRowData());
  }

  entryTableBody.innerHTML = competitors.map((entry, index) => `
    <tr>
      <td><input value="${entry.sailorName}" data-index="${index}" data-field="sailorName" /></td>
      <td>
        <select data-index="${index}" data-field="boatClass">
          ${boatOptions.map((boat) => `<option value="${boat.name}" ${boat.name === entry.boatClass ? 'selected' : ''}>${boat.name}</option>`).join('')}
        </select>
      </td>
      <td><input value="${entry.sailNumber}" data-index="${index}" data-field="sailNumber" /></td>
      <td><input value="${entry.elapsedTime}" data-index="${index}" data-field="elapsedTime" /></td>
      <td><input value="${entry.correctedTime}" data-index="${index}" data-field="correctedTime" readonly /></td>
      <td><input value="${entry.difference}" data-index="${index}" data-field="difference" readonly /></td>
      <td><button class="remove-btn" data-index="${index}">Remove</button></td>
    </tr>
  `).join('');
}

function renderResults() {
  if (!competitors.length) {
    results.innerHTML = '<h2>Results</h2><p class="placeholder">Add competitors to build the race table.</p>';
    return;
  }

  const rows = competitors.map((entry, index) => `
    <tr>
      <td>${index + 1}</td>
      <td>${entry.sailorName || '-'}</td>
      <td>${entry.sailNumber || '-'}</td>
      <td>${entry.boatClass}</td>
      <td>${entry.elapsedTime}</td>
      <td>${entry.correctedTime || '-'}</td>
      <td>${entry.difference || '-'}</td>
    </tr>
  `).join('');

  results.innerHTML = `
    <h2>Results</h2>
    <table class="results-table">
      <thead>
        <tr>
          <th>Pos</th>
          <th>Sailor</th>
          <th>Sail #</th>
          <th>Boat</th>
          <th>Elapsed</th>
          <th>Corrected</th>
          <th>Diff</th>
        </tr>
      </thead>
      <tbody>${rows}</tbody>
    </table>
  `;
}

function calculateResults() {
  if (!competitors.length) {
    alert('Add at least one competitor first.');
    return;
  }

  const rows = competitors
    .map((entry) => ({ ...entry, correctedSeconds: getCorrectedSeconds(entry) }))
    .sort((a, b) => a.correctedSeconds - b.correctedSeconds);

  const winnerSeconds = rows[0]?.correctedSeconds || 0;

  competitors = rows.map((entry, index) => ({
    ...entry,
    correctedTime: formatTime(Math.round(entry.correctedSeconds)),
    difference: index === 0 ? '00:00:00' : formatTime(Math.round(entry.correctedSeconds - winnerSeconds)),
  }));

  renderEntryTable();
  renderResults();
}

async function saveRace() {
  if (!competitors.length) {
    alert('Add competitors before saving.');
    return;
  }

  const payload = {
    race_name: raceNameInput.value || 'New Race',
    competitors: competitors.map((entry) => ({
      sailor_name: entry.sailorName,
      boat_class: entry.boatClass,
      sail_number: entry.sailNumber,
      elapsed_time: entry.elapsedTime,
    })),
  };

  await fetch('/api/races', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });

  alert('Race saved locally.');
}

function exportToExcel() {
  const rowsToExport = competitors.length ? competitors : [createRowData()];
  const raceName = (raceNameInput.value || 'Race').replace(/[^a-z0-9-_]+/gi, '-').toLowerCase();
  const lines = [
    ['Race', raceNameInput.value || 'Race'],
    [],
    ['Sailor', 'Boat', 'Sail #', 'Elapsed', 'Corrected', 'Diff'],
    ...rowsToExport.map((entry) => [entry.sailorName, entry.boatClass, entry.sailNumber, entry.elapsedTime, entry.correctedTime, entry.difference]),
  ];

  const csvContent = lines
    .map((line) => line.map((cell) => `"${String(cell).replace(/"/g, '""')}"`).join(','))
    .join('\n');

  const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = `${raceName || 'race'}.csv`;
  link.click();
  URL.revokeObjectURL(url);
}

entryTableBody.addEventListener('input', (event) => {
  const target = event.target;
  if (!(target instanceof HTMLInputElement || target instanceof HTMLSelectElement)) {
    return;
  }
  const index = Number(target.dataset.index);
  const field = target.dataset.field;
  updateCompetitor(index, field, target.value);
});

entryTableBody.addEventListener('change', (event) => {
  const target = event.target;
  if (!(target instanceof HTMLInputElement || target instanceof HTMLSelectElement)) {
    return;
  }
  const index = Number(target.dataset.index);
  const field = target.dataset.field;
  if (field === 'boatClass' || field === 'elapsedTime') {
    updateCompetitor(index, field, target.value);
  }
});

entryTableBody.addEventListener('click', (event) => {
  const target = event.target;
  if (!(target instanceof HTMLElement) || !target.classList.contains('remove-btn')) {
    return;
  }
  const index = Number(target.dataset.index);
  removeRow(index);
});

savedTemplates.addEventListener('click', (event) => {
  const target = event.target;
  if (!(target instanceof HTMLElement) || !target.classList.contains('small-btn')) {
    return;
  }
  const index = Number(target.dataset.templateIndex);
  const sheet = savedRaceSheets[index];
  if (!sheet) return;

  competitors = sheet.competitors.map((entry) => ({
    ...entry,
    correctedTime: entry.correctedTime || getCorrectedTime(entry),
    difference: entry.difference || '',
  }));
  raceNameInput.value = sheet.name || raceNameInput.value;
  renderEntryTable();
  renderResults();
});

addRowBtn.addEventListener('click', addRow);
calculateBtn.addEventListener('click', calculateResults);
saveRaceBtn.addEventListener('click', saveRace);
exportBtn.addEventListener('click', exportToExcel);
saveTemplateBtn.addEventListener('click', saveCurrentTableAsTemplate);
loadTemplateBtn.addEventListener('click', loadTemplateIntoTable);
loadBoatOptions();
renderResults();
