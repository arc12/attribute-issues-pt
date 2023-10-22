from os import  environ
import logging

from flask import Flask, render_template, session, request, abort, Blueprint

from pg_shared import prepare_app
from plaything import PLAYTHING_NAME, Langstrings, core, menu

plaything_root = core.plaything_root

# Using a blueprint is the neatest way of setting up a URL path which starts with the plaything name (see the bottom, when the blueprint is added to the app)
# This strategy would also allow for a single Flask app to deliver more than one plaything, subject to some refactoring of app creation and blueprint addition.
pt_bp = Blueprint(PLAYTHING_NAME, __name__, template_folder='templates')

@pt_bp.route("/")
# Root shows set of index cards, one for each enabled plaything specification. There is no context language for this; lang is declared at specification level.
# Order of cards follows alphanum sort of the specification ids. TODO consider sort by title.
def index():
    core.record_activity("ROOT", None, session, referrer=request.referrer)

    return render_template("index_cards.html", specifications=core.get_specifications(),
                           with_link=True, url_base=plaything_root, initial_view="questionnaire", query_string=request.query_string.decode())

@pt_bp.route("/validate")
# similar output style to root route, but performs some checks and shows error-case specifications and disabled specifications
def validate():
    core.record_activity("validate", None, session, referrer=request.referrer, tag=request.args.get("tag", None))

    return render_template("index_cards.html",
                           specifications=core.get_specifications(include_disabled=True, check_assets=["attributes"], check_optional_assets=["about"]),
                           with_link=False)

@pt_bp.route("/questionnaire/<specification_id>", methods=['GET'])
# view name = "questionnaire", the initial view
def questionnaire(specification_id: str):
    view_name = "questionnaire"

    if specification_id not in core.specification_ids:
        msg = f"Request with invalid specification id = {specification_id} for plaything {PLAYTHING_NAME}"
        logging.warn(msg)
        abort(404, msg)

    core.record_activity(view_name, specification_id, session, referrer=request.referrer, tag=request.args.get("tag", None))
    
    spec = core.get_specification(specification_id)
    langstrings = Langstrings(spec.lang)
    post_url = f"{plaything_root}/processed/{specification_id}?" + request.query_string.decode()
    return render_template("questionnaire.html",
                           langstrings=langstrings,
                           post_url=post_url,
                           title=spec.title,
                           attribute_scope=spec.detail.get("attribute_scope", None),
                           key_question=spec.detail.get("key_question", None),
                           attributes=spec.load_asset_records_dict("attributes"),
                           top_menu=spec.make_menu(menu, langstrings, plaything_root, view_name, query_string=request.query_string.decode()))

@pt_bp.route("/processed/<specification_id>", methods=['POST'])
# view name = "processed" handles a POST of responses to the questionnaire
def processed(specification_id: str):
    view_name = "processed"

    if specification_id not in core.specification_ids:
        msg = f"Request with invalid specification id = {specification_id} for plaything {PLAYTHING_NAME}"
        logging.warn(msg)
        abort(404, msg)

    selected_attributes = list(request.form)  # gets a list of the checkbox name attributes for those which are "checked". We must determine unchecked by difference.

    spec = core.get_specification(specification_id)
    langstrings = Langstrings(spec.lang)

    attributes = spec.load_asset_records_dict("attributes")
    for attribute in attributes:
        attribute["selected"] = attribute["code"] in selected_attributes

    core.record_activity(view_name, specification_id, session, referrer=request.referrer, tag=request.args.get("tag", None),
                         activity={a["code"]: a["selected"] for a in attributes})
    
    if spec.detail.get("response_type", "") == "acknowledge":
        return render_template("about.html", about=langstrings.get("FORM_ACK"),  # hi-jack the about template as it just a bare menu + content layout
                               top_menu=spec.make_menu(menu, langstrings, plaything_root, view_name, query_string=request.query_string.decode()))
        
    # prepare a formatted response
    explanation = []
    for issue_category in spec.detail.get("issue_categories", []):
        e_item = {
            "heading": issue_category["label"],
            "summary": issue_category.get("summary", ""),
            "attributes": []
        }
        for attribute in attributes:
            if attribute["category"] == issue_category["code"]:
                attribute["wrong"] = not ((issue_category["code"] == "") ^ attribute["selected"])
                e_item["attributes"].append(attribute)
        explanation.append(e_item)
    return render_template("explanation.html",
                           title=spec.title,
                           key_question=spec.detail.get("key_question", None),
                           langstrings=langstrings,
                           explanation=explanation,
                           top_menu=spec.make_menu(menu, langstrings, plaything_root, view_name, query_string=request.query_string.decode()))
        
@pt_bp.route("/about/<specification_id>", methods=['GET'])
def about(specification_id: str):
    view_name = "about"

    core.record_activity(view_name, specification_id, session, referrer=request.referrer, tag=request.args.get("tag", None))
    spec = core.get_specification(specification_id)
    if "about" not in spec.asset_map:
        abort(404, "'about' is not configured")

    langstrings = Langstrings(spec.lang)

    return render_template("about.html",
                           about=spec.load_asset_markdown(view_name, render=True),
                           top_menu=spec.make_menu(menu, langstrings, plaything_root, view_name, query_string=request.query_string.decode()))


app = prepare_app(Flask(__name__), url_prefix=plaything_root)
app.register_blueprint(pt_bp, url_prefix=plaything_root)