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

function notifyAlert(type, title){
    Swal.fire({
        position: 'top-end',
        icon: type,
        title: title,
        showConfirmButton: false,
        timer: 1500
      })
}