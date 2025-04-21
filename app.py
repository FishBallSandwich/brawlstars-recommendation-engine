from flask import Flask, render_template
from etl_service.mysql_utils import connect_to_mysql, mysql_to_df

app = Flask(__name__)


@app.route("/")
def index():
    engine = connect_to_mysql()
    sql = "SELECT * FROM player_data"
    df = mysql_to_df(engine, sql)
    print(df)
    data = df.to_dict("records")
    columns = df.columns.tolist()

    return render_template("index.html", data=data, columns=columns)


if __name__ == "__main__":
    app.run(debug=True)
