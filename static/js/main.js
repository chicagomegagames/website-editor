document.addEventListener("DOMContentLoaded", function(evt) {
  var edit_form = document.querySelector("#edit");
  if (edit_form) {
    load_model_form(edit_form);
  }

  var delete_links = document.querySelectorAll("a[data-method=delete]");
  delete_links.forEach(function(link) {
    setup_delete_link(link);
  });
});

function setup_delete_link(link) {
  var path = link.getAttribute("href");
  var form = document.createElement("form");
  form.setAttribute("method", "POST");
  form.setAttribute("action", path);

  var method_field = document.createElement("input");
  method_field.setAttribute("type", "hidden");
  method_field.setAttribute("name", "_method");
  method_field.setAttribute("value", "DELETE");

  form.appendChild(method_field);
  document.body.appendChild(form);

  link.addEventListener("click", function(evt) {
    evt.preventDefault();

    if (confirm("Actually delete file?")) {
      form.submit();
    }
  });
}

function page_alert(message) {
  var notifications = document.querySelector("#notifications");
  var notification = document.createElement("div");
  notification.setAttribute("class", "notification");

  var textElement = document.createElement("p");
  textElement.appendChild(document.createTextNode(message));
  notification.appendChild(textElement);
  notification.style.height = 0;

  notifications.appendChild(notification);
  height = textElement.offsetHeight;
  notification.style.height = height;

  window.setTimeout(function() {
    notification.style.height = 0;
    window.setTimeout(function() {
      notification.remove();
    }, 2000);
  }, 5000);

}

function load_model_form(form) {
  form.addEventListener("submit", function(e) {
    e.preventDefault();

    var model = new FormData()
    model.set("markdown", form.querySelector("textarea[name=content]").value);
    var filename_input = form.querySelector("input[name=filename]");
    if (filename_input) {
      model.set("filename", filename_input.value)
    }

    required_meta_inputs = [...form.querySelectorAll("input[name^=meta]")]
    required_meta_inputs.forEach(function(element) {
      var key = element.getAttribute("data-metadata-name");
      var value = element.value;

      //model.metadata[key] = value;
      model.set(`metadata[${key}]`, value)
    })


    var xhr = new XMLHttpRequest()
    xhr.addEventListener("load", function(evt) {
      if (xhr.responseURL !== document.location.href) {
        window.location = xhr.responseURL;
      }

      console.log(xhr.response);
      var response = JSON.parse(xhr.response);
      if (response.success === true) {
        page_alert("successfully saved!");
      }
    });

    xhr.open("POST", document.URL, true);
    xhr.overrideMimeType("application/json");
    xhr.send(model);

    return false;
  }, false);
}
