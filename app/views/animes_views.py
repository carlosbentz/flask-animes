from flask import Blueprint, request, jsonify
from app.models.animes_models import AnimesModels
from psycopg2 import errors

bp_animes = Blueprint("bp_animes", __name__, url_prefix="/animes")


@bp_animes.route("", methods=["GET", "POST"])
def get_create():
    if request.method == "POST":
        data = request.get_json()
        anime_name = data.get("anime")

        anime_to_create = AnimesModels(data)
        try:
            return jsonify(anime_to_create.insert_anime()), 201
        except errors.UniqueViolation as e:
            return {"error": f'Anime {anime_name} already exists'}, 422
        except:
            return jsonify(anime_to_create.return_keys()), 422

    if request.method == "GET":
        animes = AnimesModels.get_animes()

        return {"data": animes}, 200


@bp_animes.get("/<int:anime_id>")
def filter(anime_id):
    anime = AnimesModels.get_anime_by_id(anime_id)

    if not anime:
        return {"error": "Not found"}, 404

    return {"data": anime}, 200


@bp_animes.patch("/<int:anime_id>")
def update(anime_id):
    data = request.get_json()
    anime_name = data.get("anime")

    anime_to_create = AnimesModels(data)

    try:
        res = anime_to_create.update_anime(anime_id)

    except KeyError as e:
        return e.args[0], 422

    if not res:
        return {"error": "Not found"}, 404

    return jsonify(res), 200


@bp_animes.delete("/<int:anime_id>")
def delete(anime_id):
    res = AnimesModels.delete_anime(anime_id)

    if not res:
        return {"error": "Not found"}, 404

    return {}, 204
