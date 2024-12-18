document.addEventListener('DOMContentLoaded', function () {
  const burgerMenu = document.querySelector('.burger-menu')
  const navMenu = document.querySelector('.nav-menu')

  burgerMenu.addEventListener('click', function () {
    this.classList.toggle('active')
    navMenu.classList.toggle('active')
  })
})
