const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]')
const tooltipList = [...tooltipTriggerList].map(tooltipTriggerEl => new bootstrap.Tooltip(tooltipTriggerEl))



function startRouteExecution(){
    getReqApi("/api/start_route").then(function(resp){
        if (resp["status"]){
            notifyAlert("success", "Route execution started")
        }
    })
}

function poll_robot_info(){
    getReqApi("/api/poll_robot_status").then(function(resp){
        if (resp["status"]){
            var dot;
            //var dot_text;
            switch(resp["execution_status"]){
                case 0:
                    dot = "dot_green";
                    //dot_text = "Robot is waiting for start";
                    break;
                case 1:
                    dot = "dot_green";
                    //dot_text = "Robot is waiting for start";
                    break;
                case 2:
                    dot = "dot_yellow";
                    //dot_text = "Robot is executing route now";
                    break;
                case 3:
                    dot = "dot_red";
                    //dot_text = "Robot was emergency stopped";
                    break;
            }
            document.querySelector("#execution_dot").className = "";
            document.querySelector("#execution_dot").classList.add(dot);
            document.querySelector("#session_steps_done").innerHTML = `Steps done: ${resp["steps_done"]}`;
            document.querySelector("#session_steps_left").innerHTML = `Steps left: ${resp["steps_left"]}`;
            document.querySelector("#session_distance_drived").innerHTML = `Distance drived: ${resp["distance_drived"]}`;
            document.querySelector("#session_motors_time").innerHTML = `Motors time: ${resp["motors_time"]}`;
            document.querySelector("#session_routing_time").innerHTML = `All time: ${resp["route_time"]}`;
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

function emergencyStop(){
    getReqApi("/api/emergency_stop");
}

function openDevTab(){
    window.open("/api/dev/tmgr","_blank");
} 

function displayRouteJson(){
    getReqApi("/api/get_route_json").then(function(resp){
        if (resp["status"]){
            console.log(resp);
            document.getElementById("route_json_place").innerHTML = prettyPrintJson.toHtml(resp["data"]);            ;
        }
    })
}

// Bindings

window.onload = function(e){ 
    let side_selector = document.getElementById("side_selector");
    let colors = {0: "#651a96", 1: "#bfb119"}
    side_selector.style.color = colors[side_selector.value];
    side_selector.onchange = function(){
        side_selector.style.color = colors[side_selector.value];
    };
    // Poll robot info
    const interval = setInterval(poll_robot_info, document.querySelector("#page-data").dataset.pollingInterval);
     
}
document.querySelector("#config_form").onsubmit = async(e) => {
    e.preventDefault();
    updateConfig();
};

var myModal = document.getElementById('routeJson')

myModal.addEventListener('show.bs.modal', function (event) {
    console.log("Load json route");
    displayRouteJson();
})


