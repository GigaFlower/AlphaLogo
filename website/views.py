# -*- coding: utf-8 -*-
# @Author: GigaFlower
# @Date:   2016-12-22 20:25:31
# @Last Modified by:   GigaFlower
# @Last Modified time: 2017-01-12 21:39:10

from flask import Blueprint, render_template, abort, request, flash, redirect, url_for

from website.core import image_search, text_search
from website.utility import save_img_to_uploads, full_path_uploads, get_uploaded_logo


bp = Blueprint('bp', __name__, template_folder='templates')


@bp.route('/')
def index():
    return render_template('index.html')


@bp.route('/search', methods=['GET'])
def search():
    """
    Search logos by literal characters
    """
    type_ = request.args.get('type')
    kw = request.args.get('kw')
    ent_name = request.args.get('enterpriseName')
    n_colors = request.args.get('nColors')
    saturation = request.args.get('saturation')
    value = request.args.get('brightness')
    industry = request.args.get('industry')

    n_color_list = data_convertion(n_colors, 1)
    saturation_list = data_convertion(saturation)
    value_list = data_convertion(value)
    industry_list = data_convertion(industry)

    if len(kw) == 0:
        return redirect(url_for("bp.index"))
    else:
        if type_ == 'search':
            logo_matched, t = text_search(keywords=kw)
        else:
            logo_matched, t = text_search(keywords=kw, ent_name=ent_name, n_colors=n_color_list,
                                          saturation_levels=saturation_list, value_levels=value_list,
                                          industry=industry_list)

    return render_template("search.html", logo_matched=logo_matched, logo_similar=[],
                           kw=kw, ent_name=ent_name, n_colors=n_colors, time=t)


@bp.route('/match', methods=['POST'])
def match():
    """
    Matching the similar pictures by inputting a picture.
    """
    type_ = request.form.get('type')
    kw = None

    if type_ is None:
        flash("parameter 'type' is required in the post data!")

    elif type_ == "match":
        kw = request.files.get('logo')

        if not kw.filename:
            return redirect(url_for("bp.index"))
            flash("file with name 'logo' is required in the post data. Check your post data.")
            uploaded_logo = None
        else:
            upload_name = save_img_to_uploads(kw, clear_others_if_more_than=10)
            uploaded_logo = get_uploaded_logo(upload_name)

    if kw is None:
        return redirect(url_for("bp.index"))
    else:
        (logo_matched, logo_similar), t = image_search(full_path_uploads(upload_name), max_n=20)

    rounded_weights = [round(w, 5) for w in uploaded_logo.theme_weights]
    t = round(t, 5)

    return render_template("match.html", logo_matched=logo_matched, logo_similar=logo_similar,
                           kw=kw, upload=uploaded_logo, time=t, upload_theme_weights=rounded_weights)


def data_convertion(data, mode=0):
    # mode=0 means normal mode excluding color input; mode=1 means color input.
    data_list = []
    try:
        data_split = data.split(",")
        if (mode == 0):
            for i in range(len(data_split)):
                if (data_split[i] == u"1"):
                    data_list.append(i)
        elif (mode == 1):
            for i in range(len(data_split)):
                if (data_split[i] == u"1"):
                    if (i == len(data_split)-1):
                        data_list.append(0)
                    else:
                        data_list.append(i+2)
    except:
        pass
    return data_list
