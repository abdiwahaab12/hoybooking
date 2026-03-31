document.addEventListener("DOMContentLoaded", () => {
  // Simple client-side date guard to improve UX.
  const checkIn = document.querySelector("input[name='check_in_date']");
  const checkOut = document.querySelector("input[name='check_out_date']");
  if (!checkIn || !checkOut) return;

  const validate = () => {
    if (!checkIn.value || !checkOut.value) return;
    if (checkOut.value <= checkIn.value) {
      alert("Check-out date must be after check-in date.");
      checkOut.focus();
    }
  };

  checkIn.addEventListener("change", validate);
  checkOut.addEventListener("change", validate);
});

