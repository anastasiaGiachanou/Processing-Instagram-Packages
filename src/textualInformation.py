import emoji
import regex
import pandas as pd
import re
from itertools import groupby

class textualInformation:
    
    all_emojis = list(emoji.UNICODE_EMOJI.keys())

    def __init__(self):

        all_emojis = list(emoji.UNICODE_EMOJI.keys())

    def countEmoticons(self,text):
        emoji_counter = 0
        data = regex.findall(r'\X', text)
        for word in data:
            if any(char in emoji.UNICODE_EMOJI for char in word):
                emoji_counter += 1

        return emoji_counter

    def question_marks(self,text):
        text = re.sub(r'([^a-zA-Z0-9])', r' \1 ', text)
        count = len(re.findall(r'[?¿]', text))
        return count

    def exclamation_marks(self,text):
        text = re.sub(r'([^a-zA-Z0-9])', r' \1 ', text)
        count = len(re.findall(r'[!¡]', text))
        return count

    def sentence_len(self,text):
        count = len(text.split())
        return count

    def consecutive_chars(self,text):
        count = sum([count for count in [sum(1 for _ in group) for label, group in groupby(text)] if count > 1])
        return count

    def upper_case(self,text):
        up_count = len(re.findall(r'[A-Z]', text))
        low_count = len(re.findall(r'[a-z]', text))
        try:
            count = (up_count/low_count)
        except:
            count = 1
        return count

    def URL(self,text):
        text = re.sub(r"((http|https)://([\w_-]+(?:(?:\.[\w_-]+)+))([\w.,@?^=%&:/~+#-]*[\w@?^=%&/~+#-])?)", " htm ", text)
        count = len(re.findall(r'http', text))
        return count

    def mention(self,text):
        text = re.sub(r"(@[a-zA-Z_0-9]+)", " usr ", text)
        count = len(re.findall(r'usr', text))
        return count

    def hashtags(self,text):
        text = re.sub(r"(#[a-zA-Z_0-9]+)", " hsh ", text)
        count = len(re.findall(r'hsh', text))
        return count

    def one_vector_stylistic(self, sentences):
        lst = []
        for sentence in sentences:

            if len(sentence) < 2:
                lst.append([0,0,0,0,0,0,0,0,0])
            else:
                global_vec = []
                global_vec.append(self.question_marks(sentence))
                global_vec.append(self.exclamation_marks(sentence))
                global_vec.append(self.sentence_len(sentence))
                global_vec.append(self.consecutive_chars(sentence))
                global_vec.append(self.upper_case(sentence))
                global_vec.append(self.URL(sentence))
                global_vec.append(self.mention(sentence))
                global_vec.append(self.hashtags(sentence))
                global_vec.append(self.countEmoticons(sentence))

                lst.append(global_vec)

        dfTextual = pd.DataFrame(lst, columns =['question_marks', 'exclamation_marks', 'sentence_len', 'consecutive_chars', 'upper_case', 'URL', 'mention', 'hashtags', 'countEmoticons'], dtype = float)

        return dfTextual

if __name__ == '__main__':

    df = pd.Series(["Dat was ie weer!❤💛💚","I shoot want to be sad witt! https://www.dancemagazine.com/natalia-osipova-2648132495.htm", "https://www.dancemagazine.com/natalia-osipova-2648132495.html" ])
    tf = textualInformation()

    dfTextual = tf.one_vector_stylistic(df)

    print(dfTextual.head(3))
