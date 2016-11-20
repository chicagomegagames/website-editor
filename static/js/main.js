document.addEventListener("DOMContentLoaded", function(evt) {
  var edit_form = document.querySelector("#edit");
  if (edit_form) {
    load_form(edit_form);
  }

  var add_game = document.querySelector("#new_game");
  if (add_game) {
    add_game.addEventListener("click", function(evt) {
      evt.preventDefault();
      new_file("/game/new/")
    });
  }

  var add_page = document.querySelector("#new_page");
  if (add_page) {
    add_page.addEventListener("click", function(evt) {
      evt.preventDefault();
      new_file("/page/new/");
    });
  }

  var delete_links = document.querySelectorAll("a[data-method=delete]");
  delete_links.forEach(function(link) {
    setup_delete_link(link);
  });
});

function new_file(xhr_location) {
  var filename = prompt("Filename");
  if (filename.substr("-3") !== ".md") {
    filename = filename + ".md"
  }

  punctuation = new RegExp("[\W_]+", "g")
  spaces = new RegExp(" ", "g")
  filename = filename.replace(punctuation, "_");
  filename = filename.replace(spaces, "_");
  filename = filename.toLowerCase();

  var xhr = new XMLHttpRequest()
  xhr.addEventListener("load", function(evt) {
    console.log(xhr.response);
    var response = JSON.parse(xhr.response);
    if (response.success === true) {
      page_alert("successfully created file!");
      window.location = response.edit_path
    }
  });

  xhr.open("POST", xhr_location + filename, true);
  xhr.overrideMimeType("application/json");
  xhr.send();
}

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

  console.log("delete path");
  console.log(path)

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

function load_form(form) {
  form.addEventListener("submit", function(e) {
    e.preventDefault();

    var model = {}
    model.markdown = form.querySelector("textarea[name=content]").value;
    model.metadata = {}

    required_meta_inputs = [...form.querySelectorAll("input[name^=required_meta]")]
    required_meta_inputs.forEach(function(element) {
      var key = element.getAttribute("data-metadata-name");
      var value = element.value;

      model.metadata[key] = value;
    })

    optional_meta_keys = [...form.querySelectorAll("input.extra_meta[data-metadata-type=key]")]
    optional_meta_keys.forEach(function(element) {
      var key = element.value;
      var metadata_key = element.getAttribute("data-metadata-name");
      var value_search = "input.extra_meta[data-metadata-type=value][data-metadata-name='" + metadata_key + "']"
      var value_element = form.querySelector(value_search);
      var value = value_element.value;

      if (!(key in model.metadata)) {
        model.metadata[key] = value;
      }
    });

    console.log(model);

    var xhr = new XMLHttpRequest()
    xhr.addEventListener("load", function(evt) {
      console.log("loaded");
      console.log(xhr.response);
      var response = JSON.parse(xhr.response);
      if (response.success === true) {
        page_alert("successfully saved!");
      }
    });

    xhr.open("POST", document.URL, true);
    xhr.overrideMimeType("application/json");
    xhr.send(JSON.stringify(model));

    return false;
  }, false);
}
