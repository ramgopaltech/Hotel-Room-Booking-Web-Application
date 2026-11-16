/**
 * GRAND ROYALE LUXURY HOTEL - BOOKING INTERACTIVITY & PRICE CALCULATOR
 */

document.addEventListener('DOMContentLoaded', () => {
  initBookingPriceCalculator();
  initRoomGalleryModal();
});

function initBookingPriceCalculator() {
  const checkInInput = document.getElementById('check_in');
  const checkOutInput = document.getElementById('check_out');
  const roomIdInput = document.getElementById('room_id');
  const pricePerNightEl = document.getElementById('price_per_night');
  const nightsCountEl = document.getElementById('nights_count');
  const totalPriceEl = document.getElementById('total_price_display');
  const availabilityBadge = document.getElementById('availability_badge');
  const submitBtn = document.getElementById('book_submit_btn');

  if (!checkInInput || !checkOutInput || !roomIdInput) return;

  function calculateAndVerify() {
    const checkIn = checkInInput.value;
    const checkOut = checkOutInput.value;
    const roomId = roomIdInput.value;

    if (!checkIn || !checkOut) return;

    const startDate = new Date(checkIn);
    const endDate = new Date(checkOut);
    const timeDiff = endDate.getTime() - startDate.getTime();
    const nights = Math.ceil(timeDiff / (1000 * 3600 * 24));

    if (nights <= 0) {
      if (nightsCountEl) nightsCountEl.textContent = '0';
      if (totalPriceEl) totalPriceEl.textContent = '$0.00';
      if (availabilityBadge) {
        availabilityBadge.className = 'badge badge-danger';
        availabilityBadge.textContent = 'Check-out must be after Check-in';
      }
      if (submitBtn) submitBtn.disabled = true;
      return;
    }

    if (nightsCountEl) nightsCountEl.textContent = nights;

    // Fetch availability and price via backend API
    fetch('/api/check-availability', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        room_id: roomId,
        check_in: checkIn,
        check_out: checkOut
      })
    })
    .then(res => res.json())
    .then(data => {
      if (data.success) {
        if (totalPriceEl) {
          totalPriceEl.textContent = `$${data.total_price.toLocaleString('en-US', { minimumFractionDigits: 2 })}`;
        }
        if (availabilityBadge) {
          if (data.available) {
            availabilityBadge.className = 'badge badge-success';
            availabilityBadge.textContent = 'Available for selected dates';
            if (submitBtn) submitBtn.disabled = false;
          } else {
            availabilityBadge.className = 'badge badge-danger';
            availabilityBadge.textContent = 'Room already booked for these dates';
            if (submitBtn) submitBtn.disabled = true;
          }
        }
      }
    })
    .catch(err => console.error('Error verifying availability:', err));
  }

  checkInInput.addEventListener('change', calculateAndVerify);
  checkOutInput.addEventListener('change', calculateAndVerify);

  // Initial run if default values are set
  if (checkInInput.value && checkOutInput.value) {
    calculateAndVerify();
  }
}

// Lightbox for Room Gallery
function initRoomGalleryModal() {
  const mainImage = document.getElementById('main_room_image');
  const thumbnails = document.querySelectorAll('.gallery-thumb');

  if (mainImage && thumbnails.length > 0) {
    thumbnails.forEach(thumb => {
      thumb.addEventListener('click', () => {
        thumbnails.forEach(t => t.classList.remove('active'));
        thumb.classList.add('active');
        mainImage.src = thumb.src;
      });
    });
  }
}
