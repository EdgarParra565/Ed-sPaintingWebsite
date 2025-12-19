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

  // Epoxy option (FIXED NAME)
  const epoxyType = document.querySelector('[name="floor_type"]');

  if (!service || !preview || !paintingFields || !epoxyFields) return;

  function updatePreview() {
    /* ======================
       PAINTING MODE
    ======================= */
    if (service.value === "painting") {
      paintingFields.style.display = "block";
      epoxyFields.style.display = "none";

      let imageName = "interior_livingroom";

      // Walls
      if (fullRepaint?.value === "yes") {
        imageName = "interior_full_repaint";
      } else {
        imageName = "interior_refresh";
      }

      // Ceiling
      if (paintCeiling?.value === "yes") {
        imageName += ceilingRepaint?.value === "yes"
          ? "_ceiling_repaint"
          : "_ceiling_fresh";
      }

      // Trim
      if (baseboards?.value === "yes") imageName += "_baseboards";
      if (crown?.value === "yes") imageName += "_crown";

      preview.src = `/static/images/previews/${imageName}.jpg`;
    }

    /* ======================
       EPOXY MODE
    ======================= */
    else if (service.value === "epoxy") {
      paintingFields.style.display = "none";
      epoxyFields.style.display = "block";

      let epoxyImage = "epoxy_solid";

      if (epoxyType?.value === "chip") {
        epoxyImage = "epoxy_chip";
      } else if (epoxyType?.value === "metallic") {
        epoxyImage = "epoxy_metallic";
      }

      preview.src = `/static/images/previews/${epoxyImage}.jpg`;
    }
  }

  /* ======================
     EVENT LISTENERS
  ======================= */
  service.addEventListener("change", updatePreview);
  fullRepaint?.addEventListener("change", updatePreview);
  paintCeiling?.addEventListener("change", updatePreview);
  ceilingRepaint?.addEventListener("change", updatePreview);
  baseboards?.addEventListener("change", updatePreview);
  crown?.addEventListener("change", updatePreview);
  epoxyType?.addEventListener("change", updatePreview);

  // Run once on page load (important after POST)
  updatePreview();
});
