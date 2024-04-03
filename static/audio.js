const playConst = document.querySelectorAll(".play")
const audio = document.querySelectorAll(".audio")

const music = document.querySelector(".prog")
const progress2 = document.querySelector(".prog")
const pro = document.querySelector(".progress")
const img_5 = document.querySelector(".img5")
const name = document.querySelector(".names1")
const artist = document.querySelector(".music_name1")

const music_text = document.querySelectorAll(".music_text")
const music_artist = document.querySelectorAll(".music_name")
const img = document.querySelectorAll(".music_img")

const prev = document.querySelector(".prev")
const next = document.querySelector(".next")
const button = document.querySelector(".button")
const pros = document.querySelectorAll(".progress1")
const progress = document.querySelectorAll(".pros12")
const like = document.querySelector(".like")
let a = document.querySelector(".au")
let ic = document.querySelectorAll(".download")
let music_id = 0;
playConst.forEach((play, index) => {
    play.addEventListener("click", () => {
        music_id = index;
        if (audio[index].paused) {
            audio.forEach(item => {
                item.pause()
            })
            audio[index].play()
            button.classList.toggle("button_pause")
            name.innerText = music_text[index].innerText
            artist.innerHTML = music_artist[index].innerHTML
            img_5.src = img[index].src
            play.classList.remove("pause")
            playConst.forEach((playSmall, index_small) => {
                if (index !== index_small) {
                    playSmall.classList.add("pause")
                }
            })
            audio.forEach((item, id) => {
                if (index !== id) {
                    item.currentTime = 0
                }
            })
            like_reds()
            a.href = `/download/${ic[music_id].dataset.id}`
        } else {
            audio[index].pause()
            button.classList.remove("button_pause")
            play.classList.toggle("pause")
        }

    })
})

function next_muc() {
    playConst[music_id].classList.remove("pause")
    playConst[music_id].classList.toggle("pause")
    button.classList.remove("button_pause")
    if (audio[music_id].paused) {
        audio.forEach(item => {
            item.pause()
        })
        audio[music_id].play()
        playConst[music_id].classList.toggle("pause")
        playConst.forEach((playSmall, index_small) => {
            if (music_id !== index_small) {
                playSmall.classList.add("pause")
            }
        })
        audio.forEach((item, id) => {
            if (music_id !== id) {
                item.currentTime = 0
            }
        })
    } else {
        audio[music_id].pause()
        playConst[music_id].classList.remove("pause")
    }
    button.classList.toggle("button_pause")
    img_5.src = img[music_id].src
    name.innerText = music_text[music_id].innerText;
    artist.innerHTML = music_artist[music_id].innerHTML
    like_reds()
    a.href = `download/${ic[music_id].dataset.id}`
}

button.addEventListener("click", () => {
    if (audio[music_id].paused) {
        audio[music_id].play()
        img_5.src = img[music_id].src
        name.innerText = music_text[music_id].innerText;
        artist.innerHTML = music_artist[music_id].innerHTML
        button.classList.toggle("button_pause")
        playConst[music_id].classList.remove("pause")
    } else {
        audio[music_id].pause()
        button.classList.remove("button_pause")
        playConst[music_id].classList.toggle("pause")
    }
    like_reds()
})
next.addEventListener("click", () => {
    music_id++
    update()
    next_muc()
    like_reds()
    a.href = `download/${ic[music_id].dataset.id}`

})
prev.addEventListener("click", () => {
    music_id--
    update()
    next_muc()
    like_reds()
    a.href = `download/${ic[music_id].dataset.id}`
})

function update() {
    if (music_id > audio.length - 1) {
        music_id = 0

    } else if (music_id < 0) {
        music_id = audio.length - 1

    }
}


audio.forEach((aud, index) => {
    aud.addEventListener("timeupdate", (e) => {
        let {duration, currentTime} = e.srcElement
        let music = (currentTime / duration) * 100
        pros[index].style.width = `${music}%`
        pro.style.width = `${music}%`
        if (aud.ended) {
            music_id++
            update()
            if (audio[music_id].paused) {
                audio[music_id].play()
                playConst[music_id].classList.remove("pause")
                playConst.forEach((playSmall, index_small) => {
                    if (music_id !== index_small) {
                        playSmall.classList.add("pause")
                    }
                })
                audio.forEach((item, id) => {
                    if (music_id !== id) {
                        item.currentTime = 0
                    }
                })
            } else {
                audio[music_id].pause()
                playConst[music_id].classList.remove("pause")
            }
            playConst[music_id].classList.remove("pause")
            img_5.src = img[music_id].src
            name.innerText = music_text[music_id].innerText;
            artist.innerHTML = music_artist[music_id].innerHTML
            like_reds()
            a.href = `download/${ic[music_id].dataset.id}`
        }

    })
})
progress.forEach((pro, id) => {
    pro.addEventListener("click", (event) => {
        let width = pro.clientWidth
        let clicked = event.offsetX
        let duration = audio[id].duration
        audio[id].currentTime = (clicked / width) * duration
    })
})
progress2.addEventListener("click", (event) => {
    let width = progress2.clientWidth
    let clicked = event.offsetX
    let duration = audio[music_id].duration
    audio[music_id].currentTime = (clicked / width) * duration
})


let likIcons = document.querySelectorAll('.likeIcon');
like.addEventListener("click", () => {
    like_reds()
    let listClass = [likIcons[music_id].classList[0], likIcons[music_id].classList[1], likIcons[music_id].classList[2]]
    console.log(listClass)
    if (listClass.includes("like_red")) {
        like.classList.remove("like_red")
        likIcons[music_id].classList.remove("like_red")
        likIcons[music_id].classList.add("like_w")
        like.classList.add("like_w")
    } else {
        like.classList.remove("like_w")
        likIcons[music_id].classList.remove("like_w")
        like.classList.add("like_red")
        likIcons[music_id].classList.add("like_red")
    }
    fetch("/get_like", {
        method: "POST", headers: {
            "Content-Type": "application/json"
        }, body: JSON.stringify({
            "music_id": likIcons[music_id].dataset.id,
        })
    })
        .then(response => response.json())
        .then(dateJson => {
        })
})

function like_reds() {
    like.className = likIcons[music_id].className
}


