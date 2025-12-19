document.addEventListener("DOMContentLoaded", function () {
  const service = document.getElementById("service_type");
  const area = document.getElementById("area_type");
  const preview = document.getElementById("previewImage");

  if (!service || !area || !preview) return;

  function updatePreview() {
    if (service.value === "epoxy") {
      preview.src = "/static/images/previews/epoxy_garage.jpg";
    } else if (area.value === "exterior") {
      preview.src = "/static/images/previews/exterior_house.jpg";
    } else {
      preview.src = "/static/images/previews/interior_livingroom.jpg";
    }
  }

  service.addEventListener("change", updatePreview);
  area.addEventListener("change", updatePreview);
});
