document.addEventListener("DOMContentLoaded", function(evt) {
  var edit_form = document.querySelector("#edit");
  if (edit_form) {
    load_form(edit_form);
  }

  var add_game = document.querySelector("#add_game");
  if (add_game) {
    load_add_game(add_game);
  }
});

function page_alert(message) {
  alert(message);
}

function load_form(form) {
  var meta_table = form.querySelector("table#meta tbody");

  var add_meta_btn = form.querySelector("#add_meta");
  add_meta_btn.addEventListener("click", function(evt) {
    evt.preventDefault();

    var now = Date.now();

    var row = document.createElement("tr");
    var key_cell = document.createElement("td");
    var key_input = document.createElement("input");
    key_input.setAttribute("type", "text");
    key_input.setAttribute("class", "extra_meta extra_meta_key");
    key_input.setAttribute("value", "new_meta");
    key_input.setAttribute("data-metadata-name", now);
    key_input.setAttribute("data-metadata-type", "key");
    key_input.setAttribute("style", "margin-right: 9px;");
    key_cell.appendChild(key_input);
    row.appendChild(key_cell);

    var value_cell = document.createElement("td");
    var value_input = document.createElement("input");
    value_input.setAttribute("type", "text");
    value_input.setAttribute("class", "extra_meta extra_meta_value");
    value_input.setAttribute("value", "some value goes here");
    value_input.setAttribute("data-metadata-name", now);
    value_input.setAttribute("data-metadata-type", "value");
    value_cell.appendChild(value_input);
    row.appendChild(value_cell);

    meta_table.appendChild(row);
  });

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
