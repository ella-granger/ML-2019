import os
import random
import math


spam_dic = {}
ham_dic = {}


def add_dict(wl, d):
    for w in wl:
        if w in d:
            d[w] += 1
        else:
            d[w] = 1


def extract(fname):
    text = open(fname)
    line = text.readline()
    while not line.split() == []:
        line = text.readline()
    body = text.read()
    return body.split()


def load_data():
    data_cut_dir = "../trec06c-utf8/data_cut"
    label_file = open("../trec06c-utf8/label/index")

    pairs = []
    for line in label_file:
        info = line.split()
        email_path = os.path.join(data_cut_dir, info[1][-7:])
        if info[0] == "spam":
            pairs.append((True, extract(email_path)))
        else:
            pairs.append((False, extract(email_path)))
    return pairs


def partition(data_list, num):
    random.seed(1)
    random.shuffle(data_list)
    length = int(math.ceil(len(data_list) * 1.0 / num))
    par_list = []
    for i in range(0, num - 1):
        par_list.append(data_list[length * i : length * (i + 1)])
    par_list.append(data_list[(num - 1) * length:])
    return par_list


def judge_spam(words, spam_num, ham_num):
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
        

def fold_train(data_list):
    n_fold = len(data_list)
    rate = 0
    for i in range(0, n_fold):
        spam_dic.clear()
        ham_dic.clear()
        spam_num = 0
        ham_num = 0
        for j in range(0, n_fold):
            if i == j:
                test_set = data_list[j]
                continue
            for item in data_list[j]:
                if item[0]:
                    add_dict(item[1], spam_dic)
                    spam_num += 1
                else:
                    add_dict(item[1], ham_dic)
                    ham_num += 1
        correct = 0
        for item in test_set:
            if item[0] == judge_spam(item[1], spam_num, ham_num):
                correct += 1
        current_rate = correct * 1.0 / len(test_set)
        print("No.%d patch: %f" % (i, current_rate))
        rate += current_rate
    rate /= n_fold
    print("Average: %f" % (rate))


if __name__ == "__main__":
    data_ori = load_data()
    data_par = partition(data_ori, 5)
    fold_train(data_par)
        
