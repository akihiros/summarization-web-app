from janome.analyzer import Analyzer
from janome.charfilter import UnicodeNormalizeCharFilter, RegexReplaceCharFilter
from janome.tokenizer import Tokenizer as JanomeTokenizer  # sumyのTokenizerと名前が被るため
from janome.tokenfilter import POSKeepFilter, ExtractAttributeFilter
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lex_rank import LexRankSummarizer
import re

text = """安倍首相とトランプ米大統領が２６日夜に足を運んだ非公式夕食会場は、東京・六本木の炉端焼き店「六本木田舎家　東店」だった。日本政府側はステーキ店も検討したが、「肉ばかりでは大統領も飽きるだろう」との配慮から選んだ店だという。


　両首脳は昭恵、メラニア両夫人と共にカウンター席に座った。店員から大きなしゃもじで最初のメニューの「じゃがバター」が渡され、皿を受け取ったトランプ氏は「すばらしい夜だ」と笑顔を見せた。首相も「ゆっくりとリラックスしながら意見交換したい」と応じた。夕食会ではほかにサラダと若鶏の串焼き、和牛ステーキ、バニラアイスクリームが振る舞われた。

　米ニューヨークにも進出する同店には、来日したハリウッドスターや米大リーグ選手が多数訪れ、海外でも人気だという。
「この後は炉端焼きでゆっくりとリラックスしながら、さまざまなことについて議論し、意見交換を行いたい」とも語った。
"""

# 1行1文となっているため、改行コードで分離
# sentences = [t for t in text.split('。')]
text = text.strip()
sentences = re.findall("[^。]+。?", text)

# 形態素解析器を作る
analyzer = Analyzer(
    [UnicodeNormalizeCharFilter(), RegexReplaceCharFilter(r'[(\)「」、。]', ' ')],  # ()「」、。は全てスペースに置き換える
    JanomeTokenizer(),
    [POSKeepFilter(['名詞', '形容詞', '副詞', '動詞']), ExtractAttributeFilter('base_form')]  # 名詞・形容詞・副詞・動詞の原型のみ
)

# 抽出された単語をスペースで連結
# 末尾の'。'は、この後使うtinysegmenterで文として分離させるため。
corpus = [' '.join(analyzer.analyze(s)) + '。' for s in sentences]
# for i in range(2):
#     print(corpus[i])

# 連結したcorpusを再度tinysegmenterでトークナイズさせる
parser = PlaintextParser.from_string(''.join(corpus), Tokenizer('japanese'))

# LexRankで要約を2文抽出
summarizer = LexRankSummarizer()
summarizer.stop_words = [' ']  # スペースも1単語として認識されるため、ストップワードにすることで除外する

summary = summarizer(document=parser.document, sentences_count=2)

x = ''
# 元の文を表示
for sentence in summary:
    x = x + sentences[corpus.index(sentence.__str__())] + '\n'

print(x)