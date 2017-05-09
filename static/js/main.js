document.addEventListener("DOMContentLoaded", function(evt) {
  var edit_form = document.querySelector("#edit");
  if (edit_form) {
    load_model_form(edit_form);
  }

  var deploy_form = document.querySelector("form#deploy")
  if (deploy_form) {
    load_deploy_form(deploy_form)
  }

  var image_upload_form = document.querySelector("form#upload_image");
  if (image_upload_form) {
    load_image_upload_form(image_upload_form);
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

function get_metadata(form) {
  meta_inputs = [...form.querySelectorAll("[name^=meta]")]
  return _.reduce(meta_inputs, function(hash, element) {
    var key = element.getAttribute("data-metadata-name");

    var value;
    if (element.type == "file") {
      value = element.files[0];
      if (value === undefined) {
        return hash;
      }
    } else if (element.type == "checkbox") {
      value = element.checked;
    } else {
      value = element.value;
    }

    hash[key] = value;
    return hash;
  }, {});
}

function load_model_form(form) {
  form.addEventListener("submit", function(e) {
    e.preventDefault();

    var model = new FormData()
    model.append("markdown", form.querySelector("textarea[name=content]").value);
    var filename_input = form.querySelector("input[name=filename]");
    if (filename_input) {
      model.append("filename", filename_input.value)
    }

    _.each(get_metadata(form), function(value, key) {
      model.append(`metadata[${key}]`, value);
    });

    var xhr = new XMLHttpRequest()
    xhr.addEventListener("load", function(evt) {
      if (xhr.responseURL !== document.location.href) {
        window.location = xhr.responseURL;
      }

      var response = JSON.parse(xhr.response);
      console.log(response);
      if (response.success === true) {
        page_alert("successfully saved!");
      } else {
        page_alert("Error: " + response.errors);
      }
    });

    xhr.open("POST", document.URL, true);
    xhr.setRequestHeader("X-Requested-With", "XMLHttpRequest")
    xhr.overrideMimeType("application/json");
    xhr.send(model);

    return false;
  }, false);
}

function load_deploy_form(form) {
  form.addEventListener("submit", function(e) {
    e.preventDefault();

    var data = new FormData(form);

    var xhr = new XMLHttpRequest();
    xhr.addEventListener("load", function(evt) {
      console.log(xhr.response);
      var response = JSON.parse(xhr.response);
      if (response.success === true) {
        page_alert("successfully saved!");
      } else {
        page_alert("Error: " + response.message);
      }
    });

    xhr.open("POST", form.action, true);
    xhr.setRequestHeader("X-Requested-With", "XMLHttpRequest")
    xhr.overrideMimeType("application/json");
    xhr.send(data);
  })
}

function load_image_upload_form(form) {
  form.addEventListener("submit", function(e) {
    e.preventDefault();

    var image_selector = document.querySelector("input#image");
    if (image_selector.files.length === 0) {
      page_alert("No image selected for upload.");
      return;
    }

    var data = new FormData();
    data.append("image", image_selector.files[0]);

    var xhr = new XMLHttpRequest();
    xhr.addEventListener("load", function(evt) {
      // if (xhr.responseURL !== document.location.href) {
      //   window.location = xhr.responseURL;
      // }

      console.log(xhr.response);
      var response = JSON.parse(xhr.response);
      if (response.success === true) {
        page_alert("Image uploaded, refreshing");

        window.setTimeout(function() {
          window.location.reload()
        }, 1500);
      }
    });

    xhr.open("POST", form.action, true);
    xhr.setRequestHeader("X-Requested-With", "XMLHttpRequest");
    xhr.overrideMimeType("application/json");
    xhr.send(data);

    page_alert("Uploading image... This may take some time.")

    return false;
  }, false);
}
