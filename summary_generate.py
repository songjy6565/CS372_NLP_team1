import nltk,re,pprint
from nltk import word_tokenize
from urllib import request
from nltk import FreqDist
import csv
from collections import defaultdict
import pickle
import time
import sys, getopt

#required files : book_tags.csv, books.csv, tags.csv
#intermediate result : bookinfo_dict.txt, new_genre_dict.txt (generated with pickle)
#final result : bookdata.csv (if used with continue option, it adds to the back)
#every 100 books are saved to bookdata.csv
#if you want to start from the middle, execute "python generate_dataset.py [offset]"
#(i.e python generate_dataset.py 100), if last saved offset was 100/8098
class BookInfo : 
    def __init__(self, title, author, book_id, rating, rate_num) :
        self.title = title
        self.author = author
        self.book_id = book_id
        self.rating = rating
        self.rated_people = rate_num

class BookData :
    def __init__(self, bookinfo, summary, rel_books) :
        self.bookinfo = bookinfo
        self.summary = summary
        self.genre = None
        self.related_books = rel_books
    
    def set_genre(self,genre) :
        self.genre = genre
    
    def to_list(self) :
        return [self.bookinfo.title, self.bookinfo.author, self.bookinfo.book_id, self.bookinfo.rating, self.bookinfo.rated_people, self.genre, self.related_books
        ,self.summary]

#book_tags
#get genre from the tag
#compare with https://www.goodreads.com/shelf
# 'fiction', 'adult', 'novels', 'series'?, 'adult-fiction', 'fantasy', 'romance', 
# 'novel','contemporary', 'mystery', 'adventure', 'young-adult', 'drama', 'literature', 
# 'general-fiction', 'ya', 'classics', 'contemporary-fiction', 'historical', 
# 'historical-fiction','thriller','sci-fi-fantasy','suspense', 'sci-fi','science-fiction',
# 'action', 'humor', 'history', 'non-fiction', 'crime', 'fantasy-sci-fi', 'chick-lit',
# 'paranomal', 'school', 'classic', 'magic', 'mystery-thriller', 'teen', 'supernatural',
# 'nonfiction', 'realistic-fiction', 'literary-fiction', 'scifi-fantasy', 'love', 'ya-fiction'
# 'mystery-suspense', 'mysteries', 'urban-fantasy', 'children', 'literary', 'horror', 'childrens'
# 'young-adult-fiction', 'thrillers', 'childeren-s', 'kids', 'science-fiction-fantasy',
# 'science', 'childeren-s-books', 'ya-books', 'scifi', 'action-adventure', 'hunour',
# 'biography', 'speculative-fiction', 'contemporary-romance', 'high-school', 'women',
# 'philosophy', 'war', 'fantasy-scifi', 'mystery-crime', 'comedy', 'juvenile', 'suspense-thriller'
# 'childrens-books', 'crime-fiction', 'youth', 'modern-fiction'
# 1. fiction, general-fiction, contemporary-fiction, historical-fiction, realistic-fiction, literary-fiction, speculative fiction, modern-fiction
# 2. adult
# 3. fantasy, magic?, urban-fantasy
# 4. romance, love, contemporary-romance
# 5. novel
# 6. mystery, 'mistery-thriller', mystery-suspense,mysteries, mystery-crime, 
# 7. adventure, action-adventure
# 8. young-adult, ya, teen, ya-fiction, young-adult-fiction, ya-books, juvenile, youth, high-school
# 9. drama
# 10. literature, literary
# 11. classics, classic,
# 12. historical, history
# 13. thriller, thrillers,
# 14. sci-fi-fantasy, sci-fi, science-fiction, fantasy-sci-fi, scifi-fantasy, science-fiction-fantasy, scifi, fantasy-scifi
# 15. suspense, suspense-thriller
# 16. action
# 17. humor, humour, comedy
# 18. non-fiction, nonfiction
# 19. crime, crime-fiction
# 20. chick-lit, women
# 21. paranomal, supernatural, horror
# 22. children, childrens, childeren-s, kids, childeren-s-books, childrens-books, school
# 23. science
# 24. biography
# 25. philosophy
# 26. war
# tag dictionary 
def get_genre_from_tags(tags) :
    f = open('tags.csv', 'r', encoding = 'utf-8')
    rdr = csv.reader(f)
    genre_list = []
    idx = 0
    for line in rdr :
        if idx ==0 :
            idx+=1
            continue 
        for (tag, freq) in tags : 
            if line[0] == tag :
                genre_list.append((line[1],freq))
    res_list = sorted(genre_list, key=lambda genre: genre[1], reverse = True)
    #print(res_list)
    #print("len : "+str(len(genre_list)))
    f.close()
    return res_list

def get_tag_from_genre(genre_list) : 
    f = open('tags.csv', 'r', encoding = 'utf-8')
    rdr = csv.reader(f)
    genre_list_temp = genre_list
    tag_dict = {}
    idx = 0
    for line in rdr : 
        if idx ==0 :
            idx+=1
            continue
        if len(genre_list_temp) == 0 :
            break
        if line[1] in genre_list_temp : 
            tag_dict[line[1]] = line[0]
            genre_list_temp.remove(line[1])
    return tag_dict

#booklist with bookdata , fill in the book data with genre
def fill_bookdata_with_genre(bookdict,genredict) :
    f = open('book_tags.csv', 'r', encoding = 'utf-8')
    rdr = csv.reader(f)
    current_id = 0
    genre_found = set()
    fill_num = len(bookdict.values())
    idx = 0
    #print(genredict)
    #print(bookdict)
    flag_fin = True
    for line in rdr :
        if idx == 0 :
            idx+=1 
            continue
        if fill_num == 0 :
            break
        if str(current_id) != line[0] :
            if line[0] in bookdict.keys() :
                if not flag_fin :
                    bookdict[str(current_id)].set_genre(list(genre_found))
                    #print("set : "+str(current_id))
                    #print(genre_found)
                    fill_num -= 1
                    genre_found = set()
                else :
                    flag_fin = False
                current_id = int(line[0])
                for main, genre_pair in genredict.items() :
                    for (tag, _) in genre_pair : 
                        if tag == line[1] :
                            genre_found.add(main)
            else : 
                continue
        else :
            if flag_fin : 
                continue
            for main, genre_pair in genredict.items() :
                for (tag, _) in genre_pair : 
                    if tag == line[1] :
                        genre_found.add(main)
            if len(genre_found) == 3 :
                #current_id += 1
                #fill genre to the dict
                bookdict[line[0]].set_genre(list(genre_found))
                #print("set : "+line[0])
                #print(genre_found)
                fill_num -= 1
                flag_fin = True
                genre_found = set()
    f.close()

#get frequently used tags top 200 
def get_freq_tags() :
    f = open('book_tags.csv', 'r', encoding = 'utf-8')
    rdr = csv.reader(f)
    tag_list = []
    idx = 0
    for line in rdr : 
        if idx == 0 :
            idx += 1
            continue
        tag_list.append(line[1])
    fd_tags = FreqDist(tag_list)
    res = fd_tags.most_common(200)
    #print(res)
    f.close()
    return res

#debugging function 
def get_data_from_id(id) : 
    url = "https://www.goodreads.com/book/show/" + str(id)
    html = request.urlopen(url).read().decode('utf8')
    sum_idx = html.find("descriptionContainer")
    sum_start_tmp1 = html[sum_idx:].find("<span id=")
    sum_start_tmp2 = re.search(r"<span id=|</div>",html[sum_idx+sum_start_tmp1+1:])
    print(sum_start_tmp2)
    if sum_start_tmp2.group() == '</div>' :
        #start from sum_start_tmp1
        sum_start_2 = html[sum_idx+sum_start_tmp1:].find(">")
        sum_end = html[sum_idx+sum_start_tmp1+sum_start_2:].find("</span>")
        sum_text = html[sum_idx+sum_start_tmp1+sum_start_2+1:sum_idx+sum_start_tmp1+sum_start_2+sum_end]
    else : 
        #start from sum_start_tmp2
        print(html[sum_idx+sum_start_tmp1+1+sum_start_tmp2.span()[1]:][:20])
        sum_start_1 = html[sum_idx+sum_start_tmp1+1+sum_start_tmp2.span()[1]:].find("display:none")
        tmp = sum_start_tmp1+1+sum_start_tmp2.span()[1]+sum_start_1
        sum_start_2 = html[sum_idx+tmp:].find(">")
        sum_end = html[sum_idx+tmp+sum_start_2:].find("</span>")
        sum_text = html[sum_idx+tmp+sum_start_2+1:sum_idx+tmp+sum_start_2+sum_end]
        print(sum_text)
    #sum_start_1 = html[sum_idx:].find("display:none")
    #find until the second <span id>
    #remove braces
    rel_idx= html.find("relatedWorks")
    rel_start = html[rel_idx:].find("<ul>")
    rel_end = html[rel_idx+rel_start:].find("</ul>")
    rel_text = html[rel_idx+rel_start+4:rel_idx+rel_start+4+rel_end]
    rel_list = []
    idx = 0
    idx_add = rel_text[idx:].find("<li")
    while idx_add > 0 :
        idx += idx_add
        id_start = rel_text[idx:].find("bookCover_")
        idx += id_start
        id_end = rel_text[idx:].find('>')
        rel_list.append(rel_text[idx+10:idx+id_end-1])
        idx += id_end
        idx_add = rel_text[idx:].find("<li")
    new_sum_text = re.sub(r'<[^>]*>','', sum_text)
    print(new_sum_text)

def get_data_from_info(bookinfo) :
    #url = "https://www.goodreads.com/book/show/2767052.The_Hunger_Games"
    url = "https://www.goodreads.com/book/show/" + bookinfo.book_id
    html = request.urlopen(url).read().decode('utf8')
    sum_idx = html.find("descriptionContainer")
    sum_start_tmp1 = html[sum_idx:].find("<span id=")
    sum_start_tmp2 = re.search(r"<span id=|</div>",html[sum_idx+sum_start_tmp1+1:])
    if sum_start_tmp2.group() == '</div>' :
        #start from sum_start_tmp1
        sum_start_2 = html[sum_idx+sum_start_tmp1:].find(">")
        sum_end = html[sum_idx+sum_start_tmp1+sum_start_2:].find("</span>")
        sum_text = html[sum_idx+sum_start_tmp1+sum_start_2+1:sum_idx+sum_start_tmp1+sum_start_2+sum_end]
    else : 
        #start from sum_start_tmp2
        sum_start_1 = html[sum_idx+sum_start_tmp1+1+sum_start_tmp2.span()[1]:].find("display:none")
        tmp = sum_start_tmp1+1+sum_start_tmp2.span()[1]+sum_start_1
        sum_start_2 = html[sum_idx+tmp:].find(">")
        sum_end = html[sum_idx+tmp+sum_start_2:].find("</span>")
        sum_text = html[sum_idx+tmp+sum_start_2+1:sum_idx+tmp+sum_start_2+sum_end]
    #sum_start_1 = html[sum_idx:].find("display:none")
    #find until the second <span id>
    #remove braces
    rel_idx= html.find("relatedWorks")
    rel_start = html[rel_idx:].find("<ul>")
    rel_end = html[rel_idx+rel_start:].find("</ul>")
    rel_text = html[rel_idx+rel_start+4:rel_idx+rel_start+4+rel_end]
    rel_list = []
    idx = 0
    idx_add = rel_text[idx:].find("<li")
    while idx_add > 0 :
        idx += idx_add
        id_start = rel_text[idx:].find("bookCover_")
        idx += id_start
        id_end = rel_text[idx:].find('>')
        rel_list.append(rel_text[idx+10:idx+id_end-1])
        idx += id_end
        idx_add = rel_text[idx:].find("<li")
    new_sum_text = re.sub(r'<[^>]*>','', sum_text)
    #print(new_sum_text)
    #print(rel_list)
    res = BookData(bookinfo, new_sum_text, rel_list)
    return res

def main(argv) :
    if len(argv) == 2:
        continue_add_data(argv[1])
    else :
        if len(argv) != 1 :
            print("For initial iteration")
            print("USAGE : python generate_dataset.py")
            print("For continued iteration")
            print("python generate_dataset.py [offset]")
            return
    start = time.strftime('%c', time.localtime(time.time()))
    #'classic' : ['classic','classics'],
    #school : academic
    genre_dict = {
        'fiction' : ['novel', 'fiction', 'general-fiction', 'contemporary-fiction', 'historical-fiction', 'realistic-fiction', 'literary-fiction', 'speculative-fiction', 'modern-fiction'],
        'adult' : ['adult'],
        'fantasy' : ['fantasy', 'urban-fantasy'],
        'romance' : ['romance', 'love', 'contemporary-romance'],
        'mystery' : ['mystery','mystery-thriller', 'mystery-suspence', 'mysteries', 'mystery-crime'],
        'action' :  ['adventure', 'action-adventure', 'action'],
        'young-adult' : ['young-adult', 'ya', 'teen', 'ya-fiction', 'young-adult-fiction', 'ya-books', 'juvenile', 'youth', 'high-school'],
        'drama' : ['drama'],
        'historical' : ['historical','history','war','biography'],
        'sci-fi' : ['sci-fi', 'sci-fi-fantasy', 'science-fiction', 'fantasy-sci-fi', 'scifi-fantasy', 'science-fiction-fantasy', 'scifi', 'fantasy-scifi' ],
        'thriller' : ['suspense', 'crime','crime-fiction','thriller','thrillers'],
        'women' : ['women','chick-lit'],
        'horror' : ['horror', 'paranormal', 'supernatural'],
        'children' : ['children', 'childrens', 'childeren-s', 'kids', 'children-s-books', 'childrens-books'],
        'science' : ['science'],
        'philosophy' : ['philosophy'],
    }
    #tags = get_freq_tags()
    #get_genre_from_tags(tags)
    genre_list = []
    for genre in genre_dict.values() :
        genre_list += genre 
    genre_to_tag = get_tag_from_genre(genre_list)
    #print(genre_to_tag)
    #print("genre_dict")
    #print(genre_dict)
    new_genre_dict = {}
    for k, v in genre_dict.items() :
        new_genre_dict[k] = [(genre_to_tag[value], value) for value in v]
    #print(new_genre_dict)

    #from csv file get book info list 
    bookinfo_dict = defaultdict(list)
    f = open('books.csv', 'r', encoding = 'utf-8')
    rdr = csv.reader(f)
    idx = 0
    for line in rdr : 
        if idx == 0 :
            idx+=1
            continue
        print(str(idx)+"/10000")
        #print(len(line))
        #remove (),.*#!?\"\'-
        ref_line = re.sub(r"[(),.*#!?\"\'-]","",line[10])
        before_len = len(ref_line)
        ref_line2 = re.sub(r"[^a-zA-Z\s\d]","",line[10])
        after_len = len(ref_line2)
        if before_len == after_len : 
            #check for the language code(11), should be eng, en-US, en-CA, 
            if line[11] in ['eng', 'en-US', 'en-CA', 'en-GB'] or len(line[11]) == 0 :
                #title(10), author(7), book_id(goodreads_id, 1), rating(12), rated_people(13)
                bookinfo_dict[line[1]] = BookInfo(line[10], line[7], line[1], line[12], line[13])
        idx+=1
    f.close()
    mid = time.strftime('%c', time.localtime(time.time()))
    print("mid : "+mid)
    bookdata_dict = {}
    idx = 1
    dict_len = len(bookinfo_dict)
    total_elapsed = 0
    #print(bookinfo_dict)
    with open('bookinfo_dict.txt','wb') as f :
        pickle.dump(bookinfo_dict, f)
    with open('new_genre_dict.txt','wb') as f :
        pickle.dump(new_genre_dict, f)
    print("pickle saved")
    for tag, bookinfo in list(bookinfo_dict.items()) :
        start_ = time.time()
        print(str(idx)+'/'+str(dict_len))
        #print(tag)
        bookdata_dict[tag] = get_data_from_info(bookinfo)
        end = time.time()
        total_elapsed += end-start_
        avg = total_elapsed/idx
        timeleft = avg*(dict_len - idx)
        print("estimated timeleft : "+str(timeleft/3600) + "h "+str((timeleft%3600)/60)+"m "+str((timeleft%3600)%60))

        if idx%100 == 0  :
            print("saving intermediate result")
            print("check if it is all filled")
            fill_bookdata_with_genre(bookdata_dict, new_genre_dict)
            for k,v in bookdata_dict.items():
                if v.genre == None : 
                    print(k)
            if idx == 100 :
                f = open('bookdata.csv','w',encoding = 'utf-8', newline = '')
            else :
                f = open('bookdata.csv','a',encoding = 'utf-8', newline = '')
            wr = csv.writer(f)
            for v in bookdata_dict.values() :
                wr.writerow(v.to_list())
            f.close()
            bookdata_dict = {} 
        idx+=1

    #bookdata_dict changed
    print("check if it is all filled")
    fill_bookdata_with_genre(bookdata_dict, new_genre_dict)
    for k,v in bookdata_dict.items():
        if v.genre == None : 
            print(k)
    f = open('bookdata.csv','a',encoding = 'utf-8', newline = '')
    wr = csv.writer(f)
    for v in bookdata_dict.values() :
        wr.writerow(v.to_list())
    f.close()
    #with open('bookdata.txt','wb') as f :
    #    pickle.dump(bookdata_dict, f)
    
    #f = open('bookdata.csv','w',encoding = 'utf-8', newline = '')
    #wr = csv.writer(f)
    #for v in bookdata_dict.values() :
    #    wr.writerow(v.to_list())
    #f.close()
    end = time.strftime('%c', time.localtime(time.time()))
    print("start : "+start)
    print("end : "+end)
    print("total : "+str(len(bookdata_dict)) + " books")

def continue_add_data(offset) : 
    with open('bookinfo_dict.txt','rb') as f :
        bookinfo_dict = pickle.load(f)
    with open('new_genre_dict.txt','rb') as f :
        new_genre_dict = pickle.load(f)
    bookdata_dict = {}
    idx = 1
    dict_len = len(bookinfo_dict) - int(offset)
    total_elapsed = 0
    for tag, bookinfo in list(bookinfo_dict.items())[int(offset):] :
        start_ = time.time()
        print(str(int(offset)+idx)+'/'+str(dict_len))
        #print(tag)
        bookdata_dict[tag] = get_data_from_info(bookinfo)
        end = time.time()
        total_elapsed += end-start_
        avg = total_elapsed/idx
        timeleft = avg*(dict_len - idx)
        print("estimated timeleft : "+str(timeleft/3600) + "h "+str((timeleft%3600)/60)+"m "+str((timeleft%3600)%60))

        if idx%100 == 0  :
            print("saving intermediate result")
            print("check if it is all filled")
            fill_bookdata_with_genre(bookdata_dict, new_genre_dict)
            for k,v in list(bookdata_dict.items()):
                if v.genre == None : 
                    print(k)
            f = open('bookdata.csv','a',encoding = 'utf-8', newline = '')
            wr = csv.writer(f)
            for v in bookdata_dict.values() :
                wr.writerow(v.to_list())
            f.close()
            bookdata_dict = {} 
        idx+=1

    #bookdata_dict changed
    print("check if it is all filled")
    fill_bookdata_with_genre(bookdata_dict, new_genre_dict)
    for k,v in bookdata_dict.items():
        if v.genre == None : 
            print(k)
    f = open('bookdata.csv','a',encoding = 'utf-8', newline = '')
    wr = csv.writer(f)
    for v in bookdata_dict.values() :
        wr.writerow(v.to_list())
    f.close()

if __name__ == "__main__":
    main(sys.argv)