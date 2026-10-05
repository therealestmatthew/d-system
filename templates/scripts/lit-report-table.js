/*
  Literature-review campaign report - sorting, filtering and column visibility for the three
  table views (REQ-027 R03, R10; phase-lrr-03). tools/lit_report_render.py inlines this file
  into each table page's {{INLINE_SCRIPT}} inside a <script> element, so the page stays one
  self-contained file: no module loader, no fetch, no CDN (R08). Deliverable pages get no script.

  The rows are already in the page as HTML (templates/html/lit-report-table.html). This script
  only reorders, hides and shows them; it never builds a row and never computes a corpus figure.
  The one number it writes is how many rows the reader's own filter left visible.

  Timing (R10, owner ruling 2026-09-30). Each filter run is measured with performance.now()
  around the handler and stored on the view as data-lr-filter-ms. The time until the next frame
  after that run is stored as data-lr-filter-frame-ms, so a browser check can read both the
  handler's cost and the cost including style and layout.
*/
(function () {
  "use strict";

  function cellText(row, column) {
    var cell = row.cells[column];
    return cell ? cell.textContent : "";
  }

  // A column sorts numerically when every non-empty cell is a finite number, otherwise as text.
  function isNumericColumn(rows, column) {
    var seen = false;
    for (var i = 0; i < rows.length; i++) {
      var value = cellText(rows[i], column).trim();
      if (value === "") continue;
      if (!isFinite(Number(value))) return false;
      seen = true;
    }
    return seen;
  }

  function compareValues(a, b, numeric) {
    if (numeric) return Number(a) - Number(b);
    return a.localeCompare(b, undefined, { sensitivity: "base", numeric: true });
  }

  function setUp(view) {
    var table = view.querySelector("table");
    var tbody = table.tBodies[0];
    var headers = Array.prototype.slice.call(table.tHead.rows[0].cells);
    var rows = Array.prototype.slice.call(tbody.rows);
    var originalIndex = new Map();
    var searchText = new Map();
    rows.forEach(function (row, index) {
      originalIndex.set(row, index);
      // Cell texts joined by a newline, so a term never matches across a cell boundary.
      var texts = [];
      for (var c = 0; c < row.cells.length; c++) texts.push(row.cells[c].textContent);
      searchText.set(row, texts.join("\n").toLowerCase());
    });
    var numericCache = {};
    var shown = view.querySelector(".lr-table-view__shown");
    var input = view.querySelector(".lr-table-view__filter-input");

    function filter() {
      var start = performance.now();
      var term = input.value.trim().toLowerCase();
      var visible = 0;
      for (var i = 0; i < rows.length; i++) {
        var match = term === "" || searchText.get(rows[i]).indexOf(term) !== -1;
        if (rows[i].hidden === match) rows[i].hidden = !match;
        if (match) visible++;
      }
      shown.textContent = visible.toLocaleString("en-US");
      view.dataset.lrVisibleRows = String(visible);
      var handler = performance.now() - start;
      view.dataset.lrFilterMs = handler.toFixed(2);
      requestAnimationFrame(function () {
        view.dataset.lrFilterFrameMs = (performance.now() - start).toFixed(2);
      });
    }

    function sortBy(column) {
      var header = headers[column];
      var direction = header.getAttribute("aria-sort") === "ascending" ? "descending" : "ascending";
      if (!(column in numericCache)) numericCache[column] = isNumericColumn(rows, column);
      var numeric = numericCache[column];
      var sign = direction === "ascending" ? 1 : -1;
      var ordered = rows.slice().sort(function (a, b) {
        var left = cellText(a, column).trim();
        var right = cellText(b, column).trim();
        // Empty cells stay at the bottom in both directions; ties keep the CSV's order.
        if (left === "" || right === "") {
          if (left !== right) return left === "" ? 1 : -1;
        } else {
          var order = compareValues(left, right, numeric);
          if (order !== 0) return sign * order;
        }
        return originalIndex.get(a) - originalIndex.get(b);
      });
      var fragment = document.createDocumentFragment();
      ordered.forEach(function (row) { fragment.appendChild(row); });
      tbody.appendChild(fragment);
      headers.forEach(function (other) { other.setAttribute("aria-sort", "none"); });
      header.setAttribute("aria-sort", direction);
    }

    function setColumnVisible(column, visible) {
      headers[column].hidden = !visible;
      for (var i = 0; i < rows.length; i++) {
        var cell = rows[i].cells[column];
        if (cell) cell.hidden = !visible;
      }
    }

    headers.forEach(function (header, column) {
      var button = header.querySelector("button");
      if (button) button.addEventListener("click", function () { sortBy(column); });
    });
    input.addEventListener("input", filter);

    var toggles = view.querySelectorAll("input[data-lr-col]");
    var summary = view.querySelector(".lr-table-view__columns-count");
    function countShownColumns() {
      if (!summary) return;
      var count = 0;
      toggles.forEach(function (toggle) { if (toggle.checked) count++; });
      summary.textContent = String(count);
    }
    toggles.forEach(function (toggle) {
      var column = Number(toggle.getAttribute("data-lr-col"));
      setColumnVisible(column, toggle.checked);
      toggle.addEventListener("change", function () {
        setColumnVisible(column, toggle.checked);
        countShownColumns();
      });
    });
    countShownColumns();
    view.dataset.lrReady = "true";
  }

  document.querySelectorAll(".lr-table-view").forEach(setUp);
})();
