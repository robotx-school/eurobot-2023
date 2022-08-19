const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]')
const tooltipList = [...tooltipTriggerList].map(tooltipTriggerEl => new bootstrap.Tooltip(tooltipTriggerEl))

function sendForm(api_endpoint, formData){
    // Send form data via post using modern fetchApi
    return fetch(api_endpoint, { 
        method: 'POST',
        body: formData
      })
      .then((response) => response.json())
      .then((responseData) => {
        return responseData;
      })
      .catch (error => console.warn(error));
}

function getReqApi(api_endpoint){
    return fetch(api_endpoint)
    .then(data => {
        return data.json();
    })

}


function statusAlert(type, title, text){
    Swal.fire({
        icon: type,
        title: title,
        text: text,
      });
}

function startRouteExecution(){
    getReqApi("/api/start_route").then(function(resp){
        if (resp["status"]){
            
        }
    })
}


function updateConfig(){
    var form = document.querySelector("#config_form");
    var api_endpoint = form.getAttribute("action");
    var formData = new FormData(form);
    sendForm(api_endpoint, formData).then(function(resp){
        if (resp["status"]){
            statusAlert("success", "Success", "Config updated successfully");
        }else{
            statusAlert("error", "Error", resp["text"]);
        }
    });
}
window.onload = function(e){ 
    let side_selector = document.getElementById("side_selector");
    let colors = {0: "#651a96", 1: "#bfb119"}
    side_selector.style.color = colors[side_selector.value];
    side_selector.onchange = function(){
        side_selector.style.color = colors[side_selector.value];
    };
    
}
document.querySelector("#config_form").onsubmit = async(e) => {
    e.preventDefault();
    updateConfig();
};