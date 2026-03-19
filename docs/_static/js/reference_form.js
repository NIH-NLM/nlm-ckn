/**
 * Cell-KN Reference Selection Form
 * Handles reference dataset selection (radio-like checkboxes),
 * reviewer name/notes input, and CSV export.
 */
document.addEventListener("DOMContentLoaded", function () {
  // Make reference checkboxes behave like radio buttons (one per tissue)
  document.querySelectorAll(".ref-checkbox").forEach(function (checkbox) {
    checkbox.addEventListener("change", function () {
      if (this.checked) {
        var tissue = this.dataset.tissue;
        document
          .querySelectorAll('.ref-checkbox[data-tissue="' + tissue + '"]')
          .forEach(function (other) {
            if (other !== checkbox) {
              other.checked = false;
            }
          });
      }
    });
  });

  // CSV Download button handler
  document.querySelectorAll(".download-csv-btn").forEach(function (btn) {
    btn.addEventListener("click", function () {
      var tissue = this.dataset.tissue;
      var formContainer = document.getElementById("form-" + tissue);
      if (!formContainer) return;

      var reviewerName =
        formContainer.querySelector(".reviewer-name")?.value || "";
      var rows = formContainer.querySelectorAll("tr.dataset-row");
      var csvLines = [
        "tissue,dataset,first_author,year,collection_url,explorer_url,is_reference,reviewer_name,notes",
      ];

      rows.forEach(function (row) {
        var dataset = row.dataset.dataset || "";
        var author = row.dataset.author || "";
        var year = row.dataset.year || "";
        var collectionUrl = row.dataset.collectionUrl || "";
        var explorerUrl = row.dataset.explorerUrl || "";
        var isRef = row.querySelector(".ref-checkbox")?.checked ? "YES" : "NO";
        var notes = row.querySelector(".notes-input")?.value || "";

        // Escape CSV fields
        var escapeCsv = function (val) {
          if (val.indexOf(",") >= 0 || val.indexOf('"') >= 0 || val.indexOf("\n") >= 0) {
            return '"' + val.replace(/"/g, '""') + '"';
          }
          return val;
        };

        csvLines.push(
          [
            escapeCsv(tissue),
            escapeCsv(dataset),
            escapeCsv(author),
            escapeCsv(year),
            escapeCsv(collectionUrl),
            escapeCsv(explorerUrl),
            isRef,
            escapeCsv(reviewerName),
            escapeCsv(notes),
          ].join(",")
        );
      });

      var csvContent = csvLines.join("\n");
      var blob = new Blob([csvContent], { type: "text/csv;charset=utf-8;" });
      var url = URL.createObjectURL(blob);
      var link = document.createElement("a");
      link.href = url;
      link.download = tissue + "_reference_selection.csv";
      link.style.display = "none";
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      URL.revokeObjectURL(url);
    });
  });
});
