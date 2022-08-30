let dbg_pressed = document.querySelector("#key_pressed_dbg");
let name = "";
document.onkeydown = function(e) {
    switch (e.keyCode) {
        case 37:
            name = "left";
            break;
        case 38:
            name = "forward";
            break;
        case 39:
            name = "right";
            break;
        case 40:
            name = "backward";
            break;
    }
    dbg_pressed.innerHTML = name;
};