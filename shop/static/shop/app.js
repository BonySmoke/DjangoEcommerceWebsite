catalog = "Catalog";
document.querySelector('#catalog-0').innerHTML = '<em>' + catalog + '</em>';
main()

function main(){
    const text = document.querySelector(".aboutUs");
    const strText = text.textContent;
    const letter = strText.split("");
    text.textContent = " ";
    for(let i=0; i < letter.length; i++){
        text.innerHTML += "<span>" + letter[i] + "</span>";
    }
    let charAnimation = 0;
    let timer = setInterval(onTick, 70);


    function onTick(){
        const span = text.querySelectorAll("span")[charAnimation];
        span.classList.add("waterBlue");
        charAnimation++;
        if(charAnimation === letter.length){
            breakTimer();
            return;
        }
    }

    function breakTimer(){
        clearInterval(timer);
        timer = null;
    }
}

function toggle_visibility(){
    var filterBtn = document.getElementById("FilterBtn");
    var x = document.getElementById("SearchFilter");
    if (x.style.display === "none") {
        filterBtn.innerHTML = "Hide Filters";
        x.style.display = "block";
    } else {
        filterBtn.innerHTML = "Show Filters";
        x.style.display = "none";
    }
}
