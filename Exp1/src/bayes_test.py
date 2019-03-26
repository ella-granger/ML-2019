import pickle
import os

with open('./spam_dic', 'rb') as f:
    spam_dic = pickle.load(f)

with open('./ham_dic', 'rb') as f:
    ham_dic = pickle.load(f)

with open('./statics', 'rb') as f:
    spam_num, ham_num, spam_word_num, ham_word_num, labels = pickle.load(f)

print("%d, %d, %d, %d, %d, %d" % (len(spam_dic), len(ham_dic), spam_num, ham_num, spam_word_num, ham_word_num))

data_cut_dir = "../trec06c-utf8/data_cut"


def extract(fname):
    text = open(fname)
    line = text.readline()
    while not line.split() == []:
        line = text.readline()
    body = text.read()
    return body.split()


def judge_spam(words):
    # P(h|x1, ..., xn) : P(x1|h) * ... * P(xn|h)P(h)
    # [x]: email, h: spam
    spam_p = spam_num
    ham_p = ham_num
    for word in words:
        if word in spam_dic:
            spam_p *= spam_dic[word]
        if word in ham_dic:
            ham_p *= ham_dic[word]

    if spam_p > ham_p:
        return True
    else:
        return False

if __name__ == "__main__":
    folders = (os.listdir(data_cut_dir))
    folders.sort()
    num = 0
    correct = 0
    for folder in folders:
        directory = os.path.join(data_cut_dir, folder)
        emails = os.listdir(directory)
        emails.sort()
        for email in emails:
            if judge_spam(extract(os.path.join(directory, email))) == labels[num]:
                correct += 1
            num += 1
    print("total: %d, correct: %d" % (spam_num + ham_num, correct))
            
    
