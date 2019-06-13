from flask import Flask, render_template, request
import re
from janome.analyzer import Analyzer
from janome.charfilter import UnicodeNormalizeCharFilter, RegexReplaceCharFilter
from janome.tokenizer import Tokenizer as JanomeTokenizer  # sumyのTokenizerと名前が被るため
from janome.tokenfilter import POSKeepFilter, ExtractAttributeFilter
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lex_rank import LexRankSummarizer
 
app = Flask(__name__)

def count_word(text):
    words = re.findall(r'[a-z0-9\\’\\\']+', text.lower())
    return len(words)


def lexrank_sumy(text):
    '''
    LexRankを実行する
    text:要約したい文章
    '''
    text = text.strip()
    sentences = re.findall("[^。]+。?", text)

    analyzer = Analyzer(
        [UnicodeNormalizeCharFilter(), RegexReplaceCharFilter(r'[(\)「」、。]', ' ')],  # ()「」、。は全てスペースに置き換える
        JanomeTokenizer(),
        [POSKeepFilter(['名詞', '形容詞', '副詞', '動詞']), ExtractAttributeFilter('base_form')]  # 名詞・形容詞・副詞・動詞の原型のみ
    )

    corpus = [' '.join(analyzer.analyze(s)) + '。' for s in sentences]
    parser = PlaintextParser.from_string(''.join(corpus), Tokenizer('japanese'))

    summarizer = LexRankSummarizer()
    summarizer.stop_words = [' ']

    summary = summarizer(document=parser.document, sentences_count=3)
    summary_text = ''
    for sentence in summary:
        summary_text = summary_text + sentences[corpus.index(sentence.__str__())] + '\n'
   
    return summary_text
 
 
# @app.route('/', methods=['POST', 'GET'])
# def home(): 
#     total = ''
#     if request.method == 'POST':
#         text = request.form['text']
#         total = count_word(text)
#         return render_template('main.html', total=total, sentence=text)
 
#     return render_template('main.html', total=total)

@app.route('/', methods=['POST', 'GET'])
def home(): 
    summary_text = ''
    if request.method == 'POST':
        text = request.form['text']
        summary_text = lexrank_sumy(text)    
        return render_template('main.html', summary_text=summary_text, sentence=text)
 
    return render_template('main.html', summary_text=summary_text)

if __name__ == "__main__":
    app.run(debug=True)