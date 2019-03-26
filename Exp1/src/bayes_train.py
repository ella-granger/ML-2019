import os
import pickle

def add_dict(w, d):
    if w in d:
        d[w] += 1
    else:
        d[w] = 1

data_cut_dir = "../trec06c-utf8/data_cut"
label_file = open("../trec06c-utf8/label/index")

labels = []
spam_num = 0
ham_num = 0
for line in label_file:
    info = line.split()
    if info[0] == "spam":
        labels.append(True)
        spam_num += 1
    else:
        labels.append(False)
        ham_num += 1
print("spams: %d, ham: %d, total: %d" % (spam_num, ham_num, len(labels)))
label_file.close()

# P(h|x1, ..., xn) : P(x1|h) * ... * P(xn|h)P(h)
# [x]: email, h: spam

spam_dic = {}
ham_dic = {}
spam_word_num = 0
ham_word_num = 0

folders = (os.listdir(data_cut_dir))
folders.sort()
num = 0
for folder in folders:
    directory = os.path.join(data_cut_dir, folder)
    print("dir: %s, size of spam_dict: %d, size of ham_dic: %d, totol words: %d" % (directory, len(spam_dic), len(ham_dic), spam_word_num + ham_word_num))
    emails = os.listdir(directory)
    emails.sort()
    for email in emails:
        text = open(os.path.join(directory, email))
        line = text.readline()
        while not line.split() == []:
            line = text.readline()
        body = text.read()
        words = body.split()
        
        for word in words:
            if labels[num]:
                add_dict(word, spam_dic)
                spam_word_num += 1
            else:
                add_dict(word, ham_dic)
                ham_word_num += 1
        
        text.close()
        num += 1

print("size of spam_dict: %d, size of ham_dic: %d, totol words: %d" % (len(spam_dic), len(ham_dic), spam_word_num + ham_word_num))

with open('./spam_dic', 'wb') as f:
    pickle.dump(spam_dic, f)

with open('./ham_dic', 'wb') as f:
    pickle.dump(ham_dic, f)
        
with open('./statics', 'wb') as f:
    pickle.dump((spam_num, ham_num, spam_word_num, ham_word_num, labels), f)
