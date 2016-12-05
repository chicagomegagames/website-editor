from app.utils import form_to_dict
from flask import Blueprint, render_template, request, redirect, url_for, jsonify

class BaseController(Blueprint):
    def __init__(self, route_prefix, site_config):
        super().__init__(route_prefix, __name__, url_prefix="/{}".format(route_prefix))
        self.route_prefix = route_prefix
        self.site_config = site_config

        self.errorhandler(FileNotFoundError)(self.file_not_found)

    def template(self, name, **kwargs):
        if callable(self.site_config):
            config = self.site_config()
        else:
            config = self.site_config

        return render_template(name, site=config, prefix=self.route_prefix, **kwargs)

    def file_not_found(self, error):
        return self.template("404.html"), 404

    def is_delete_request(self):
        if request.method == "POST" and "_method" in request.form:
            return request.form["_method"] == "DELETE"
        return False


class ModelController(BaseController):
    def __init__(self, cls, route_prefix, site_config):
        super().__init__(route_prefix, site_config)
        self.cls = cls
        self.model_name = cls.__name__

        self.route("/")(self.index)
        self.route("/new", methods=["GET", "POST"])(self.new)
        self.route("/<filename>", methods=["GET", "POST"])(self.show)
        self.route("/<filename>/edit", methods=["GET", "POST"])(self.edit)

    def template(self, name, **kwargs):
        return super().template(name, model_name=self.model_name, **kwargs)

    def index(self):
        all_models = self.cls.all()
        return self.template("models/index.html", models=all_models)

    def show(self, filename):
        model = self.cls(filename)
        if self.is_delete_request():
            model.delete()
            return redirect(url_for(".index"))

        return self.template("models/show.html", model=model)

    def edit(self, filename):
        model = self.cls(filename)

        errors = []
        if request.method == "POST":
            form = form_to_dict(request.form)
            model.update(**form)
            if not model.validate():
                errors = model.errors
                success = False
                status_code = 400
            else:
                model.save()
                success = True
                status_code = 200

            response = {
                "errors": errors,
                "success": success,
                "model": model.serialize(),
            }

            if success and "filename" in form:
                return redirect(url_for(".show", filename=form["filename"]))
            return jsonify(**response), status_code

        return self.template("models/edit.html", model=model, required_meta=model.REQUIRED_META, optional_meta=model.OPTIONAL_META)

    def new(self):
        if request.method == "POST":
            form = form_to_dict(request.form)
            model = self.cls.create(form["filename"], markdown=form["markdown"], **form["metadata"])

            return redirect(url_for(".show", filename=form["filename"]))

        return self.template("models/edit.html", model=None, required_meta=self.cls.REQUIRED_META, optional_meta=self.cls.OPTIONAL_META)
