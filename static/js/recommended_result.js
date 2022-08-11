let slideIndex = 0;
let slideTimer;
const slideDelay = 10;
const slides = document.getElementsByClassName("slide");
const pills = document.getElementsByClassName("pill");
const bar = document.getElementsByClassName("progress");

ShowSlide = (index) => {
  if (index == slides.length) slideIndex = 0;
  else if (index < 0) slideIndex = slides.length - 1;
  else slideIndex = index;

  for (i = 0; i < slides.length; i++) {
    slides[i].style.display = "none";
    pills[i].classList.remove("active");
  }

  SlideReset();
  slides[slideIndex].style.display = "block";
  pills[slideIndex].classList.add("active");
};

SlideReset = () => {
  window.clearInterval(slideTimer);

  bar[0].style.animation = null;
};

for (i = 0; i < pills.length; i++) {
  pills[i].addEventListener("click", function () {
    let si = this.getAttribute("data-index");
    ShowSlide(Number(si));
  });
}

neg.addEventListener("click", function () {
  ShowSlide((slideIndex -= 1));
});
pos.addEventListener("click", function () {
  ShowSlide((slideIndex += 1));
});

ShowSlide(slideIndex);
