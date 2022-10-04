function sendForm(api_endpoint, formData) {
  // Send form data via post using modern fetchApi
  return fetch(api_endpoint, {
    method: 'POST',
    body: formData
  })
    .then((response) => response.json())
    .then((responseData) => {
      return responseData;
    })
    .catch(error => console.warn(error));
}

function getReqApi(api_endpoint) {
  return fetch(api_endpoint)
    .then(data => {
      return data.json();
    })
}

// Binding

document.getElementById("update_coords_form").addEventListener('submit', function (e) {
  e.preventDefault();
  let api_endpoint = this.getAttribute("action");
  var formData = new FormData(document.getElementById("update_coords_form"));
  sendForm(api_endpoint, formData).then(function (resp) {
    console.log(resp);
  });
});

