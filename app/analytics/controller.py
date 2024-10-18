from analytics import analytics
from flask import request, render_template
import json
from analytics.model import labels, datasets

@analytics.route("/graph", methods=['GET', 'POST'])
def graph():
    if request.method == 'POST':

        return json.dumps({
            "labels": labels,
            "datasets": datasets
        })
    else:
        return render_template("graph.html")