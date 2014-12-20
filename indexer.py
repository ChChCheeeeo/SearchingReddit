#!/usr/bin/env python
from util import *
import argparse
import base64
import os
import json

# Two main types of indexes
# -- Forward index
# -- Inverted index

# Forward index
# doc1 -> [learning, python, how, to]
# doc2 -> [learning, C++]
# doc3 -> [python, C++]

# Inverted index
# learning -> [doc1, doc2]
# python -> [doc1, doc3]
# how -> [doc1]
# to -> [doc1]
# C++ -> [doc2, doc3]

# TODO: improve this:
# Indexer assumes that collection fits in RAM
class Indexer(object):
    def __init__(self):
        self.inverted_index = dict()
        self.forward_index  = dict()
        self.url_to_id      = dict()
        self.doc_count      = 0

    # TODO: remove these assumptions
    # assumes that add_document() is never called twice for a document
    # assumes that a document has an unique url
    # parsed_text is a list of words
    def add_document(self, url, parsed_text):
        self.doc_count += 1
        assert url not in self.url_to_id
        current_id = self.doc_count
        self.url_to_id[url] = current_id
        self.forward_index[current_id] = parsed_text
        for position,word in enumerate(parsed_text):
            # TODO: defaultdict
            if word not in self.inverted_index:
                self.inverted_index[word] = []
            self.inverted_index[word].append((position, current_id))
    
    def save_on_disk(self, index_dir):

        def dump_json_to_file(source, file_name):
            file_path = os.path.join(index_dir, file_name)
            json.dump(source, open(file_path, "w"), indent=4)

        dump_json_to_file(self.inverted_index, "inverted_index")
        dump_json_to_file(self.forward_index, "forward_index")
        dump_json_to_file(self.url_to_id, "url_to_id")

class Searcher(object):
    def __init__(self, index_dir):
        self.inverted_index = dict()
        self.forward_index  = dict()
        self.url_to_id      = dict()

        def load_json_from_file(file_name):
            file_path = os.path.join(index_dir, file_name)
            dst = json.load(open(file_path))
            return dst

        self.inverted_index = load_json_from_file("inverted_index")
        self.forward_index = load_json_from_file("forward_index")
        self.url_to_id = load_json_from_file("url_to_id")

        self.id_to_url = {v : k for k,v in self.url_to_id.iteritems()}
    
    # query [word1, word2] -> returns all documents that contain one of these words
    # sort of OR
    def find_documents(self, words):
        return sum([self.inverted_index[word] for word in words], [])

    def get_url(self, id):
        return self.id_to_url[id]


def create_index_from_dir(stored_documents_dir, index_dir):
    indexer = Indexer()
    for filename in os.listdir(stored_documents_dir):
        opened_file = open(os.path.join(stored_documents_dir, filename))
        # TODO: words are separated not just by space, but by commas, semicolons, etc
        parsed_doc = parseRedditPost(opened_file.read()).split(" ")
        indexer.add_document(base64.b16decode(filename), parsed_doc)

    indexer.save_on_disk(index_dir)

def main():
    parser = argparse.ArgumentParser(description='Index /r/learnprogramming')
    parser.add_argument("--stored_documents_dir", dest="stored_documents_dir", required=True)
    parser.add_argument("--index_dir", dest="index_dir", required=True)
    args = parser.parse_args()
    create_index_from_dir(args.stored_documents_dir, args.index_dir)

if __name__ == "__main__": # are we invoking it from cli
    main()
