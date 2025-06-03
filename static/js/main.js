document.addEventListener("DOMContentLoaded", function () {
  // Quantity controls (fixed to prevent error)
  const quantityInput = document.getElementById("quantity");
  const increaseBtn = document.getElementById("increase-quantity");
  const decreaseBtn = document.getElementById("decrease-quantity");

  if (quantityInput && increaseBtn && decreaseBtn) {
    const quantityControls = document.querySelector(".quantity-controls");
    if (quantityControls) {
      // Event delegation for quantity controls
      quantityControls.addEventListener("click", function (e) {
        const btn = e.target.closest("#increase-quantity, #decrease-quantity");
        if (!btn) return;

        let currentVal = parseInt(quantityInput.value) || 1;
        const maxVal = parseInt(quantityInput.getAttribute("max")) || 10;
        const minVal = parseInt(quantityInput.getAttribute("min")) || 1;

        if (btn.id === "increase-quantity" && currentVal < maxVal) {
          quantityInput.value = currentVal + 1;
        } else if (btn.id === "decrease-quantity" && currentVal > minVal) {
          quantityInput.value = currentVal - 1;
        }
      });

      quantityInput.addEventListener("change", function () {
        let currentVal = parseInt(quantityInput.value) || 1;
        const minVal = parseInt(quantityInput.getAttribute("min")) || 1;
        const maxVal = parseInt(quantityInput.getAttribute("max")) || 10;

        if (currentVal < minVal) {
          quantityInput.value = minVal;
        } else if (currentVal > maxVal) {
          quantityInput.value = maxVal;
        }
      });
    }
  } else {
    console.log(
      "Quantity controls not present on this page, skipping initialization."
    );
  }

  // Add to cart button
  const addToCartBtn = document.querySelector(".add-to-cart-btn");
  if (addToCartBtn) {
    addToCartBtn.addEventListener("click", async function (e) {
      e.preventDefault();
      const selectedSize = document.querySelector('input[name="size"]:checked');
      if (!selectedSize) {
        showAlert("Будь ласка, оберіть розмір", "danger");
        return;
      }

      const productId = this.getAttribute("data-product-id");
      const stock = await getStock(productId, selectedSize.value);
      const quantity = parseInt(quantityInput?.value) || 1;

      if (quantity > stock) {
        showAlert(`Недостатньо товару на складі. Доступно: ${stock}`, "danger");
        return;
      }

      showAlert("Товар додано до кошика!", "success");
      animateCartIcon();
      // Add actual cart logic here (e.g., AJAX call)
    });

    addToCartBtn.addEventListener("keydown", function (e) {
      if (e.key === "Enter" || e.key === " ") {
        e.preventDefault();
        this.click();
      }
    });
  }

  // Buy now button
  const buyNowBtn = document.getElementById("buy-now");
  if (buyNowBtn) {
    buyNowBtn.addEventListener("click", function (e) {
      e.preventDefault();
      const selectedSize = document.querySelector('input[name="size"]:checked');
      const cartErrorAlert = document.getElementById("cart-error");
      if (cartErrorAlert) cartErrorAlert.classList.add("d-none");
      if (!selectedSize) {
        if (cartErrorAlert) {
          cartErrorAlert.textContent = "Будь ласка, оберіть розмір";
          cartErrorAlert.classList.remove("d-none");
        } else {
          showAlert("Будь ласка, оберіть розмір", "danger");
        }
        return;
      }
      window.location.href = "/checkout/";
    });

    buyNowBtn.addEventListener("keydown", function (e) {
      if (e.key === "Enter" || e.key === " ") {
        e.preventDefault();
        this.click();
      }
    });
  }

  // Product image gallery
  const productThumbnails = document.querySelectorAll(".product-thumbnail");
  if (productThumbnails.length > 0) {
    const mainImage = document.querySelector(".product-detail-img");
    productThumbnails.forEach((thumbnail) => {
      thumbnail.addEventListener("click", function () {
        mainImage.src = this.getAttribute("data-image");
        productThumbnails.forEach((item) => item.classList.remove("active"));
        this.classList.add("active");
      });
    });
  }

  // Prevent button clicks from triggering card click
  const buttons = document.querySelectorAll(".stop-propagation");
  buttons.forEach((button) => {
    button.addEventListener("click", function (event) {
      event.stopPropagation();
    });
  });
  // Card click navigation
  const clickableCards = document.querySelectorAll(".clickable-card");
  clickableCards.forEach((card) => {
    card.addEventListener("click", function (event) {
      // Prevent navigation if clicking on the button
      if (event.target.closest(".stop-propagation")) return;

      const url = this.getAttribute("data-url");
      if (url) {
        window.location.href = url;
      }
    });
  });
  // Banner carousel auto-slide
  const slides = document.querySelectorAll(".banner-slide");
  const slideContainer = document.querySelector(".banner-slides");
  let currentSlide = 0;

  if (slideContainer && slides.length > 0) {
    const firstClone = slides[0].cloneNode(true);
    slideContainer.appendChild(firstClone);

    const totalSlides = slides.length + 1;

    slideContainer.style.width = `${totalSlides * 100}%`;
    slideContainer.querySelectorAll(".banner-slide").forEach((slide) => {
      slide.style.flex = `0 0 ${100 / totalSlides}%`;
    });

    function showSlide(index) {
      currentSlide = index;
      const offset = -currentSlide * (100 / totalSlides);
      slideContainer.style.transition =
        "transform 0.7s cubic-bezier(0.4,0,0.2,1)";
      slideContainer.style.transform = `translateX(${offset}%)`;

      slideContainer.querySelectorAll(".banner-slide").forEach((slide, i) => {
        slide.classList.toggle("active", i === currentSlide);
      });
    }

    slideContainer.addEventListener("transitionend", function () {
      if (currentSlide === totalSlides - 1) {
        slideContainer.style.transition = "none";
        currentSlide = 0;
        const offset = -currentSlide * (100 / totalSlides);
        slideContainer.style.transform = `translateX(${offset}%)`;
        slideContainer.querySelectorAll(".banner-slide").forEach((slide, i) => {
          slide.classList.toggle("active", i === currentSlide);
        });
      }
    });

    function nextSlide() {
      showSlide(currentSlide + 1);
    }

    setInterval(nextSlide, 10000);
    showSlide(currentSlide);
  }

  // Helper function to show alerts
  function showAlert(message, type) {
    const alertDiv = document.createElement("div");
    alertDiv.className = `alert alert-${type} alert-dismissible fade show position-fixed top-0 start-50 translate-middle-x mt-4`;
    alertDiv.setAttribute("role", "alert");
    alertDiv.setAttribute("aria-live", "polite");
    alertDiv.style.zIndex = "1050";
    alertDiv.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        `;
    document.body.appendChild(alertDiv);
    setTimeout(() => {
      alertDiv.classList.remove("show");
      setTimeout(() => alertDiv.remove(), 150);
    }, 3000);
  }

  // Animation for cart icon
  function animateCartIcon() {
    const cartIcon = document.querySelector(".add-to-cart-btn i");
    if (cartIcon) {
      cartIcon.classList.add("fa-bounce");
      setTimeout(() => {
        cartIcon.classList.remove("fa-bounce");
      }, 1000);
    }
  }

  // Stock check (mock function)
  async function getStock(productId, sizeValue) {
    // Replace with actual API call
    return 10; // Mock stock
  }

  // Enable all tooltips
  const tooltipTriggerList = [].slice.call(
    document.querySelectorAll('[data-bs-toggle="tooltip"]')
  );
  tooltipTriggerList.map(function (tooltipTriggerEl) {
    return new bootstrap.Tooltip(tooltipTriggerEl);
  });

  // Product Slider
  const productSlides = document.getElementById("product-slides");
  let currentProductSlide = 0;
  let startX = 0;
  let isDragging = false;
  let startTranslateX = 0;
  let lastTranslateX = 0;
  let velocity = 0;
  let lastTime = 0;
  let lastX = 0;

  if (productSlides) {
    function getSliderBounds() {
      const slideWidth =
        productSlides.querySelector(".col-md-3")?.offsetWidth || 0;
      const totalSlides = productSlides.children.length;
      const containerWidth = productSlides.parentElement.offsetWidth;
      const maxVisibleSlides = Math.floor(containerWidth / slideWidth);
      const maxSlideIndex = Math.max(0, totalSlides - maxVisibleSlides);
      return { slideWidth, maxSlideIndex };
    }

    function updateProductSlider(translateX, withTransition = true) {
      const { slideWidth, maxSlideIndex } = getSliderBounds();
      // Clamp translateX to prevent over-scrolling
      const maxTranslate = 0;
      const minTranslate = -maxSlideIndex * slideWidth;
      translateX = Math.min(maxTranslate, Math.max(minTranslate, translateX));

      productSlides.style.transition = withTransition
        ? "transform 0.3s ease"
        : "none";
      productSlides.style.transform = `translateX(${translateX}px)`;
      lastTranslateX = translateX;

      // Update current slide based on position
      currentProductSlide = Math.round(Math.abs(translateX) / slideWidth);
      currentProductSlide = Math.min(
        maxSlideIndex,
        Math.max(0, currentProductSlide)
      );
    }

    // Touch and Mouse Drag Functionality
    productSlides.addEventListener("touchstart", (e) => {
      startX = e.touches[0].clientX;
      lastX = startX;
      startTranslateX = lastTranslateX;
      isDragging = true;
      productSlides.style.transition = "none";
      lastTime = Date.now();
      velocity = 0;
    });

    productSlides.addEventListener("touchmove", (e) => {
      if (!isDragging) return;
      const currentX = e.touches[0].clientX;
      const diffX = currentX - startX;
      const translateX = startTranslateX + diffX;

      // Calculate velocity for momentum
      const currentTime = Date.now();
      const timeDelta = currentTime - lastTime;
      if (timeDelta > 0) {
        const distance = currentX - lastX;
        velocity = distance / timeDelta;
      }
      lastX = currentX;
      lastTime = currentTime;

      updateProductSlider(translateX, false);
    });

    productSlides.addEventListener("touchend", (e) => {
      if (!isDragging) return;
      isDragging = false;
      const { slideWidth, maxSlideIndex } = getSliderBounds();
      const endX = e.changedTouches[0].clientX;
      const diffX = endX - startX;

      // Apply momentum
      let targetTranslate = lastTranslateX + velocity * 100; // Adjust momentum factor
      targetTranslate = Math.min(
        0,
        Math.max(-maxSlideIndex * slideWidth, targetTranslate)
      );

      // Snap to nearest slide
      const nearestSlide = Math.round(Math.abs(targetTranslate) / slideWidth);
      const finalTranslate = -nearestSlide * slideWidth;

      updateProductSlider(finalTranslate);
    });

    // Mouse drag functionality
    productSlides.addEventListener("mousedown", (e) => {
      startX = e.clientX;
      lastX = startX;
      startTranslateX = lastTranslateX;
      isDragging = true;
      productSlides.style.transition = "none";
      productSlides.style.cursor = "grabbing";
      lastTime = Date.now();
      velocity = 0;
    });

    productSlides.addEventListener("mousemove", (e) => {
      if (!isDragging) return;
      const currentX = e.clientX;
      const diffX = currentX - startX;
      const translateX = startTranslateX + diffX;

      // Calculate velocity for momentum
      const currentTime = Date.now();
      const timeDelta = currentTime - lastTime;
      if (timeDelta > 0) {
        const distance = currentX - lastX;
        velocity = distance / timeDelta;
      }
      lastX = currentX;
      lastTime = currentTime;

      updateProductSlider(translateX, false);
    });

    productSlides.addEventListener("mouseup", () => {
      if (!isDragging) return;
      isDragging = false;
      const { slideWidth, maxSlideIndex } = getSliderBounds();

      // Apply momentum
      let targetTranslate = lastTranslateX + velocity * 100; // Adjust momentum factor
      targetTranslate = Math.min(
        0,
        Math.max(-maxSlideIndex * slideWidth, targetTranslate)
      );

      // Snap to nearest slide
      const nearestSlide = Math.round(Math.abs(targetTranslate) / slideWidth);
      const finalTranslate = -nearestSlide * slideWidth;

      productSlides.style.cursor = "grab";
      updateProductSlider(finalTranslate);
    });

    // Prevent drag on mouseout if not released
    productSlides.addEventListener("mouseout", () => {
      if (isDragging) {
        isDragging = false;
        const { slideWidth, maxSlideIndex } = getSliderBounds();

        // Apply momentum
        let targetTranslate = lastTranslateX + velocity * 100;
        targetTranslate = Math.min(
          0,
          Math.max(-maxSlideIndex * slideWidth, targetTranslate)
        );

        // Snap to nearest slide
        const nearestSlide = Math.round(Math.abs(targetTranslate) / slideWidth);
        const finalTranslate = -nearestSlide * slideWidth;

        productSlides.style.cursor = "grab";
        updateProductSlider(finalTranslate);
      }
    });

    // Update slider on resize
    window.addEventListener("resize", () => {
      updateProductSlider(lastTranslateX);
    });

    // Initial update
    updateProductSlider(0);
  }

  // Video Player Functionality
  const videoIframe = document.getElementById("video-player-iframe");
  const videoButtons = document.querySelectorAll(".video-switch-btn");

  if (videoIframe && videoButtons.length > 0) {
    videoButtons.forEach((button, index) => {
      button.addEventListener("click", function () {
        const src = this.getAttribute("data-src");
        console.log(`Switching to video ${index + 1}, src: ${src}`);
        videoIframe.src = src; // Update iframe src
        // Update active button
        videoButtons.forEach((btn) => btn.classList.remove("active"));
        this.classList.add("active");
      });
    });
  } else {
    console.error("Video player elements not found:", {
      videoIframe: !!videoIframe,
      videoButtons: videoButtons.length,
    });
  }
});

// Custom filter for splitting strings in templates
if (typeof django !== "undefined" && django.templatetags) {
  django.templatetags.add("split", function (value, arg) {
    return value.split(arg);
  });
}
