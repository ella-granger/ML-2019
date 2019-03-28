import os
import random
import math
import copy
import re


def add_dict(wl, d):
    for w in wl:
        if w in d:
            d[w] += 1
        else:
            d[w] = 1

# extract info from email
def extract(fname):
    text = open(fname)
    line = text.readline()
    searchObj = re.search( r'Received: from (.*)', line, re.M|re.I)
    url = searchObj.group(1)
    priority = 0
    while not line.split() == []:
        line = text.readline()
        searchObj = re.search( r'X-Priority: (.)', line, re.M|re.I)
        if not searchObj == None:
            priority = int(searchObj.group(1))
    body = text.read()
    return body.split(), url, priority


def load_data():
    data_cut_dir = "../trec06c-utf8/data_cut"
    label_file = open("../trec06c-utf8/label/index")

    pairs = []
    for line in label_file:
        info = line.split()
        email_path = os.path.join(data_cut_dir, info[1][-7:])
        # print(email_path)
        body, url, priority = extract(email_path)
        if info[0] == "spam":
            pairs.append((True, body, [url], [priority]))
        else:
            pairs.append((False, body, [url], [priority]))
    return pairs


def partition(data_list, num, train_rate):
    random.seed(1)
    random.shuffle(data_list)
    
    data_pack = {}

    train_size = int(len(data_list) * train_rate)
    test_set = data_list[train_size:]
    data_pack["test_set"] = test_set

    data_list = data_list[:train_size]
    length = int(math.ceil(len(data_list) * 1.0 / num))
    par_list = []
    for i in range(0, num - 1):
        par_list.append(data_list[length * i : length * (i + 1)])
    par_list.append(data_list[(num - 1) * length:])
    data_pack["train_set"] = par_list
    return data_pack


def judge_spam(words, spam_dic, ham_dic, url_l, spam_url, ham_url, pri_l, spam_pri, ham_pri, spam_num, ham_num, alpha, url_figure, pri_figure):
    url = url_l[0]
    pri = pri_l[0]
    # P(h|x1, ..., xn) : P(x1|h) * ... * P(xn|h)P(h)
    # [x]: email, h: spam
    spam_p = math.log(spam_num)
    ham_p = math.log(ham_num)
    for word in words:
        if word in spam_dic:
            spam_p += math.log(spam_dic[word])
        else:
            spam_p += math.log(alpha)
        if word in ham_dic:
            ham_p += math.log(ham_dic[word])
        else:
            ham_p += math.log(alpha)

    # print("spam: %f, ham: %f" % (spam_p, ham_p))
    if url in spam_url:
        spam_p += url_figure * math.log(spam_url[url])
    else:
        spam_p += url_figure * math.log(alpha)
    if url in ham_url:
        ham_p += url_figure * math.log(ham_url[url])
    else:
        ham_p += url_figure * math.log(alpha)
    # print("url spam: %f, ham: %f" % (spam_p, ham_p))

    if pri in spam_pri:
        spam_p += pri_figure * math.log(spam_pri[pri])
    else:
        spam_p += pri_figure * math.log(alpha)
    if pri in ham_pri:
        ham_p += pri_figure * math.log(ham_pri[pri])
    else:
        ham_p += pri_figure * math.log(alpha)

    if spam_p > ham_p:
        return True
    else:
        return False
        

def fold_train(data_pack, alpha, url_figure, pri_figure):
    data_list = data_pack["train_set"]
    test_set = data_pack["test_set"]
    
    n_fold = len(data_list)
    
    val_rate = 0
    best_spam_dic = {}
    best_ham_dic = {}
    best_spam_url = {}
    best_ham_url = {}
    best_spam_pri = {}
    best_ham_pri = {}
    best_spam_num = 0
    best_ham_num = 0
    best_accuracy = 0.0

    spam_dic = {}
    ham_dic = {}
    spam_url = {}
    ham_url = {}
    spam_pri = {}
    ham_pri = {}
    for i in range(0, n_fold):
        spam_dic.clear()
        ham_dic.clear()
        spam_num = 0
        ham_num = 0
        for j in range(0, n_fold):
            if i == j:
                val_set = data_list[j]
                continue
            for item in data_list[j]:
                if item[0]:
                    add_dict(item[1], spam_dic)
                    add_dict(item[2], spam_url)
                    add_dict(item[3], spam_pri)
                    spam_num += 1
                else:
                    add_dict(item[1], ham_dic)
                    add_dict(item[2], ham_url)
                    add_dict(item[3], ham_pri)
                    ham_num += 1
        correct = 0
        for item in val_set:
            if item[0] == judge_spam(item[1], spam_dic, ham_dic, item[2], spam_url, ham_url, item[3], spam_pri, ham_pri, spam_num, ham_num, alpha, url_figure, pri_figure):
                correct += 1
        current_rate = correct * 1.0 / len(val_set)
        print("No.%d patch: %f" % (i, current_rate))
        val_rate += current_rate

        if current_rate > best_accuracy:
            best_spam_dic = copy.deepcopy(spam_dic)
            best_ham_dic = copy.deepcopy(ham_dic)
            best_spam_url = copy.deepcopy(spam_url)
            best_ham_url = copy.deepcopy(ham_url)
            best_spam_pri = copy.deepcopy(spam_pri)
            best_ham_pri = copy.deepcopy(ham_pri)
            best_spam_num = spam_num
            best_ham_num = ham_num
            best_accuracy = current_rate

    val_rate /= n_fold
    print("Average Validate Accuracy: %f" % (val_rate))

    # test set
    correct = 0
    True2False = 0
    False2True = 0
    True_tol = 0
    False_tol = 0
    for item in test_set:
        if item[0]:
            True_tol += 1
        else:
            False_tol += 1
        if item[0] == judge_spam(item[1], best_spam_dic, best_ham_dic, item[2], best_spam_url, best_ham_url, item[3], best_spam_pri, best_ham_pri, best_spam_num, best_ham_num, alpha, url_figure, pri_figure):
            correct += 1
        else:
            if item[0]:
                True2False += 1
            else:
                False2True += 1
    test_rate = correct * 1.0 / len(test_set)
    print("Test Accuracy: %f" % (test_rate))
    print("Test Size: %d" % (len(test_set)))
    print("True2False: %d, %f" % (True2False, True2False * 1.0 / True_tol))
    print("False2True: %d, %f" % (False2True, False2True * 1.0 / False_tol))


if __name__ == "__main__":
    data_ori = load_data()
    data_pack = partition(data_ori, 10, 0.9)
    fold_train(data_pack, 0.00000001, 1000, 0)

