from flask import Flask, render_template, abort
from utils.mysql_utils import connect_to_mysql, mysql_to_df

app = Flask(__name__)


@app.route("/")
def index():
    engine = connect_to_mysql()
    sql = "SELECT distinct country from player_data ORDER BY 1"
    df = mysql_to_df(engine, sql)
    print(df)
    country_codes_list = df["country"].tolist()

    return render_template("index.html", countries=country_codes_list)


@app.route("/<country_code>", methods=["GET"])
def player_ranking_data(country_code):
    try:
        engine = connect_to_mysql()
        sql = f"SELECT * FROM player_data WHERE country = '{country_code}'"
        df = mysql_to_df(engine, sql)
        if df.empty:
            abort(404)

        print(df)
        data = df.to_dict("records")
        columns = df.columns.tolist()
        country_code_upper_case = country_code.upper()
        print(f"country_code: {country_code}")
        return render_template(
            "player_data.html",
            data=data,
            columns=columns,
            country_code=country_code_upper_case,
        )

    except Exception as e:
        print(e)
        abort(404)


@app.errorhandler(404)
def page_not_found(e):
    print(e)
    return render_template("404.html")


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
