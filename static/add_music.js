const albom = document.querySelector(".albom")
const genre = document.querySelector(".genre")
const artist = document.querySelector(".artist")
const bosh = document.querySelector(".bosh")
const genre_add = document.querySelector(".genre_add")
const file_add = document.querySelector(".file_add")
const artist_add = document.querySelector(".artist_add")
const add = document.querySelector(".addd")
const add_f = document.querySelector(".adds")
const ark_add = document.querySelector(".ark_add")

const je = document.querySelectorAll(".genres")
const ge = document.querySelector(".Genres")
const alb_name = document.querySelectorAll(".files")
const alb_input = document.querySelector(".alboms")
const art_name = document.querySelectorAll(".artists")
const art_input = document.querySelector(".artist7")
add.addEventListener("click", () => {
    genre_add.classList.toggle("flask")
})
add_f.addEventListener("click", () => {
    file_add.classList.toggle("flask")
})
ark_add.addEventListener("click", () => {
    artist_add.classList.toggle("flask")
})

let artists = []
fetch('/get_artists')
    .then(function (musicc) {
        return musicc.json()
    })
    .then(function (jsonResponse) {
        artists.push(jsonResponse)


    })
console.log(artists)
let genres = []

je.forEach((gen, id) => {
    gen.addEventListener("click", () => {
        ge.value += gen.innerHTML
    })
})
alb_name.forEach(albo => {
    albo.addEventListener("click", () => {
        alb_input.value += albo.innerHTML
    })
})
art_name.forEach(art => {
    art.addEventListener("click", () => {
        art_input.value += art.innerHTML
    })
})


let input = 0;

function chang() {
    bosh.style.transform = `translateX(${input * -500}px)`
}

let int = 0;

function chan() {
    bosh.style.transform = `translateX(${int * -1000}px)`
}

albom.addEventListener("click", () => {
    input = 1
    chang()
})
genre.addEventListener("click", () => {
    input = 0
    chang()
})
artist.addEventListener("click", () => {
    int = 1
    chan()
})