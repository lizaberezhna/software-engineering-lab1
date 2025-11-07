from flask import Flask, render_template, request, flash, redirect
import pandas as pd
import matplotlib.pyplot as plt
import os
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = '/tmp'
ALLOWED_EXTENSIONS = {'csv', 'xlsx', 'xls'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def data(filename):
    df = pd.read_excel(filename)
df['cat_blkPostDateglobal_pdate']=pd.to_datetime(df['cat_blkPostDateglobal_pdate'], errors='coerce')
    # Порахуємо кількість публікацій за кожну дату
publication_count=df['cat_blkPostDateglobal_pdate'].value_counts().sort_index()

    # Виведемо результат
    print(publication_count)
    # Побудова графіка
    plt.figure(figsize=(10, 6))
    plt.plot(publication_count.index, publication_count.values, marker='o', linestyle='-')
    plt.title('Кількість публікацій за датою')
    plt.xlabel('Дата')
    plt.ylabel('Кількість публікацій')
    plt.xticks(rotation=45)
    plt.grid(True)
    plt.tight_layout()
    plt.savefig('/home/detectormedia/mysite/static/plot.png', bbox_inches='tight')

def authors (filename):
    df = pd.read_excel(filename)
    # Підрахунок кількості публікацій для кожного автора
    authors =df['cat_blkPostAuthorliman_1global_authorslima_end'].value_counts()

    # Знайти автора з найбільшою кількістю публікацій
    most_author = authors.idxmax()
    max_publications = authors.max()
    # знайти автора з найменшою кількістю публікацій
    mast_author = authors.idxmin()
    min_publications = authors.min()
    #збереження результатів
    result_df = pd.DataFrame({
        'Найбільше написано статей': [most_author, max_publications],
        'Найменше написано статей':  [mast_author, min_publications]
        })
    result_html = result_df.to_html(index=False)

    with open('/home/detectormedia/mysite/static/authors_results.html', 'w') as f:
        f.write(result_html)


def post(filename):
    df = pd.read_excel(filename)
    # найбільш популярний пост
popular_post=df.groupby('cat_blkPostTitleglobal_ptitle')['cat_blkPostCntglobal_pcnt'].nunique()

    # Знайти пост з найбільшою кількістю читачів
    most_popular_post = popular_post.idxmax()
    max_readers = popular_post.max()
    result_df = pd.DataFrame({
        'Найпопулярніший пост за кількістю читачів': [most_popular_post]
        })
    result_html = result_df.to_html(index=False)

    with open('/home/detectormedia/mysite/static/post_results.html', 'w') as f:
        f.write(result_html)

def popular_author(filename):
    df = pd.read_excel(filename)
    # Згрупуйте дані за іменами авторів
    grouped_data = df.groupby('cat_blkPostAuthorliman_1global_authorslima_end')

    # Порахуйте загальну кількість читачів і кількість статей для кожного автора
    total_readers = grouped_data['cat_blkPostCntglobal_pcnt'].sum()
    total_articles = grouped_data.size()  # кількість статей

    total_readers = pd.to_numeric(total_readers, errors='coerce')

    # Перетворіть стовпець на цілі числа, попередньо видаливши пробіли
    total_readers = total_readers.astype(float)

    # Обчисліть середню кількість читачів на статтю для кожного автора
    average_readers_per_article = total_readers.sum() / total_articles

    # Виведіть результат
    print("Середня кількість читачів для кожного автора:")
    print(average_readers_per_article)

    # Побудова графіка
    plt.figure(figsize=(10, 10))
    plt.bar(average_readers_per_article.index, average_readers_per_article.values, color='skyblue')
    plt.title('Популярність авторів за кількістю читачів')
    plt.xlabel('Автори')
    plt.ylabel('Кількість читачів')
    plt.xticks(rotation=90)
    plt.tight_layout()
    plt.savefig('/home/detectormedia/mysite/static/plots.png', bbox_inches='tight')

@app.route('/')
def hello_world():
    return render_template("main.html")

@app.route('/help')
def help_page():
    return '<h1>help page</h1>'

@app.route('/upload', methods=['POST'])
def data_page():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            full_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(full_path)
            data(full_path)
            popular_author(full_path)
            authors (full_path)
            post(full_path)
            os.remove(full_path)
            return render_template("index.html")
    return 'Неможливо обробити файл'
