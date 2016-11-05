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
  // add_meta_btn = form.querySelector("#add_meta");
  // add_meta_btn.addEventListener("click", function(evt) {
  //   evt.preventDefault();
  //
  //   now = Date.now()
  // });

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
      var value_search = "input.extra_meta[data-metadata-type=value][data-metadata-name=" + metadata_key + "]"
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
