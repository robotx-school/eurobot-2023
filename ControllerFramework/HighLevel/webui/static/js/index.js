

function updateConfig(){

}
window.onload = function(e){ 
    let side_selector = document.getElementById("side_selector");
    let colors = {0: "#651a96", 1: "#bfb119"}
    side_selector.style.color = colors[side_selector.value];
    side_selector.onchange = function(){
        side_selector.style.color = colors[side_selector.value];
    };
}