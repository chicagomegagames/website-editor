from app.config import Config
from app.utils import form_to_dict
from flask import Blueprint, render_template, request, redirect, url_for, jsonify
import orator

class BaseController(Blueprint):
    image_service = None

    @classmethod
    def set_image_service(cls, service):
        cls.image_service = service

    def __init__(self, route_prefix):
        super().__init__(route_prefix, __name__, url_prefix="/{}".format(route_prefix))
        self.route_prefix = route_prefix

        self.errorhandler(FileNotFoundError)(self.file_not_found)
        self.errorhandler(orator.exceptions.orm.ModelNotFound)(self.file_not_found)

    def template(self, name, **kwargs):
        return render_template(name, config=Config, prefix=self.route_prefix, **kwargs)

    def _template(self, name, **kwargs):
        return render_template(name, config=Config, prefix=self.route_prefix, **kwargs)


    def file_not_found(self, error):
        return self._template("404.html"), 404

    def is_delete_request(self):
        if request.method == "POST" and "_method" in request.form:
            return request.form["_method"] == "DELETE"
        return False


class BaseModelController(BaseController):
    def __init__(self, cls, route_prefix):
        super().__init__(route_prefix)
        self.cls = cls
        self.model_name = cls.__name__

        meta = dict(self.cls.REQUIRED_META)
        meta.update(self.cls.OPTIONAL_META)
        self.image_metadata = [
            key for key, value in meta.items() if value["type"] == "image"
        ]

        self._setup_routes()


    def _setup_routes(self):
        self.route("/")(self.index)
        self.route("/new", methods=["GET", "POST"])(self.new)
        self.route("/<slug>", methods=["GET", "POST"])(self.show)
        self.route("/<slug>/edit", methods=["GET", "POST"])(self.edit)


    def index(self):
        all_models = self.cls.all_sorted()
        return self.template("index.html", models=all_models)

    def show(self, slug):
        model = self.get(slug)
        if self.is_delete_request():
            model.delete()
            return redirect(url_for(".index"))

        return self.template("show.html", model=model)

    def edit(self, slug):
        model = self.get(slug)

        errors = []
        if request.method == "POST":
            form = form_to_dict(request.form)

            self.clean_form(form)
            form = model._convert_form(form)

            images = {}
            for key in self.image_metadata:
                file_key = "metadata[{key}]".format(key=key)
                if file_key in request.files:
                    img = request.files[file_key]
                    uploaded_image = self.image_service.upload_image(
                        img.filename,
                        img.stream
                    )
                    image_path = "/images/{}".format(uploaded_image.name)
                    form["metadata"][key] = image_path

            response, status_code = self.update(model, form)

            return jsonify(**response), status_code

        return self.template("edit.html", model=model, required_meta=model.REQUIRED_META, optional_meta=model.OPTIONAL_META)

    def new(self):
        if request.method == "POST":
            form = form_to_dict(request.form)
            model = self._model_create(form)

            return redirect(self._new_redirect_location(model))

        return self.template("edit.html", model=None, required_meta=self.cls.REQUIRED_META, optional_meta=self.cls.OPTIONAL_META)

    def _model_create(self, form):
        pass

    def _new_redirect_location(self, model):
        pass

    def clean_form(self, form):
        pass

    def get(self, slug):
        pass

    def update(self, model, form):
        pass


class FileModelController(BaseModelController):
    def __init__(self, cls, route_prefix):
        super().__init__(cls, route_prefix)
        self.view_options = {
            "edit_show_filename": True,
        }

    def template(self, name, **kwargs):
        return super().template("file_models/{}".format(name), model_name=self.model_name, show_filename = self.view_options["edit_show_filename"], **kwargs)

    def get(self, slug):
        return self.cls(slug)

    def clean_form(self, form):
        if "filename" in form and form["filename"] == model.filename:
            del form["filename"]

    def update(self, model, form):
        model.update(**form)
        if not model.validate():
            errors = model.errors
            success = False
            status_code = 400
        else:
            model.save()
            success = True
            errors = []
            status_code = 200

        return ({
            "errors": errors,
            "success": success,
            "model": model.serialize(),
        }, status_code)

    def _new_redirect_location(self, model):
        return url_for(".show", slug=model.filename)

    def _model_create(self, form):
        return self.cls.create(form["filename"], markdown=form["markdown"], **form["metadata"])


class DatabaseModelController(BaseModelController):
    def template(self, name, **kwargs):
        return super().template("models/{}".format(name), model_name=self.model_name, **kwargs)

    def get(self, slug):
        return self.cls.where('slug', '=', slug).first_or_fail()

    def update(self, model, form):
        try:
            model.update(**form)
        except orator.exceptions.query.QueryException as e:
            return ({
                "errors": [e.message],
                "success": False,
                "model": model.to_json(),
            }, 400)

        return ({
            "errors": [],
            "success": True,
            "model": model.to_json(),
        }, 200)

    def _new_redirect_location(self, model):
        return url_for(".show", slug=model.slug)

    def _model_create(self, form):
        return self.cls.create(**form)


class ModelController(FileModelController):
    pass
