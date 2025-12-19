document.addEventListener("DOMContentLoaded", function () {
  const service = document.getElementById("service_type");
  const preview = document.getElementById("previewImage");

  const paintingFields = document.getElementById("painting-fields");
  const epoxyFields = document.getElementById("epoxy-fields");

  // Painting options
  const fullRepaint = document.querySelector('[name="full_repaint"]');
  const paintCeiling = document.querySelector('[name="paint_ceiling"]');
  const ceilingRepaint = document.querySelector('[name="ceiling_repaint"]');
  const baseboards = document.querySelector('[name="baseboards"]');
  const crown = document.querySelector('[name="crown"]');

  // Epoxy option
  const epoxyType = document.querySelector('[name="epoxy_type"]');

  if (!service || !preview || !paintingFields || !epoxyFields) return;

  function updatePreview() {
    if (service.value === "painting") {
      paintingFields.style.display = "block";
      epoxyFields.style.display = "none";

      // Determine which painting image to show
      let imageName = "interior_livingroom"; // default

      // Walls type
      if (fullRepaint && fullRepaint.value === "yes") {
        imageName = "interior_full_repaint";
      } else if (fullRepaint && fullRepaint.value === "no") {
        imageName = "interior_refresh";
      }

      // Ceiling
      if (paintCeiling && paintCeiling.value === "yes") {
        if (ceilingRepaint && ceilingRepaint.value === "yes") {
          imageName += "_ceiling_repaint";
        } else {
          imageName += "_ceiling_fresh";
        }
      }

      // Trims
      if (baseboards && baseboards.value === "yes") {
        imageName += "_baseboards";
      }
      if (crown && crown.value === "yes") {
        imageName += "_crown";
      }

      preview.src = `/static/images/previews/${imageName}.jpg`;

    } else if (service.value === "epoxy") {
      paintingFields.style.display = "none";
      epoxyFields.style.display = "block";

      let epoxyImage = "epoxy_garage";

      if (epoxyType) {
        if (epoxyType.value === "chip") {
          epoxyImage = "epoxy_chip";
        } else if (epoxyType.value === "metallic") {
          epoxyImage = "epoxy_metallic";
        } else {
          epoxyImage = "epoxy_solid";
        }
      }

      preview.src = `/static/images/previews/${epoxyImage}.jpg`;
    }
  }

  // Update preview on page load
  updatePreview();

  // Update preview when any relevant option changes
  service.addEventListener("change", updatePreview);
  if (fullRepaint) fullRepaint.addEventListener("change", updatePreview);
  if (paintCeiling) paintCeiling.addEventListener("change", updatePreview);
  if (ceilingRepaint) ceilingRepaint.addEventListener("change", updatePreview);
  if (baseboards) baseboards.addEventListener("change", updatePreview);
  if (crown) crown.addEventListener("change", updatePreview);
  if (epoxyType) epoxyType.addEventListener("change", updatePreview);
});

const ceiling = document.querySelector('[name="paint_ceiling"]');

if (ceiling) {
  ceiling.addEventListener("change", () => {
    if (ceiling.value === "yes") {
      preview.src = "/static/images/previews/interior_ceiling.jpg";
    }
  });
}
